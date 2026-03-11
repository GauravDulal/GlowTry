import numpy as np
import cv2
from utils import alpha_blend

def apply_lipstick(img: np.ndarray, landmarks: list, kwargs: dict) -> np.ndarray:
    """
    Apply a lipstick overlay to the lips using FaceMesh landmarks.
    """
    # Verify settings point at least one color
    color = kwargs.get("color", [200, 50, 50])  # RGB defaults
    intensity = kwargs.get("intensity", 0.6)
    
    # Needs to be at least a tiny bit visible
    if intensity <= 0:
        return img
        
    # Standard MediaPipe lip landmarks
    upper_lip_outer = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291]
    upper_lip_inner = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308]
    lower_lip_outer = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291]
    lower_lip_inner = [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308]
    
    lip_outer_pts = np.array([landmarks[idx] for idx in upper_lip_outer + lower_lip_outer[::-1]], np.int32)
    lip_inner_pts = np.array([landmarks[idx] for idx in upper_lip_inner + lower_lip_inner[::-1]], np.int32)
    
    h, w, _ = img.shape
    
    # 1. Create a mask of the lips
    mask = np.zeros((h, w), dtype=np.uint8)
    
    # Fill the outer lips
    cv2.fillPoly(mask, [lip_outer_pts], 255)
    
    # Subtract the inner mouth (so teeth remain white)
    cv2.fillPoly(mask, [lip_inner_pts], 0)
    
    # 2. Blur the mask for feathered edges
    mask = cv2.GaussianBlur(mask, (7, 7), 0)
    
    # 3. Create the colored overlay
    overlay = np.zeros_like(img)
    overlay[:] = color[::-1]  # Convert RGB to BGR for OpenCV
    
    # 4. Blend using our utility
    blended = alpha_blend(img, overlay, mask, intensity)
    
    return blended
