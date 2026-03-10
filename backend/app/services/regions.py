from __future__ import annotations

import numpy as np


def _poly(pts: np.ndarray, idx: list[int]) -> np.ndarray:
    return pts[idx].astype(np.int32)


# MediaPipe FaceMesh landmark indices for key regions.
# These are stable indices from the canonical 468-point mesh.
# References (conceptually): FACEMESH_LIPS, FACEMESH_LEFT_EYE, FACEMESH_RIGHT_EYE.

# Lips: outer contour (approx) + inner contour (for cutout)
OUTER_LIPS = [
    61,
    146,
    91,
    181,
    84,
    17,
    314,
    405,
    321,
    375,
    291,
    308,
    324,
    318,
    402,
    317,
    14,
    87,
    178,
    88,
    95,
    78,
]

INNER_LIPS = [
    78,
    191,
    80,
    81,
    82,
    13,
    312,
    311,
    310,
    415,
    308,
    324,
    318,
    402,
    317,
    14,
    87,
    178,
    88,
    95,
]


# Eye regions (approx eyelid/shadow area) using ring points.
LEFT_EYE_RING = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_RING = [362, 385, 387, 263, 373, 380]

# Brows help expand shadow upwards slightly (a few brow points).
LEFT_BROW = [70, 63, 105, 66]
RIGHT_BROW = [300, 293, 334, 296]


def lip_polygons(pts_xy: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return _poly(pts_xy, OUTER_LIPS), _poly(pts_xy, INNER_LIPS)


def eye_polygons(pts_xy: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    left = _poly(pts_xy, LEFT_EYE_RING + LEFT_BROW)
    right = _poly(pts_xy, RIGHT_EYE_RING + RIGHT_BROW)
    return left, right


def cheek_centers(pts_xy: np.ndarray) -> tuple[tuple[int, int], tuple[int, int]]:
    # Cheekbone-ish anchors:
    # left: 234, right: 454 are commonly used for cheeks.
    left = tuple(np.round(pts_xy[234]).astype(int).tolist())
    right = tuple(np.round(pts_xy[454]).astype(int).tolist())
    return left, right


def face_scale_px(pts_xy: np.ndarray) -> float:
    # Distance between temples-ish points gives robust scale.
    a = pts_xy[234]
    b = pts_xy[454]
    return float(np.linalg.norm(a - b))

