#!/bin/bash

# Directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Start the frontend in background, ensuring proper detachment
cd $DIR
setsid nohup npm run dev > frontend.log 2>&1 < /dev/null &

# Save the PID to a file
echo $! > frontend.pid

echo "Frontend started with PID $(cat frontend.pid)"
echo "Logs available at $DIR/frontend.log"
