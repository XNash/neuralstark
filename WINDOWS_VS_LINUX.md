# Windows vs Linux Command Reference

This document shows the mapping between Linux (run.sh) and Windows (run_windows.bat) commands for NeuralStark.

## Quick Reference

| Task | Linux/macOS | Windows |
|------|-------------|---------|
| Start all services | `./run.sh` | `run_windows.bat` |
| Stop all services | `./stop.sh` | `stop_windows.bat` |
| View backend logs | `tail -f logs/backend.log` | `type logs\backend.log` |
| Live log monitoring | `tail -f logs/backend.log` | `Get-Content logs\backend.log -Wait` (PowerShell) |
| Check if port in use | `lsof -i:8001` | `netstat -ano \| findstr :8001` |
| Kill process by name | `pkill -f uvicorn` | `taskkill /F /IM uvicorn.exe` |
| Make script executable | `chmod +x run.sh` | Not needed (.bat is executable) |
| Python virtual env activate | `source .venv/bin/activate` | `.venv\Scripts\activate.bat` |
| Check Python version | `python3 --version` | `python --version` |
| Check if service running | `pgrep -f celery` | `tasklist \| findstr celery.exe` |

---

## Detailed Command Comparisons

### 1. Directory Operations

**Linux:**
```bash
mkdir -p backend/knowledge_base/internal
```

**Windows:**
```cmd
mkdir backend\knowledge_base\internal
```
or
```cmd
if not exist "backend\knowledge_base\internal" mkdir "backend\knowledge_base\internal"
```

---

### 2. Check if Directory Exists

**Linux:**
```bash
if [ -d "chroma_db" ]; then
    echo "Directory exists"
fi
```

**Windows:**
```cmd
if exist "chroma_db" (
    echo Directory exists
)
```

---

### 3. Check if Command Available

**Linux:**
```bash
if command -v python3 &>/dev/null; then
    echo "Python found"
fi
```

**Windows:**
```cmd
python --version >nul 2>&1
if not errorlevel 1 (
    echo Python found
)
```
or
```cmd
where python >nul 2>&1
if not errorlevel 1 (
    echo Python found
)
```

---

### 4. Virtual Environment

**Linux:**
```bash
# Create
python3 -m venv .venv

# Activate
source .venv/bin/activate

# Deactivate
deactivate
```

**Windows:**
```cmd
REM Create
python -m venv .venv

REM Activate
call .venv\Scripts\activate.bat

REM Deactivate
deactivate
```

---

### 5. Install Dependencies

**Linux:**
```bash
pip install -r requirements.txt
npm install
# or
yarn install
```

**Windows:**
```cmd
pip install -r requirements.txt
npm install
REM or
yarn install
```
*(Same commands work on both platforms)*

---

### 6. Start Services in Background

**Linux:**
```bash
# Using nohup
nohup uvicorn server:app --host 0.0.0.0 --port 8001 > logs/backend.log 2>&1 &

# Using screen (alternative)
screen -dmS backend uvicorn server:app --host 0.0.0.0 --port 8001
```

**Windows:**
```cmd
REM In new window (visible)
start "Backend" cmd /k "uvicorn server:app --host 0.0.0.0 --port 8001"

REM In new window (minimized)
start "Backend" /MIN cmd /c "uvicorn server:app --host 0.0.0.0 --port 8001 > logs\backend.log 2>&1"

REM In background (hidden)
start /B uvicorn server:app --host 0.0.0.0 --port 8001
```

---

### 7. Check if Port is in Use

**Linux:**
```bash
# Method 1: lsof
lsof -i:8001

# Method 2: netstat
netstat -tuln | grep :8001

# Method 3: ss
ss -tuln | grep :8001
```

**Windows:**
```cmd
REM Method 1: netstat
netstat -ano | findstr :8001

REM Method 2: Get PID and details
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do tasklist /FI "PID eq %%a"
```

---

### 8. Check if Process is Running

**Linux:**
```bash
# Method 1: pgrep
pgrep -f "celery.*worker"

# Method 2: ps with grep
ps aux | grep celery | grep -v grep

# Method 3: pidof
pidof celery
```

**Windows:**
```cmd
REM Method 1: tasklist
tasklist | findstr celery.exe

REM Method 2: Check if running
tasklist /FI "IMAGENAME eq celery.exe" 2>nul | findstr celery.exe >nul
if not errorlevel 1 (
    echo Celery is running
)
```

---

### 9. Kill Process

**Linux:**
```bash
# By name
pkill -f uvicorn

# By name (force)
pkill -9 -f uvicorn

# By PID
kill 12345
kill -9 12345  # Force kill
```

**Windows:**
```cmd
REM By image name
taskkill /F /IM uvicorn.exe

REM By window title
taskkill /F /FI "WINDOWTITLE eq Backend*"

REM By PID
taskkill /F /PID 12345

REM All node processes
taskkill /F /IM node.exe
```

---

### 10. HTTP Health Check

**Linux:**
```bash
# Method 1: curl
curl -s http://localhost:8001/health

# Method 2: wget
wget -q -O - http://localhost:8001/health

# Method 3: curl with timeout
curl -s -m 2 http://localhost:8001/health
```

**Windows:**
```cmd
REM Method 1: curl (Windows 10+)
curl -s http://localhost:8001/health

REM Method 2: PowerShell
powershell -Command "Invoke-WebRequest -Uri 'http://localhost:8001/health' -UseBasicParsing"

REM Method 3: PowerShell with timeout
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8001/api/health' -TimeoutSec 2 -UseBasicParsing; exit 0 } catch { exit 1 }"
```

---

### 11. View Logs

**Linux:**
```bash
# View entire log
cat logs/backend.log

# View last 100 lines
tail -n 100 logs/backend.log

# Live monitoring
tail -f logs/backend.log

# Live with color
tail -f logs/backend.log | ccze
```

**Windows:**
```cmd
REM View entire log
type logs\backend.log

REM View last 20 lines (no direct equivalent to tail -n)
powershell Get-Content logs\backend.log -Tail 20

REM Live monitoring (PowerShell)
powershell Get-Content logs\backend.log -Wait

REM In CMD (no native solution, must use PowerShell)
```

---

### 12. Sleep/Wait

**Linux:**
```bash
sleep 5      # Wait 5 seconds
sleep 0.5    # Wait 500ms
```

**Windows:**
```cmd
REM Wait 5 seconds (with message)
timeout /t 5

REM Wait 5 seconds (no message)
timeout /t 5 /nobreak >nul

REM PowerShell alternative
powershell Start-Sleep -Seconds 5
```

---

### 13. Environment Variables

**Linux:**
```bash
# Set temporary
export PYTHONPATH=/app:$PYTHONPATH

# Set in script
PYTHONPATH=/app

# Use in script
echo $PYTHONPATH
```

**Windows:**
```cmd
REM Set temporary
set PYTHONPATH=%SCRIPT_DIR%;%PYTHONPATH%

REM Set in script
set PYTHONPATH=C:\app

REM Use in script
echo %PYTHONPATH%
```

---

### 14. Path Separators

**Linux:**
```bash
cd /app/backend
python /app/backend/server.py
```

**Windows:**
```cmd
cd C:\app\backend
python C:\app\backend\server.py

REM Or use forward slashes (usually works)
cd C:/app/backend
```

---

### 15. Get Script Directory

**Linux:**
```bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"
```

**Windows:**
```cmd
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
```

---

### 16. Suppress Output

**Linux:**
```bash
command > /dev/null 2>&1
```

**Windows:**
```cmd
command >nul 2>&1
```

---

### 17. Colors in Terminal

**Linux:**
```bash
RED='33[0;31m'
GREEN='33[0;32m'
NC='33[0m'
echo -e "${GREEN}Success${NC}"
```

**Windows:**
```cmd
REM No native color support in CMD
REM Must use PowerShell or third-party tools

REM PowerShell:
powershell Write-Host "Success" -ForegroundColor Green

REM Or use ANSI codes (Windows 10+)
echo [32mSuccess[0m
```

---

### 18. Check File Exists

**Linux:**
```bash
if [ -f "requirements.txt" ]; then
    echo "File exists"
fi
```

**Windows:**
```cmd
if exist "requirements.txt" (
    echo File exists
)
```

---

### 19. Test Write Permissions

**Linux:**
```bash
touch chroma_db/test_write.tmp 2>/dev/null
if [ $? -eq 0 ]; then
    rm chroma_db/test_write.tmp
    echo "Writable"
fi
```

**Windows:**
```cmd
echo test > chroma_db\test_write.tmp 2>nul
if exist chroma_db\test_write.tmp (
    del chroma_db\test_write.tmp 2>nul
    echo Writable
)
```

---

### 20. Increment Counter

**Linux:**
```bash
ERRORS=0
ERRORS=$((ERRORS + 1))
```

**Windows:**
```cmd
set ERRORS=0
set /a ERRORS+=1
```

---

## Platform-Specific Considerations

### Linux/macOS Advantages

1. **Package Managers**: apt, yum, brew for easy dependency installation
2. **Process Management**: Better background process handling with nohup, screen, tmux
3. **Native Redis/MongoDB**: Easier to install and configure
4. **Shell Features**: More powerful scripting with bash
5. **POSIX Tools**: Rich set of command-line utilities (grep, awk, sed, etc.)

### Windows Advantages

1. **GUI Integration**: Easier to manage services through Task Manager
2. **Windows Services**: Can install services permanently
3. **PowerShell**: Modern scripting with object-oriented approach
4. **Native Path Handling**: Better Windows path support

### Common Challenges on Windows

1. **Redis**: No official Windows version (need WSL or unofficial builds)
2. **MongoDB**: Installation is manual (no package manager by default)
3. **Celery**: Requires `--pool=solo` on Windows (no fork support)
4. **Path Issues**: Backslash vs forward slash
5. **Process Management**: No native equivalent to nohup
6. **Log Monitoring**: No native tail -f equivalent in CMD

---

## Recommendations

### For Windows Users

1. **Use Windows Subsystem for Linux (WSL)** if you need better Linux compatibility
2. **Install Docker Desktop** for easier Redis and MongoDB setup
3. **Use PowerShell** for more advanced scripting needs
4. **Consider Chocolatey** as a package manager for Windows

### For Cross-Platform Development

1. **Use Docker** for all services (Redis, MongoDB, backend, frontend)
2. **Use Python/Node scripts** instead of bash/batch for critical logic
3. **Abstract OS-specific commands** into functions
4. **Test on both platforms** regularly

---

## Additional Resources

- [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/)
- [PowerShell Documentation](https://docs.microsoft.com/en-us/powershell/)
- [Redis for Windows](https://github.com/microsoftarchive/redis/releases)
- [MongoDB for Windows](https://www.mongodb.com/try/download/community)
- [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)

---

## Quick Migration Guide

If you're familiar with the Linux `run.sh` and want to understand `run_windows.bat`:

1. **11 Phases**: Both scripts have the same 11 phases
2. **Same Logic**: Directory setup, dependency installation, service startup, health checks
3. **Different Syntax**: CMD/Batch syntax instead of Bash
4. **Same Results**: Both achieve the same goal of starting all services
5. **Logs**: Both create logs in `logs/` directory
6. **Virtual Env**: Both use Python virtual environments
7. **Health Checks**: Both perform comprehensive service validation

**The Windows version is functionally equivalent to the Linux version!**
