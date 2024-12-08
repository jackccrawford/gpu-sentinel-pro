#!/bin/bash

# Directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
FRONTEND_PORT=3055
FRONTEND_LOG="frontend.log"
PID_FILE="frontend.pid"

cd $DIR

# Check if port is in use
if [[ $(lsof -i :${FRONTEND_PORT} | grep LISTEN) ]]; then
    echo "Port ${FRONTEND_PORT} is in use. Current processes:"
    lsof -i :${FRONTEND_PORT}
    read -p "Kill these processes? (y/N) " response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        kill $(lsof -t -i :${FRONTEND_PORT})
        sleep 2
    else
        echo "Startup aborted"
        exit 1
    fi
fi

# Start the frontend service
nohup npm run dev > "${FRONTEND_LOG}" 2>&1 &
FRONTEND_PID=$!

# Store the PID
echo $FRONTEND_PID > "${PID_FILE}"
echo "Frontend started with PID ${FRONTEND_PID}"
echo "Logs available at $DIR/${FRONTEND_LOG}"
