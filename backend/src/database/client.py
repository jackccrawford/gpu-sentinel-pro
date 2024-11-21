import psycopg2
from psycopg2.extras import Json
from datetime import datetime
from ..models.gpu_metrics import GpuMetricsRecord

class DatabaseClient:
    def __init__(self):
        self.conn_params = {
            'dbname': 'postgres',
            'user': 'postgres',
            'password': 'postgres',
            'host': 'localhost',
            'port': 54432
        }

    def get_connection(self):
        return psycopg2.connect(**self.conn_params)

    def insert_gpu_metrics(self, metrics: GpuMetricsRecord) -> dict:
        """
        Insert GPU metrics into PostgreSQL
        Returns the inserted record
        """
        if not metrics.timestamp:
            metrics.timestamp = datetime.utcnow().isoformat()

        data = metrics.model_dump()
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO gpu_metrics (
                        timestamp,
                        duration,
                        errors,
                        running,
                        cuda_version,
                        driver_version,
                        gpus,
                        processes,
                        success,
                        created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                    ) RETURNING id
                """, (
                    data['timestamp'],
                    data['gpu_burn_metrics']['duration'],
                    data['gpu_burn_metrics']['errors'],
                    data['gpu_burn_metrics']['running'],
                    data['nvidia_info']['cuda_version'],
                    data['nvidia_info']['driver_version'],
                    Json(data['gpus']),
                    Json(data['processes']),
                    data['success']
                ))
                record_id = cur.fetchone()[0]
                return {"id": record_id}

    def get_metrics_in_timerange(self, start_time: str, end_time: str):
        """
        Retrieve metrics within a specific time range
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT *
                    FROM gpu_metrics
                    WHERE timestamp >= %s AND timestamp <= %s
                    ORDER BY timestamp DESC
                """, (start_time, end_time))
                
                columns = [desc[0] for desc in cur.description]
                results = []
                
                for row in cur.fetchall():
                    result = dict(zip(columns, row))
                    results.append(result)
                
                return results

# Create a singleton instance
db = DatabaseClient()
