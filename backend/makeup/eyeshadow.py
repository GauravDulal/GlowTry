import numpy as np
import cv2
from utils import alpha_blend

def apply_eyeshadow(img: np.ndarray, landmarks: list, kwargs: dict) -> np.ndarray:
    """
    Apply an eyeshadow overlay to the eyelids using FaceMesh landmarks.
    """
    color = kwargs.get("color", [150, 100, 200])  # Purple default
    intensity = kwargs.get("intensity", 0.4)
    
    if intensity <= 0:
        return img
        
    h, w, _ = img.shape
    
    # Eyelid regions
    # These map roughly from the crease to the upper lash line
    left_eyelid_idx = [33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7]
    right_eyelid_idx = [362, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382]
    
    left_eyelid_pts = np.array([landmarks[i] for i in left_eyelid_idx], np.int32)
    right_eyelid_pts = np.array([landmarks[i] for i in right_eyelid_idx], np.int32)
    
    mask = np.zeros((h, w), dtype=np.uint8)
    
    # Fill the eyelid areas
    cv2.fillPoly(mask, [left_eyelid_pts], 255)
    cv2.fillPoly(mask, [right_eyelid_pts], 255)
    
    # Soften the edges significantly
    mask = cv2.GaussianBlur(mask, (15, 15), 0)
    
    # Create the colored overlay
    overlay = np.zeros_like(img)
    overlay[:] = color[::-1]  # RGB to BGR
    
    blended = alpha_blend(img, overlay, mask, intensity)
    
    return blended
