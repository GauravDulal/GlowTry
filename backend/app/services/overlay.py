from __future__ import annotations

import cv2
import numpy as np


def _ensure_uint8_bgr(img: np.ndarray) -> np.ndarray:
    if img.dtype != np.uint8:
        img = np.clip(img, 0, 255).astype(np.uint8)
    if img.ndim != 3 or img.shape[2] != 3:
        raise ValueError("Expected BGR image with 3 channels.")
    return img


def feather_mask(mask: np.ndarray, feather_px: int) -> np.ndarray:
    """
    mask: uint8 [0..255]
    returns float32 [0..1] blurred.
    """
    feather_px = max(1, int(feather_px))
    k = feather_px * 2 + 1
    blurred = cv2.GaussianBlur(mask, (k, k), sigmaX=0, sigmaY=0)
    return (blurred.astype(np.float32) / 255.0).clip(0.0, 1.0)


def fill_polygon_mask(shape_hw: tuple[int, int], poly: np.ndarray) -> np.ndarray:
    h, w = shape_hw
    m = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(m, [poly], 255)
    return m


def subtract_polygon(mask: np.ndarray, poly: np.ndarray) -> np.ndarray:
    cv2.fillPoly(mask, [poly], 0)
    return mask


def alpha_blend_color(
    base_bgr: np.ndarray,
    mask_f: np.ndarray,
    color_bgr: tuple[int, int, int],
    strength: float,
) -> np.ndarray:
    """
    strength: 0..1 global multiplier, mask_f already 0..1.
    """
    base_bgr = _ensure_uint8_bgr(base_bgr)
    h, w = base_bgr.shape[:2]
    if mask_f.shape[:2] != (h, w):
        raise ValueError("Mask size mismatch.")

    a = (mask_f * float(np.clip(strength, 0.0, 1.0))).astype(np.float32)
    a3 = np.dstack([a, a, a])
    color = np.zeros_like(base_bgr, dtype=np.float32)
    color[:, :] = np.array(color_bgr, dtype=np.float32)

    out = base_bgr.astype(np.float32) * (1.0 - a3) + color * a3
    return np.clip(out, 0, 255).astype(np.uint8)


def add_soft_circle(
    base_bgr: np.ndarray,
    center_xy: tuple[int, int],
    radius_px: int,
    color_bgr: tuple[int, int, int],
    strength: float,
    feather_px: int,
) -> np.ndarray:
    base_bgr = _ensure_uint8_bgr(base_bgr)
    h, w = base_bgr.shape[:2]
    cx, cy = center_xy
    cx = int(np.clip(cx, 0, w - 1))
    cy = int(np.clip(cy, 0, h - 1))
    radius_px = max(1, int(radius_px))

    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, (cx, cy), radius_px, 255, thickness=-1)
    mask_f = feather_mask(mask, feather_px=feather_px)
    return alpha_blend_color(base_bgr, mask_f, color_bgr=color_bgr, strength=strength)


def add_soft_polygon(
    base_bgr: np.ndarray,
    poly: np.ndarray,
    color_bgr: tuple[int, int, int],
    strength: float,
    feather_px: int,
    cutout_poly: np.ndarray | None = None,
) -> np.ndarray:
    base_bgr = _ensure_uint8_bgr(base_bgr)
    h, w = base_bgr.shape[:2]
    mask = fill_polygon_mask((h, w), poly)
    if cutout_poly is not None and len(cutout_poly) >= 3:
        subtract_polygon(mask, cutout_poly)
    mask_f = feather_mask(mask, feather_px=feather_px)
    return alpha_blend_color(base_bgr, mask_f, color_bgr=color_bgr, strength=strength)


def add_liner_hint(
    base_bgr: np.ndarray,
    eye_poly: np.ndarray,
    strength: float,
) -> np.ndarray:
    """
    Minimalistic "liner": draw a thin polyline around the eye ring and blend softly.
    Kept subtle to avoid uncanny edges.
    """
    base_bgr = _ensure_uint8_bgr(base_bgr)
    h, w = base_bgr.shape[:2]
    strength = float(np.clip(strength, 0.0, 1.0))
    if strength <= 0:
        return base_bgr

    mask = np.zeros((h, w), dtype=np.uint8)
    pts = eye_poly.astype(np.int32)
    cv2.polylines(mask, [pts], isClosed=True, color=255, thickness=2)
    mask_f = feather_mask(mask, feather_px=10)
    # Darken slightly (not pure black).
    return alpha_blend_color(base_bgr, mask_f, color_bgr=(20, 20, 20), strength=0.35 * strength)

