"""
VisionSpec QC — Prediction Route (Phase 2 + Phase 3 Grad-CAM)
POST /predict — accepts an uploaded PCB image, returns AI prediction + Grad-CAM heatmap.
"""

import time
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.app.config.settings import settings
from backend.app.schemas.prediction import PredictionResponse
from backend.app.services.preprocessing import preprocess_image, validate_image
from backend.app.services.inference import predict, is_model_loaded
from backend.app.services.gradcam import generate_gradcam
from backend.app.models.database import get_db, PredictionLog

router = APIRouter(tags=["Prediction"])

# Maximum upload size in bytes
MAX_UPLOAD_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@router.post("/predict", response_model=PredictionResponse)
async def predict_image(
    file: UploadFile = File(..., description="PCB image file (JPG, PNG, BMP)"),
    db: Session = Depends(get_db),
):
    """
    Upload a PCB image for AI-powered defect detection with Grad-CAM visualization.

    **Accepts:** JPG, PNG, BMP images up to 10MB.

    **Returns:**
    - `predicted_label` — "Pass" or "Defect"
    - `confidence` — AI confidence score (0.0 – 1.0)
    - `heatmap_base64` — Base64-encoded Grad-CAM heatmap overlay
    - `inference_time_ms` — Time taken for prediction
    - `image_size` — Original image dimensions
    """

    # ── Validate model is loaded ───────────────────────────
    if not is_model_loaded():
        raise HTTPException(
            status_code=503,
            detail="AI model is not loaded. Please train the model first and restart the server.",
        )

    # ── Validate file type ─────────────────────────────────
    allowed_types = ["image/jpeg", "image/png", "image/bmp", "image/tiff"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed: JPG, PNG, BMP, TIFF.",
        )

    # ── Read and validate ──────────────────────────────────
    image_bytes = await file.read()

    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum upload size is {settings.MAX_UPLOAD_SIZE_MB}MB.",
        )

    if not validate_image(image_bytes):
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not a valid image or is corrupted.",
        )

    # ── Get original image dimensions ──────────────────────
    from PIL import Image
    import io
    original_image = Image.open(io.BytesIO(image_bytes))
    image_size_str = f"{original_image.width}x{original_image.height}"

    # ── Preprocess ─────────────────────────────────────────
    image_array = preprocess_image(image_bytes)

    # ── Run inference ──────────────────────────────────────
    try:
        predicted_label, confidence, inference_time_ms = predict(image_array)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Inference failed: {str(e)}",
        )

    # ── Phase 3: Generate Grad-CAM heatmap ─────────────────
    heatmap_base64 = None
    try:
        heatmap_base64 = generate_gradcam(image_array)
    except Exception as e:
        # Don't fail the prediction if heatmap generation fails
        print(f"⚠️  Grad-CAM generation failed (non-critical): {e}")

    # ── Log prediction to database ─────────────────────────
    try:
        log_entry = PredictionLog(
            image_filename=file.filename,
            predicted_label=predicted_label,
            confidence=confidence,
            inference_time_ms=inference_time_ms,
            source="upload",
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        # Don't fail the prediction if logging fails
        print(f"⚠️  Failed to log prediction: {e}")
        db.rollback()

    # ── Return response ────────────────────────────────────
    return PredictionResponse(
        predicted_label=predicted_label,
        confidence=confidence,
        heatmap_base64=heatmap_base64,
        inference_time_ms=inference_time_ms,
        image_size=image_size_str,
    )
