from typing import List, Optional
from pydantic import BaseModel


class GpuBurnMetrics(BaseModel):
    duration: int
    errors: int
    running: bool


class NvidiaInfo(BaseModel):
    cuda_version: str
    driver_version: str


class GpuMetrics(BaseModel):
    compute_mode: str
    fan_speed: int
    gpu_utilization: int
    index: int
    memory_total: int
    memory_used: int
    name: str
    peak_temperature: int
    power_draw: float
    power_limit: int
    temp_change_rate: int
    temperature: int


class GpuMetricsRecord(BaseModel):
    gpu_burn_metrics: GpuBurnMetrics
    gpus: List[GpuMetrics]
    nvidia_info: NvidiaInfo
    processes: List[dict] = []
    success: bool
    timestamp: Optional[str] = None  # We'll add this for tracking when the record was created