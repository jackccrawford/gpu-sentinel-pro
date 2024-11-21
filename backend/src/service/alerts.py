from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any
from src.service.settings import settings
from src.database.client import db
from src.models.gpu_metrics import GpuMetricsRecord

logger = logging.getLogger(__name__)

class AlertLevel:
    CRITICAL = "critical"
    WARNING = "warning"
    CAUTION = "caution"
    GOOD = "good"
    IDEAL = "ideal"

class AlertSystem:
    def __init__(self):
        # Cache structure: {f"{gpu_index}:{metric}:{severity}": timestamp}
        self.alert_cache = {}
        # Minimum time between similar alerts (5 minutes)
        self.alert_cooldown = timedelta(minutes=5)

    def should_trigger_alert(self, gpu_index: int, metric: str, 
                           severity: str, value: float) -> bool:
        """Determine if an alert should be triggered based on cache and cooldown"""
        cache_key = f"{gpu_index}:{metric}:{severity}"
        current_time = datetime.utcnow()

        # If no previous alert, always trigger
        if cache_key not in self.alert_cache:
            self.alert_cache[cache_key] = current_time
            return True

        # Check if enough time has passed since last alert
        last_alert_time = self.alert_cache[cache_key]
        if current_time - last_alert_time >= self.alert_cooldown:
            self.alert_cache[cache_key] = current_time
            return True

        return False

    def get_metric_level(self, metric: str, value: float) -> str:
        """Determine alert level for any metric based on thresholds"""
        thresholds = settings.get('alerts', metric)
        if value >= thresholds['critical']:
            return AlertLevel.CRITICAL
        elif value >= thresholds['warning']:
            return AlertLevel.WARNING
        elif value >= thresholds['caution']:
            return AlertLevel.CAUTION
        elif value >= thresholds['good']:
            return AlertLevel.GOOD
        return AlertLevel.IDEAL

    def check_metrics(self, metrics: GpuMetricsRecord) -> List[Dict[str, Any]]:
        """Check GPU metrics against all threshold levels"""
        alerts = []
        current_time = datetime.utcnow()

        for gpu in metrics.gpus:
            # Temperature check
            temp_level = self.get_metric_level('temperature', gpu.temperature)
            if temp_level in [AlertLevel.CRITICAL, AlertLevel.WARNING]:
                if self.should_trigger_alert(gpu.index, 'temperature', temp_level, gpu.temperature):
                    alerts.append(self._create_alert(
                        'temperature', gpu.index, gpu.temperature,
                        settings.get('alerts', 'temperature', temp_level),
                        temp_level, current_time
                    ))

            # GPU utilization check
            util_level = self.get_metric_level('gpu_utilization', gpu.gpu_utilization)
            if util_level in [AlertLevel.CRITICAL, AlertLevel.WARNING]:
                if self.should_trigger_alert(gpu.index, 'gpu_utilization', util_level, gpu.gpu_utilization):
                    alerts.append(self._create_alert(
                        'gpu_utilization', gpu.index, gpu.gpu_utilization,
                        settings.get('alerts', 'gpu_utilization', util_level),
                        util_level, current_time
                    ))

            # Fan speed check
            fan_level = self.get_metric_level('fan_speed', gpu.fan_speed)
            if fan_level in [AlertLevel.CRITICAL, AlertLevel.WARNING]:
                if self.should_trigger_alert(gpu.index, 'fan_speed', fan_level, gpu.fan_speed):
                    alerts.append(self._create_alert(
                        'fan_speed', gpu.index, gpu.fan_speed,
                        settings.get('alerts', 'fan_speed', fan_level),
                        fan_level, current_time
                    ))

            # Memory usage check
            memory_percent = (gpu.memory_used / gpu.memory_total) * 100
            mem_level = self.get_metric_level('memory_usage', memory_percent)
            if mem_level in [AlertLevel.CRITICAL, AlertLevel.WARNING]:
                if self.should_trigger_alert(gpu.index, 'memory_usage', mem_level, memory_percent):
                    alerts.append(self._create_alert(
                        'memory_usage', gpu.index, memory_percent,
                        settings.get('alerts', 'memory_usage', mem_level),
                        mem_level, current_time
                    ))

        if alerts:
            self._store_alerts(alerts)
            logger.warning(f"Generated {len(alerts)} alerts")

        return alerts

    def _create_alert(self, metric: str, gpu_index: int, value: float, 
                     threshold: float, severity: str, timestamp: datetime) -> Dict[str, Any]:
        """Create alert dictionary"""
        return {
            'metric': metric,
            'gpu_index': gpu_index,
            'value': value,
            'threshold': threshold,
            'severity': severity,
            'timestamp': timestamp
        }

    def _store_alerts(self, alerts: List[Dict[str, Any]]):
        """Store alerts in database"""
        try:
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    for alert in alerts:
                        cur.execute("""
                            INSERT INTO alert_history (
                                gpu_index, metric_value, threshold_value, 
                                severity, created_at
                            ) VALUES (%s, %s, %s, %s, %s)
                        """, (
                            alert['gpu_index'],
                            alert['value'],
                            alert['threshold'],
                            alert['severity'],
                            alert['timestamp']
                        ))
        except Exception as e:
            logger.error(f"Failed to store alerts: {e}")

    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts from database"""
        try:
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT * FROM alert_history
                        WHERE created_at > NOW() - interval '%s hours'
                        ORDER BY created_at DESC
                    """, (hours,))
                    columns = [desc[0] for desc in cur.description]
                    return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get recent alerts: {e}")
            return []

# Create singleton instance
alert_system = AlertSystem()
