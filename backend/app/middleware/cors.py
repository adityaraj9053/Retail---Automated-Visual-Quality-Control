"""
VisionSpec QC - CORS Middleware
Configures Cross-Origin Resource Sharing for the FastAPI app.
"""

from fastapi.middleware.cors import CORSMiddleware
from backend.app.config.settings import settings


def setup_cors(app):
    """
    Add CORS middleware to the FastAPI app to allow frontend communication.

    Args:
        app: The FastAPI application instance.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
