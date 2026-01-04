#!/usr/bin/env python3
from __future__ import annotations

import argparse

import cv2
import numpy as np

from extractors.line_detection.pipeline_utils import build_kernel, load_mask, save_json, save_mask


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Repair gaps and remove small artifacts from a binary mask.")
    parser.add_argument("--mask", required=True, help="Binary mask input")
    parser.add_argument("--output", required=True, help="Filtered mask output")
    parser.add_argument("--output-debug", required=True, help="Debug image output")
    parser.add_argument("--output-stats", required=True, help="JSON stats output")
    parser.add_argument("--do-close", action="store_true")
    parser.add_argument("--do-open", action="store_true")
    parser.add_argument("--close-kernel", type=int, default=3)
    parser.add_argument("--open-kernel", type=int, default=3)
    parser.add_argument("--kernel-shape", choices=["rect", "ellipse", "cross"], default="ellipse")
    parser.add_argument("--close-iterations", type=int, default=1)
    parser.add_argument("--open-iterations", type=int, default=1)
    parser.add_argument("--min-area", type=int, default=20)
    parser.add_argument("--min-extent", type=int, default=10)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    mask = load_mask(args.mask)

    processed = mask.copy()
    if args.do_close:
        kernel = build_kernel(args.kernel_shape, args.close_kernel)
        processed = cv2.morphologyEx(processed, cv2.MORPH_CLOSE, kernel, iterations=args.close_iterations)
    if args.do_open:
        kernel = build_kernel(args.kernel_shape, args.open_kernel)
        processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, kernel, iterations=args.open_iterations)

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(processed, connectivity=8)
    kept = np.zeros_like(processed)
    removed = np.zeros_like(processed)
    removed_count = 0
    kept_count = 0
    for label in range(1, num_labels):
        x, y, w, h, area = stats[label]
        extent = max(w, h)
        component = labels == label
        if area >= args.min_area and extent >= args.min_extent:
            kept[component] = 255
            kept_count += 1
        else:
            removed[component] = 255
            removed_count += 1

    debug = cv2.cvtColor(kept, cv2.COLOR_GRAY2BGR)
    debug[removed > 0] = (0, 0, 255)

    save_mask(args.output, kept)
    cv2.imwrite(args.output_debug, debug)
    save_json(
        args.output_stats,
        {
            "components_total": int(num_labels - 1),
            "components_kept": int(kept_count),
            "components_removed": int(removed_count),
            "min_area": args.min_area,
            "min_extent": args.min_extent,
        },
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
