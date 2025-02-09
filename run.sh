#!/bin/bash

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "Port $1 is already in use"
        return 1
    fi
    return 0
}

# Function to kill process on port
kill_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "Killing process on port $1..."
        lsof -ti:$1 | xargs kill -9
    fi
}

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install backend requirements
echo "Installing backend requirements..."
pip install -r requirements.txt

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend && npm install && cd ..
fi

# Kill any existing processes on our ports
kill_port 8000  # FastAPI
kill_port 5173  # Vite dev server

# Start all components in background
echo "Starting GPU stats collector..."
python -m src.collector.collector &

echo "Starting FastAPI server..."
cd backend && python -m src.service.app &

echo "Starting frontend dev server..."
cd frontend && npm run dev &

# Wait for servers to start
sleep 3

echo "
🚀 GPU Sentinel Pro is running!

📊 Frontend: http://localhost:5173
🔧 API Docs: http://localhost:8000/docs
📘 ReDoc: http://localhost:8000/redoc

Press Ctrl+C to stop all services
"

# Wait for Ctrl+C
trap 'kill $(jobs -p)' INT
wait