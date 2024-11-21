#!/bin/bash

echo "Stopping Supabase services..."

# Stop all containers
docker-compose down

echo "Supabase services stopped."

# Optional cleanup flag
if [ "$1" == "--clean" ]; then
    echo "Cleaning up volumes..."
    docker-compose down -v
    rm -f .env.supabase docker-compose.yml.bak
    echo "Cleanup complete. All data has been removed."
fi