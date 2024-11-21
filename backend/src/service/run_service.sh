#!/bin/bash

# Directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment
source $DIR/../../venv/bin/activate

# Start the service in background with nohup
nohup python $DIR/app.py > $DIR/gpu_service.log 2>&1 &

# Save the PID to a file
echo $! > $DIR/service.pid

echo "GPU Metrics Service started with PID $(cat $DIR/service.pid)"
echo "Logs available at $DIR/gpu_service.log"
