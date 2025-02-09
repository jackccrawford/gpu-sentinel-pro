# GPU Sentinel Pro

> "Information should not be displayed all at once; let people gradually become familiar with it." - Edward Tufte

Transform GPU monitoring from complex metrics into intuitive visual patterns. Enterprise-grade NVIDIA GPU monitoring with real-time analytics, intelligent alerts, and historical analysis.

[![CodeQL](https://github.com/jackccrawford/gpu-sentinel-pro/actions/workflows/codeql.yml/badge.svg)](https://github.com/jackccrawford/gpu-sentinel-pro/actions/workflows/codeql.yml)
[![X Follow](https://img.shields.io/badge/style--blue?style=social&logo=x&label=Follow%20%40jackccrawford)](https://x.com/intent/follow?screen_name=jackccrawford)
![License](https://img.shields.io/github/license/Exafunction/codeium.vim)
[![Built with Codeium](https://codeium.com/badges/main)](https://codeium.com)

![Dark Mode Dashboard](images/DarkMode-Stressed.png)
*Real-time GPU metrics visualized for instant comprehension*

## Project Overview
- [Requirements & User Stories](docs/requirements/REQUIREMENTS.md)
- [Technical Architecture](docs/architecture/ARCHITECTURE.md)
- [Development Guide](docs/requirements/DEVELOPMENT_GUIDE.md)
- [API Documentation](docs/API.md)

## Why GPU Sentinel Pro?

Do you find yourself:
- Parsing dense terminal output when you should be focusing on your work?
- Missing critical temperature spikes or memory leaks?
- Lacking historical data for performance analysis?
- Needing better alerting for GPU health?
- Managing multiple GPUs across different workloads?

## Features

### 🎯 Intuitive Monitoring
- Real-time visual dashboard with modern UI components
- Color-coded temperature and utilization ranges
- Resource utilization patterns and trends
- Multi-GPU support with individual monitoring
- Dark/light mode with Material Design
- System health diagnostics and troubleshooting

### 🔔 Intelligent Alerts
- Fully configurable alert thresholds
- Multi-level severity system (warning/critical)
- Temperature and resource spike detection
- Custom alert rules and durations
- Alert history and acknowledgment workflow
- Email/webhook notifications with customizable templates

### 📊 Advanced Analytics
- Comprehensive historical performance data
- Advanced time-series analysis with anomaly detection
- Usage pattern recognition and trend analysis
- Power efficiency metrics and cost analysis
- Resource utilization heatmaps
- Performance prediction and optimization suggestions

### 🛠 Enterprise Integration
- RESTful API with full documentation
- Supabase time-series storage with retention policies
- Zero-config deployment with health monitoring
- Multi-user access control
- Data export and backup capabilities
- Configurable logging and diagnostics

## Visual Intelligence

### Traditional Output vs. GPU Sentinel Pro
![Traditional vs Modern](images/nvidia-smi.png)
*Transform dense metrics into intuitive patterns*

### Real-world Usage

#### Machine Learning Workloads
![ML Monitoring](images/Ollama-Mistral-Small.png)
*Clear resource utilization during ML model training*

#### Critical Temperature Monitoring
![Temperature Alerts](images/gpu-burn-danger-zone.png)
*Immediate visual alerts during intensive workloads*

## Temperature Monitoring

Intuitive color-coding for instant recognition:
- 🔴 ≥85°C: Critical
- 🟠 75-84°C: Warning
- 🟡 65-74°C: Normal
- 🟢 50-64°C: Optimal
- 🔵 <50°C: Cool

## System Requirements

### Hardware Requirements
- NVIDIA GPU with compute capability 3.0 or higher
- 4GB RAM minimum (8GB recommended)
- 1GB free disk space

### Software Requirements
- NVIDIA Driver 450.80.02 or higher
- CUDA 11.0 or higher (optional, for advanced features)
- Python 3.8 or higher
- Node.js 16.0 or higher

## Installation

```bash
# Clone repository
git clone https://github.com/jackccrawford/gpu-sentinel-pro.git
cd gpu-sentinel-pro

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install

# Start services
cd ../backend/src/service
./run_service.sh

cd ../../../frontend
npm run dev

# Access dashboard
http://localhost:3055
```

For detailed setup instructions and configuration options, see our [Installation Guide](docs/INSTALLATION.md).

## Quick Start

```bash
# Clone repository
git clone https://github.com/jackccrawford/gpu-sentinel-pro.git

# Start services
./backend/src/service/run_service.sh
./frontend/run_frontend.sh

# Access dashboard
http://localhost:3055
```

See [Installation Guide](docs/INSTALLATION.md) for detailed setup instructions.

## Documentation

- [Requirements & User Stories](docs/requirements/REQUIREMENTS.md)
- [Technical Architecture](docs/architecture/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Installation Guide](docs/INSTALLATION.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)

## Tech Stack

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-181818?style=for-the-badge&logo=supabase&logoColor=white)

## License

[MIT License](LICENSE) - Free for personal and commercial use.

---

<p align="center">Built for Orphaned NVIDIAs</p>
