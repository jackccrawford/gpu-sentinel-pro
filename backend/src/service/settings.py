import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Settings:
    def __init__(self):
        self.config_path = Path(__file__).parent / 'config.yaml'
        self.load_config()

    def load_config(self):
        """Load configuration from yaml file"""
        try:
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f)
                logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            # Provide sensible defaults
            self._config = {
                'polling': {
                    'base_interval': 0.25,
                    'max_interval': 3600,
                    'activity_thresholds': {
                        'low': {'idle_time': 300, 'interval': 60},
                        'medium': {'idle_time': 1800, 'interval': 300},
                        'high': {'idle_time': 7200, 'interval': 3600}
                    }
                },
                'retention': {
                    'days_to_keep': 30,
                    'cleanup_on_startup': True,
                    'cleanup_on_shutdown': True
                },
                'alerts': {
                    'temperature': {'warning': 80, 'critical': 90},
                    'gpu_utilization': {'warning': 90, 'critical': 95},
                    'memory_usage': {'warning': 90, 'critical': 95}
                }
            }
            logger.info("Using default configuration")

    def get(self, *keys, default=None):
        """Get configuration value using dot notation"""
        try:
            value = self._config
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def reload(self):
        """Reload configuration file"""
        self.load_config()
        return self._config

# Create singleton instance
settings = Settings()
