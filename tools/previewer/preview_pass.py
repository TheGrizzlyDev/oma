#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np

from extractors.line_detection.pipeline_utils import Bounds, load_image, load_mask, mask_to_rgba
from tools.previewer.preview_utils import (
    PreviewAsset,
    build_asset_list,
    build_debug_section,
    build_opacity_panels,
    build_parameters_section,
    encode_png,
    wrap_html,
)


def render_geojson_overlay(geojson: dict, bounds: Bounds, width: int, height: int) -> np.ndarray:
    overlay = np.zeros((height, width, 4), dtype=np.uint8)
    for feature in geojson.get("features", []):
        coords = feature.get("geometry", {}).get("coordinates", [])
        points = []
        for x, y in coords:
            x_ratio = (x - bounds.min_x) / (bounds.max_x - bounds.min_x)
            y_ratio = (bounds.max_y - y) / (bounds.max_y - bounds.min_y)
            px = int(round(x_ratio * (width - 1)))
            py = int(round(y_ratio * (height - 1)))
            points.append((px, py))
        if len(points) >= 2:
            cv2.polylines(overlay, [np.array(points, dtype=np.int32)], False, (255, 0, 0, 200), 2)
    return overlay


def load_assets(path: Optional[str]) -> List[PreviewAsset]:
    if not path:
        return []
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    assets = []
    for asset in data:
        assets.append(PreviewAsset(label=asset.get("label", ""), path=asset.get("path", "")))
    return assets


def load_parameters(path: Optional[str]) -> dict:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate HTML previews with multi-opacity overlays.")
    parser.add_argument("--image", required=True, help="Background image")
    parser.add_argument("--mask", help="Binary mask to overlay")
    parser.add_argument("--geojson", help="GeoJSON overlay instead of mask")
    parser.add_argument("--bbox", nargs=4, metavar=("MIN_X", "MIN_Y", "MAX_X", "MAX_Y"))
    parser.add_argument("--overlay-color", default="0,200,255", help="Overlay color as R,G,B")
    parser.add_argument("--debug", action="append", default=[], help="Debug image paths")
    parser.add_argument("--assets-json", help="JSON list of build assets")
    parser.add_argument("--params-json", help="JSON parameters for the pass")
    parser.add_argument("--title", default="Line detection preview")
    parser.add_argument("--output", required=True, help="HTML output")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if not args.mask and not args.geojson:
        raise ValueError("Provide --mask or --geojson for overlay generation")

    image = load_image(args.image)
    height, width = image.shape[:2]

    overlay_rgba: Optional[np.ndarray] = None
    if args.mask:
        mask = load_mask(args.mask)
        color = tuple(int(c) for c in args.overlay_color.split(","))
        overlay_rgba = mask_to_rgba(mask, color)
    else:
        if not args.bbox:
            raise ValueError("--bbox is required for GeoJSON overlays")
        bounds = Bounds.from_sequence(args.bbox)
        geojson = json.loads(Path(args.geojson).read_text(encoding="utf-8"))
        overlay_rgba = render_geojson_overlay(geojson, bounds, width, height)

    overlay_png = encode_png(overlay_rgba)

    debug_images = []
    for debug_path in args.debug:
        debug_image = cv2.imread(debug_path, cv2.IMREAD_UNCHANGED)
        if debug_image is None:
            continue
        debug_images.append((Path(debug_path).stem, encode_png(debug_image)))

    assets = load_assets(args.assets_json)
    parameters = load_parameters(args.params_json)

    image_png = encode_png(image)
    panels = build_opacity_panels(image_png, overlay_png)
    assets_html = build_asset_list(assets)
    parameters_html = build_parameters_section(parameters)
    debug_html = build_debug_section(debug_images)

    html = wrap_html(args.title, panels, assets_html, parameters_html, debug_html)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
