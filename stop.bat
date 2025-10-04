@echo off
REM NeuralStark Application Stop Script for Windows
REM This script stops all services for the NeuralStark application

echo ==========================================
echo   NeuralStark - Stopping All Services
echo ==========================================

echo.
echo Stopping Celery worker...
taskkill /F /IM celery.exe 2>nul
if errorlevel 1 (
    echo No Celery process found
) else (
    echo [OK] Celery worker stopped
)

echo.
echo Stopping Backend...
taskkill /F /FI "WINDOWTITLE eq Backend - FastAPI*" 2>nul
if errorlevel 1 (
    echo No Backend window found
) else (
    echo [OK] Backend stopped
)

echo.
echo Stopping Frontend...
taskkill /F /FI "WINDOWTITLE eq Frontend - React*" 2>nul
if errorlevel 1 (
    echo No Frontend window found
) else (
    echo [OK] Frontend stopped
)

echo.
echo Stopping any remaining Node.js processes related to the app...
taskkill /F /IM node.exe 2>nul
if not errorlevel 1 (
    echo [OK] Node processes stopped
)

REM Optionally stop Redis (uncomment if needed)
REM echo.
REM echo Stopping Redis...
REM taskkill /F /IM redis-server.exe 2>nul

REM Optionally stop MongoDB (uncomment if needed)
REM echo.
REM echo Stopping MongoDB...
REM taskkill /F /IM mongod.exe 2>nul

echo.
echo ==========================================
echo   All Services Stopped
echo ==========================================
echo.
pause
