import yaml
import os
from pathlib import Path

class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        config_path = Path(__file__).parent / 'config.yaml'
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
            
    def get(self, *keys):
        """Get a config value using dot notation, e.g., config.get('polling', 'base_interval')"""
        value = self._config
        for key in keys:
            value = value[key]
        return value
    
    def reload(self):
        """Reload configuration file"""
        self._load_config()
        return self._config

# Create singleton instance
config = Config()

