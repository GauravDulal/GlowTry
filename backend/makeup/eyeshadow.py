import numpy as np
import cv2
from utils import alpha_blend

# ── Eyeshadow region landmarks ──
# The eyeshadow region is bounded by:
#   TOP:    lower edge of the eyebrow (crease line)
#   BOTTOM: upper eyelid lash line
# We build a closed polygon: brow-bottom going left→right, then lashline going right→left.

LEFT_EYEBROW_LOWER = [70, 63, 105, 66, 107]
LEFT_UPPER_LASHLINE = [33, 7, 163, 144, 145, 153, 154, 155, 133]

RIGHT_EYEBROW_LOWER = [300, 293, 334, 296, 336]
RIGHT_UPPER_LASHLINE = [362, 382, 381, 380, 374, 373, 390, 249, 263]


def _eyelid_polygon(landmarks: list, brow_indices: list, lash_indices: list) -> np.ndarray:
    """
    Create a closed polygon for the upper eyelid region.
    Goes along the brow bottom edge left→right, then along the upper lash line right→left.
    """
    # Brow bottom points (left→right)
    brow_pts = [landmarks[i] for i in brow_indices]
    # Upper lash line reversed so the polygon closes cleanly
    lash_pts = [landmarks[i] for i in reversed(lash_indices)]
    return np.array(brow_pts + lash_pts, np.int32)


def apply_eyeshadow(img: np.ndarray, landmarks: list, kwargs: dict) -> np.ndarray:
    """Apply eyeshadow to the upper eyelid only (crease to lash line)."""
    color = kwargs.get("color", [150, 100, 200])  # Purple default (RGB)
    intensity = kwargs.get("intensity", 0.4)

    if intensity <= 0:
        return img

    h, w, _ = img.shape

    left_lid = _eyelid_polygon(landmarks, LEFT_EYEBROW_LOWER, LEFT_UPPER_LASHLINE)
    right_lid = _eyelid_polygon(landmarks, RIGHT_EYEBROW_LOWER, RIGHT_UPPER_LASHLINE)

    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(mask, [left_lid], 255)
    cv2.fillPoly(mask, [right_lid], 255)

    # Adaptive feathering based on eye width
    eye_width = abs(landmarks[33][0] - landmarks[133][0])
    blur_k = max(5, int(eye_width * 0.15) | 1)  # ensure odd
    mask = cv2.GaussianBlur(mask, (blur_k, blur_k), 0)

    overlay = np.zeros_like(img)
    overlay[:] = color[::-1]  # RGB → BGR

    return alpha_blend(img, overlay, mask, intensity)
