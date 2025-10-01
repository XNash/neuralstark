#!/bin/bash

# Define the virtual environment directory
VENV_DIR="neuralstark/venv"

# Check if the virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating and installing dependencies..."
    # Create the virtual environment
    python -m venv $VENV_DIR
    
    # Activate and install dependencies
    source $VENV_DIR/bin/activate
    pip install -r neuralstark/requirements.txt
else
    # Activate the existing virtual environment
    source $VENV_DIR/bin/activate
fi

echo "Starting all services..."

# Start FastAPI server in the background
echo "Starting FastAPI server on port 8000..."
uvicorn neuralstark.main:app --reload --host 0.0.0.0 --port 8000 &
UVICORN_PID=$!

# Start Celery worker with eventlet pool in the background
echo "Starting Celery worker..."
celery -A neuralstark.celery_app worker -l info &
CELERY_WORKER_PID=$!

# Start Celery beat scheduler in the background
echo "Starting Celery beat..."
celery -A neuralstark.celery_app beat -l info &
CELERY_BEAT_PID=$!

echo "All services started."
echo "FastAPI running with PID: $UVICORN_PID"
echo "Celery Worker running with PID: $CELERY_WORKER_PID"
echo "Celery Beat running with PID: $CELERY_BEAT_PID"
echo "Press Ctrl+C to stop all services."

# Function to clean up background processes on exit
cleanup() {
    echo "Stopping all services..."
    kill $UVICORN_PID
    kill $CELERY_WORKER_PID
    kill $CELERY_BEAT_PID
    exit 0
}

# Trap Ctrl+C and call the cleanup function
trap cleanup SIGINT

# Wait for all background processes to complete (which they won't, until cleanup)
wait