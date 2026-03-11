import numpy as np
import cv2
from utils import alpha_blend

# ── Upper lash line landmarks (the actual lash line, NOT the crease) ──
# Ordered inner corner → outer corner.
LEFT_UPPER_LASHLINE = [33, 7, 163, 144, 145, 153, 154, 155, 133]
RIGHT_UPPER_LASHLINE = [362, 382, 381, 380, 374, 373, 390, 249, 263]

# Eye corner landmarks for wing calculation
LEFT_INNER_CORNER = 133
LEFT_OUTER_CORNER = 33
RIGHT_INNER_CORNER = 362
RIGHT_OUTER_CORNER = 263


def _wing_endpoint(landmarks: list, outer_idx: int, inner_idx: int, eye_width: float):
    """
    Calculate a wing endpoint that extends from the outer eye corner
    at an upward angle, scaled relative to eye width.
    """
    outer = np.array(landmarks[outer_idx], dtype=np.float64)
    inner = np.array(landmarks[inner_idx], dtype=np.float64)

    # Direction vector from inner to outer corner
    direction = outer - inner
    direction = direction / (np.linalg.norm(direction) + 1e-6)

    # Rotate upward by ~30 degrees for a classic wing angle
    cos_a, sin_a = np.cos(-0.52), np.sin(-0.52)  # -30 deg (upward)
    rotated = np.array([
        direction[0] * cos_a - direction[1] * sin_a,
        direction[0] * sin_a + direction[1] * cos_a,
    ])

    wing_length = eye_width * 0.25
    wing_end = outer + rotated * wing_length
    return tuple(wing_end.astype(int))


def apply_eyeliner(img: np.ndarray, landmarks: list, kwargs: dict) -> np.ndarray:
    """Apply eyeliner along the upper lash line with optional wing."""
    color = kwargs.get("color", [0, 0, 0])  # Black default (RGB)
    intensity = kwargs.get("intensity", 0.7)
    thickness = kwargs.get("thickness", 2)
    wing_enabled = kwargs.get("wing", False)

    if intensity <= 0:
        return img

    h, w, _ = img.shape

    # Scale thickness relative to face size so it looks consistent across resolutions
    face_width = abs(landmarks[234][0] - landmarks[454][0])
    scaled_thickness = max(1, int(thickness * face_width / 300))

    left_pts = np.array([landmarks[i] for i in LEFT_UPPER_LASHLINE], np.int32)
    right_pts = np.array([landmarks[i] for i in RIGHT_UPPER_LASHLINE], np.int32)

    mask = np.zeros((h, w), dtype=np.uint8)

    # Draw the lash lines
    cv2.polylines(mask, [left_pts], False, 255, scaled_thickness, cv2.LINE_AA)
    cv2.polylines(mask, [right_pts], False, 255, scaled_thickness, cv2.LINE_AA)

    # Optional wing
    if wing_enabled:
        l_eye_w = abs(landmarks[LEFT_OUTER_CORNER][0] - landmarks[LEFT_INNER_CORNER][0])
        r_eye_w = abs(landmarks[RIGHT_OUTER_CORNER][0] - landmarks[RIGHT_INNER_CORNER][0])

        l_wing = _wing_endpoint(landmarks, LEFT_OUTER_CORNER, LEFT_INNER_CORNER, l_eye_w)
        r_wing = _wing_endpoint(landmarks, RIGHT_OUTER_CORNER, RIGHT_INNER_CORNER, r_eye_w)

        cv2.line(mask, landmarks[LEFT_OUTER_CORNER], l_wing, 255, scaled_thickness, cv2.LINE_AA)
        cv2.line(mask, landmarks[RIGHT_OUTER_CORNER], r_wing, 255, scaled_thickness, cv2.LINE_AA)

    # Tiny blur for anti-aliasing
    mask = cv2.GaussianBlur(mask, (3, 3), 0)

    overlay = np.zeros_like(img)
    overlay[:] = color[::-1]  # RGB → BGR

    return alpha_blend(img, overlay, mask, intensity)
