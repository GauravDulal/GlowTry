import numpy as np
import cv2
from utils import alpha_blend

def apply_blush(img: np.ndarray, landmarks: list, kwargs: dict) -> np.ndarray:
    """
    Apply a blush overlay to the cheeks using FaceMesh landmarks.
    """
    color = kwargs.get("color", [255, 105, 180])  # Hot pink default
    intensity = kwargs.get("intensity", 0.5)
    
    if intensity <= 0:
        return img
        
    h, w, _ = img.shape
    
    # Rough cheek center landmarks (left and right)
    left_cheek_idx = [234, 93, 132, 58, 172, 136, 150, 176]
    right_cheek_idx = [454, 323, 361, 288, 397, 365, 379, 400]
    
    left_xs = [landmarks[i][0] for i in left_cheek_idx]
    left_ys = [landmarks[i][1] for i in left_cheek_idx]
    
    right_xs = [landmarks[i][0] for i in right_cheek_idx]
    right_ys = [landmarks[i][1] for i in right_cheek_idx]
    
    # Calculate centroids and approximate radius
    left_center = (int(np.mean(left_xs)), int(np.mean(left_ys)))
    right_center = (int(np.mean(right_xs)), int(np.mean(right_ys)))
    
    # Cheek size relative to face
    radius_x = int((max(left_xs) - min(left_xs)) * 0.8)
    radius_y = int((max(left_ys) - min(left_ys)) * 0.6)
    
    # Create mask with two ellipses (one for each cheek)
    mask = np.zeros((h, w), dtype=np.uint8)
    
    cv2.ellipse(mask, left_center, (radius_x, radius_y), 0, 0, 360, 255, -1)
    cv2.ellipse(mask, right_center, (radius_x, radius_y), 0, 0, 360, 255, -1)
    
    # Apply a massive blur to create that soft radial gradient effect
    blur_kernel = (101, 101)  # Needs to be very large and odd
    mask = cv2.GaussianBlur(mask, blur_kernel, 0)
    
    # Create the colored overlay
    overlay = np.zeros_like(img)
    overlay[:] = color[::-1]  # RGB to BGR
    
    blended = alpha_blend(img, overlay, mask, intensity)
    
    return blended
