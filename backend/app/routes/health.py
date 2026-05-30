"""
VisionSpec QC - Health Route
Provides system health check and status information.
"""

import time
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.config.settings import settings
from backend.app.models.database import get_db
from backend.app.schemas.prediction import HealthResponse

router = APIRouter(tags=["System"])

# Track server start time
_start_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.
    Returns the current status of the backend, model, and database.
    """
    # Check database connectivity
    db_connected = False
    try:
        db.execute("SELECT 1")
        db_connected = True
    except Exception:
        db_connected = False

    # Check if model file exists
    from pathlib import Path
    model_loaded = Path(settings.MODEL_PATH).exists()

    uptime = time.time() - _start_time

    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        model_loaded=model_loaded,
        database_connected=db_connected,
        uptime_seconds=round(uptime, 2),
    )
