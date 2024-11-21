# GPU Sentinel Pro Installation Guide

## Prerequisites

### System Requirements
- NVIDIA GPU(s)
- NVIDIA drivers installed and functional
- `nvidia-smi` command available
- Docker and Docker Compose (for database)
- Python 3.10 or higher
- Node.js 18 or higher

### NVIDIA Driver Verification
```bash
nvidia-smi
```
Should display your GPU information. If not, install NVIDIA drivers first.

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/jackccrawford/gpu-sentinel-pro.git
cd gpu-sentinel-pro
```

### 2. Database Setup (Supabase)
```bash
cd supabase
docker-compose up -d
```
Verify Supabase is running:
- Database: http://localhost:54432
- API: http://localhost:54321

### 3. Backend Setup
```bash
# Create and activate virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the service
cd src/service
./run_service.sh
```
Verify backend is running:
- API: http://localhost:5500
- Documentation: http://localhost:5500/docs

### 4. Frontend Setup
```bash
cd frontend
npm install
./run_frontend.sh
```
Access the dashboard at http://localhost:3055

## Configuration

### Environment Variables
Create `.env` file in backend directory:
```env
SUPABASE_URL=http://localhost:54321
SUPABASE_KEY=your_supabase_key
```

### Database Migrations
```bash
cd backend/migrations
# Run migrations in order
psql -h localhost -p 54432 -U postgres -d postgres -f 001_create_gpu_metrics_table.sql
psql -h localhost -p 54432 -U postgres -d postgres -f 002_create_alerts_table.sql
```

### Alert Configuration
Edit `backend/src/service/config.yaml`:
```yaml
alerts:
  temperature:
    critical: 80
    warning: 70
    caution: 60
```

## Service Management

### Backend Service
- Start: `backend/src/service/run_service.sh`
- Stop: `backend/src/service/stop_service.sh`
- Logs: `backend/src/service/gpu_service.log`

### Frontend Service
- Start: `frontend/run_frontend.sh`
- Stop: `frontend/stop_frontend.sh`
- Logs: `frontend/frontend.log`

## Troubleshooting

### Common Issues

#### NVIDIA Driver Not Found
```bash
# Check driver installation
nvidia-smi

# If not found, install drivers
sudo ubuntu-drivers autoinstall  # Ubuntu
# or
sudo dnf install nvidia-driver   # Fedora
```

#### Database Connection Issues
```bash
# Check Supabase containers
docker ps | grep supabase

# Check logs
docker logs supabase-db-1

# Reset database
cd supabase
docker-compose down -v
docker-compose up -d
```

#### Service Won't Start
1. Check logs in respective log files
2. Verify ports are not in use:
   ```bash
   netstat -tulpn | grep -E '5500|3055|54321|54432'
   ```
3. Ensure all dependencies are installed
4. Verify Python/Node.js versions

## Security Considerations

### Production Deployment
1. Use proper SSL/TLS certificates
2. Configure proper authentication
3. Set up proper firewall rules
4. Use secure database passwords
5. Enable rate limiting

### Access Control
- Configure CORS settings in backend/src/service/app.py
- Set up proper database user permissions
- Use environment variables for sensitive data

## Updating

### Backend Updates
```bash
git pull
cd backend
source venv/bin/activate
pip install -r requirements.txt
./src/service/run_service.sh
```

### Frontend Updates
```bash
git pull
cd frontend
npm install
./run_frontend.sh
```

## Support
- GitHub Issues: [Report bugs](https://github.com/jackccrawford/gpu-sentinel-pro/issues)
- Documentation: [Full documentation](https://github.com/jackccrawford/gpu-sentinel-pro/docs)