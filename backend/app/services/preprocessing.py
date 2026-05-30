"""
VisionSpec QC - Image Preprocessing Service
Handles resizing, normalization, and cleaning of PCB images before inference.
"""

import numpy as np
from PIL import Image
import io
from backend.app.config.settings import settings


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Preprocess an uploaded image for model inference.

    Steps:
    1. Load and convert to RGB
    2. Resize to the model's expected input size (224x224)
    3. Normalize pixel values to [0, 1]
    4. Expand dimensions for batch inference

    Args:
        image_bytes: Raw bytes of the uploaded image.

    Returns:
        Preprocessed numpy array ready for model prediction.
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = image.resize((settings.IMAGE_SIZE, settings.IMAGE_SIZE))
    image_array = np.array(image, dtype=np.float32) / 255.0
    image_array = np.expand_dims(image_array, axis=0)
    return image_array


def preprocess_frame(frame: np.ndarray) -> np.ndarray:
    """
    Preprocess a single OpenCV webcam frame for inference.

    Args:
        frame: BGR numpy array from OpenCV.

    Returns:
        Preprocessed numpy array ready for model prediction.
    """
    import cv2
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_resized = cv2.resize(frame_rgb, (settings.IMAGE_SIZE, settings.IMAGE_SIZE))
    frame_normalized = frame_resized.astype(np.float32) / 255.0
    frame_batch = np.expand_dims(frame_normalized, axis=0)
    return frame_batch


def validate_image(image_bytes: bytes) -> bool:
    """
    Validate that the uploaded file is a legitimate image.

    Args:
        image_bytes: Raw bytes of the uploaded file.

    Returns:
        True if valid image, False otherwise.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()
        return True
    except Exception:
        return False
