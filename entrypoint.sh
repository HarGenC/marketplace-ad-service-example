#!/bin/sh
set -e

echo "Running migrations..."
alembic upgrade head

echo "Starting app..."
python -m bin.outbox &

echo "Starting API..."
exec uvicorn bin.api:app --host 0.0.0.0 --port 8000