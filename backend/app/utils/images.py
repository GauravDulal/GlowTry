from __future__ import annotations

import io

from PIL import Image


class ImageValidationError(ValueError):
    def __init__(self, message: str, code: str):
        super().__init__(message)
        self.code = code


ALLOWED_TYPES = {"jpeg", "png", "webp"}
MAX_BYTES = 8 * 1024 * 1024  # 8MB


def sniff_and_validate_image(*, filename: str, content_type: str, data: bytes) -> str:
    if not data:
        raise ImageValidationError("Empty upload. Please choose an image file.", "EMPTY_UPLOAD")
    if len(data) > MAX_BYTES:
        raise ImageValidationError(
            "Image is too large. Please upload a file under 8MB.", "FILE_TOO_LARGE"
        )

    try:
        img = Image.open(io.BytesIO(data))
        kind = (img.format or "").lower()
    except Exception as e:
        raise ImageValidationError(
            "Unsupported or corrupted image format. Please upload a JPG, PNG, or WEBP file.",
            "UNSUPPORTED_FORMAT",
        ) from e

    if kind == "jpg":
        kind = "jpeg"
    if kind not in ALLOWED_TYPES:
        raise ImageValidationError(
            "Unsupported image format. Please upload a JPG, PNG, or WEBP file.",
            "UNSUPPORTED_FORMAT",
        )

    # Some browsers send empty/incorrect content-types; we still rely on sniffing.
    return kind

