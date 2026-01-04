#!/usr/bin/env python3
from __future__ import annotations

import argparse
from typing import List, Tuple

import cv2
import numpy as np

from extractors.line_detection.pipeline_utils import load_mask, save_mask


def detect_grid_lines(mask: np.ndarray, min_length: int, max_gap: int) -> List[Tuple[int, int, int, int]]:
    edges = cv2.Canny(mask, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=min_length, maxLineGap=max_gap)
    results: List[Tuple[int, int, int, int]] = []
    if lines is None:
        return results
    for line in lines:
        x1, y1, x2, y2 = line[0]
        results.append((x1, y1, x2, y2))
    return results


def detect_circles(mask: np.ndarray, min_radius: int, max_radius: int, param1: float, param2: float) -> List[Tuple[int, int, int]]:
    blurred = cv2.GaussianBlur(mask, (9, 9), 2)
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=min_radius * 2,
        param1=param1,
        param2=param2,
        minRadius=min_radius,
        maxRadius=max_radius,
    )
    results: List[Tuple[int, int, int]] = []
    if circles is None:
        return results
    for circle in circles[0]:
        x, y, r = circle
        results.append((int(x), int(y), int(r)))
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Suppress known artifacts before skeletonization.")
    parser.add_argument("--mask", required=True, help="Input binary mask")
    parser.add_argument("--output", required=True, help="Masked output")
    parser.add_argument("--output-debug", required=True, help="Debug visualization output")
    parser.add_argument("--roi-mask", help="Optional ROI mask bitmap")
    parser.add_argument("--roi-mode", choices=["exclude", "include"], default="exclude")
    parser.add_argument("--detect-grid", action="store_true")
    parser.add_argument("--grid-min-length", type=int, default=120)
    parser.add_argument("--grid-gap", type=int, default=8)
    parser.add_argument("--grid-thickness", type=int, default=6)
    parser.add_argument("--detect-circles", action="store_true")
    parser.add_argument("--circle-min-radius", type=int, default=30)
    parser.add_argument("--circle-max-radius", type=int, default=200)
    parser.add_argument("--circle-param1", type=float, default=120)
    parser.add_argument("--circle-param2", type=float, default=30)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    mask = load_mask(args.mask)
    suppressed = np.zeros_like(mask)

    if args.roi_mask:
        roi = load_mask(args.roi_mask)
        if args.roi_mode == "exclude":
            suppressed = cv2.bitwise_or(suppressed, roi)
        else:
            mask = cv2.bitwise_and(mask, roi)

    if args.detect_grid:
        lines = detect_grid_lines(mask, args.grid_min_length, args.grid_gap)
        for x1, y1, x2, y2 in lines:
            cv2.line(suppressed, (x1, y1), (x2, y2), 255, args.grid_thickness)

    if args.detect_circles:
        circles = detect_circles(mask, args.circle_min_radius, args.circle_max_radius, args.circle_param1, args.circle_param2)
        for x, y, r in circles:
            cv2.circle(suppressed, (x, y), r, 255, thickness=-1)

    output = cv2.bitwise_and(mask, cv2.bitwise_not(suppressed))
    debug = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    debug[suppressed > 0] = (0, 0, 255)

    save_mask(args.output, output)
    cv2.imwrite(args.output_debug, debug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
