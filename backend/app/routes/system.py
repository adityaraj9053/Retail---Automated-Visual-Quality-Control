"""
VisionSpec QC — Phase 5: System Monitor Route
GET /system/metrics — returns CPU, Memory, GPU(mock), and Uptime.
"""
import psutil
import time
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["System"])

class SystemMetricsResponse(BaseModel):
    cpu_percent: float
    memory_percent: float
    gpu_percent: float
    uptime_seconds: float

# Start time
start_time = time.time()

@router.get("/system/metrics", response_model=SystemMetricsResponse)
async def get_system_metrics():
    """Returns hardware and system usage metrics for the dashboard."""
    return SystemMetricsResponse(
        cpu_percent=psutil.cpu_percent(interval=0.1),
        memory_percent=psutil.virtual_memory().percent,
        gpu_percent=0.0, # Placeholder as we might not have GPU tools in psutil
        uptime_seconds=time.time() - start_time
    )
