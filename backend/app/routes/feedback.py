"""
VisionSpec QC — Extra Feature: Feedback (Human-in-the-Loop)
POST /feedback — Allows operators to correct a prediction label.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.schemas.prediction import FeedbackRequest
from backend.app.models.database import get_db, PredictionLog

router = APIRouter(tags=["Feedback"])

@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    """
    Submit feedback on a prediction to support Human-in-the-Loop (HITL).
    Updates the prediction log with the corrected label.
    """
    log_entry = db.query(PredictionLog).filter(PredictionLog.id == request.prediction_id).first()
    
    if not log_entry:
        raise HTTPException(status_code=404, detail="Prediction not found")
        
    log_entry.predicted_label = f"{request.corrected_label} (Corrected)"
    # A real system might also save the notes or a boolean flag `is_corrected`
    db.commit()
    
    return {"message": "Feedback received and prediction updated.", "prediction_id": request.prediction_id}
