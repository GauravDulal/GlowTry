"""
Debug visualization helpers for GlowTry.

Usage: POST to /debug-landmarks to get an image with landmarks + region outlines drawn.
Or call draw_debug_overlay() from any makeup module to visualize masks.
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional

# ──────────────────────────────────────────────────────────────
# Canonical MediaPipe FaceMesh landmark groups (478-point model)
# These are the CORRECT index sets used by the makeup modules.
# ──────────────────────────────────────────────────────────────

UPPER_LIP_OUTER = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291]
LOWER_LIP_OUTER = [291, 375, 321, 405, 314, 17, 84, 181, 91, 146, 61]
UPPER_LIP_INNER = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308]
LOWER_LIP_INNER = [308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 78]

LEFT_EYE_UPPER_LASHLINE = [33, 7, 163, 144, 145, 153, 154, 155, 133]
LEFT_EYE_LOWER_LASHLINE = [33, 246, 161, 160, 159, 158, 157, 173, 133]
RIGHT_EYE_UPPER_LASHLINE = [362, 382, 381, 380, 374, 373, 390, 249, 263]
RIGHT_EYE_LOWER_LASHLINE = [362, 466, 388, 387, 386, 385, 384, 398, 263]

LEFT_EYEBROW_LOWER = [70, 63, 105, 66, 107]
RIGHT_EYEBROW_LOWER = [300, 293, 334, 296, 336]

LEFT_CHEEK_ANCHORS = [116, 123, 147, 187, 205, 36, 50]
RIGHT_CHEEK_ANCHORS = [345, 352, 376, 411, 425, 266, 280]


# ──── Drawing helpers ────

def draw_landmarks(img: np.ndarray, landmarks: list, indices: Optional[list] = None,
                   color: Tuple[int, int, int] = (0, 255, 0), radius: int = 2) -> np.ndarray:
    """Draw landmark dots on a copy of the image."""
    out = img.copy()
    draw_indices = indices if indices is not None else range(len(landmarks))
    for idx in draw_indices:
        pt = landmarks[idx]
        cv2.circle(out, pt, radius, color, -1, cv2.LINE_AA)
    return out


def draw_polyline(img: np.ndarray, landmarks: list, indices: list,
                  color: Tuple[int, int, int] = (0, 255, 0), thickness: int = 1,
                  closed: bool = False) -> np.ndarray:
    """Draw a polyline through the given landmark indices."""
    out = img.copy()
    pts = np.array([landmarks[i] for i in indices], np.int32)
    cv2.polylines(out, [pts], closed, color, thickness, cv2.LINE_AA)
    return out


def draw_full_debug(img: np.ndarray, landmarks: list) -> np.ndarray:
    """
    Draw all makeup-relevant regions on the image for visual debugging.
    Returns a BGR image with annotations.
    """
    out = img.copy()

    # All 478 landmarks in light gray
    for pt in landmarks:
        cv2.circle(out, pt, 1, (180, 180, 180), -1, cv2.LINE_AA)

    regions = [
        # Lips
        ("Upper lip outer", UPPER_LIP_OUTER, (0, 0, 255), True),
        ("Lower lip outer", LOWER_LIP_OUTER, (0, 0, 200), True),
        ("Upper lip inner", UPPER_LIP_INNER, (0, 100, 255), True),
        ("Lower lip inner", LOWER_LIP_INNER, (0, 100, 200), True),
        # Eyes — upper lash lines (where eyeliner goes)
        ("L upper lashline", LEFT_EYE_UPPER_LASHLINE, (255, 0, 0), False),
        ("R upper lashline", RIGHT_EYE_UPPER_LASHLINE, (255, 0, 0), False),
        # Eyes — lower lash lines (crease, top of eyeshadow region)
        ("L lower crease", LEFT_EYE_LOWER_LASHLINE, (255, 200, 0), False),
        ("R lower crease", RIGHT_EYE_LOWER_LASHLINE, (255, 200, 0), False),
        # Eyebrows
        ("L brow lower", LEFT_EYEBROW_LOWER, (0, 255, 255), False),
        ("R brow lower", RIGHT_EYEBROW_LOWER, (0, 255, 255), False),
    ]

    for name, indices, color, closed in regions:
        pts = np.array([landmarks[i] for i in indices], np.int32)
        cv2.polylines(out, [pts], closed, color, 2, cv2.LINE_AA)
        # Label
        mid_idx = indices[len(indices) // 2]
        mid_pt = landmarks[mid_idx]
        cv2.putText(out, name, (mid_pt[0] + 5, mid_pt[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1, cv2.LINE_AA)

    # Cheek anchor points
    for idx in LEFT_CHEEK_ANCHORS:
        cv2.circle(out, landmarks[idx], 4, (255, 0, 255), -1, cv2.LINE_AA)
    for idx in RIGHT_CHEEK_ANCHORS:
        cv2.circle(out, landmarks[idx], 4, (255, 0, 255), -1, cv2.LINE_AA)

    # Draw cheek ellipses that blush would use
    left_xs = [landmarks[i][0] for i in LEFT_CHEEK_ANCHORS]
    left_ys = [landmarks[i][1] for i in LEFT_CHEEK_ANCHORS]
    right_xs = [landmarks[i][0] for i in RIGHT_CHEEK_ANCHORS]
    right_ys = [landmarks[i][1] for i in RIGHT_CHEEK_ANCHORS]

    lc = (int(np.mean(left_xs)), int(np.mean(left_ys)))
    rc = (int(np.mean(right_xs)), int(np.mean(right_ys)))

    l_rx = max(int((max(left_xs) - min(left_xs)) * 0.65), 1)
    l_ry = max(int((max(left_ys) - min(left_ys)) * 0.55), 1)
    r_rx = max(int((max(right_xs) - min(right_xs)) * 0.65), 1)
    r_ry = max(int((max(right_ys) - min(right_ys)) * 0.55), 1)

    cv2.ellipse(out, lc, (l_rx, l_ry), 0, 0, 360, (255, 0, 255), 2, cv2.LINE_AA)
    cv2.ellipse(out, rc, (r_rx, r_ry), 0, 0, 360, (255, 0, 255), 2, cv2.LINE_AA)

    return out
