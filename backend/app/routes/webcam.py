"""
VisionSpec QC — Phase 3: Webcam Prediction Route
POST /webcam/predict — accepts a webcam frame and returns real-time prediction.
WebSocket endpoint /ws/live-feed — streams continuous frame-by-frame predictions.
"""

import time
import base64
import io
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import numpy as np

from backend.app.config.settings import settings
from backend.app.schemas.prediction import WebcamPredictionResponse
from backend.app.services.preprocessing import preprocess_image, validate_image
from backend.app.services.inference import predict, is_model_loaded
from backend.app.services.gradcam import generate_gradcam
from backend.app.models.database import get_db, PredictionLog

router = APIRouter(tags=["Webcam"])


@router.post("/webcam/predict", response_model=WebcamPredictionResponse)
async def predict_webcam_frame(
    frame: UploadFile = File(..., description="Webcam frame image"),
    db: Session = Depends(get_db),
):
    """
    Process a single webcam frame for real-time PCB defect detection.

    **Accepts:** A single frame as JPG/PNG from the webcam feed.

    **Returns:**
    - `predicted_label` — "Pass" or "Defect"
    - `confidence` — AI confidence score
    - `heatmap_base64` — Grad-CAM overlay (if defect detected)
    - `fps` — Estimated frames per second
    - `inference_time_ms` — Time taken for inference
    """
    if not is_model_loaded():
        raise HTTPException(
            status_code=503,
            detail="AI model is not loaded.",
        )

    # Read frame bytes
    frame_bytes = await frame.read()

    if not frame_bytes:
        raise HTTPException(status_code=400, detail="Empty frame received.")

    # Validate
    if not validate_image(frame_bytes):
        raise HTTPException(status_code=400, detail="Invalid image frame.")

    # Preprocess
    image_array = preprocess_image(frame_bytes)

    # Inference
    start_total = time.perf_counter()
    try:
        predicted_label, confidence, inference_time_ms = predict(image_array)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

    # Generate heatmap only for defects (to save processing time)
    heatmap_b64 = None
    if predicted_label == "Defect":
        heatmap_b64 = generate_gradcam(image_array)

    total_time = (time.perf_counter() - start_total) * 1000
    fps = 1000.0 / total_time if total_time > 0 else 0

    # Log to database (async-safe, non-blocking)
    try:
        log_entry = PredictionLog(
            image_filename="webcam_frame",
            predicted_label=predicted_label,
            confidence=confidence,
            inference_time_ms=inference_time_ms,
            source="webcam",
        )
        db.add(log_entry)
        db.commit()
    except Exception:
        db.rollback()

    return WebcamPredictionResponse(
        predicted_label=predicted_label,
        confidence=confidence,
        heatmap_base64=heatmap_b64,
        fps=round(fps, 1),
        inference_time_ms=inference_time_ms,
    )


@router.websocket("/ws/live-feed")
async def websocket_live_feed(websocket: WebSocket):
    """
    WebSocket endpoint for continuous live webcam feed predictions.

    Protocol:
    - Client sends: base64-encoded JPEG frame as text
    - Server responds: JSON with prediction result

    Response format:
    {
        "predicted_label": "Pass" | "Defect",
        "confidence": 0.95,
        "inference_time_ms": 42.3,
        "fps": 23.7,
        "heatmap_base64": "..." | null
    }
    """
    await websocket.accept()
    print("📡 WebSocket live feed connected")

    frame_count = 0
    fps_start_time = time.perf_counter()

    try:
        while True:
            # Receive base64-encoded frame from client
            data = await websocket.receive_text()

            if not is_model_loaded():
                await websocket.send_json({
                    "error": "Model not loaded",
                    "predicted_label": "Unknown",
                    "confidence": 0.0,
                    "inference_time_ms": 0.0,
                    "fps": 0.0,
                    "heatmap_base64": None,
                })
                continue

            try:
                # Decode base64 frame
                frame_bytes = base64.b64decode(data)

                # Preprocess
                image_array = preprocess_image(frame_bytes)

                # Inference
                predicted_label, confidence, inference_time_ms = predict(image_array)

                # Generate heatmap for defects
                heatmap_b64 = None
                if predicted_label == "Defect":
                    heatmap_b64 = generate_gradcam(image_array)

                # Calculate FPS
                frame_count += 1
                elapsed = time.perf_counter() - fps_start_time
                current_fps = frame_count / elapsed if elapsed > 0 else 0

                # Reset FPS counter every 30 frames
                if frame_count >= 30:
                    frame_count = 0
                    fps_start_time = time.perf_counter()

                await websocket.send_json({
                    "predicted_label": predicted_label,
                    "confidence": confidence,
                    "inference_time_ms": inference_time_ms,
                    "fps": round(current_fps, 1),
                    "heatmap_base64": heatmap_b64,
                })

            except Exception as e:
                await websocket.send_json({
                    "error": str(e),
                    "predicted_label": "Error",
                    "confidence": 0.0,
                    "inference_time_ms": 0.0,
                    "fps": 0.0,
                    "heatmap_base64": None,
                })

    except WebSocketDisconnect:
        print("📡 WebSocket live feed disconnected")
    except Exception as e:
        print(f"⚠️  WebSocket error: {e}")
