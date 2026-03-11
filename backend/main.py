from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import os

from utils import decode_image, encode_image
from face_detection import get_landmarks
from makeup.lipstick import apply_lipstick
from makeup.blush import apply_blush
from makeup.eyeshadow import apply_eyeshadow
from makeup.eyeliner import apply_eyeliner

app = FastAPI(title="GlowTry Backend MVP")

MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB

# Allow requests from the Next.js frontend (env-configurable)
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def read_health():
    """Health check endpoint to verify the server is running."""
    return {"status": "ok"}

@app.post("/apply-makeup")
async def process_makeup(
    image: UploadFile = File(...),
    config: str = Form(...)  # Expect JSON string
):
    """
    Main endpoint for applying virtual makeup to an uploaded selfie.
    """
    # 1. Read & validate image bytes
    file_bytes = await image.read()
    if len(file_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image exceeds 10 MB limit")

    img = decode_image(file_bytes)
    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode image. Upload a valid JPG/PNG.")

    # 2. Parse configuration string into dict (guard against malformed JSON)
    try:
        options = json.loads(config)
    except (json.JSONDecodeError, TypeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid config JSON: {e}")

    # 3. Detect 478 face landmarks
    landmarks = get_landmarks(img)

    # If no face is detected, return the unmodified original image
    if landmarks is None:
        return {"image": encode_image(img), "error": "No face detected"}

    output = img.copy()

    # 4. Pipeline: sequentially apply enabled makeup modules
    eyeliner_conf = options.get("eyeliner", {})
    if eyeliner_conf.get("enabled", False):
        output = apply_eyeliner(output, landmarks, eyeliner_conf)

    eyeshadow_conf = options.get("eyeshadow", {})
    if eyeshadow_conf.get("enabled", False):
        output = apply_eyeshadow(output, landmarks, eyeshadow_conf)

    blush_conf = options.get("blush", {})
    if blush_conf.get("enabled", False):
        output = apply_blush(output, landmarks, blush_conf)

    lipstick_conf = options.get("lipstick", {})
    if lipstick_conf.get("enabled", False):
        output = apply_lipstick(output, landmarks, lipstick_conf)

    # 5. Return modified image as base64 string
    return {"image": encode_image(output)}


@app.post("/debug-landmarks")
async def debug_landmarks(
    image: UploadFile = File(...),
):
    """
    Debug endpoint: returns the image with all facial landmark regions drawn.
    Use this to visually verify landmark placement.
    """
    from debug_viz import draw_full_debug

    file_bytes = await image.read()
    if len(file_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image exceeds 10 MB limit")

    img = decode_image(file_bytes)
    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode image.")

    landmarks = get_landmarks(img)
    if landmarks is None:
        return {"image": encode_image(img), "error": "No face detected"}

    debug_img = draw_full_debug(img, landmarks)
    return {"image": encode_image(debug_img)}
