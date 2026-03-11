from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import json

from utils import decode_image, encode_image
from face_detection import get_landmarks
from makeup.lipstick import apply_lipstick
from makeup.blush import apply_blush
from makeup.eyeshadow import apply_eyeshadow
from makeup.eyeliner import apply_eyeliner

app = FastAPI(title="GlowTry Backend MVP")

# Allow requests from the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
    # 1. Parse image into cv2 BGR format
    file_bytes = await image.read()
    img = decode_image(file_bytes)
    
    # 2. Parse configuration string into dict
    options = json.loads(config)
    
    # 3. Detect 478 face landmarks
    landmarks = get_landmarks(img)
    
    # If no face is detected, we return the unmodified original image back to the user
    if landmarks is None:
        return {"image": encode_image(img), "error": "No face detected"}
        
    output = img.copy()
    
    # 4. Pipeline: sequentially apply enabled makeup modules
    # Eyeliner
    eyeliner_conf = options.get("eyeliner", {})
    if eyeliner_conf.get("enabled", False):
        output = apply_eyeliner(output, landmarks, eyeliner_conf)
        
    # Eyeshadow
    eyeshadow_conf = options.get("eyeshadow", {})
    if eyeshadow_conf.get("enabled", False):
        output = apply_eyeshadow(output, landmarks, eyeshadow_conf)
        
    # Blush
    blush_conf = options.get("blush", {})
    if blush_conf.get("enabled", False):
        output = apply_blush(output, landmarks, blush_conf)
        
    # Lipstick
    lipstick_conf = options.get("lipstick", {})
    if lipstick_conf.get("enabled", False):
        output = apply_lipstick(output, landmarks, lipstick_conf)

    # 5. Return modified image as base64 string
    base64_result = encode_image(output)
    
    # Return raw base64; the frontend will add the data URI prefix
    return {"image": base64_result}
