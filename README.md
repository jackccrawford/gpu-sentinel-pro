# GPU Metrics Dashboard

Real-time NVIDIA GPU monitoring dashboard with FastAPI backend and React frontend, featuring time-series data storage using Supabase.

## Service Management

### Backend Service
- Start: `backend/src/service/run_service.sh`
- Stop: `backend/src/service/stop_service.sh`
- Default Port: 5500
- Logs: `backend/src/service/gpu_service.log`
- Endpoints:
  - GPU Stats: http://localhost:5500/api/gpu-stats
  - Alerts: http://localhost:5500/api/alerts
  - Historical Data: http://localhost:5500/api/gpu-stats/history
  - API Docs: http://localhost:5500/docs

Example startup output:
```
Backend log:
INFO:__main__:Starting GPU Metrics Service
INFO:     Uvicorn running on http://127.0.0.1:5500
INFO:     Application startup complete.
```

### Frontend Service
- Start: `frontend/run_frontend.sh`
- Stop: `frontend/stop_frontend.sh`
- Default Port: 3055
- Logs: `frontend/frontend.log`
- URL: http://localhost:3055

Example startup output:
```
Frontend log:
> gpu-metrics-dashboard@1.0.0 dev
> vite

VITE v4.5.5  ready in 219 ms
➜  Local:   http://localhost:3055/
➜  Network: http://192.168.0.11:3055/
```

## Service Health Checks

### Check Backend Status
```bash
curl http://localhost:5500/api/gpu-stats
```

### Check Frontend Status
Frontend health can be verified by accessing http://localhost:3055 in a web browser.

## Logs

- Backend logs are stored in `backend/src/service/gpu_service.log`
- Frontend logs are stored in `frontend/frontend.log`
- Use `tail -f <logfile>` to follow log updates in real-time

## Configuration

### Backend Configuration
- Main config: `backend/src/service/config.yaml`
- Environment variables: `backend/.env`

### Frontend Configuration
- Port configuration: `frontend/vite.config.ts`
- API endpoint configuration: `frontend/src/config.ts`

## Data Persistence Layer

The system uses Supabase for time-series data storage, allowing for:
- Historical data analysis
- Performance trending
- Long-term GPU health monitoring
- Data-driven insights

### Data Structure

The system captures GPU metrics in a denormalized format:

```json
{
  "timestamp": "2023-11-20T10:00:00Z",
  "gpu_burn_metrics": {
    "duration": 0,
    "errors": 0,
    "running": false
  },
  "gpus": [
    {
      "compute_mode": "Default",
      "fan_speed": 27,
      "gpu_utilization": 10,
      "index": 0,
      "memory_total": 12288,
      "memory_used": 135,
      "name": "NVIDIA TITAN Xp",
      "peak_temperature": 48,
      "power_draw": 67.17,
      "power_limit": 250,
      "temp_change_rate": 0,
      "temperature": 48
    }
  ],
  "nvidia_info": {
    "cuda_version": "12.2",
    "driver_version": "535.183.01"
  }
}
```

### Supabase Setup

1. Create a `.env` file from the template:
```bash
cp .env.template .env
```

2. Add your Supabase credentials to `.env`:
```
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_anon_key
```

3. Run the database migrations:
```sql
# Execute the SQL in migrations/001_create_gpu_metrics_table.sql in your Supabase SQL editor
```

### Security

- Uses Supabase Row Level Security (RLS)
- Credentials stored in environment variables
- Data validation before storage
- Error handling and logging

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - See LICENSE file
