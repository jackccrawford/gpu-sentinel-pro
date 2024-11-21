#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PID_FILE="$DIR/service.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null; then
        echo "Stopping GPU Metrics Service (PID: $PID)"
        kill $PID
        rm "$PID_FILE"
    else
        echo "Service not running (stale PID file)"
        rm "$PID_FILE"
    fi
else
    echo "No PID file found"
fi
