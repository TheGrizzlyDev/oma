#!/usr/bin/env python3
from __future__ import annotations

import argparse
from typing import List, Tuple

import cv2
import numpy as np

from extractors.line_detection.pipeline_utils import load_mask, save_mask, skeleton_neighbors


def morphological_skeleton(mask: np.ndarray) -> np.ndarray:
    skeleton = np.zeros_like(mask)
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    working = mask.copy()
    while True:
        opened = cv2.morphologyEx(working, cv2.MORPH_OPEN, kernel)
        temp = cv2.subtract(working, opened)
        skeleton = cv2.bitwise_or(skeleton, temp)
        working = cv2.erode(working, kernel)
        if cv2.countNonZero(working) == 0:
            break
    return skeleton


def find_endpoints_and_junctions(skeleton: np.ndarray) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    endpoints: List[Tuple[int, int]] = []
    junctions: List[Tuple[int, int]] = []
    ys, xs = np.where(skeleton > 0)
    for y, x in zip(ys, xs):
        neighbors = sum(1 for _ in skeleton_neighbors(skeleton, x, y))
        if neighbors == 1:
            endpoints.append((x, y))
        elif neighbors > 2:
            junctions.append((x, y))
    return endpoints, junctions


def prune_spurs(skeleton: np.ndarray, max_length: int) -> np.ndarray:
    if max_length <= 0:
        return skeleton
    pruned = skeleton.copy()
    endpoints, _ = find_endpoints_and_junctions(pruned)
    for endpoint in endpoints:
        path = [endpoint]
        current = endpoint
        prev = None
        while True:
            neighbors = [n for n in skeleton_neighbors(pruned, current[0], current[1]) if n != prev]
            if not neighbors:
                break
            next_pixel = neighbors[0]
            path.append(next_pixel)
            prev, current = current, next_pixel
            neighbor_count = sum(1 for _ in skeleton_neighbors(pruned, current[0], current[1]))
            if neighbor_count != 2:
                break
            if len(path) > max_length:
                break
        if len(path) <= max_length:
            for x, y in path:
                pruned[y, x] = 0
    return pruned


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract a 1-pixel skeleton from a binary mask.")
    parser.add_argument("--mask", required=True, help="Input binary mask")
    parser.add_argument("--output", required=True, help="Skeleton output")
    parser.add_argument("--output-debug", required=True, help="Debug visualization output")
    parser.add_argument("--method", choices=["morphological"], default="morphological")
    parser.add_argument("--prune-spurs", type=int, default=0)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    mask = load_mask(args.mask)

    if args.method == "morphological":
        skeleton = morphological_skeleton(mask)
    else:
        raise ValueError(f"Unsupported method: {args.method}")

    skeleton = prune_spurs(skeleton, args.prune_spurs)

    endpoints, junctions = find_endpoints_and_junctions(skeleton)
    debug = cv2.cvtColor(skeleton, cv2.COLOR_GRAY2BGR)
    for x, y in endpoints:
        cv2.circle(debug, (x, y), 2, (0, 0, 255), -1)
    for x, y in junctions:
        cv2.circle(debug, (x, y), 2, (0, 255, 255), -1)

    save_mask(args.output, skeleton)
    cv2.imwrite(args.output_debug, debug)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
