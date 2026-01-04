from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence, Tuple

import cv2
import numpy as np


cv2.setNumThreads(0)
cv2.setRNGSeed(0)


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

    @classmethod
    def from_sequence(cls, values: Sequence[str]) -> "Bounds":
        if len(values) != 4:
            raise ValueError("--bbox requires exactly four values: min_x min_y max_x max_y")
        min_x, min_y, max_x, max_y = map(float, values)
        if min_x >= max_x or min_y >= max_y:
            raise ValueError("--bbox values must be ordered as min_x min_y max_x max_y")
        return cls(min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y)


def load_image(path: str) -> np.ndarray:
    image = cv2.imread(path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Failed to read image at '{path}'.")
    return image


def load_mask(path: str) -> np.ndarray:
    mask = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise ValueError(f"Failed to read mask at '{path}'.")
    _, binary = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY)
    return binary


def save_mask(path: str, mask: np.ndarray) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(path, mask)


def save_json(path: str, payload: dict) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def ensure_odd(value: int) -> int:
    return value if value % 2 == 1 else value + 1


def build_kernel(shape: str, size: int) -> np.ndarray:
    if size <= 0:
        raise ValueError("Kernel size must be positive.")
    if shape == "rect":
        return cv2.getStructuringElement(cv2.MORPH_RECT, (size, size))
    if shape == "ellipse":
        return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))
    if shape == "cross":
        return cv2.getStructuringElement(cv2.MORPH_CROSS, (size, size))
    raise ValueError(f"Unsupported kernel shape: {shape}")


def apply_clahe(gray: np.ndarray, clip_limit: float, tile_size: int) -> np.ndarray:
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
    return clahe.apply(gray)


def mask_to_rgba(mask: np.ndarray, color: Tuple[int, int, int], alpha: int = 200) -> np.ndarray:
    if mask.ndim != 2:
        raise ValueError("Mask must be single-channel.")
    rgba = np.zeros((mask.shape[0], mask.shape[1], 4), dtype=np.uint8)
    for idx, channel in enumerate(color):
        rgba[..., idx] = channel
    rgba[..., 3] = (mask > 0).astype(np.uint8) * alpha
    return rgba


def overlay_images(base: np.ndarray, overlay: np.ndarray) -> np.ndarray:
    if overlay.shape[2] != 4:
        raise ValueError("Overlay must be RGBA.")
    overlay_rgb = overlay[..., :3].astype(np.float32)
    overlay_alpha = overlay[..., 3:4].astype(np.float32) / 255.0
    base_rgb = base.astype(np.float32)
    blended = base_rgb * (1 - overlay_alpha) + overlay_rgb * overlay_alpha
    return np.clip(blended, 0, 255).astype(np.uint8)


def skeleton_neighbors(skeleton: np.ndarray, x: int, y: int) -> Iterable[Tuple[int, int]]:
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < skeleton.shape[1] and 0 <= ny < skeleton.shape[0]:
                if skeleton[ny, nx] > 0:
                    yield nx, ny
