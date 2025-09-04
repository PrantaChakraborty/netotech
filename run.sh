#!/bin/bash
set -e

# Build and start containers
docker compose build
docker compose up -d

# Wait for API to become ready
echo "Waiting for FastAPI to be available on http://localhost:8000 ..."
until curl -s http://localhost:8000/docs > /dev/null; do
  sleep 1
done

echo "FastAPI is up and running at http://localhost:8000"
