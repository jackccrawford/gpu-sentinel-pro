import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json
import re
from collections import deque
from datetime import datetime, timedelta
from typing import Optional
import logging

# Import our components
from src.database.client import db
from src.models.gpu_metrics import GpuMetricsRecord, GpuBurnMetrics, NvidiaInfo, GpuMetrics
from src.service.alerts import alert_system

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GPU Metrics Service",
    description="Monitors NVIDIA GPUs and stores metrics in PostgreSQL",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory state
temperature_history = {}
peak_temperatures = {}
logging_enabled = True  # New state variable

def get_nvidia_info() -> NvidiaInfo:
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        cuda_version = "Unknown"
        driver_version = "Unknown"
        
        if result.stdout:
            cuda_match = re.search(r'CUDA Version: ([\d\.]+)', result.stdout)
            if cuda_match:
                cuda_version = cuda_match.group(1)
            
            driver_match = re.search(r'Driver Version: ([\d\.]+)', result.stdout)
            if driver_match:
                driver_version = driver_match.group(1)

        return NvidiaInfo(
            driver_version=driver_version,
            cuda_version=cuda_version
        )
    except Exception as e:
        logger.error(f"Error getting NVIDIA info: {str(e)}")
        return NvidiaInfo(
            driver_version="Unknown",
            cuda_version="Unknown"
        )

def get_gpu_metrics() -> GpuMetricsRecord:
    try:
        nvidia_info = get_nvidia_info()
        
        gpu_info = subprocess.run([
            'nvidia-smi', 
            '--query-gpu=index,name,fan.speed,power.draw,memory.total,memory.used,utilization.gpu,temperature.gpu,compute_mode,power.limit',
            '--format=csv,noheader,nounits'
        ], capture_output=True, text=True)

        gpus = []
        current_time = datetime.now().timestamp()
        
        if gpu_info.stdout.strip():
            for line in gpu_info.stdout.strip().split('\n'):
                values = [v.strip() for v in line.split(',')]
                if len(values) >= 10:
                    gpu_index = int(values[0])
                    temperature = float(values[7])
                    
                    if gpu_index not in temperature_history:
                        temperature_history[gpu_index] = deque(maxlen=40)
                    temperature_history[gpu_index].append((current_time, temperature))
                    
                    if gpu_index not in peak_temperatures or temperature > peak_temperatures[gpu_index]:
                        peak_temperatures[gpu_index] = temperature

                    gpu = GpuMetrics(
                        index=gpu_index,
                        name=values[1],
                        fan_speed=int(float(values[2])),
                        power_draw=float(values[3]),
                        power_limit=int(float(values[9])),
                        memory_total=int(float(values[4])),
                        memory_used=int(float(values[5])),
                        gpu_utilization=int(float(values[6])),
                        temperature=int(temperature),
                        peak_temperature=int(peak_temperatures[gpu_index]),
                        temp_change_rate=0,
                        compute_mode=values[8]
                    )
                    gpus.append(gpu)

        metrics = GpuMetricsRecord(
            nvidia_info=nvidia_info,
            gpus=gpus,
            processes=[],
            gpu_burn_metrics=GpuBurnMetrics(
                running=False,
                duration=0,
                errors=0
            ),
            success=True,
            timestamp=datetime.utcnow().isoformat()
        )

        # Check for alerts
        alert_system.check_metrics(metrics)

        # Store in database only if logging is enabled
        if logging_enabled:
            try:
                db.insert_gpu_metrics(metrics)
                logger.info("Metrics stored in database")
            except Exception as e:
                logger.error(f"Failed to store metrics: {e}")
        else:
            logger.debug("Metrics logging is disabled, skipping database insert")

        return metrics
    except Exception as e:
        logger.error(f"Error getting GPU metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Service information and status"""
    return {
        "name": "GPU Metrics Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "GET /api/gpu-stats": "Current GPU metrics",
            "GET /api/gpu-stats/history": "Historical GPU metrics (optional: start_time, end_time, hours=24)",
            "GET /api/alerts": "Recent alerts"
        }
    }

@app.get("/api/gpu-stats")
async def get_gpu_stats():
    """Get current GPU statistics"""
    return get_gpu_metrics()

@app.get("/api/gpu-stats/history")
async def get_gpu_history(
    start_time: Optional[str] = Query(
        None,
        description="Start time in ISO format (default: 24 hours ago)"
    ),
    end_time: Optional[str] = Query(
        None,
        description="End time in ISO format (default: current time)"
    ),
    hours: Optional[int] = Query(
        24,
        description="Number of hours to look back (used if start_time not provided)",
        ge=1,
        le=168  # 1 week max
    )
):
    """Get historical GPU metrics"""
    try:
        # If no start_time provided, use hours parameter
        if not start_time:
            start_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        
        # If no end_time provided, use current time
        if not end_time:
            end_time = datetime.utcnow().isoformat()

        # Validate and parse timestamps
        try:
            datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid timestamp format. Use ISO format (e.g., 2024-01-01T00:00:00Z)"
            )

        return db.get_metrics_in_timerange(start_time, end_time)
    except Exception as e:
        logger.error(f"Error getting historical data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alerts")
async def get_alerts(hours: int = 24):
    """Get recent alerts"""
    return alert_system.get_recent_alerts(hours)

@app.post("/api/logging/toggle")
async def toggle_logging():
    """Toggle metrics logging to database"""
    global logging_enabled
    logging_enabled = not logging_enabled
    logger.info(f"Metrics logging {'enabled' if logging_enabled else 'disabled'}")
    return {"logging_enabled": logging_enabled}

@app.get("/api/logging/status")
async def get_logging_status():
    """Get current logging status"""
    return {"logging_enabled": logging_enabled}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting GPU Metrics Service")
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=5500,
        reload=True,
        workers=1
    )
