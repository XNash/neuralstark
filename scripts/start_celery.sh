#!/bin/bash
# Start Celery worker for document processing

cd /app
export PYTHONPATH=/app:$PYTHONPATH

# Kill any existing celery workers
pkill -f "celery.*worker" 2>/dev/null

# Start celery worker in background with optimized settings
celery -A backend.celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    --max-tasks-per-child=50 \
    --logfile=/var/log/celery_worker.log \
    --pidfile=/tmp/celery_worker.pid \
    --detach

echo "Celery worker started"
