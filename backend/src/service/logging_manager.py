import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import psycopg2
from psycopg2.extras import Json
from contextlib import contextmanager
import yaml

logger = logging.getLogger(__name__)

class LoggingManager:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.is_logging_enabled = True
        self._setup_db_connection()

    def _load_config(self) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    def _setup_db_connection(self):
        """Setup database connection parameters."""
        db_config = self.config.get('database', {})
        self.db_params = {
            'dbname': db_config.get('name', 'gpu_sentinel'),
            'user': db_config.get('user', 'postgres'),
            'password': db_config.get('password', ''),
            'host': db_config.get('host', 'localhost'),
            'port': db_config.get('port', 5432)
        }

    @contextmanager
    def get_db_connection(self):
        """Context manager for database connections."""
        conn = None
        try:
            conn = psycopg2.connect(**self.db_params)
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def toggle_logging(self, enabled: bool) -> bool:
        """Enable or disable logging."""
        self.is_logging_enabled = enabled
        return self.is_logging_enabled

    def log_gpu_metrics(self, metrics: Dict) -> bool:
        """Log GPU metrics to database if logging is enabled."""
        if not self.is_logging_enabled:
            return False

        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO gpu_metrics (
                            timestamp, duration, errors, running,
                            cuda_version, driver_version, gpus, processes, success
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        datetime.now(),
                        metrics.get('duration', 0),
                        metrics.get('errors', 0),
                        metrics.get('running', False),
                        metrics.get('cuda_version', ''),
                        metrics.get('driver_version', ''),
                        Json(metrics.get('gpus', [])),
                        Json(metrics.get('processes', [])),
                        metrics.get('success', False)
                    ))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error logging GPU metrics: {e}")
            return False

    def get_retention_policy(self) -> Dict[str, int]:
        """Get current data retention policy."""
        return {
            'metrics_retention_days': self.config.get('retention', {}).get('metrics_days', 30),
            'alerts_retention_days': self.config.get('retention', {}).get('alerts_days', 90)
        }

    def update_retention_policy(self, metrics_days: int, alerts_days: int) -> bool:
        """Update data retention policy."""
        try:
            self.config['retention'] = {
                'metrics_days': metrics_days,
                'alerts_days': alerts_days
            }
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f)
            return True
        except Exception as e:
            logger.error(f"Error updating retention policy: {e}")
            return False

    def cleanup_old_data(self) -> Dict[str, int]:
        """Clean up data based on retention policy."""
        retention = self.get_retention_policy()
        deleted_counts = {'metrics': 0, 'alerts': 0}

        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Clean up old metrics
                    cur.execute("""
                        DELETE FROM gpu_metrics
                        WHERE timestamp < NOW() - INTERVAL '%s days'
                        RETURNING COUNT(*)
                    """, (retention['metrics_retention_days'],))
                    deleted_counts['metrics'] = cur.fetchone()[0]

                    # Clean up old alerts
                    cur.execute("""
                        DELETE FROM alert_history
                        WHERE created_at < NOW() - INTERVAL '%s days'
                        RETURNING COUNT(*)
                    """, (retention['alerts_retention_days'],))
                    deleted_counts['alerts'] = cur.fetchone()[0]

                conn.commit()
            return deleted_counts
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return deleted_counts

    def export_data(self, start_date: datetime, end_date: datetime, 
                   export_path: str) -> bool:
        """Export data within date range to JSON file."""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT * FROM gpu_metrics
                        WHERE timestamp BETWEEN %s AND %s
                        ORDER BY timestamp
                    """, (start_date, end_date))
                    
                    columns = [desc[0] for desc in cur.description]
                    data = []
                    
                    for row in cur:
                        data.append(dict(zip(columns, row)))

            # Convert datetime objects to ISO format
            for record in data:
                record['timestamp'] = record['timestamp'].isoformat()
                record['created_at'] = record['created_at'].isoformat()

            with open(export_path, 'w') as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return False

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    manager = LoggingManager()
    
    # Example: Toggle logging
    manager.toggle_logging(False)
    
    # Example: Update retention policy
    manager.update_retention_policy(metrics_days=60, alerts_days=120)
    
    # Example: Clean up old data
    deleted = manager.cleanup_old_data()
    print(f"Cleaned up {deleted['metrics']} metrics and {deleted['alerts']} alerts")
