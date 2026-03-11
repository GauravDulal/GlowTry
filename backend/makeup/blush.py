import numpy as np
import cv2
from utils import alpha_blend

# ── Cheek anchor landmarks ──
# These are on the cheekbone area: below the outer eye corner, above the jawline.
# Chosen to center the ellipse on the apple of the cheek.
LEFT_CHEEK_ANCHORS = [116, 123, 147, 187, 205, 36, 50]
RIGHT_CHEEK_ANCHORS = [345, 352, 376, 411, 425, 266, 280]

# Nose tip for symmetry reference
NOSE_TIP = 1


def _cheek_ellipse(landmarks: list, anchor_indices: list):
    """
    Compute an ellipse center and radii from a set of cheek anchor landmarks.
    Returns (center_x, center_y), (radius_x, radius_y).
    """
    xs = [landmarks[i][0] for i in anchor_indices]
    ys = [landmarks[i][1] for i in anchor_indices]
    cx = int(np.mean(xs))
    cy = int(np.mean(ys))
    rx = max(int((max(xs) - min(xs)) * 0.65), 1)
    ry = max(int((max(ys) - min(ys)) * 0.55), 1)
    return (cx, cy), (rx, ry)


def apply_blush(img: np.ndarray, landmarks: list, kwargs: dict) -> np.ndarray:
    """Apply blush with correctly anchored, per-side ellipses."""
    color = kwargs.get("color", [255, 105, 180])  # Hot pink default (RGB)
    intensity = kwargs.get("intensity", 0.5)

    if intensity <= 0:
        return img

    h, w, _ = img.shape

    # Compute per-cheek ellipses (fixes the old bug of using left-side data for both)
    left_center, (l_rx, l_ry) = _cheek_ellipse(landmarks, LEFT_CHEEK_ANCHORS)
    right_center, (r_rx, r_ry) = _cheek_ellipse(landmarks, RIGHT_CHEEK_ANCHORS)

    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.ellipse(mask, left_center, (l_rx, l_ry), 0, 0, 360, 255, -1)
    cv2.ellipse(mask, right_center, (r_rx, r_ry), 0, 0, 360, 255, -1)

    # Adaptive blur — kernel proportional to face width for consistent softness
    face_width = abs(landmarks[234][0] - landmarks[454][0])  # ear-to-ear
    blur_k = max(31, int(face_width * 0.3) | 1)  # ensure odd, minimum 31
    mask = cv2.GaussianBlur(mask, (blur_k, blur_k), 0)

    overlay = np.zeros_like(img)
    overlay[:] = color[::-1]  # RGB → BGR

    return alpha_blend(img, overlay, mask, intensity)
