import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import cv2

import os

# Initialize MediaPipe Face Landmarker Tasks API
# Use absolute path to ensure the model is found regardless of where the server is started
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'face_landmarker.task')

if not os.path.exists(model_path):
    print(f"CRITICAL ERROR: Model file not found at {model_path}")

base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    output_face_blendshapes=False,
    output_facial_transformation_matrixes=False,
    num_faces=1,
    min_face_detection_confidence=0.1,
    min_face_presence_confidence=0.1
)
detector = vision.FaceLandmarker.create_from_options(options)

def get_landmarks(img: np.ndarray):
    """
    Detect face landmarks using MediaPipe FaceLandmarker.
    
    Args:
        img: OpenCV BGR image.
        
    Returns:
        A list of (x, y) tuples representing the pixel coordinates of the 478 landmarks.
        Returns None if no face is detected.
    """
    # MediaPipe expects RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Convert to MediaPipe Image object format
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
    
    # Process the image
    detection_result = detector.detect(mp_image)
    
    if not detection_result.face_landmarks:
        print("DEBUG: FaceLandmarker returned no face landmarks")
        return None
        
    print(f"DEBUG: Successfully detected {len(detection_result.face_landmarks)} face(s)")
        
    h, w, _ = img.shape
    
    # We only care about the first face
    face_landmarks = detection_result.face_landmarks[0]
    
    # Convert normalized coordinates to pixel coordinates
    landmarks = []
    for landmark in face_landmarks:
        x = int(landmark.x * w)
        y = int(landmark.y * h)
        landmarks.append((x, y))
        
    return landmarks
