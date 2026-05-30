"""
VisionSpec QC — Phase 4: Analytics Route
GET /analytics — returns aggregated system and prediction statistics.
"""

from datetime import datetime, date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.schemas.prediction import AnalyticsResponse
from backend.app.models.database import get_db, PredictionLog

router = APIRouter(tags=["Analytics"])


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(db: Session = Depends(get_db)):
    """
    Retrieve aggregated analytics for the Dashboard.
    Calculates total pass/defects, defect rate, average confidence, etc.
    """
    
    # Total predictions
    total_predictions = db.query(PredictionLog).count()
    
    # If no predictions yet, return default empty stats
    if total_predictions == 0:
        return AnalyticsResponse(
            total_predictions=0,
            total_defects=0,
            total_pass=0,
            defect_rate=0.0,
            average_confidence=0.0,
            average_inference_time_ms=0.0,
            predictions_today=0,
        )
        
    # Get pass and defect counts
    total_defects = db.query(PredictionLog).filter(PredictionLog.predicted_label == "Defect").count()
    total_pass = db.query(PredictionLog).filter(PredictionLog.predicted_label == "Pass").count()
    
    # Calculate defect rate
    defect_rate = (total_defects / total_predictions) * 100.0 if total_predictions > 0 else 0.0
    
    # Averages
    avg_conf = db.query(func.avg(PredictionLog.confidence)).scalar() or 0.0
    avg_inf = db.query(func.avg(PredictionLog.inference_time_ms)).scalar() or 0.0
    
    # Predictions today
    today = date.today()
    predictions_today = db.query(PredictionLog).filter(
        func.date(PredictionLog.timestamp) == today
    ).count()
    
    return AnalyticsResponse(
        total_predictions=total_predictions,
        total_defects=total_defects,
        total_pass=total_pass,
        defect_rate=round(defect_rate, 2),
        average_confidence=round(avg_conf, 4),
        average_inference_time_ms=round(avg_inf, 2),
        predictions_today=predictions_today,
    )
