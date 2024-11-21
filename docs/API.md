# GPU Sentinel Pro API Documentation

## API Overview
Base URL: `http://localhost:5500`

The GPU Sentinel Pro API provides real-time and historical GPU metrics through a RESTful interface.

## Endpoints

### Service Status
```http
GET /
```
Returns service information and status.

**Response Example:**
```json
{
    "name": "GPU Metrics Service",
    "version": "1.0.0",
    "status": "running",
    "endpoints": {
        "GET /api/gpu-stats": "Current GPU metrics",
        "GET /api/gpu-stats/history": "Historical GPU metrics",
        "GET /api/alerts": "Recent alerts"
    }
}
```

### Current GPU Statistics
```http
GET /api/gpu-stats
```
Returns real-time GPU metrics for all detected NVIDIA GPUs.

**Response Example:**
```json
{
    "nvidia_info": {
        "driver_version": "535.183.01",
        "cuda_version": "12.2"
    },
    "gpus": [
        {
            "index": 0,
            "name": "NVIDIA GeForce RTX 3080",
            "fan_speed": 45,
            "power_draw": 125.5,
            "power_limit": 250,
            "memory_total": 10240,
            "memory_used": 3584,
            "gpu_utilization": 85,
            "temperature": 72,
            "peak_temperature": 75,
            "temp_change_rate": 0.5,
            "compute_mode": "Default"
        }
    ],
    "processes": [],
    "gpu_burn_metrics": {
        "running": false,
        "duration": 0,
        "errors": 0
    },
    "success": true,
    "timestamp": "2024-02-20T15:30:00Z"
}
```

### Historical GPU Metrics
```http
GET /api/gpu-stats/history
```
Retrieves historical GPU metrics within a specified time range.

**Query Parameters:**
- `start_time` (optional): ISO format timestamp (e.g., "2024-02-20T00:00:00Z")
- `end_time` (optional): ISO format timestamp (e.g., "2024-02-20T23:59:59Z")
- `hours` (optional): Number of hours to look back (1-168, default: 24)

**Response Example:**
```json
[
    {
        "timestamp": "2024-02-20T15:00:00Z",
        "gpu_metrics": {
            // Same structure as current GPU stats
        }
    }
]
```

### Alert History
```http
GET /api/alerts
```
Retrieves recent system alerts.

**Query Parameters:**
- `hours` (optional): Number of hours of alert history to retrieve (default: 24)

**Response Example:**
```json
[
    {
        "id": "alert-123",
        "timestamp": "2024-02-20T15:25:00Z",
        "severity": "warning",
        "message": "GPU temperature exceeded 80°C",
        "gpu_index": 0,
        "metric": "temperature",
        "value": 82,
        "threshold": 80
    }
]
```

## Error Responses

### Validation Error
```json
{
    "detail": [
        {
            "loc": ["query", "hours"],
            "msg": "ensure this value is less than or equal to 168",
            "type": "value_error.number.not_le"
        }
    ]
}
```

## Rate Limiting
- Default: 100 requests per minute per IP
- Historical data endpoints: 30 requests per minute per IP

## Authentication
Currently using direct access. Token-based authentication planned for future releases.

## Best Practices
1. Use appropriate polling intervals (recommended: ≥250ms)
2. Include error handling for all API calls
3. Implement exponential backoff for retries
4. Cache responses when appropriate
5. Use historical endpoints for trend analysis
6. Monitor rate limits in production environments

## Future Endpoints (Planned)
- POST /api/alerts/config - Configure alert thresholds
- POST /api/logging/control - Control logging behavior
- GET /api/metrics/analysis - Get performance analysis
- POST /api/gpu/tasks - Manage GPU tasks

## Support
For API issues or feature requests, please use our [GitHub Issues](https://github.com/jackccrawford/gpu-sentinel-pro/issues) page.