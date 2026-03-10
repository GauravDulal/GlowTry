from __future__ import annotations

import io

import cv2
import numpy as np
from PIL import Image

from app.services.landmarks import LandmarkError, detect_face_landmarks_bgr
from app.services.overlay import add_liner_hint, add_soft_circle, add_soft_polygon
from app.services.regions import cheek_centers, eye_polygons, face_scale_px, lip_polygons
from app.styles.presets import STYLES, StyleName


class MakeupError(ValueError):
    def __init__(self, message: str, code: str):
        super().__init__(message)
        self.code = code


def _pil_to_bgr(img: Image.Image) -> np.ndarray:
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    if img.mode == "RGBA":
        # Composite on white to avoid weird dark halos in overlays.
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(bg, img).convert("RGB")
    arr = np.array(img, dtype=np.uint8)  # RGB
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def _bgr_to_png_bytes(img_bgr: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".png", img_bgr)
    if not ok:
        raise MakeupError("Failed to encode output image.", "ENCODE_FAILED")
    return buf.tobytes()


def apply_makeup_from_bytes(image_bytes: bytes, style_name: StyleName) -> tuple[bytes, str]:
    try:
        img = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        raise MakeupError("Unsupported or corrupted image file.", "UNSUPPORTED_FORMAT") from e

    bgr = _pil_to_bgr(img)

    try:
        face = detect_face_landmarks_bgr(bgr)
    except LandmarkError as e:
        raise MakeupError(str(e), e.code) from e

    style = STYLES[style_name]
    pts = face.xy
    scale = face_scale_px(pts)

    # Lips
    outer, inner = lip_polygons(pts)
    out = add_soft_polygon(
        bgr,
        poly=outer,
        cutout_poly=inner,
        color_bgr=style.lip_bgr,
        strength=style.lip_alpha,
        feather_px=style.feather_px,
    )

    # Blush
    left, right = cheek_centers(pts)
    r = int(max(10, 0.12 * scale))
    out = add_soft_circle(
        out,
        center_xy=left,
        radius_px=r,
        color_bgr=style.blush_bgr,
        strength=style.blush_alpha,
        feather_px=max(18, style.feather_px),
    )
    out = add_soft_circle(
        out,
        center_xy=right,
        radius_px=r,
        color_bgr=style.blush_bgr,
        strength=style.blush_alpha,
        feather_px=max(18, style.feather_px),
    )

    # Eyes
    leye, reye = eye_polygons(pts)
    out = add_soft_polygon(
        out,
        poly=leye,
        color_bgr=style.eye_bgr,
        strength=style.eye_alpha,
        feather_px=max(18, style.feather_px),
        cutout_poly=None,
    )
    out = add_soft_polygon(
        out,
        poly=reye,
        color_bgr=style.eye_bgr,
        strength=style.eye_alpha,
        feather_px=max(18, style.feather_px),
        cutout_poly=None,
    )
    out = add_liner_hint(out, leye[:6], strength=style.liner_strength)
    out = add_liner_hint(out, reye[:6], strength=style.liner_strength)

    png = _bgr_to_png_bytes(out)
    return png, "image/png"

