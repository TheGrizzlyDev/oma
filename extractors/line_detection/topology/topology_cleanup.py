#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from typing import Dict, List, Tuple

from shapely.geometry import LineString, MultiLineString, mapping, shape


def collect_lines(geojson: dict) -> List[LineString]:
    lines: List[LineString] = []
    for feature in geojson.get("features", []):
        geometry = shape(feature.get("geometry"))
        if isinstance(geometry, LineString):
            lines.append(geometry)
        elif isinstance(geometry, MultiLineString):
            lines.extend(list(geometry.geoms))
    return lines


def prune_spurs(lines: List[LineString], min_length: float) -> List[LineString]:
    if min_length <= 0:
        return lines
    return [line for line in lines if line.length >= min_length]


def cluster_endpoints(lines: List[LineString], tolerance: float) -> Dict[Tuple[float, float], Tuple[float, float]]:
    if tolerance <= 0:
        return {}
    points: List[Tuple[float, float]] = []
    for line in lines:
        coords = list(line.coords)
        points.append(coords[0])
        points.append(coords[-1])

    clusters: Dict[int, List[Tuple[float, float]]] = {}
    assignments: Dict[int, int] = {}

    for idx, point in enumerate(points):
        assigned = False
        for cluster_id, members in clusters.items():
            cx, cy = members[0]
            if ((point[0] - cx) ** 2 + (point[1] - cy) ** 2) ** 0.5 <= tolerance:
                members.append(point)
                assignments[idx] = cluster_id
                assigned = True
                break
        if not assigned:
            cluster_id = len(clusters)
            clusters[cluster_id] = [point]
            assignments[idx] = cluster_id

    snapped: Dict[Tuple[float, float], Tuple[float, float]] = {}
    for members in clusters.values():
        xs = [p[0] for p in members]
        ys = [p[1] for p in members]
        centroid = (sum(xs) / len(xs), sum(ys) / len(ys))
        for point in members:
            snapped[point] = centroid
    return snapped


def apply_snapping(lines: List[LineString], snapped: Dict[Tuple[float, float], Tuple[float, float]]) -> List[LineString]:
    if not snapped:
        return lines
    output: List[LineString] = []
    for line in lines:
        coords = list(line.coords)
        start = snapped.get(coords[0], coords[0])
        end = snapped.get(coords[-1], coords[-1])
        coords[0] = start
        coords[-1] = end
        output.append(LineString(coords))
    return output


def simplify_lines(lines: List[LineString], epsilon: float) -> List[LineString]:
    if epsilon <= 0:
        return lines
    return [line.simplify(epsilon, preserve_topology=True) for line in lines]


def smooth_line(line: LineString, iterations: int) -> LineString:
    coords = list(line.coords)
    for _ in range(iterations):
        if len(coords) < 3:
            break
        new_coords = [coords[0]]
        for i in range(len(coords) - 1):
            p0 = coords[i]
            p1 = coords[i + 1]
            q = (0.75 * p0[0] + 0.25 * p1[0], 0.75 * p0[1] + 0.25 * p1[1])
            r = (0.25 * p0[0] + 0.75 * p1[0], 0.25 * p0[1] + 0.75 * p1[1])
            new_coords.extend([q, r])
        new_coords[-1] = coords[-1]
        coords = new_coords
    return LineString(coords)


def smooth_lines(lines: List[LineString], iterations: int) -> List[LineString]:
    if iterations <= 0:
        return lines
    return [smooth_line(line, iterations) for line in lines]


def build_geojson(lines: List[LineString]) -> dict:
    return {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": mapping(line), "properties": {}}
            for line in lines
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cleanup line topology after vectorization.")
    parser.add_argument("--input", required=True, help="Input GeoJSON")
    parser.add_argument("--output", required=True, help="Cleaned GeoJSON")
    parser.add_argument("--output-debug", required=True, help="Debug stats JSON")
    parser.add_argument("--spur-length", type=float, default=0.0)
    parser.add_argument("--snap-tolerance", type=float, default=0.0)
    parser.add_argument("--simplify", type=float, default=0.0)
    parser.add_argument("--smooth-iterations", type=int, default=0)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    data = json.loads(open(args.input, "r", encoding="utf-8").read())
    lines = collect_lines(data)
    original_count = len(lines)

    lines = prune_spurs(lines, args.spur_length)
    snapped = cluster_endpoints(lines, args.snap_tolerance)
    lines = apply_snapping(lines, snapped)
    lines = simplify_lines(lines, args.simplify)
    lines = smooth_lines(lines, args.smooth_iterations)

    result = build_geojson(lines)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)

    debug = {
        "input_lines": original_count,
        "output_lines": len(lines),
        "spur_length": args.spur_length,
        "snap_tolerance": args.snap_tolerance,
        "simplify": args.simplify,
        "smooth_iterations": args.smooth_iterations,
    }
    with open(args.output_debug, "w", encoding="utf-8") as handle:
        json.dump(debug, handle, ensure_ascii=False, indent=2)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
