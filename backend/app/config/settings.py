"""
VisionSpec QC - Application Configuration
Centralized settings for the backend server, model paths, and database.
"""

import os
from pathlib import Path
from pydantic import BaseModel

# ── Base Paths ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATASETS_DIR = BASE_DIR / "datasets"
MODELS_DIR = BASE_DIR / "trained_models"
LOGS_DIR = BASE_DIR / "logs"
UPLOADS_DIR = BASE_DIR / "uploads"

# Create directories if they don't exist
for directory in [DATASETS_DIR, MODELS_DIR, LOGS_DIR, UPLOADS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


# ── Application Settings ────────────────────────────────────
class AppSettings(BaseModel):
    APP_NAME: str = "VisionSpec QC"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Model settings
    MODEL_PATH: str = str(MODELS_DIR / "pcb_model.h5")
    IMAGE_SIZE: int = 224
    BATCH_SIZE: int = 32
    CONFIDENCE_THRESHOLD: float = 0.5

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'visionspec.db'}"

    # Upload limits
    MAX_UPLOAD_SIZE_MB: int = 10

    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    # Class labels
    CLASS_LABELS: list = ["Defect", "Pass"]


settings = AppSettings()
