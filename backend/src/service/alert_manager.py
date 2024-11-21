from datetime import datetime, timedelta
import logging
from .config import config
from src.database.client import db

logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self):
        self.alert_cache = {}  # {metric_name_gpu_index: last_alert_time}
        self.load_config()

    def load_config(self):
        """Load alert configuration"""
        self.thresholds = config.get('alerts')
        logger.info("Alert thresholds loaded from config")

    def check_metrics(self, gpu_metrics):
        """Check GPU metrics against thresholds"""
        alerts = []
        current_time = datetime.utcnow()

        for gpu in gpu_metrics.gpus:
            # Temperature checks
            alerts.extend(self._check_metric(
                metric_name='temperature',
                metric_value=gpu.temperature,
                gpu_index=gpu.index,
                warning=self.thresholds['temperature']['warning'],
                critical=self.thresholds['temperature']['critical'],
                duration=self.thresholds['temperature']['duration'],
                current_time=current_time
            ))

            # GPU utilization checks
            alerts.extend(self._check_metric(
                metric_name='gpu_utilization',
                metric_value=gpu.gpu_utilization,
                gpu_index=gpu.index,
                warning=self.thresholds['gpu_utilization']['warning'],
                critical=self.thresholds['gpu_utilization']['critical'],
                duration=self.thresholds['gpu_utilization']['duration'],
                current_time=current_time
            ))

            # Memory usage checks
            memory_usage_percent = (gpu.memory_used / gpu.memory_total) * 100
            alerts.extend(self._check_metric(
                metric_name='memory_usage',
                metric_value=memory_usage_percent,
                gpu_index=gpu.index,
                warning=self.thresholds['memory_usage']['warning'],
                critical=self.thresholds['memory_usage']['critical'],
                duration=self.thresholds['memory_usage']['duration'],
                current_time=current_time
            ))

            # Power usage checks
            power_usage_percent = (gpu.power_draw / gpu.power_limit) * 100
            alerts.extend(self._check_metric(
                metric_name='power_draw',
                metric_value=power_usage_percent,
                gpu_index=gpu.index,
                warning=self.thresholds['power_draw']['warning'],
                critical=self.thresholds['power_draw']['critical'],
                duration=self.thresholds['power_draw']['duration'],
                current_time=current_time
            ))

        if alerts:
            self._store_alerts(alerts)
            logger.warning(f"Generated {len(alerts)} alerts")

        return alerts

    def _check_metric(self, metric_name, metric_value, gpu_index, warning, critical, 
                     duration, current_time):
        """Check a single metric against its thresholds"""
        alerts = []
        cache_key = f"{metric_name}_gpu{gpu_index}"
        
        # Check if we should alert based on duration
        last_alert = self.alert_cache.get(cache_key)
        should_alert = (
            last_alert is None or 
            (current_time - last_alert).total_seconds() >= duration
        )

        if not should_alert:
            return alerts

        if metric_value >= critical:
            alerts.append({
                'metric_name': metric_name,
                'gpu_index': gpu_index,
                'value': metric_value,
                'threshold': critical,
                'severity': 'critical',
                'timestamp': current_time
            })
            self.alert_cache[cache_key] = current_time
        elif metric_value >= warning:
            alerts.append({
                'metric_name': metric_name,
                'gpu_index': gpu_index,
                'value': metric_value,
                'threshold': warning,
                'severity': 'warning',
                'timestamp': current_time
            })
            self.alert_cache[cache_key] = current_time

        return alerts

    def _store_alerts(self, alerts):
        """Store alerts in the database"""
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

    def cleanup_old_alerts(self):
        """Clean up old alerts based on retention config"""
        try:
            retention_days = config.get('retention', 'days_to_keep')
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT cleanup_old_alerts(%s)", (retention_days,))
            logger.info(f"Cleaned up alerts older than {retention_days} days")
        except Exception as e:
            logger.error(f"Failed to cleanup old alerts: {e}")

    def get_recent_alerts(self, hours=24):
        """Get recent alerts"""
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
alert_manager = AlertManager()
