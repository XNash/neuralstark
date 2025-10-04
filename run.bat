@echo off
REM NeuralStark Application Startup Script for Windows
REM This script starts all required services for the NeuralStark application

echo ==========================================
echo   NeuralStark - Starting All Services
echo ==========================================

REM Get the script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo.
echo Checking prerequisites...

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)
echo [OK] Python found

REM Check for Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed or not in PATH
    pause
    exit /b 1
)
echo [OK] Node.js found

REM Check for MongoDB
where mongod >nul 2>&1
if errorlevel 1 (
    echo Warning: MongoDB not found in PATH
    echo Please ensure MongoDB is installed and running
) else (
    echo [OK] MongoDB found
)

REM Check for Redis
where redis-server >nul 2>&1
if errorlevel 1 (
    echo Warning: Redis not found in PATH
    echo Please install Redis from: https://github.com/microsoftarchive/redis/releases
    echo Or use Redis on WSL/Docker
) else (
    echo [OK] Redis found
)

echo.
echo ==========================================
echo   Starting Services...
echo ==========================================

REM Set Python path
set PYTHONPATH=%SCRIPT_DIR%;%PYTHONPATH%

REM Start Redis (if available)
echo.
echo Starting Redis...
start /B redis-server 2>nul
if errorlevel 1 (
    echo Warning: Redis may not be installed. The application requires Redis to function properly.
    echo Please install Redis or run it separately.
) else (
    timeout /t 2 /nobreak >nul
    echo [OK] Redis started
)

REM Start MongoDB (if available)
echo.
echo Starting MongoDB...
start /B mongod --bind_ip_all 2>nul
if errorlevel 1 (
    echo Warning: MongoDB may not be installed or already running.
) else (
    timeout /t 2 /nobreak >nul
    echo [OK] MongoDB started
)

REM Start Celery Worker
echo.
echo Starting Celery worker...
cd "%SCRIPT_DIR%"
start "Celery Worker" cmd /k "celery -A backend.celery_app worker --loglevel=info --concurrency=2 --max-tasks-per-child=50 --pool=solo"
timeout /t 3 /nobreak >nul
echo [OK] Celery worker started in new window

REM Start Backend (FastAPI)
echo.
echo Starting Backend (FastAPI)...
cd "%SCRIPT_DIR%\backend"
start "Backend - FastAPI" cmd /k "uvicorn server:app --host 0.0.0.0 --port 8001 --reload"
timeout /t 3 /nobreak >nul
echo [OK] Backend started on port 8001 in new window

REM Start Frontend (React + Vite)
echo.
echo Starting Frontend (React)...
cd "%SCRIPT_DIR%\frontend"

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call yarn install
    if errorlevel 1 (
        echo Error: Failed to install frontend dependencies
        pause
        exit /b 1
    )
)

start "Frontend - React" cmd /k "yarn start"
timeout /t 5 /nobreak >nul
echo [OK] Frontend started on port 3000 in new window

REM Summary
echo.
echo ==========================================
echo   All Services Started Successfully!
echo ==========================================
echo.
echo Service Status:
echo   - Redis:      Running on port 6379
echo   - MongoDB:    Running on port 27017
echo   - Celery:     Running (2 workers) - Check Celery window
echo   - Backend:    http://localhost:8001 - Check Backend window
echo   - Frontend:   http://localhost:3000 - Check Frontend window
echo.
echo The services are running in separate command windows.
echo Close those windows to stop the services.
echo.
echo Application is ready to use!
echo Open http://localhost:3000 in your browser.
echo.
echo ==========================================
echo.
pause
