from __future__ import annotations

import io
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.services.makeup import MakeupError, apply_makeup_from_bytes
from app.styles.presets import list_styles, normalize_style_name
from app.utils.images import ImageValidationError, sniff_and_validate_image


app = FastAPI(title="GlowTry Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/styles")
def styles():
    return {"styles": list_styles()}


@app.post("/apply-makeup")
async def apply_makeup(
    image: Annotated[UploadFile, File(...)],
    style: Annotated[str, Form(...)],
):
    style_name = normalize_style_name(style)
    if not style_name:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_STYLE",
                "message": "Unknown style. Call /styles to see available presets.",
            },
        )

    raw = await image.read()
    try:
        sniff_and_validate_image(
            filename=image.filename or "upload",
            content_type=image.content_type or "",
            data=raw,
        )
    except ImageValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={"code": e.code, "message": str(e)},
        ) from e

    try:
        out_bytes, out_mime = apply_makeup_from_bytes(raw, style_name=style_name)
    except MakeupError as e:
        raise HTTPException(
            status_code=400,
            detail={"code": e.code, "message": str(e)},
        ) from e
    except Exception:
        # Avoid leaking internals; return a user-friendly message.
        raise HTTPException(
            status_code=500,
            detail={
                "code": "PROCESSING_FAILED",
                "message": "Sorry — something went wrong while applying makeup. Try a clearer, front-facing selfie.",
            },
        )

    return Response(content=out_bytes, media_type=out_mime)

