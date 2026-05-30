"""
VisionSpec QC — FastAPI Main Application Entry Point
Initializes the FastAPI server, middleware, routes, and database.
"""

import time
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.app.config.settings import settings
from backend.app.middleware.cors import setup_cors
from backend.app.models.database import init_db
from backend.app.routes import health, predict, webcam, analytics, history, system, feedback
from backend.app.services.inference import load_model as load_ai_model, is_model_loaded

# ── Initialize FastAPI App ──────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered PCB Visual Inspection System with Explainable AI",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware ──────────────────────────────────────────────
setup_cors(app)

# ── Register Routes ─────────────────────────────────────────
app.include_router(health.router, prefix="/api")
app.include_router(predict.router, prefix="/api")      # Phase 2 ✅
app.include_router(webcam.router, prefix="/api")       # Phase 3 ✅
app.include_router(analytics.router, prefix="/api")    # Phase 4 ✅
app.include_router(history.router, prefix="/api")      # Phase 4 ✅
app.include_router(system.router, prefix="/api")       # Phase 5 ✅
app.include_router(feedback.router, prefix="/api")     # Extra Unique Feature ✅


# ── Startup & Shutdown Events ──────────────────────────────
@app.on_event("startup")
async def on_startup():
    """Initialize database and load AI model on server start."""
    print(f"\n[*] {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    init_db()
    print("[*] Database initialized.")
    # Phase 2: Load the trained AI model
    model_status = load_ai_model()
    if model_status:
        print("[*] AI Model loaded and ready for inference.")
    else:
        print("[!] AI Model not found — upload predictions will be unavailable.")
        print("    Train first: python -m backend.scripts.train_model")
    print(f"[*] Server running at http://{settings.HOST}:{settings.PORT}")
    print(f"[*] API Docs at http://{settings.HOST}:{settings.PORT}/docs\n")


@app.on_event("shutdown")
async def on_shutdown():
    """Cleanup on server shutdown."""
    print(f"\n[-] {settings.APP_NAME} shutting down...\n")


# ── Root Endpoint ───────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


# ── Run Server ──────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )
