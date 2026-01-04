#!/usr/bin/env python3
from __future__ import annotations

import argparse
from typing import Iterable, Tuple

import cv2
import numpy as np

from extractors.line_detection.pipeline_utils import apply_clahe, load_image, save_mask


def parse_tuple(value: str) -> Tuple[int, int, int]:
    parts = value.split(",")
    if len(parts) != 3:
        raise ValueError("Value must be formatted as v1,v2,v3")
    return tuple(int(part) for part in parts)  # type: ignore[return-value]


def select_channels(image: np.ndarray, channels: Iterable[int]) -> np.ndarray:
    channel_list = list(channels)
    if not channel_list:
        return image
    return image[..., channel_list]


def threshold_mask(image: np.ndarray, lower: Tuple[int, int, int], upper: Tuple[int, int, int]) -> np.ndarray:
    lower_array = np.array(lower, dtype=np.uint8)
    upper_array = np.array(upper, dtype=np.uint8)
    return cv2.inRange(image, lower_array, upper_array)


def merge_masks(conservative: np.ndarray, aggressive: np.ndarray, strategy: str, radius: int) -> np.ndarray:
    if strategy == "union":
        return cv2.bitwise_or(conservative, aggressive)
    if strategy == "seed_proximity":
        if radius <= 0:
            return conservative
        dist = cv2.distanceTransform(255 - conservative, cv2.DIST_L2, 3)
        near = (dist <= radius).astype(np.uint8) * 255
        gated_aggressive = cv2.bitwise_and(aggressive, near)
        return cv2.bitwise_or(conservative, gated_aggressive)
    raise ValueError(f"Unsupported merge strategy: {strategy}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Segment candidate line pixels from a map image.")
    parser.add_argument("--image", required=True, help="Input map image")
    parser.add_argument("--output-conservative", required=True, help="Conservative mask output")
    parser.add_argument("--output-aggressive", required=True, help="Aggressive mask output")
    parser.add_argument("--output-merged", required=True, help="Merged mask output")
    parser.add_argument("--output-debug", required=True, help="Debug overlay output")
    parser.add_argument("--colorspace", choices=["hsv", "lab", "gray"], default="hsv")
    parser.add_argument("--channels", default="0,1,2", help="Comma-separated channel indices")
    parser.add_argument("--lower", required=True, help="Lower threshold (v1,v2,v3)")
    parser.add_argument("--upper", required=True, help="Upper threshold (v1,v2,v3)")
    parser.add_argument("--aggressive-lower", help="Aggressive lower threshold (v1,v2,v3)")
    parser.add_argument("--aggressive-upper", help="Aggressive upper threshold (v1,v2,v3)")
    parser.add_argument("--merge-strategy", choices=["seed_proximity", "union"], default="seed_proximity")
    parser.add_argument("--merge-radius", type=int, default=4)
    parser.add_argument("--clahe", action="store_true", help="Enable CLAHE contrast normalization")
    parser.add_argument("--clahe-clip", type=float, default=2.0)
    parser.add_argument("--clahe-tile", type=int, default=8)
    return parser


def main() -> int:
    args = build_parser().parse_args()

    image = load_image(args.image)
    if args.colorspace == "hsv":
        converted = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    elif args.colorspace == "lab":
        converted = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    else:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if args.clahe:
            gray = apply_clahe(gray, args.clahe_clip, args.clahe_tile)
        converted = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    channels = [int(item) for item in args.channels.split(",") if item.strip() != ""]
    converted = select_channels(converted, channels)

    lower = parse_tuple(args.lower)
    upper = parse_tuple(args.upper)
    conservative = threshold_mask(converted, lower, upper)

    aggressive_lower = parse_tuple(args.aggressive_lower) if args.aggressive_lower else lower
    aggressive_upper = parse_tuple(args.aggressive_upper) if args.aggressive_upper else upper
    aggressive = threshold_mask(converted, aggressive_lower, aggressive_upper)

    merged = merge_masks(conservative, aggressive, args.merge_strategy, args.merge_radius)

    debug = np.zeros((merged.shape[0], merged.shape[1], 3), dtype=np.uint8)
    debug[aggressive > 0] = (255, 0, 0)
    debug[conservative > 0] = (0, 255, 0)
    debug[merged > 0] = (0, 0, 255)

    save_mask(args.output_conservative, conservative)
    save_mask(args.output_aggressive, aggressive)
    save_mask(args.output_merged, merged)
    cv2.imwrite(args.output_debug, debug)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
