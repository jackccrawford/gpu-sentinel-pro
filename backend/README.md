# GPU Metrics Service Backend

A FastAPI service that monitors NVIDIA GPUs and provides metrics via REST API.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the service:
```bash
python src/service/app.py
```

## API Endpoints

- `GET /api/gpu-stats` - Current GPU metrics
- `GET /api/gpu-stats/history` - Historical metrics
- `GET /api/alerts` - Recent alerts

## Configuration

Edit `src/service/config.yaml` to customize:
- Alert thresholds
- Polling intervals
- Data retention
