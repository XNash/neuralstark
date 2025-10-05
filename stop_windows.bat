@echo off
setlocal enabledelayedexpansion

REM ##########################################
REM NeuralStark - Complete Stop Script
REM Version: 6.0 - Windows
REM ##########################################

echo ==========================================
echo   NeuralStark - Stopping All Services
echo ==========================================
echo.

set STOPPED=0
set FAILED=0

REM ##########################################
REM Stop Celery Worker
REM ##########################################
echo [INFO] Stopping Celery worker...
taskkill /F /IM celery.exe >nul 2>&1
if errorlevel 1 (
    echo [WARN] No Celery process found
) else (
    echo [OK] Celery worker stopped
    set /a STOPPED+=1
)

REM Also try to close Celery window
taskkill /F /FI "WINDOWTITLE eq Celery Worker*" >nul 2>&1

echo.

REM ##########################################
REM Stop Backend
REM ##########################################
echo [INFO] Stopping Backend...

REM Stop by window title
taskkill /F /FI "WINDOWTITLE eq Backend*" >nul 2>&1
if errorlevel 1 (
    echo [WARN] No Backend window found
) else (
    echo [OK] Backend window closed
    set /a STOPPED+=1
)

REM Also stop uvicorn processes
taskkill /F /IM uvicorn.exe >nul 2>&1

REM Check if port 8001 is now free
timeout /t 1 /nobreak >nul
netstat -ano | findstr ":8001" >nul 2>&1
if errorlevel 1 (
    echo [OK] Port 8001 is now free
) else (
    echo [WARN] Port 8001 still in use
    set /a FAILED+=1
)

echo.

REM ##########################################
REM Stop Frontend
REM ##########################################
echo [INFO] Stopping Frontend...

REM Stop by window title
taskkill /F /FI "WINDOWTITLE eq Frontend*" >nul 2>&1
if errorlevel 1 (
    echo [WARN] No Frontend window found
) else (
    echo [OK] Frontend window closed
    set /a STOPPED+=1
)

REM Check if port 3000 is now free
timeout /t 1 /nobreak >nul
netstat -ano | findstr ":3000" >nul 2>&1
if errorlevel 1 (
    echo [OK] Port 3000 is now free
) else (
    echo [WARN] Port 3000 still in use
    
    echo [INFO] Attempting to forcefully stop Node.js processes...
    taskkill /F /IM node.exe >nul 2>&1
    if not errorlevel 1 (
        echo [OK] Node.js processes stopped
        set /a STOPPED+=1
    )
)

echo.

REM ##########################################
REM Optional: Stop Redis
REM ##########################################
echo [INFO] Redis Status (not stopped by default^)
netstat -ano | findstr ":6379" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Redis is not running
) else (
    echo [INFO] Redis is still running on port 6379
    echo [INFO] To stop Redis manually: taskkill /F /IM redis-server.exe
)

echo.

REM ##########################################
REM Optional: Stop MongoDB
REM ##########################################
echo [INFO] MongoDB Status (not stopped by default^)
netstat -ano | findstr ":27017" >nul 2>&1
if errorlevel 1 (
    echo [INFO] MongoDB is not running
) else (
    echo [INFO] MongoDB is still running on port 27017
    echo [INFO] To stop MongoDB manually: taskkill /F /IM mongod.exe
)

echo.

REM ##########################################
REM Summary
REM ##########################################
echo ==========================================
echo   Shutdown Summary
echo ==========================================
echo.

if !FAILED! EQU 0 (
    echo [OK] All application services stopped successfully
    echo      Services stopped: !STOPPED!
    echo.
    echo [INFO] Background services (Redis, MongoDB^) left running
    echo [INFO] This is normal - they can be shared across applications
) else (
    echo [WARN] Some services may still be running
    echo       Services stopped: !STOPPED!
    echo       Issues encountered: !FAILED!
    echo.
    echo [INFO] Check Task Manager for remaining processes:
    echo        - python.exe
    echo        - node.exe
    echo        - celery.exe
    echo        - uvicorn.exe
)

echo ==========================================
echo.

REM Keep window open briefly
timeout /t 3 /nobreak >nul

exit /b 0
