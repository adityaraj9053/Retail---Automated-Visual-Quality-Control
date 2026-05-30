"""
VisionSpec QC — Phase 4: History Route
GET /history — returns paginated prediction history from the database.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.schemas.prediction import PredictionHistoryResponse, PredictionHistoryItem
from backend.app.models.database import get_db, PredictionLog

router = APIRouter(tags=["History"])


@router.get("/history", response_model=PredictionHistoryResponse)
async def get_history(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Retrieve prediction history for the analytics dashboard and session logs.
    Results are ordered by timestamp (newest first).
    """
    
    # Calculate offset
    offset = (page - 1) * limit
    
    # Get total count
    total = db.query(PredictionLog).count()
    
    # Get paginated results
    logs = (
        db.query(PredictionLog)
        .order_by(desc(PredictionLog.timestamp))
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    # Convert ORM models to Pydantic models
    predictions = [
        PredictionHistoryItem(
            id=log.id,
            timestamp=log.timestamp,
            image_filename=log.image_filename,
            predicted_label=log.predicted_label,
            confidence=log.confidence,
            inference_time_ms=log.inference_time_ms,
            source=log.source,
        )
        for log in logs
    ]
    
    return PredictionHistoryResponse(
        total=total,
        predictions=predictions
    )
