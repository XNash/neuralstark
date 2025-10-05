@echo off
setlocal enabledelayedexpansion

REM ##########################################
REM NeuralStark - Complete All-in-One Script
REM Version: 6.0 - Setup + Install + Run (Windows)
REM Everything you need in one command!
REM ##########################################

echo ==========================================
echo   NeuralStark Complete Setup and Start
echo   Version 6.0 - All-in-One Solution
echo ==========================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

set ERRORS=0
set WARNINGS=0

REM Create logs directory if not exists
if not exist "logs" mkdir logs
set "LOG_DIR=%SCRIPT_DIR%logs"

REM ##########################################
REM PHASE 1: DIRECTORY SETUP
REM ##########################################
echo ============================================
echo Phase 1: Directory Setup
echo ============================================
echo.

echo [INFO] Creating required directories...

REM Create directories
if not exist "backend\knowledge_base\internal" mkdir "backend\knowledge_base\internal"
if not exist "backend\knowledge_base\external" mkdir "backend\knowledge_base\external"
if not exist "chroma_db" mkdir "chroma_db"
if not exist "logs" mkdir "logs"

REM Verify directories
set MISSING_DIRS=
if not exist "backend\knowledge_base\internal" set MISSING_DIRS=!MISSING_DIRS! backend\knowledge_base\internal
if not exist "backend\knowledge_base\external" set MISSING_DIRS=!MISSING_DIRS! backend\knowledge_base\external
if not exist "chroma_db" set MISSING_DIRS=!MISSING_DIRS! chroma_db
if not exist "logs" set MISSING_DIRS=!MISSING_DIRS! logs

if "!MISSING_DIRS!"=="" (
    echo [OK] All required directories created
) else (
    echo [ERROR] Failed to create directories: !MISSING_DIRS!
    set /a ERRORS+=1
)

REM Verify ChromaDB directory is writable
echo test > "chroma_db\test_write.tmp" 2>nul
if exist "chroma_db\test_write.tmp" (
    del "chroma_db\test_write.tmp" 2>nul
    echo [OK] ChromaDB directory is writable
) else (
    echo [WARN] ChromaDB directory may not be writable
    set /a WARNINGS+=1
)

echo.

REM ##########################################
REM PHASE 2: SYSTEM PREREQUISITES
REM ##########################################
echo ============================================
echo Phase 2: System Prerequisites Check
echo ============================================
echo.

REM Check Python
echo [INFO] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+ from https://www.python.org/downloads/
    set /a ERRORS+=1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [OK] Python !PYTHON_VERSION! found
)

REM Check Node.js
echo [INFO] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Please install Node.js 16+ from https://nodejs.org/
    set /a ERRORS+=1
) else (
    for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    echo [OK] Node.js !NODE_VERSION! found
)

echo.

REM ##########################################
REM PHASE 3: VIRTUAL ENVIRONMENT
REM ##########################################
echo ============================================
echo Phase 3: Python Virtual Environment
echo ============================================
echo.

echo [INFO] Setting up Python virtual environment...

REM Check if venv exists
if exist ".venv\Scripts\activate.bat" (
    echo [OK] Virtual environment found (.venv^)
) else (
    echo [INFO] Creating new virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [WARN] Could not create venv, will use system Python
        set /a WARNINGS+=1
        set "PYTHON_BIN=python"
        set "PIP_BIN=pip"
    ) else (
        echo [OK] Virtual environment created
    )
)

REM Activate venv
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo [OK] Virtual environment activated
    set "PYTHON_BIN=.venv\Scripts\python.exe"
    set "PIP_BIN=.venv\Scripts\pip.exe"
) else (
    echo [WARN] Using system Python
    set "PYTHON_BIN=python"
    set "PIP_BIN=pip"
)

echo.

REM ##########################################
REM PHASE 4: PYTHON DEPENDENCIES
REM ##########################################
echo ============================================
echo Phase 4: Python Dependencies
echo ============================================
echo.

cd "%SCRIPT_DIR%backend"

if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found!
    set /a ERRORS+=1
) else (
    echo [INFO] Checking Python dependencies...
    
    REM Check if key packages are installed
    %PYTHON_BIN% -c "import fastapi, chromadb, langchain, celery, redis" 2>nul
    if errorlevel 1 (
        echo [INFO] Installing Python packages (this may take a few minutes^)...
        %PIP_BIN% install --upgrade pip setuptools wheel -q
        %PIP_BIN% install -r requirements.txt
        
        REM Verify installation
        %PYTHON_BIN% -c "import fastapi, chromadb, langchain, celery" 2>nul
        if errorlevel 1 (
            echo [WARN] Some dependencies may be missing
            set /a WARNINGS+=1
        ) else (
            echo [OK] Python dependencies installed successfully
        )
    ) else (
        echo [OK] Key Python packages already installed
    )
)

cd "%SCRIPT_DIR%"

echo.

REM ##########################################
REM PHASE 5: FRONTEND DEPENDENCIES
REM ##########################################
echo ============================================
echo Phase 5: Frontend Dependencies
echo ============================================
echo.

cd "%SCRIPT_DIR%frontend"

if not exist "package.json" (
    echo [ERROR] package.json not found!
    set /a ERRORS+=1
) else (
    REM Check if yarn is available
    where yarn >nul 2>&1
    if errorlevel 1 (
        echo [INFO] Yarn not found, installing...
        npm install -g yarn
    )
    
    REM Check if node_modules exists
    if exist "node_modules\react" (
        echo [OK] Frontend dependencies already installed
    ) else (
        echo [INFO] Installing frontend packages (this may take a few minutes^)...
        where yarn >nul 2>&1
        if errorlevel 1 (
            call npm install
        ) else (
            call yarn install
        )
        
        if exist "node_modules" (
            echo [OK] Frontend dependencies installed
        ) else (
            echo [ERROR] Failed to install frontend dependencies
            set /a ERRORS+=1
        )
    )
)

cd "%SCRIPT_DIR%"

echo.

REM ##########################################
REM PHASE 6: REDIS SERVICE
REM ##########################################
echo ============================================
echo Phase 6: Redis Service
echo ============================================
echo.

echo [INFO] Checking Redis...

REM Check if Redis is running
netstat -ano | findstr ":6379" >nul 2>&1
if errorlevel 1 (
    REM Redis not running, try to start it
    where redis-server >nul 2>&1
    if errorlevel 1 (
        echo [WARN] Redis not installed.
        echo [INFO] Please install Redis from:
        echo        https://github.com/microsoftarchive/redis/releases
        echo        OR run Redis via WSL/Docker
        set /a WARNINGS+=1
    ) else (
        echo [INFO] Starting Redis...
        start /B redis-server --bind 127.0.0.1
        timeout /t 2 /nobreak >nul
        
        netstat -ano | findstr ":6379" >nul 2>&1
        if errorlevel 1 (
            echo [ERROR] Redis failed to start
            set /a ERRORS+=1
        ) else (
            echo [OK] Redis started on port 6379
        )
    )
) else (
    echo [OK] Redis already running on port 6379
)

echo.

REM ##########################################
REM PHASE 7: MONGODB SERVICE
REM ##########################################
echo ============================================
echo Phase 7: MongoDB Service
echo ============================================
echo.

echo [INFO] Checking MongoDB...

REM Check if MongoDB is running
netstat -ano | findstr ":27017" >nul 2>&1
if errorlevel 1 (
    REM MongoDB not running, try to start it
    where mongod >nul 2>&1
    if errorlevel 1 (
        echo [WARN] MongoDB not installed (optional^)
        echo [INFO] Please install MongoDB from:
        echo        https://www.mongodb.com/try/download/community
        set /a WARNINGS+=1
    ) else (
        echo [INFO] Starting MongoDB...
        if not exist "mongodb_data" mkdir "mongodb_data"
        start /B mongod --bind_ip_all --dbpath mongodb_data --logpath "%LOG_DIR%\mongodb.log"
        timeout /t 3 /nobreak >nul
        
        netstat -ano | findstr ":27017" >nul 2>&1
        if errorlevel 1 (
            echo [WARN] MongoDB may not have started (check logs\mongodb.log^)
            set /a WARNINGS+=1
        ) else (
            echo [OK] MongoDB started on port 27017
        )
    )
) else (
    echo [OK] MongoDB already running on port 27017
)

echo.

REM ##########################################
REM PHASE 8: CELERY WORKER
REM ##########################################
echo ============================================
echo Phase 8: Celery Worker
echo ============================================
echo.

echo [INFO] Starting Celery worker...

REM Stop existing workers
taskkill /F /IM celery.exe >nul 2>&1

REM Set Python path
set "PYTHONPATH=%SCRIPT_DIR%;%PYTHONPATH%"

REM Find celery binary
if exist ".venv\Scripts\celery.exe" (
    set "CELERY_BIN=.venv\Scripts\celery.exe"
) else (
    set "CELERY_BIN=celery"
)

REM Check if celery is available
where %CELERY_BIN% >nul 2>&1
if errorlevel 1 (
    %PYTHON_BIN% -c "import celery" 2>nul
    if errorlevel 1 (
        echo [WARN] Celery not found, installing...
        %PIP_BIN% install celery redis
    )
)

REM Start Celery in a new window (pool=solo for Windows compatibility)
start "Celery Worker" /MIN cmd /c "%CELERY_BIN% -A backend.celery_app worker --loglevel=info --concurrency=2 --max-tasks-per-child=50 --pool=solo > "%LOG_DIR%\celery_worker.log" 2>&1"

timeout /t 4 /nobreak >nul

REM Check if Celery is running
tasklist | findstr celery.exe >nul 2>&1
if errorlevel 1 (
    echo [WARN] Celery may not have started (check logs\celery_worker.log^)
    set /a WARNINGS+=1
) else (
    echo [OK] Celery worker started
)

echo.

REM ##########################################
REM PHASE 9: BACKEND (FASTAPI)
REM ##########################################
echo ============================================
echo Phase 9: Backend Service
echo ============================================
echo.

echo [INFO] Starting Backend...

REM Check if backend is already running
netstat -ano | findstr ":8001" >nul 2>&1
if not errorlevel 1 (
    echo [WARN] Port 8001 already in use
    REM Try to check if it's responding
    powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8001/api/health' -TimeoutSec 2 -UseBasicParsing; exit 0 } catch { exit 1 }" >nul 2>&1
    if not errorlevel 1 (
        echo [OK] Backend already running on port 8001
        goto :skip_backend_start
    ) else (
        echo [WARN] Port 8001 occupied, attempting to restart...
        taskkill /F /FI "WINDOWTITLE eq Backend*" >nul 2>&1
        timeout /t 2 /nobreak >nul
    )
)

REM Find uvicorn
if exist ".venv\Scripts\uvicorn.exe" (
    set "UVICORN_BIN=.venv\Scripts\uvicorn.exe"
) else (
    set "UVICORN_BIN=uvicorn"
)

REM Start backend in new window
cd "%SCRIPT_DIR%backend"
start "Backend - FastAPI" /MIN cmd /c "%UVICORN_BIN% server:app --host 0.0.0.0 --port 8001 --reload > "%LOG_DIR%\backend.log" 2>&1"

echo [INFO] Waiting for backend to load (loading ML models, 20-30s^)...

REM Wait up to 40 seconds for backend to be ready
set BACKEND_READY=false
for /L %%i in (1,1,40) do (
    timeout /t 1 /nobreak >nul
    netstat -ano | findstr ":8001" >nul 2>&1
    if not errorlevel 1 (
        powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8001/api/health' -TimeoutSec 2 -UseBasicParsing; exit 0 } catch { exit 1 }" >nul 2>&1
        if not errorlevel 1 (
            echo [OK] Backend started on port 8001
            set BACKEND_READY=true
            goto :backend_ready
        )
    )
)

:backend_ready
if "!BACKEND_READY!"=="false" (
    echo [WARN] Backend may still be loading (check logs\backend.log^)
    set /a WARNINGS+=1
)

:skip_backend_start
cd "%SCRIPT_DIR%"

echo.

REM ##########################################
REM PHASE 10: FRONTEND (REACT + VITE)
REM ##########################################
echo ============================================
echo Phase 10: Frontend Service
echo ============================================
echo.

echo [INFO] Starting Frontend...

REM Check if frontend is already running
netstat -ano | findstr ":3000" >nul 2>&1
if not errorlevel 1 (
    echo [WARN] Port 3000 already in use
    powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:3000' -TimeoutSec 2 -UseBasicParsing; exit 0 } catch { exit 1 }" >nul 2>&1
    if not errorlevel 1 (
        echo [OK] Frontend already running on port 3000
        goto :skip_frontend_start
    ) else (
        echo [WARN] Port 3000 occupied, attempting to restart...
        taskkill /F /FI "WINDOWTITLE eq Frontend*" >nul 2>&1
        timeout /t 2 /nobreak >nul
    )
)

REM Start frontend in new window
cd "%SCRIPT_DIR%frontend"

where yarn >nul 2>&1
if errorlevel 1 (
    start "Frontend - React" /MIN cmd /c "npm start > "%LOG_DIR%\frontend.log" 2>&1"
) else (
    start "Frontend - React" /MIN cmd /c "yarn start > "%LOG_DIR%\frontend.log" 2>&1"
)

echo [INFO] Waiting for frontend to start...

REM Wait up to 15 seconds for frontend to be ready
set FRONTEND_READY=false
for /L %%i in (1,1,15) do (
    timeout /t 1 /nobreak >nul
    netstat -ano | findstr ":3000" >nul 2>&1
    if not errorlevel 1 (
        echo [OK] Frontend started on port 3000
        set FRONTEND_READY=true
        goto :frontend_ready
    )
)

:frontend_ready
if "!FRONTEND_READY!"=="false" (
    echo [WARN] Frontend may not have started (check logs\frontend.log^)
    set /a WARNINGS+=1
)

:skip_frontend_start
cd "%SCRIPT_DIR%"

echo.

REM ##########################################
REM PHASE 11: VALIDATION & HEALTH CHECKS
REM ##########################################
echo ============================================
echo Phase 11: Service Validation
echo ============================================
echo.

echo [INFO] Running health checks...
echo.

REM Redis
netstat -ano | findstr ":6379" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Redis - Not running
    set /a ERRORS+=1
) else (
    echo [OK] Redis - Running on port 6379
)

REM MongoDB
netstat -ano | findstr ":27017" >nul 2>&1
if errorlevel 1 (
    echo [WARN] MongoDB - Not running (optional^)
) else (
    echo [OK] MongoDB - Running on port 27017
)

REM Celery
tasklist | findstr celery.exe >nul 2>&1
if errorlevel 1 (
    echo [WARN] Celery - Not running
    set /a WARNINGS+=1
) else (
    echo [OK] Celery - Running
)

REM Backend
netstat -ano | findstr ":8001" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Backend - Not running
    set /a ERRORS+=1
) else (
    powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8001/api/health' -TimeoutSec 2 -UseBasicParsing; Write-Host '[OK] Backend - Running on port 8001 (healthy)' } catch { Write-Host '[WARN] Backend - Running on port 8001 (still loading)' }" 2>nul
)

REM Frontend
netstat -ano | findstr ":3000" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Frontend - Not running
    set /a ERRORS+=1
) else (
    echo [OK] Frontend - Running on port 3000
)

echo.
echo ==========================================
echo   Startup Summary
echo ==========================================
echo.

if !ERRORS! EQU 0 if !WARNINGS! EQU 0 (
    echo [OK] All services started successfully! 
    echo.
    echo [INFO] Application URLs:
    echo        Frontend:  http://localhost:3000
    echo        Backend:   http://localhost:8001
    echo        API Docs:  http://localhost:8001/docs
    echo.
    echo [INFO] Logs directory: %LOG_DIR%
    echo [INFO] To stop: stop.bat
    echo.
    echo [OK] NeuralStark is ready!
) else if !ERRORS! EQU 0 (
    echo [WARN] !WARNINGS! warning(s^) - Some services may need attention
    echo.
    echo [INFO] Application should be functional, but check:
    echo        Backend:  type logs\backend.log
    echo        Frontend: type logs\frontend.log
    echo        Celery:   type logs\celery_worker.log
    echo.
    echo [INFO] Try accessing: http://localhost:3000
) else (
    echo [ERROR] !ERRORS! critical error(s^) - Some services failed to start
    echo.
    echo [INFO] Check logs for details:
    echo        Backend:  type logs\backend.log
    echo        Frontend: type logs\frontend.log
    echo        Celery:   type logs\celery_worker.log
    echo.
    echo [INFO] Try running again or check the INSTALLATION_GUIDE.md
)

echo ==========================================
echo.

REM Keep window open to see services running
echo Press any key to continue (services will keep running in background^)...
pause >nul

REM Exit with appropriate code
if !ERRORS! GTR 0 (
    exit /b 1
) else (
    exit /b 0
)
