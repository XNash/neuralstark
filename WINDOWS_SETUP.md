# NeuralStark - Windows Setup Guide

This guide explains how to run NeuralStark on Windows using the provided batch scripts.

## 🚀 Quick Start (Windows)

### Prerequisites

Before running the application, ensure you have:

1. **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
   - ✅ Make sure to check "Add Python to PATH" during installation
   
2. **Node.js 16+** - [Download Node.js](https://nodejs.org/)
   - ✅ Includes npm package manager
   
3. **Redis** (Required for Celery)
   - **Option 1**: Download Windows binaries from [Redis for Windows](https://github.com/microsoftarchive/redis/releases)
   - **Option 2**: Use WSL (Windows Subsystem for Linux) and install Redis there
   - **Option 3**: Use Docker: `docker run -d -p 6379:6379 redis`
   
4. **MongoDB** (Recommended)
   - Download from [MongoDB Community Server](https://www.mongodb.com/try/download/community)
   - Or use Docker: `docker run -d -p 27017:27017 mongo`

### One-Command Setup & Start

**Run this in Command Prompt (as Administrator recommended):**

```cmd
run_windows.bat
```

**That's it!** The script handles everything:
- ✅ Creates all required directories (chroma_db, logs, knowledge_base)
- ✅ Sets up Python virtual environment
- ✅ Validates system prerequisites (Python, Node.js)
- ✅ Installs Python packages from requirements.txt
- ✅ Installs frontend dependencies (yarn/npm)
- ✅ Starts Redis (if available)
- ✅ Starts MongoDB (if available)
- ✅ Starts Celery worker
- ✅ Starts Backend (FastAPI)
- ✅ Starts Frontend (React + Vite)
- ✅ Performs health checks on all services

**First-time startup:** ~3-5 minutes (installs dependencies)  
**Subsequent startups:** ~30-40 seconds

---

## 📁 Scripts Overview

### `run_windows.bat` - Complete Setup & Start Script

This is the main script that:
- Creates all required directories
- Sets up Python virtual environment
- Installs all dependencies
- Starts all services
- Performs health checks

**Features:**
- Automatic dependency installation
- Virtual environment management
- Comprehensive error checking
- Service health validation
- Detailed status reporting

### `stop_windows.bat` - Stop All Services

Gracefully stops all NeuralStark services:
- Celery worker
- Backend (FastAPI)
- Frontend (React)
- Leaves Redis and MongoDB running (they can be shared)

**Usage:**
```cmd
stop_windows.bat
```

### Legacy Scripts (Simple Version)

- `run.bat` - Simpler startup script (original)
- `stop.bat` - Simpler stop script (original)

**Note:** Use `run_windows.bat` and `stop_windows.bat` for the full-featured experience that matches the Linux `run.sh` functionality.

---

## 🎯 Access the Application

Once started:

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8001](http://localhost:8001)
- **API Documentation**: [http://localhost:8001/docs](http://localhost:8001/docs)

---

## 📊 View Logs

All logs are stored in the `logs\` directory:

```cmd
REM View backend logs
type logs\backend.log

REM View frontend logs
type logs\frontend.log

REM View Celery logs
type logs\celery_worker.log

REM View MongoDB logs
type logs\mongodb.log
```

**Live monitoring (PowerShell):**
```powershell
Get-Content logs\backend.log -Wait
```

---

## 🛠️ Troubleshooting

### Port Already in Use

If you get port conflict errors:

```cmd
REM Find what's using the port
netstat -ano | findstr :8001
netstat -ano | findstr :3000

REM Kill the process using the port (replace PID)
taskkill /F /PID <PID>

REM Or run the stop script first
stop_windows.bat
run_windows.bat
```

### Redis Not Running

**Error:** `Redis - Not running`

**Solutions:**

1. **Install Redis for Windows:**
   - Download from [Redis Releases](https://github.com/microsoftarchive/redis/releases)
   - Extract and run `redis-server.exe`
   
2. **Use WSL:**
   ```bash
   wsl
   sudo service redis-server start
   ```

3. **Use Docker:**
   ```cmd
   docker run -d -p 6379:6379 --name redis redis
   ```

### MongoDB Not Running

**Error:** `MongoDB - Not running`

**Solutions:**

1. **Install MongoDB:**
   - Download from [MongoDB Downloads](https://www.mongodb.com/try/download/community)
   - Run the installer
   - Start MongoDB service

2. **Use Docker:**
   ```cmd
   docker run -d -p 27017:27017 --name mongodb mongo
   ```

### Backend Takes Long to Start

**This is normal!** The backend loads ML models (SentenceTransformer) which takes 20-30 seconds.

Wait for:
```
[OK] Backend started on port 8001
```

Check logs if it takes longer than 1 minute:
```cmd
type logs\backend.log
```

### Python Package Errors

If you see import errors:

```cmd
REM Activate virtual environment
.venv\Scripts\activate.bat

REM Reinstall packages
pip install -r backend\requirements.txt

REM Deactivate
deactivate
```

### Node.js / Frontend Errors

If frontend fails to start:

```cmd
cd frontend

REM Clear cache and reinstall
rmdir /s /q node_modules
del package-lock.json
del yarn.lock

REM Reinstall
yarn install

REM Or use npm
npm install

cd ..
```

### Permission Errors

Run Command Prompt as Administrator:
1. Search for "cmd" in Start Menu
2. Right-click "Command Prompt"
3. Select "Run as administrator"
4. Navigate to project directory
5. Run `run_windows.bat`

### Firewall Issues

If Windows Firewall blocks the application:
1. Allow Python and Node.js through firewall when prompted
2. Or manually add exceptions in Windows Defender Firewall

---

## 🔧 Manual Service Control

### Start Services Individually

**Redis:**
```cmd
redis-server --bind 127.0.0.1
```

**MongoDB:**
```cmd
mongod --bind_ip_all --dbpath mongodb_data
```

**Backend:**
```cmd
cd backend
.venv\Scripts\activate.bat
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Frontend:**
```cmd
cd frontend
yarn start
```

**Celery:**
```cmd
.venv\Scripts\activate.bat
celery -A backend.celery_app worker --loglevel=info --pool=solo
```

### Stop Services Individually

**Celery:**
```cmd
taskkill /F /IM celery.exe
```

**Backend:**
```cmd
taskkill /F /IM uvicorn.exe
```

**Frontend:**
```cmd
taskkill /F /IM node.exe
```

**Redis:**
```cmd
taskkill /F /IM redis-server.exe
```

**MongoDB:**
```cmd
taskkill /F /IM mongod.exe
```

---

## 🌐 Network Access

To access from other devices on your network:

1. **Find your IP address:**
   ```cmd
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., 192.168.1.100)

2. **Access from other devices:**
   - Frontend: `http://YOUR_IP:3000`
   - Backend: `http://YOUR_IP:8001`

3. **Firewall Configuration:**
   - Ensure Windows Firewall allows connections on ports 3000 and 8001
   - Add inbound rules for these ports if needed

---

## 📝 Differences from Linux Version

### Windows-Specific Changes

1. **Batch Script Syntax**: `.bat` files use Windows command syntax instead of Bash
2. **Process Management**: Uses `START` and `taskkill` instead of `nohup` and `pkill`
3. **Service Detection**: Uses `netstat` and `tasklist` instead of `lsof` and `pgrep`
4. **Virtual Environment**: Uses `.venv\Scripts\activate.bat` instead of `source .venv/bin/activate`
5. **Path Separators**: Uses backslashes `\` instead of forward slashes `/`
6. **Background Processes**: Opens separate windows for services (minimized)

### Feature Parity

The Windows version (`run_windows.bat`) provides the same functionality as the Linux version (`run.sh`):

✅ All 11 setup phases  
✅ Automatic directory creation  
✅ Virtual environment management  
✅ Dependency installation  
✅ Service health checks  
✅ Error and warning tracking  
✅ Comprehensive logging  
✅ Status reporting  

---

## 💡 Tips

1. **First Run**: Be patient - installing dependencies takes time
2. **Antivirus**: Some antivirus software may slow down installation
3. **WSL**: For better Linux compatibility, consider using WSL2
4. **Docker**: For easier Redis/MongoDB setup, use Docker Desktop
5. **Admin Rights**: Some operations may require administrator privileges

---

## 🔄 Updates and Maintenance

### Update Dependencies

**Python packages:**
```cmd
.venv\Scripts\activate.bat
pip install --upgrade -r backend\requirements.txt
deactivate
```

**Frontend packages:**
```cmd
cd frontend
yarn upgrade
cd ..
```

### Clean Installation

To start fresh:

```cmd
REM Stop all services
stop_windows.bat

REM Remove virtual environment
rmdir /s /q .venv

REM Remove frontend dependencies
rmdir /s /q frontend\node_modules

REM Remove database
rmdir /s /q chroma_db

REM Start fresh
run_windows.bat
```

---

## 📞 Getting Help

If you encounter issues:

1. **Check logs** in `logs\` directory
2. **Review error messages** from the startup script
3. **Verify prerequisites** are installed correctly
4. **Check firewall** and antivirus settings
5. **Try running as Administrator**

For more detailed information:
- [README.md](README.md) - Complete project documentation
- [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) - Detailed installation instructions
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Production deployment guide

---

## ✅ Quick Checklist

Before running `run_windows.bat`, ensure:

- [ ] Python 3.8+ installed and in PATH
- [ ] Node.js 16+ installed
- [ ] Redis installed or running via Docker/WSL
- [ ] MongoDB installed (optional but recommended)
- [ ] Git installed (if cloning from repository)
- [ ] Command Prompt opened in project directory
- [ ] Internet connection for downloading dependencies

---

**Happy building with NeuralStark on Windows! 🚀**
