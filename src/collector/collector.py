import requests
import time
from datetime import datetime
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.gpu_metrics import GpuMetricsRecord
from src.database.client import supabase

class GpuStatsCollector:
    def __init__(self, api_url="http://localhost:5000/api/gpu-stats", interval=0.25):
        self.api_url = api_url
        self.interval = interval

    def fetch_stats(self):
        """Fetch GPU stats from the local API"""
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching GPU stats: {e}")
            return None

    def collect_and_store(self):
        """Fetch stats and store them in Supabase"""
        data = self.fetch_stats()
        if data:
            try:
                metrics = GpuMetricsRecord(**data)
                result = supabase.insert_gpu_metrics(metrics)
                return result
            except Exception as e:
                print(f"Error storing metrics: {e}")
                return None

    def run_collector(self):
        """Run the collector continuously"""
        print(f"Starting GPU stats collection every {self.interval} seconds...")
        while True:
            try:
                self.collect_and_store()
                time.sleep(self.interval)
            except KeyboardInterrupt:
                print("\nStopping GPU stats collection...")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                time.sleep(self.interval)

def main():
    collector = GpuStatsCollector()
    collector.run_collector()

if __name__ == "__main__":
    main()