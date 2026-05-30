"""
VisionSpec QC — Phase 3: Grad-CAM Explainable AI Service
Generates visual heatmaps highlighting the regions the CNN focuses on
when classifying a PCB image as Pass or Defect.

Reference: Selvaraju et al., "Grad-CAM: Visual Explanations from Deep Networks"
"""

import io
import base64
import numpy as np
from typing import Optional, Tuple

try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    tf = None
    TF_AVAILABLE = False
from PIL import Image
import cv2

from backend.app.services.inference import get_model
from backend.app.config.settings import settings


def generate_gradcam(
    image_array: np.ndarray,
    target_layer_name: Optional[str] = None,
) -> Optional[str]:
    """
    Generate a Grad-CAM heatmap for the given preprocessed image.

    Steps:
    1. Identify the last convolutional layer in MobileNetV2
    2. Build a gradient model that outputs both conv activations and predictions
    3. Compute gradients of the predicted class w.r.t. the conv output
    4. Pool gradients and weight the activations
    5. Generate a heatmap, overlay onto the original image
    6. Return as base64-encoded PNG

    Args:
        image_array: Preprocessed numpy array of shape (1, 224, 224, 3),
                     normalized to [0, 1].
        target_layer_name: Name of the convolutional layer to visualize.
                           If None, auto-detects the last Conv2D layer.

    Returns:
        Base64-encoded PNG string of the heatmap overlay, or None on failure.
    """
    if not TF_AVAILABLE:
        return None

    model = get_model()
    if model is None:
        return None

    try:
        # ── Step 1: Find the target convolutional layer ────────
        if target_layer_name is None:
            target_layer_name = _find_last_conv_layer(model)

        if target_layer_name is None:
            print("⚠️  Grad-CAM: No convolutional layer found in model.")
            return None

        # ── Step 2: Build gradient model ───────────────────────
        base_model = model.layers[0]  # MobileNetV2 base
        conv_layer = base_model.get_layer(target_layer_name)

        # Create a sub-model that outputs both the conv layer and base output
        base_grad_model = tf.keras.Model(
            inputs=base_model.inputs,
            outputs=[conv_layer.output, base_model.output]
        )

        # Build a functional wrapper model for the entire sequence
        inp = tf.keras.Input(shape=(settings.IMAGE_SIZE, settings.IMAGE_SIZE, 3))
        conv_out, base_out = base_grad_model(inp)

        x = base_out
        for layer in model.layers[1:]:
            x = layer(x, training=False)

        grad_model = tf.keras.Model(inputs=inp, outputs=[conv_out, x])

        # ── Step 3: Compute gradients ──────────────────────────
        image_tensor = tf.cast(image_array, tf.float32)

        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(image_tensor)
            # For binary classification (sigmoid), use the output directly
            predicted_class = predictions[:, 0]

        # Gradients of the predicted class w.r.t. the conv layer output
        grads = tape.gradient(predicted_class, conv_outputs)

        if grads is None:
            print("⚠️  Grad-CAM: Gradients are None. Layer may be disconnected.")
            return None

        # ── Step 4: Pool gradients and weight activations ──────
        # Global average pooling of gradients
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        # Weighted combination of feature maps
        conv_outputs = conv_outputs[0]  # Remove batch dimension
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)

        # ReLU — only positive contributions
        heatmap = tf.maximum(heatmap, 0)

        # Normalize to [0, 1]
        max_val = tf.reduce_max(heatmap)
        if max_val > 0:
            heatmap = heatmap / max_val

        heatmap = heatmap.numpy()

        # ── Step 5: Create the overlay image ───────────────────
        overlay_b64 = _create_heatmap_overlay(image_array[0], heatmap)
        return overlay_b64

    except Exception as e:
        print(f"⚠️  Grad-CAM generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


from typing import Optional, Tuple, Any

def _find_last_conv_layer(model: Any) -> Optional[str]:
    """
    Find the name of the last Conv2D layer in the model.
    Searches inside Sequential model's base (MobileNetV2).

    Args:
        model: The Keras model.

    Returns:
        Name of the last Conv2D layer, or None.
    """
    if not TF_AVAILABLE:
        return None

    # For our Sequential model, the base is layers[0] (MobileNetV2)
    base_model = model.layers[0]

    last_conv_name = None
    for layer in base_model.layers:
        if isinstance(layer, tf.keras.layers.Conv2D):
            last_conv_name = layer.name

    return last_conv_name


def _create_heatmap_overlay(
    original_image: np.ndarray,
    heatmap: np.ndarray,
    alpha: float = 0.4,
    colormap: int = cv2.COLORMAP_JET,
) -> str:
    """
    Create a heatmap overlay on the original image.

    Args:
        original_image: Normalized image array of shape (224, 224, 3) in [0, 1].
        heatmap: 2D heatmap array from Grad-CAM.
        alpha: Opacity of the heatmap overlay (0 = invisible, 1 = opaque).
        colormap: OpenCV colormap to apply.

    Returns:
        Base64-encoded PNG string.
    """
    # Convert original image to uint8
    img = (original_image * 255).astype(np.uint8)

    # Resize heatmap to match image size
    heatmap_resized = cv2.resize(heatmap, (img.shape[1], img.shape[0]))

    # Apply colormap
    heatmap_colored = cv2.applyColorMap(
        (heatmap_resized * 255).astype(np.uint8), colormap
    )
    # OpenCV uses BGR, convert to RGB
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

    # Blend
    overlay = cv2.addWeighted(img, 1 - alpha, heatmap_colored, alpha, 0)

    # Convert to PIL Image and then to base64
    pil_image = Image.fromarray(overlay)
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG", quality=95)
    buffer.seek(0)

    return base64.b64encode(buffer.read()).decode("utf-8")


def generate_gradcam_from_bytes(image_bytes: bytes) -> Tuple[Optional[str], np.ndarray]:
    """
    Convenience function: preprocess image bytes and generate Grad-CAM.

    Args:
        image_bytes: Raw image bytes.

    Returns:
        Tuple of (base64_heatmap, preprocessed_image_array).
    """
    from backend.app.services.preprocessing import preprocess_image

    image_array = preprocess_image(image_bytes)
    heatmap_b64 = generate_gradcam(image_array)
    return heatmap_b64, image_array
