from __future__ import annotations

from dataclasses import dataclass

import cv2
import mediapipe as mp
import numpy as np
import threading
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

from app.utils.model_cache import ensure_face_landmarker_model


class LandmarkError(ValueError):
    def __init__(self, message: str, code: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class FaceLandmarks:
    # Pixel coordinates, shape (468, 2)
    xy: np.ndarray


_lock = threading.Lock()
_landmarker: vision.FaceLandmarker | None = None


def _get_landmarker() -> vision.FaceLandmarker:
    global _landmarker
    if _landmarker is not None:
        return _landmarker
    with _lock:
        if _landmarker is not None:
            return _landmarker
        model_path = ensure_face_landmarker_model()
        base_options = mp_python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_faces=2,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )
        _landmarker = vision.FaceLandmarker.create_from_options(options)
        return _landmarker


def detect_face_landmarks_bgr(image_bgr: np.ndarray) -> FaceLandmarks:
    """
    Detect 468 face mesh landmarks. Expects BGR uint8 image (OpenCV).
    Raises LandmarkError with friendly codes.
    """
    if image_bgr is None or image_bgr.size == 0:
        raise LandmarkError("Invalid image.", "INVALID_IMAGE")

    h, w = image_bgr.shape[:2]
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
    result = _get_landmarker().detect(mp_image)

    faces = result.face_landmarks or []
    if len(faces) == 0:
        raise LandmarkError(
            "No face detected. Try a front-facing selfie with good lighting.",
            "NO_FACE_DETECTED",
        )
    if len(faces) > 1:
        raise LandmarkError(
            "Multiple faces detected. Please upload a selfie with only one face.",
            "MULTIPLE_FACES_DETECTED",
        )

    lm = faces[0]
    pts = np.array([[p.x * w, p.y * h] for p in lm], dtype=np.float32)
    pts = np.clip(pts, [0, 0], [w - 1, h - 1])
    return FaceLandmarks(xy=pts)

