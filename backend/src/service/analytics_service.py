import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from scipy import stats
from .config import config
from src.database.client import db

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.anomaly_threshold = 2.0  # Standard deviations for anomaly detection

    def get_historical_metrics(self, start_time: datetime, 
                             end_time: datetime) -> pd.DataFrame:
        """Fetch historical GPU metrics within the specified time range."""
        try:
            with db.get_connection() as conn:
                query = """
                    SELECT 
                        timestamp,
                        jsonb_array_elements(gpus) as gpu_data
                    FROM gpu_metrics
                    WHERE timestamp BETWEEN %s AND %s
                    ORDER BY timestamp
                """
                df = pd.read_sql_query(query, conn, params=(start_time, end_time))
                
                # Parse GPU data from JSONB
                df['gpu_data'] = df['gpu_data'].apply(eval)
                metrics_df = pd.json_normalize(df['gpu_data'])
                
                # Combine with timestamp
                metrics_df['timestamp'] = df['timestamp']
                
                return metrics_df
        except Exception as e:
            logger.error(f"Error fetching historical metrics: {e}")
            return pd.DataFrame()

    def calculate_usage_patterns(self, days: int = 7) -> Dict:
        """Calculate GPU usage patterns over time."""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        df = self.get_historical_metrics(start_time, end_time)
        if df.empty:
            return {}

        patterns = {
            'hourly_avg': self._calculate_hourly_averages(df),
            'daily_avg': self._calculate_daily_averages(df),
            'peak_usage_times': self._find_peak_usage_times(df),
            'utilization_distribution': self._calculate_utilization_distribution(df)
        }
        
        return patterns

    def detect_anomalies(self, hours: int = 24) -> List[Dict]:
        """Detect anomalies in GPU metrics."""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        df = self.get_historical_metrics(start_time, end_time)
        if df.empty:
            return []

        anomalies = []
        
        # Check for anomalies in different metrics
        metrics = ['utilization', 'temperature', 'memory_used', 'power_draw']
        for metric in metrics:
            if metric in df.columns:
                anomalies.extend(
                    self._detect_metric_anomalies(df, metric)
                )
        
        return anomalies

    def analyze_performance_trends(self, days: int = 30) -> Dict:
        """Analyze long-term performance trends."""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        df = self.get_historical_metrics(start_time, end_time)
        if df.empty:
            return {}

        trends = {
            'utilization_trend': self._calculate_trend(df, 'utilization'),
            'temperature_trend': self._calculate_trend(df, 'temperature'),
            'memory_trend': self._calculate_trend(df, 'memory_used'),
            'power_trend': self._calculate_trend(df, 'power_draw')
        }
        
        return trends

    def calculate_efficiency_metrics(self, days: int = 7) -> Dict:
        """Calculate GPU efficiency metrics."""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        df = self.get_historical_metrics(start_time, end_time)
        if df.empty:
            return {}

        metrics = {}
        
        # Calculate power efficiency (GFLOPS/Watt if available)
        if all(col in df.columns for col in ['power_draw', 'utilization']):
            metrics['power_efficiency'] = self._calculate_power_efficiency(df)
        
        # Calculate memory efficiency
        if all(col in df.columns for col in ['memory_used', 'memory_total']):
            metrics['memory_efficiency'] = self._calculate_memory_efficiency(df)
        
        return metrics

    def _calculate_hourly_averages(self, df: pd.DataFrame) -> Dict:
        """Calculate average metrics by hour of day."""
        df['hour'] = df['timestamp'].dt.hour
        hourly_avg = df.groupby('hour').agg({
            'utilization': 'mean',
            'temperature': 'mean',
            'memory_used': 'mean',
            'power_draw': 'mean'
        }).to_dict()
        
        return hourly_avg

    def _calculate_daily_averages(self, df: pd.DataFrame) -> Dict:
        """Calculate average metrics by day of week."""
        df['day'] = df['timestamp'].dt.dayofweek
        daily_avg = df.groupby('day').agg({
            'utilization': 'mean',
            'temperature': 'mean',
            'memory_used': 'mean',
            'power_draw': 'mean'
        }).to_dict()
        
        return daily_avg

    def _find_peak_usage_times(self, df: pd.DataFrame) -> List[Dict]:
        """Find times of peak GPU usage."""
        peaks = []
        metrics = ['utilization', 'temperature', 'memory_used', 'power_draw']
        
        for metric in metrics:
            if metric in df.columns:
                peak_idx = df[metric].idxmax()
                peaks.append({
                    'metric': metric,
                    'value': df.loc[peak_idx, metric],
                    'timestamp': df.loc[peak_idx, 'timestamp']
                })
        
        return peaks

    def _calculate_utilization_distribution(self, df: pd.DataFrame) -> Dict:
        """Calculate distribution of GPU utilization."""
        if 'utilization' not in df.columns:
            return {}

        bins = [0, 20, 40, 60, 80, 100]
        labels = ['0-20%', '21-40%', '41-60%', '61-80%', '81-100%']
        df['util_bin'] = pd.cut(df['utilization'], bins=bins, labels=labels)
        
        distribution = df['util_bin'].value_counts().to_dict()
        return {str(k): v for k, v in distribution.items()}

    def _detect_metric_anomalies(self, df: pd.DataFrame, 
                               metric: str) -> List[Dict]:
        """Detect anomalies in a specific metric."""
        if metric not in df.columns:
            return []

        mean = df[metric].mean()
        std = df[metric].std()
        threshold = self.anomaly_threshold * std
        
        anomalies = []
        anomaly_points = df[abs(df[metric] - mean) > threshold]
        
        for idx, row in anomaly_points.iterrows():
            anomalies.append({
                'metric': metric,
                'value': row[metric],
                'timestamp': row['timestamp'],
                'deviation': abs(row[metric] - mean) / std
            })
        
        return anomalies

    def _calculate_trend(self, df: pd.DataFrame, metric: str) -> Dict:
        """Calculate trend for a specific metric."""
        if metric not in df.columns:
            return {}

        # Calculate linear regression
        x = np.arange(len(df))
        y = df[metric].values
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        return {
            'slope': slope,
            'r_squared': r_value**2,
            'p_value': p_value,
            'trend_direction': 'increasing' if slope > 0 else 'decreasing',
            'significance': p_value < 0.05
        }

    def _calculate_power_efficiency(self, df: pd.DataFrame) -> Dict:
        """Calculate power efficiency metrics."""
        efficiency = (df['utilization'] / df['power_draw']).mean()
        return {
            'avg_efficiency': efficiency,
            'peak_efficiency': (df['utilization'] / df['power_draw']).max()
        }

    def _calculate_memory_efficiency(self, df: pd.DataFrame) -> Dict:
        """Calculate memory efficiency metrics."""
        memory_util = (df['memory_used'] / df['memory_total']).mean() * 100
        return {
            'avg_memory_utilization': memory_util,
            'peak_memory_utilization': (df['memory_used'] / df['memory_total']).max() * 100
        }

# Create singleton instance
analytics_service = AnalyticsService()
