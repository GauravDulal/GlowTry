import numpy as np
import cv2
from utils import alpha_blend

# ── Canonical MediaPipe FaceMesh lip contour indices ──
# Each path forms a proper closed loop (first == last conceptually, traced in order).
UPPER_LIP_OUTER = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291]
LOWER_LIP_OUTER = [291, 375, 321, 405, 314, 17, 84, 181, 91, 146, 61]
UPPER_LIP_INNER = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308]
LOWER_LIP_INNER = [308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 78]


def _lip_mask(h: int, w: int, landmarks: list) -> np.ndarray:
    """
    Build a precise lip mask by tracing outer and inner contours separately.
    The outer contour is the full visible lip boundary.
    The inner contour (mouth opening) is subtracted so teeth stay untouched.
    """
    # Outer lip: combine upper-outer going left→right, then lower-outer going right→left
    # This traces one continuous closed polygon around the entire lip edge.
    outer_indices = UPPER_LIP_OUTER + LOWER_LIP_OUTER[1:]  # skip duplicate 291
    outer_pts = np.array([landmarks[i] for i in outer_indices], np.int32)

    # Inner mouth opening: same idea
    inner_indices = UPPER_LIP_INNER + LOWER_LIP_INNER[1:]  # skip duplicate 308
    inner_pts = np.array([landmarks[i] for i in inner_indices], np.int32)

    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(mask, [outer_pts], 255)
    cv2.fillPoly(mask, [inner_pts], 0)
    return mask


def apply_lipstick(img: np.ndarray, landmarks: list, kwargs: dict) -> np.ndarray:
    """Apply lipstick with accurate lip contour mapping and optional matte/glossy finish."""
    color = kwargs.get("color", [200, 50, 50])  # RGB
    intensity = kwargs.get("intensity", 0.6)
    matte = kwargs.get("matte", True)

    if intensity <= 0:
        return img

    h, w, _ = img.shape

    # 1. Build precise lip mask
    mask = _lip_mask(h, w, landmarks)

    # 2. Adaptive feathering — kernel scales with lip size
    lip_pts = np.array([landmarks[i] for i in UPPER_LIP_OUTER], np.int32)
    lip_width = lip_pts[:, 0].max() - lip_pts[:, 0].min()
    blur_k = max(3, int(lip_width * 0.06) | 1)  # ensure odd
    mask = cv2.GaussianBlur(mask, (blur_k, blur_k), 0)

    # 3. Colored overlay
    overlay = np.zeros_like(img)
    overlay[:] = color[::-1]  # RGB → BGR

    # 4. For glossy finish, add a subtle specular highlight along the center of each lip
    if not matte:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Emphasize existing highlights inside the lip mask region
        highlight = cv2.GaussianBlur(gray, (15, 15), 0)
        highlight = np.clip(highlight.astype(np.float32) * 1.3, 0, 255).astype(np.uint8)
        # Blend a white highlight where mask is active
        gloss_mask = cv2.bitwise_and(mask, highlight)
        gloss_overlay = np.full_like(img, 255)
        overlay_blend = alpha_blend(overlay, gloss_overlay, gloss_mask, 0.25)
        overlay = overlay_blend

    # 5. Blend
    return alpha_blend(img, overlay, mask, intensity)
