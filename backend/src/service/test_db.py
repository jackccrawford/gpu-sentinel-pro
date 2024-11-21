import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.database.client import db
from src.models.gpu_metrics import GpuMetricsRecord, GpuBurnMetrics, NvidiaInfo, GpuMetrics
from datetime import datetime

def test_db_connection():
    try:
        # Create a test record
        metrics = GpuMetricsRecord(
            gpu_burn_metrics=GpuBurnMetrics(
                duration=0,
                errors=0,
                running=False
            ),
            gpus=[
                GpuMetrics(
                    compute_mode="Default",
                    fan_speed=30,
                    gpu_utilization=10,
                    index=0,
                    memory_total=12288,
                    memory_used=135,
                    name="NVIDIA TITAN Xp",
                    peak_temperature=48,
                    power_draw=67.17,
                    power_limit=250,
                    temp_change_rate=0,
                    temperature=48
                )
            ],
            nvidia_info=NvidiaInfo(
                cuda_version="12.2",
                driver_version="535.183.01"
            ),
            processes=[],
            success=True,
            timestamp=datetime.utcnow().isoformat()
        )

        print("Inserting test record...")
        result = db.insert_gpu_metrics(metrics)
        print(f"Insert successful, record ID: {result['id']}")

        print("\nRetrieving recent metrics...")
        recent = db.get_metrics_in_timerange(
            start_time=(datetime.utcnow().replace(hour=0, minute=0, second=0)).isoformat(),
            end_time=datetime.utcnow().isoformat()
        )
        print(f"Found {len(recent)} records today")
        
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing database connection...")
    success = test_db_connection()
    print(f"\nTest {'successful' if success else 'failed'}")
