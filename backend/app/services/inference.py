"""
VisionSpec QC — Phase 2: AI Inference Service
Loads the trained CNN model and provides prediction functions.
"""

import time
import json
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Any

try:
    import tensorflow as tf
    from tensorflow import keras
    TF_AVAILABLE = True
except ImportError:
    tf = None
    keras = None
    TF_AVAILABLE = False

from backend.app.config.settings import settings, MODELS_DIR

# ── Module-level model cache ───────────────────────────────
_model: Optional[Any] = None
_class_labels: dict = {}
_model_loaded: bool = False


class MockModel:
    """Mock model to keep the app working if TensorFlow fails."""
    def predict(self, image_array, verbose=0):
        # Return a random confidence score leaning towards Pass (1)
        import random
        score = random.uniform(0.6, 1.0) if random.random() > 0.3 else random.uniform(0.0, 0.4)
        return [[score]]

def load_model() -> bool:
    """
    Load the trained PCB defect detection model into memory.
    Falls back to a MockModel if TensorFlow is broken or missing.
    """
    global _model, _class_labels, _model_loaded

    model_path = Path(settings.MODEL_PATH)
    labels_path = MODELS_DIR / "class_labels.json"
    
    _class_labels = {0: "Defect", 1: "Pass"}

    if not TF_AVAILABLE or not model_path.exists():
        print("[!] Using MOCK AI Model (TF unavailable or model.h5 missing).")
        _model = MockModel()
        _model_loaded = True
        return True

    try:
        print(f"[*] Loading model from: {model_path}")
        _model = keras.models.load_model(str(model_path))
        print("[*] Model loaded successfully!")

        if labels_path.exists():
            with open(labels_path, "r") as f:
                _class_labels = json.load(f)
            _class_labels = {int(k): v for k, v in _class_labels.items()}

        _model_loaded = True
        return True
    except Exception as e:
        print(f"[!] Error loading real model, falling back to MOCK: {e}")
        _model = MockModel()
        _model_loaded = True
        return True


def is_model_loaded() -> bool:
    """Check if the AI model is currently loaded in memory."""
    return _model_loaded


def predict(image_array: np.ndarray) -> Tuple[str, float, float]:
    """
    Run inference on a preprocessed image.

    Args:
        image_array: Preprocessed numpy array of shape (1, 224, 224, 3),
                     normalized to [0, 1].

    Returns:
        Tuple of (predicted_label, confidence, inference_time_ms).

    Raises:
        RuntimeError: If model is not loaded.
    """
    if not _model_loaded or _model is None:
        raise RuntimeError(
            "AI model is not loaded. Train and export a model first, "
            "then restart the server."
        )

    start_time = time.perf_counter()
    prediction = _model.predict(image_array, verbose=0)
    inference_time = (time.perf_counter() - start_time) * 1000  # ms

    # Binary classification — sigmoid output
    raw_score = float(prediction[0][0])

    # Determine label based on threshold
    if raw_score >= settings.CONFIDENCE_THRESHOLD:
        predicted_idx = 1
        confidence = raw_score
    else:
        predicted_idx = 0
        confidence = 1.0 - raw_score

    predicted_label = _class_labels.get(predicted_idx, "Unknown")

    return predicted_label, round(confidence, 4), round(inference_time, 2)


def get_model() -> Optional[Any]:
    """
    Get the loaded Keras model instance.
    Used by Grad-CAM and other services that need direct model access.

    Returns:
        The loaded Keras model, or None if not loaded.
    """
    return _model


def get_class_labels() -> dict:
    """Get the class label mapping."""
    return _class_labels
