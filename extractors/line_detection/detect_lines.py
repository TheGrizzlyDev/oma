#!/usr/bin/env python3
"""Detect colored lines in a map image and export GeoJSON LineStrings.

Example:
  python extractors/line_detection/detect_lines.py \
    --image path/to/map.png \
    --bbox 12.0 44.0 12.5 44.5 \
    --polygon "12.1,44.1 12.4,44.1 12.4,44.4 12.1,44.4" \
    --output lines.geojson
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

import numpy as np

try:
    import cv2
except ImportError as exc:  # pragma: no cover - runtime dependency
    raise SystemExit("Missing dependency: opencv-python. Install with 'pip install opencv-python'.") from exc

try:
    from shapely.geometry import LineString, MultiLineString, Polygon
except ImportError as exc:  # pragma: no cover - runtime dependency
    raise SystemExit("Missing dependency: shapely. Install with 'pip install shapely'.") from exc


@dataclass(frozen=True)
class Bounds:
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    def to_world(self, x: float, y: float, width: int, height: int) -> Tuple[float, float]:
        if width <= 1 or height <= 1:
            raise ValueError("Image dimensions must be larger than 1x1.")
        x_ratio = x / (width - 1)
        y_ratio = y / (height - 1)
        world_x = self.min_x + x_ratio * (self.max_x - self.min_x)
        world_y = self.max_y - y_ratio * (self.max_y - self.min_y)
        return world_x, world_y


def load_image(path: str) -> np.ndarray:
    image = cv2.imread(path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Failed to read image at '{path}'.")
    return image


def parse_bbox(values: Sequence[str]) -> Bounds:
    if len(values) != 4:
        raise ValueError("--bbox requires exactly four values: min_x min_y max_x max_y")
    min_x, min_y, max_x, max_y = map(float, values)
    if min_x >= max_x or min_y >= max_y:
        raise ValueError("--bbox values must be ordered as min_x min_y max_x max_y")
    return Bounds(min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y)


def parse_polygon(value: str) -> List[Tuple[float, float]]:
    points = []
    for pair in value.split():
        if "," not in pair:
            raise ValueError("Polygon coordinates must be in 'x,y' format separated by spaces")
        x_str, y_str = pair.split(",", 1)
        points.append((float(x_str), float(y_str)))
    if len(points) < 3:
        raise ValueError("Polygon requires at least three points")
    return points


def extract_color_mask(image: np.ndarray, lower_hsv: Tuple[int, int, int], upper_hsv: Tuple[int, int, int]) -> np.ndarray:
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array(lower_hsv), np.array(upper_hsv))
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
    return mask


def contours_to_lines(
    contours: Iterable[np.ndarray],
    bounds: Bounds,
    width: int,
    height: int,
    simplify_tolerance: float,
    polygon: Polygon | None,
) -> List[LineString]:
    lines: List[LineString] = []
    for contour in contours:
        if contour.shape[0] < 2:
            continue
        arc_length = cv2.arcLength(contour, False)
        epsilon = simplify_tolerance * arc_length if simplify_tolerance > 0 else 0
        simplified = cv2.approxPolyDP(contour, epsilon, False) if epsilon > 0 else contour
        coords = [bounds.to_world(float(point[0][0]), float(point[0][1]), width, height) for point in simplified]
        if len(coords) < 2:
            continue
        line = LineString(coords)
        if polygon is not None:
            clipped = line.intersection(polygon)
            if clipped.is_empty:
                continue
            if isinstance(clipped, LineString):
                lines.append(clipped)
            elif isinstance(clipped, MultiLineString):
                lines.extend(list(clipped.geoms))
            else:
                continue
        else:
            lines.append(line)
    return lines


def lines_to_geojson(lines: Iterable[LineString]) -> dict:
    features = []
    for line in lines:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": list(line.coords),
            },
            "properties": {},
        })
    return {"type": "FeatureCollection", "features": features}


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detect colored lines into GeoJSON")
    parser.add_argument("--image", required=True, help="Path to the source image")
    parser.add_argument(
        "--bbox",
        required=True,
        nargs=4,
        metavar=("MIN_X", "MIN_Y", "MAX_X", "MAX_Y"),
        help="World-coordinate bounds for the image",
    )
    parser.add_argument(
        "--polygon",
        required=True,
        help="Polygon clip region as space-separated x,y pairs",
    )
    parser.add_argument(
        "--output",
        default="-",
        help="Output GeoJSON file (default: stdout)",
    )
    parser.add_argument(
        "--lower-hsv",
        default="100,50,50",
        help="Lower HSV threshold for blue as H,S,V (default: 100,50,50)",
    )
    parser.add_argument(
        "--upper-hsv",
        default="140,255,255",
        help="Upper HSV threshold for blue as H,S,V (default: 140,255,255)",
    )
    parser.add_argument(
        "--simplify",
        type=float,
        default=0.002,
        help="Simplification tolerance as fraction of contour length (default: 0.002)",
    )
    return parser


def parse_hsv(value: str) -> Tuple[int, int, int]:
    parts = value.split(",")
    if len(parts) != 3:
        raise ValueError("HSV must be formatted as H,S,V")
    return tuple(int(part) for part in parts)  # type: ignore[return-value]


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    bounds = parse_bbox(args.bbox)
    polygon_points = parse_polygon(args.polygon)
    polygon = Polygon(polygon_points)
    if not polygon.is_valid:
        polygon = polygon.buffer(0)
    if polygon.is_empty:
        raise SystemExit("Provided polygon is invalid or empty.")

    image = load_image(args.image)
    height, width = image.shape[:2]

    lower_hsv = parse_hsv(args.lower_hsv)
    upper_hsv = parse_hsv(args.upper_hsv)
    mask = extract_color_mask(image, lower_hsv, upper_hsv)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    lines = contours_to_lines(contours, bounds, width, height, args.simplify, polygon)

    geojson = lines_to_geojson(lines)
    output_text = json.dumps(geojson, ensure_ascii=False, indent=2)

    if args.output == "-":
        print(output_text)
    else:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(output_text)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - surface errors
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
