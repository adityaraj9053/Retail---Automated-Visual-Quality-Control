"""
VisionSpec QC - Database Models
SQLAlchemy ORM models for prediction logging and analytics.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from backend.app.config.settings import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PredictionLog(Base):
    """Stores every prediction made by the system for history & analytics."""
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    image_filename = Column(String(255), nullable=True)
    predicted_label = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    inference_time_ms = Column(Float, nullable=True)
    source = Column(String(50), default="upload")  # "upload" or "webcam"
    heatmap_path = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)


class SystemMetric(Base):
    """Tracks system performance metrics over time."""
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    fps = Column(Float, nullable=True)
    cpu_usage = Column(Float, nullable=True)
    memory_usage = Column(Float, nullable=True)
    gpu_usage = Column(Float, nullable=True)
    api_latency_ms = Column(Float, nullable=True)


def init_db():
    """Initialize the database and create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
