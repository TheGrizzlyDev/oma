#!/usr/bin/env python3
from __future__ import annotations

import argparse
from typing import Tuple

import cv2
import numpy as np

from extractors.line_detection.pipeline_utils import ensure_odd, load_image, load_mask, save_mask


def parse_tuple(value: str) -> Tuple[int, int]:
    parts = value.split(",")
    if len(parts) != 2:
        raise ValueError("Value must be formatted as low,high")
    return int(parts[0]), int(parts[1])


def apply_blur(gray: np.ndarray, blur_type: str, radius: int) -> np.ndarray:
    if blur_type == "none" or radius <= 0:
        return gray
    if blur_type == "gaussian":
        size = ensure_odd(radius)
        return cv2.GaussianBlur(gray, (size, size), 0)
    if blur_type == "median":
        size = ensure_odd(radius)
        return cv2.medianBlur(gray, size)
    if blur_type == "bilateral":
        return cv2.bilateralFilter(gray, radius, radius * 2, radius // 2)
    raise ValueError(f"Unsupported blur type: {blur_type}")


def hysteresis_threshold(gray: np.ndarray, low: int, high: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    strong = (gray >= high).astype(np.uint8) * 255
    weak = (gray >= low).astype(np.uint8) * 255
    labels, count = cv2.connectedComponents(weak)
    output = np.zeros_like(gray, dtype=np.uint8)
    for label in range(1, count):
        component = labels == label
        if np.any(strong[component] > 0):
            output[component] = 255
    return output, strong, weak


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Binarize isolated line pixels with adaptive/hysteresis thresholding.")
    parser.add_argument("--image", required=True, help="Input map image")
    parser.add_argument("--mask", required=True, help="Candidate mask from segmentation")
    parser.add_argument("--output", required=True, help="Binary mask output")
    parser.add_argument("--output-debug", required=True, help="Debug visualization output")
    parser.add_argument("--method", choices=["adaptive", "hysteresis", "global"], default="adaptive")
    parser.add_argument("--adaptive-window", type=int, default=31)
    parser.add_argument("--adaptive-c", type=float, default=2.0)
    parser.add_argument("--hysteresis", default="60,140", help="Low,high thresholds for hysteresis")
    parser.add_argument("--global-threshold", type=int, default=120)
    parser.add_argument("--blur", choices=["none", "gaussian", "median", "bilateral"], default="gaussian")
    parser.add_argument("--blur-radius", type=int, default=3)
    return parser


def main() -> int:
    args = build_parser().parse_args()

    image = load_image(args.image)
    candidate = load_mask(args.mask)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = apply_blur(gray, args.blur, args.blur_radius)
    masked_gray = cv2.bitwise_and(gray, gray, mask=candidate)

    if args.method == "adaptive":
        window = ensure_odd(max(args.adaptive_window, 3))
        thresh = cv2.adaptiveThreshold(
            masked_gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            window,
            args.adaptive_c,
        )
        binary = cv2.bitwise_and(thresh, thresh, mask=candidate)
        debug = cv2.cvtColor(masked_gray, cv2.COLOR_GRAY2BGR)
        debug[thresh > 0] = (255, 255, 255)
    elif args.method == "global":
        _, thresh = cv2.threshold(masked_gray, args.global_threshold, 255, cv2.THRESH_BINARY)
        binary = cv2.bitwise_and(thresh, thresh, mask=candidate)
        debug = cv2.cvtColor(masked_gray, cv2.COLOR_GRAY2BGR)
        debug[thresh > 0] = (255, 255, 255)
    else:
        low, high = parse_tuple(args.hysteresis)
        binary, strong, weak = hysteresis_threshold(masked_gray, low, high)
        binary = cv2.bitwise_and(binary, binary, mask=candidate)
        debug = np.zeros((binary.shape[0], binary.shape[1], 3), dtype=np.uint8)
        debug[weak > 0] = (80, 80, 80)
        debug[strong > 0] = (255, 255, 255)
        debug[binary > 0] = (0, 200, 255)

    save_mask(args.output, binary)
    cv2.imwrite(args.output_debug, debug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
