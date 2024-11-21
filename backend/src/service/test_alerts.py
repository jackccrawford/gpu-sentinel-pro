import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.service.alerts import alert_system
from src.models.gpu_metrics import GpuMetricsRecord, GpuMetrics, NvidiaInfo, GpuBurnMetrics
from datetime import datetime

def test_alerts():
    print("Testing alert system...")
    
    # Create test metrics with high temperature
    metrics = GpuMetricsRecord(
        gpu_burn_metrics=GpuBurnMetrics(
            duration=0,
            errors=0,
            running=False
        ),
        gpus=[
            GpuMetrics(
                compute_mode="Default",
                fan_speed=100,  # High fan speed
                gpu_utilization=95,  # High utilization
                index=0,
                memory_total=12288,
                memory_used=11674,  # High memory usage
                name="NVIDIA TITAN Xp",
                peak_temperature=85,
                power_draw=240,
                power_limit=250,
                temp_change_rate=0,
                temperature=85  # High temperature
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

    # Check for alerts
    alerts = alert_system.check_metrics(metrics)
    print(f"\nGenerated {len(alerts)} alerts:")
    for alert in alerts:
        print(f"Alert: {alert['metric']} on GPU {alert['gpu_index']}")
        print(f"Value: {alert['value']:.1f}, Threshold: {alert['threshold']}")
        print(f"Severity: {alert['severity']}\n")

    # Get recent alerts
    recent = alert_system.get_recent_alerts(hours=1)
    print(f"Recent alerts in database: {len(recent)}")

if __name__ == "__main__":
    test_alerts()
