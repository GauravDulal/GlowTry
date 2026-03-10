from __future__ import annotations

import os
import pathlib
import urllib.request


FACE_LANDMARKER_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "face_landmarker/face_landmarker/float16/1/face_landmarker.task"
)


def ensure_face_landmarker_model() -> str:
    """
    Ensures the Face Landmarker `.task` file exists locally and returns its path.
    Download is deterministic and cached on disk inside the repo.
    """
    assets_dir = pathlib.Path(__file__).resolve().parents[2] / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    model_path = assets_dir / "face_landmarker.task"

    if model_path.exists() and model_path.stat().st_size > 1_000_000:
        return str(model_path)

    tmp_path = assets_dir / "face_landmarker.task.download"
    urllib.request.urlretrieve(FACE_LANDMARKER_URL, tmp_path)  # noqa: S310 (trusted URL)
    os.replace(tmp_path, model_path)
    return str(model_path)

