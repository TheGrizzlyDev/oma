#!/usr/bin/env python3
"""Render an HTML viewer to compare an image with its GeoJSON extraction.

Example:
  python extractors/line_detection/visualize_overlay.py \
    --image cam_waterlines_map.png \
    --geojson cam_waterlines.geojson \
    --bbox 0 0 1200 958 \
    --output cam_waterlines_overlay.html
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence, Tuple


def parse_bbox(values: Sequence[str]) -> Tuple[float, float, float, float]:
    if len(values) != 4:
        raise ValueError("--bbox requires exactly four values: min_x min_y max_x max_y")
    min_x, min_y, max_x, max_y = map(float, values)
    if min_x >= max_x or min_y >= max_y:
        raise ValueError("--bbox values must be ordered as min_x min_y max_x max_y")
    return min_x, min_y, max_x, max_y


def resolve_path(target: Path, base: Path) -> str:
    try:
        return str(target.relative_to(base))
    except ValueError:
        return str(target)


def build_html(
    image_path: str,
    geojson: dict,
    bbox: Tuple[float, float, float, float],
    title: str,
    opacity: float,
    crs: str,
) -> str:
    min_x, min_y, max_x, max_y = bbox
    geojson_text = json.dumps(geojson, ensure_ascii=False)
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>{title}</title>
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <link
    rel=\"stylesheet\"
    href=\"https://unpkg.com/leaflet@1.9.4/dist/leaflet.css\"
    integrity=\"sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=\"
    crossorigin=\"\"
  />
  <style>
    html, body {{
      height: 100%;
      margin: 0;
      font-family: "Inter", system-ui, -apple-system, sans-serif;
    }}
    #map {{
      height: 100%;
    }}
    .controls {{
      position: absolute;
      top: 12px;
      left: 12px;
      z-index: 1000;
      background: rgba(255, 255, 255, 0.9);
      padding: 12px 14px;
      border-radius: 10px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
      display: grid;
      gap: 6px;
      min-width: 220px;
    }}
    .controls label {{
      font-size: 14px;
      color: #1d1d1f;
    }}
    .controls input[type=\"range\"] {{
      width: 100%;
    }}
    .legend {{
      font-size: 12px;
      color: #444;
    }}
  </style>
</head>
<body>
  <div class=\"controls\">
    <label for=\"opacity\">Image opacity: <span id=\"opacity-value\">{opacity:.2f}</span></label>
    <input id=\"opacity\" type=\"range\" min=\"0\" max=\"1\" step=\"0.05\" value=\"{opacity:.2f}\">
    <div class=\"legend\">GeoJSON overlay is shown in red.</div>
  </div>
  <div id=\"map\"></div>
  <script
    src=\"https://unpkg.com/leaflet@1.9.4/dist/leaflet.js\"
    integrity=\"sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=\"
    crossorigin=\"\"
  ></script>
  <script>
    const imageUrl = {json.dumps(image_path)};
    const geojsonData = {geojson_text};
    const bounds = [[{min_y}, {min_x}], [{max_y}, {max_x}]];
    const crsMap = {{
      simple: L.CRS.Simple,
      epsg4326: L.CRS.EPSG4326,
      epsg3857: L.CRS.EPSG3857,
    }};
    const crs = crsMap[{json.dumps(crs)}];

    const map = L.map('map', {{
      crs,
      minZoom: -4,
    }});

    const imageLayer = L.imageOverlay(imageUrl, bounds, {{ opacity: {opacity:.2f} }}).addTo(map);
    const lineLayer = L.geoJSON(geojsonData, {{
      style: () => ({{ color: '#ff3b30', weight: 2, opacity: 0.9 }}),
    }}).addTo(map);

    map.fitBounds(bounds, {{ padding: [20, 20] }});

    L.control.layers(
      {{ 'Source image': imageLayer }},
      {{ 'GeoJSON lines': lineLayer }},
      {{ collapsed: false }}
    ).addTo(map);

    const opacityInput = document.getElementById('opacity');
    const opacityValue = document.getElementById('opacity-value');

    opacityInput.addEventListener('input', (event) => {{
      const value = Number(event.target.value);
      imageLayer.setOpacity(value);
      opacityValue.textContent = value.toFixed(2);
    }});
  </script>
</body>
</html>
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create an HTML overlay viewer for an image and GeoJSON.")
    parser.add_argument("--image", required=True, help="Path to the source image")
    parser.add_argument("--geojson", required=True, help="Path to the GeoJSON file")
    parser.add_argument(
        "--bbox",
        required=True,
        nargs=4,
        metavar=("MIN_X", "MIN_Y", "MAX_X", "MAX_Y"),
        help="Bounds for the image and GeoJSON coordinates",
    )
    parser.add_argument(
        "--output",
        default="overlay.html",
        help="Output HTML file (default: overlay.html)",
    )
    parser.add_argument(
        "--title",
        default="Image/GeoJSON Overlay",
        help="HTML page title",
    )
    parser.add_argument(
        "--opacity",
        type=float,
        default=0.65,
        help="Initial opacity for the image overlay (default: 0.65)",
    )
    parser.add_argument(
        "--crs",
        choices=["simple", "epsg4326", "epsg3857"],
        default="simple",
        help="Leaflet CRS for the map (default: simple)",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    bbox = parse_bbox(args.bbox)
    if not 0.0 <= args.opacity <= 1.0:
        raise ValueError("--opacity must be between 0 and 1")

    output_path = Path(args.output)
    image_path = Path(args.image)
    geojson_path = Path(args.geojson)

    with geojson_path.open("r", encoding="utf-8") as handle:
        geojson = json.load(handle)

    image_ref = resolve_path(image_path, output_path.parent)
    html = build_html(image_ref, geojson, bbox, args.title, args.opacity, args.crs)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
