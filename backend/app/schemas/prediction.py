"""
VisionSpec QC - Pydantic Schemas
Request/Response validation schemas for all API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ── Prediction Schemas ──────────────────────────────────────
class PredictionResponse(BaseModel):
    """Response from the /predict endpoint."""
    predicted_label: str = Field(..., description="Pass or Defect")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Prediction confidence score")
    heatmap_base64: Optional[str] = Field(None, description="Base64-encoded Grad-CAM heatmap")
    inference_time_ms: float = Field(..., description="Inference time in milliseconds")
    image_size: Optional[str] = Field(None, description="Original image dimensions")


class PredictionHistoryItem(BaseModel):
    """Single item in prediction history."""
    id: int
    timestamp: datetime
    image_filename: Optional[str]
    predicted_label: str
    confidence: float
    inference_time_ms: Optional[float]
    source: str


class PredictionHistoryResponse(BaseModel):
    """Response from the /history endpoint."""
    total: int
    predictions: List[PredictionHistoryItem]


# ── Analytics Schemas ───────────────────────────────────────
class AnalyticsResponse(BaseModel):
    """Response from the /analytics endpoint."""
    total_predictions: int
    total_defects: int
    total_pass: int
    defect_rate: float
    average_confidence: float
    average_inference_time_ms: float
    predictions_today: int


# ── System Health Schemas ───────────────────────────────────
class HealthResponse(BaseModel):
    """Response from the /health endpoint."""
    status: str
    app_name: str
    version: str
    model_loaded: bool
    database_connected: bool
    uptime_seconds: float


# ── Webcam Schemas ──────────────────────────────────────────
class WebcamPredictionResponse(BaseModel):
    """Response from the /webcam/predict endpoint."""
    predicted_label: str
    confidence: float
    heatmap_base64: Optional[str]
    fps: float
    inference_time_ms: float


# ── Feedback Schemas (Unique Feature) ──────────────────────
class FeedbackRequest(BaseModel):
    """Request for the human-in-the-loop feedback system."""
    prediction_id: int
    corrected_label: str = Field(..., description="The correct label provided by the operator")
    notes: Optional[str] = None
