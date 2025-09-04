#!/bin/bash
set -e

echo "Waiting for DB to be ready..."
while ! pg_isready -h db -p 5432; do
  sleep 1
done

echo "Running Alembic migrations..."
alembic upgrade head

echo "Seeding some data"
python -m src.seed_data

echo "Starting FastAPI..."
uvicorn src.main:app --host 0.0.0.0 --port 8000
