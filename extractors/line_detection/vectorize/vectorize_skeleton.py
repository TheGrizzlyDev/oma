#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from typing import Dict, List, Sequence, Tuple

import cv2
import numpy as np

from extractors.line_detection.pipeline_utils import Bounds, load_mask, save_json, skeleton_neighbors


def build_graph(skeleton: np.ndarray) -> Tuple[List[Tuple[int, int]], Dict[Tuple[int, int], List[Tuple[int, int]]]]:
    nodes: List[Tuple[int, int]] = []
    adjacency: Dict[Tuple[int, int], List[Tuple[int, int]]] = defaultdict(list)
    ys, xs = np.where(skeleton > 0)
    for y, x in zip(ys, xs):
        neighbors = list(skeleton_neighbors(skeleton, x, y))
        if len(neighbors) != 2:
            nodes.append((x, y))
        for nx, ny in neighbors:
            adjacency[(x, y)].append((nx, ny))
    return nodes, adjacency


def trace_paths(
    nodes: List[Tuple[int, int]],
    adjacency: Dict[Tuple[int, int], List[Tuple[int, int]]],
) -> List[List[Tuple[int, int]]]:
    node_set = set(nodes)
    visited_edges = set()
    paths: List[List[Tuple[int, int]]] = []

    def edge_key(a: Tuple[int, int], b: Tuple[int, int]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        return (a, b) if a <= b else (b, a)

    for node in nodes:
        for neighbor in adjacency.get(node, []):
            key = edge_key(node, neighbor)
            if key in visited_edges:
                continue
            path = [node]
            prev = node
            current = neighbor
            visited_edges.add(key)
            while True:
                path.append(current)
                if current in node_set and current != node:
                    break
                neighbors = [n for n in adjacency.get(current, []) if n != prev]
                if not neighbors:
                    break
                next_pixel = neighbors[0]
                key = edge_key(current, next_pixel)
                if key in visited_edges:
                    break
                visited_edges.add(key)
                prev, current = current, next_pixel
            if len(path) > 1:
                paths.append(path)
    return paths


def bridge_gaps(paths: List[List[Tuple[int, int]]], tolerance: float) -> List[List[Tuple[int, int]]]:
    if tolerance <= 0:
        return paths
    endpoints = []
    for index, path in enumerate(paths):
        endpoints.append((index, 0, path[0]))
        endpoints.append((index, -1, path[-1]))
    merged = paths[:]
    used = set()
    for i, (idx_a, pos_a, pt_a) in enumerate(endpoints):
        if i in used:
            continue
        for j, (idx_b, pos_b, pt_b) in enumerate(endpoints[i + 1 :], start=i + 1):
            if j in used:
                continue
            dist = np.hypot(pt_a[0] - pt_b[0], pt_a[1] - pt_b[1])
            if dist <= tolerance:
                if idx_a == idx_b:
                    continue
                path_a = merged[idx_a]
                path_b = merged[idx_b]
                if pos_a == 0:
                    path_a = list(reversed(path_a))
                if pos_b == -1:
                    path_b = list(reversed(path_b))
                merged[idx_a] = path_a + path_b
                merged[idx_b] = []
                used.update({i, j})
                break
    return [path for path in merged if path]


def to_geojson(paths: Sequence[Sequence[Tuple[int, int]]], bounds: Bounds, width: int, height: int) -> dict:
    features = []
    for path in paths:
        coords = [bounds.to_world(float(x), float(y), width, height) for x, y in path]
        if len(coords) < 2:
            continue
        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {},
        })
    return {"type": "FeatureCollection", "features": features}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Vectorize a skeleton mask into GeoJSON LineStrings.")
    parser.add_argument("--mask", required=True, help="Skeleton mask input")
    parser.add_argument("--bbox", required=True, nargs=4, metavar=("MIN_X", "MIN_Y", "MAX_X", "MAX_Y"))
    parser.add_argument("--output", required=True, help="GeoJSON output")
    parser.add_argument("--output-debug", required=True, help="Debug image output")
    parser.add_argument("--output-stats", required=True, help="JSON stats output")
    parser.add_argument("--min-path-length", type=int, default=10)
    parser.add_argument("--gap-bridge", type=float, default=0.0)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    skeleton = load_mask(args.mask)
    height, width = skeleton.shape[:2]
    bounds = Bounds.from_sequence(args.bbox)

    nodes, adjacency = build_graph(skeleton)
    raw_paths = trace_paths(nodes, adjacency)
    bridged_paths = bridge_gaps(raw_paths, args.gap_bridge)
    filtered_paths = [path for path in bridged_paths if len(path) >= args.min_path_length]

    geojson = to_geojson(filtered_paths, bounds, width, height)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(geojson, handle, ensure_ascii=False, indent=2)

    debug = cv2.cvtColor(skeleton, cv2.COLOR_GRAY2BGR)
    for x, y in nodes:
        cv2.circle(debug, (x, y), 2, (0, 255, 255), -1)
    cv2.imwrite(args.output_debug, debug)

    save_json(
        args.output_stats,
        {
            "nodes": len(nodes),
            "paths_raw": len(raw_paths),
            "paths_filtered": len(filtered_paths),
            "min_path_length": args.min_path_length,
            "gap_bridge": args.gap_bridge,
        },
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
