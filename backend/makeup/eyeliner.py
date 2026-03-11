import numpy as np
import cv2
from utils import alpha_blend

def apply_eyeliner(img: np.ndarray, landmarks: list, kwargs: dict) -> np.ndarray:
    """
    Apply eyeliner along the upper lashline with an optional wing.
    """
    color = kwargs.get("color", [0, 0, 0])  # Black default
    intensity = kwargs.get("intensity", 0.7)
    thickness = kwargs.get("thickness", 3)
    
    if intensity <= 0:
        return img
        
    h, w, _ = img.shape
    
    # Upper lash lines (ordered from inner to outer corner)
    left_lashline_idx = [133, 173, 157, 158, 159, 160, 161, 246, 33]
    right_lashline_idx = [362, 398, 384, 385, 386, 387, 388, 466, 263]
    
    left_pts = [landmarks[i] for i in left_lashline_idx]
    right_pts = [landmarks[i] for i in right_lashline_idx]
    
    mask = np.zeros((h, w), dtype=np.uint8)
    
    # Draw primary lash lines as curves (polylines)
    cv2.polylines(mask, [np.array(left_pts, np.int32)], False, 255, thickness, cv2.LINE_AA)
    cv2.polylines(mask, [np.array(right_pts, np.int32)], False, 255, thickness, cv2.LINE_AA)
    
    # Simple wing calculation: Extend the outer corner point slightly upwards
    # Left eye wing
    p1 = np.array(left_pts[-2])
    p2 = np.array(left_pts[-1])
    diff = p2 - p1
    
    # Adjust vector slightly pointing upwards for the wing
    wing_vector = np.array([diff[0] * 1.5, diff[1] * 1.5 - 5])
    left_wing_end = p2 + wing_vector
    
    # Right eye wing
    p3 = np.array(right_pts[-2])
    p4 = np.array(right_pts[-1])
    diff_r = p4 - p3
    
    wing_vector_r = np.array([diff_r[0] * 1.5, diff_r[1] * 1.5 - 5])
    right_wing_end = p4 + wing_vector_r
    
    # Draw the wings
    cv2.line(mask, tuple(p2.astype(int)), tuple(left_wing_end.astype(int)), 255, thickness, cv2.LINE_AA)
    cv2.line(mask, tuple(p4.astype(int)), tuple(right_wing_end.astype(int)), 255, thickness, cv2.LINE_AA)
    
    # Tiny blur for anti-aliasing edge
    mask = cv2.GaussianBlur(mask, (3, 3), 0)
    
    # Create the colored overlay
    overlay = np.zeros_like(img)
    overlay[:] = color[::-1]  # RGB to BGR
    
    blended = alpha_blend(img, overlay, mask, intensity)
    
    return blended
