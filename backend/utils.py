import base64
import cv2
import numpy as np
import io
from PIL import Image

def decode_image(file_bytes: bytes) -> np.ndarray:
    """Decode uploaded file bytes into an OpenCV BGR numpy array."""
    # Convert bytes to numpy array
    nparr = np.frombuffer(file_bytes, np.uint8)
    # Decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def encode_image(img: np.ndarray) -> str:
    """Encode an OpenCV BGR image to a base64 PNG string."""
    # Convert to RGB for PIL
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb_img)
    
    # Save to bytes
    buffer = io.BytesIO()
    pil_img.save(buffer, format="PNG")
    # Encode to base64
    base64_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return base64_str

def alpha_blend(base_img: np.ndarray, overlay_img: np.ndarray, mask: np.ndarray, intensity: float) -> np.ndarray:
    """
    Blend an overlay image onto a base image using a combined mask and intensity.
    
    Args:
        base_img: The original BGR image
        overlay_img: The colored BGR overlay
        mask: Single channel 0-255 mask
        intensity: 0.0 to 1.0 multiplier for the mask
        
    Returns:
        The blended BGR image.
    """
    # Normalize mask to 0-1 and apply user intensity
    alpha = (mask.astype(float) / 255.0) * intensity
    
    # Needs to be 3-channel for blending with BGR images
    alpha = np.expand_dims(alpha, axis=2)
    
    # Blend!
    blended = (base_img * (1 - alpha) + overlay_img * alpha).astype(np.uint8)
    
    return blended
