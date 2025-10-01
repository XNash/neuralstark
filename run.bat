@echo off

:: Define the virtual environment directory
set VENV_DIR=neuralstark\venv

:: Check if the virtual environment exists
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Virtual environment not found. Creating and installing dependencies...
    python -m venv %VENV_DIR%
    call %VENV_DIR%\Scripts\activate.bat
    pip install -r neuralstark\requirements.txt
) else (
    call %VENV_DIR%\Scripts\activate.bat
)

echo Starting all services...

:: Start FastAPI, Celery Worker, and Celery Beat in separate windows
echo Starting FastAPI server on port 8000...
start "NeuralStark FastAPI" cmd /k "uvicorn neuralstark.main:app --reload --host 0.0.0.0 --port 8000"

start "Celery Worker" cmd /k "celery -A neuralstark.celery_app worker -l info -P solo"

:: Start Celery beat
echo "Starting Celery beat..."
start "Celery Beat" cmd /k "celery -A neuralstark.celery_app beat -l info"

echo All services have been launched in separate windows.