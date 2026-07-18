#!/usr/bin/env bash
set -euo pipefail

echo "Running database migrations..."
alembic upgrade head || echo "WARNING: migrations failed or database unavailable"

WORKERS="${WEB_CONCURRENCY:-2}"
PORT="${PORT:-8000}"

echo "Starting Gunicorn on port ${PORT} with ${WORKERS} workers..."
exec gunicorn app.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers "${WORKERS}" \
    --bind "0.0.0.0:${PORT}" \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
