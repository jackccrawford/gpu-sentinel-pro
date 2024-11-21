# GPU Metrics Dashboard Frontend

React-based dashboard for monitoring NVIDIA GPUs.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The dashboard will be available at http://localhost:5501

## Configuration

The dashboard connects to the backend service at http://localhost:5500 by default.
To change this, edit the API_URL in src/config.ts.

## Features

- Real-time GPU metrics display
- Temperature, utilization, and memory monitoring
- Historical data viewing
- Alert notifications
