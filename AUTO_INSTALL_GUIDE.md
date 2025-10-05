# NeuralStark - Auto-Installation Guide

## 🚀 Automatic Dependency Installation

The `run.sh` script has been enhanced with **automatic dependency installation**. It will now automatically install any missing packages or dependencies when you run it.

---

## ✨ What Gets Auto-Installed

### System Packages
- ✅ **Python 3** (if not installed)
- ✅ **Node.js** (if not installed)
- ✅ **MongoDB** (if not installed)
- ✅ **Redis** (if not installed)
- ✅ **Yarn** (if not installed, falls back to npm)

### Python Dependencies
- ✅ **Virtual environment** (auto-created if missing)
- ✅ **All packages from requirements.txt**, including:
  - FastAPI, Uvicorn (web framework)
  - Celery, Redis (task queue)
  - LangChain, ChromaDB (AI/vector DB)
  - Google Generative AI (LLM)
  - Sentence Transformers (embeddings)
  - PyPDF, python-docx (document processing)
  - Pytesseract, Pillow (OCR)
  - And 140+ more packages

### Frontend Dependencies
- ✅ **All npm/yarn packages from package.json**, including:
  - React, React DOM
  - Vite (build tool)
  - Tailwind CSS
  - Radix UI components
  - Chart.js
  - And 50+ more packages

### Project Structure
- ✅ **Required directories** (auto-created):
  - `/app/backend/knowledge_base/internal/`
  - `/app/backend/knowledge_base/external/`
  - `/app/chroma_db/`
  - `/app/logs/`

---

## 🎯 Quick Start

### First Time Setup

Just run the script - everything will be installed automatically:

```bash
cd /app
./run.sh
```

**What happens:**
1. ✅ Checks and creates virtual environment
2. ✅ Installs all Python dependencies
3. ✅ Installs all frontend dependencies
4. ✅ Installs system packages (MongoDB, Redis)
5. ✅ Creates required directories
6. ✅ Starts all services
7. ✅ Performs health checks

**Time estimate:**
- First run: 3-5 minutes (installing dependencies)
- Subsequent runs: 30-40 seconds (just starting services)

---

## 📋 Prerequisites

### Minimum Requirements

**Operating System:**
- Ubuntu 18.04+ / Debian 10+
- CentOS 7+ / RHEL 7+
- macOS 10.15+
- Any Linux with apt-get or yum

**Permissions:**
- Sudo access (for installing system packages)
- Or pre-installed: Python 3.8+, Node.js 16+, MongoDB, Redis

**Resources:**
- CPU: 2+ cores recommended
- RAM: 2GB minimum, 4GB recommended
- Disk: 5GB free space

---

## 🔍 What run.sh Does Step-by-Step

### Step 1: Setup Virtual Environment
```
✓ Checks for existing venv at /app/.venv or /root/.venv
✓ Creates new venv if not found
✓ Activates venv for all Python operations
```

### Step 2: Check System Prerequisites
```
✓ Verifies Python 3 is installed (installs if missing)
✓ Verifies Node.js is installed (installs if missing)
✓ Shows versions of installed tools
```

### Step 3: Install Python Dependencies
```
✓ Reads backend/requirements.txt
✓ Updates pip, setuptools, wheel
✓ Installs all packages (150+ packages)
✓ Verifies critical packages (fastapi, celery, etc.)
✓ Installs missing packages individually if needed
```

### Step 4: Install Frontend Dependencies
```
✓ Checks for node_modules directory
✓ Installs yarn if not available
✓ Runs yarn install (or npm install)
✓ Installs 50+ frontend packages
```

### Step 5: Setup and Start MongoDB
```
✓ Checks if MongoDB is running
✓ Installs MongoDB if not found
✓ Starts MongoDB on port 27017
✓ Creates data directory if needed
```

### Step 6: Setup and Start Redis
```
✓ Checks if Redis is running
✓ Installs Redis if not found
✓ Starts Redis on port 6379
✓ Verifies connection with PING
```

### Step 7: Start Celery Workers
```
✓ Stops existing workers
✓ Installs Celery if not found
✓ Starts 2 workers with concurrency
✓ Logs to logs/celery_worker.log
```

### Step 8: Start Backend (FastAPI)
```
✓ Checks if port 8001 is available
✓ Starts uvicorn server
✓ Waits for ML models to load (20-30s)
✓ Verifies health check endpoint
✓ Logs to logs/backend.log
```

### Step 9: Start Frontend (React + Vite)
```
✓ Checks if port 3000 is available
✓ Starts Vite dev server
✓ Waits for frontend to be ready
✓ Logs to logs/frontend.log
```

### Step 10: Status Summary
```
✓ Shows status of all services
✓ Reports any issues
✓ Provides access URLs
✓ Shows log file locations
```

---

## 🧪 Testing Installation

### Test Dependencies Before Running

```bash
# Run the dependency checker
./test_dependencies.sh
```

This will verify:
- ✅ 29+ different checks
- ✅ System prerequisites
- ✅ Python packages
- ✅ Frontend packages
- ✅ Project structure
- ✅ Script permissions

**Expected output:**
```
==========================================
  📊 Test Results
==========================================

Passed: 29/29
Failed: 0/29
Success Rate: 100%

✓ All dependencies are installed!
```

---

## 📊 Verify Services After Running

### Check All Services

```bash
# Quick status check
echo "MongoDB:" && mongosh --quiet --eval "db.serverStatus().ok"
echo "Redis:" && redis-cli ping
echo "Backend:" && curl -s http://localhost:8001/docs | head -5
echo "Frontend:" && curl -s -I http://localhost:3000 | head -1
echo "Celery:" && pgrep -f "celery.*worker" | wc -l
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001/docs
- **API Documentation**: http://localhost:8001/docs

---

## 🔧 Customization

### Skip Certain Installations

If you want to skip auto-installation of specific components, you can modify `run.sh`:

**Skip MongoDB installation:**
```bash
# Comment out MongoDB installation section
# Lines ~165-180 in run.sh
```

**Skip Redis installation:**
```bash
# Comment out Redis installation section
# Lines ~185-210 in run.sh
```

**Use system Python instead of venv:**
```bash
# Comment out venv activation
# Lines ~48-75 in run.sh
```

---

## 🐛 Troubleshooting Auto-Installation

### Issue: "Permission denied" during package installation

**Solution:**
```bash
# Make sure you have sudo access
sudo -v

# Or install system packages manually first
sudo apt-get install python3 python3-pip nodejs mongodb redis-server

# Then run without sudo for the script
./run.sh
```

### Issue: "Cannot install Python dependencies"

**Solution:**
```bash
# Activate venv manually
source /app/.venv/bin/activate

# Install dependencies manually
cd /app/backend
pip install -r requirements.txt

# Then run the script
cd /app
./run.sh
```

### Issue: "Frontend installation fails"

**Solution:**
```bash
# Install yarn globally
npm install -g yarn

# Install frontend dependencies manually
cd /app/frontend
yarn install

# Then run the script
cd /app
./run.sh
```

### Issue: "MongoDB won't start"

**Solution:**
```bash
# Check if MongoDB is already running
lsof -i:27017

# If occupied, kill the process
pkill mongod

# Or use supervisor if available
sudo supervisorctl restart mongodb

# Then run the script
./run.sh
```

### Issue: "Redis installation fails"

**Solution:**
```bash
# Install Redis manually
sudo apt-get update
sudo apt-get install redis-server

# Start Redis
redis-server --daemonize yes

# Verify
redis-cli ping

# Then run the script
./run.sh
```

### Issue: "Services start but don't work"

**Solution:**
```bash
# Check logs for errors
tail -f /app/logs/backend.log
tail -f /app/logs/frontend.log
tail -f /app/logs/celery_worker.log

# Common fixes:
# 1. Wait longer (backend takes 20-30s to load ML models)
# 2. Check if ports are available (8001, 3000, 6379, 27017)
# 3. Verify all dependencies installed: ./test_dependencies.sh
```

---

## 📁 File Locations

### Scripts
```
/app/run.sh                      - Main startup script (with auto-install)
/app/stop.sh                     - Stop script
/app/test_dependencies.sh        - Dependency checker
/app/run_standalone.sh           - Alternative standalone script
/app/stop_standalone.sh          - Alternative stop script
```

### Backups
```
/app/run.sh.backup              - Original run.sh
/app/stop.sh.backup             - Original stop.sh
```

### Logs
```
/app/logs/backend.log           - Backend logs
/app/logs/frontend.log          - Frontend logs
/app/logs/celery_worker.log     - Celery logs
/app/logs/mongodb.log           - MongoDB logs
```

### Configuration
```
/app/backend/requirements.txt   - Python dependencies (150+ packages)
/app/frontend/package.json      - Frontend dependencies (50+ packages)
/app/backend/config.py          - Backend configuration
```

---

## 🎓 Understanding the Auto-Installation

### Why Auto-Install?

1. **Convenience**: One command to set up everything
2. **Consistency**: Same setup across different environments
3. **Speed**: Fast deployment on new systems
4. **Reliability**: Automatic detection and installation
5. **Documentation**: Self-documenting setup process

### What's Safe to Auto-Install?

The script only auto-installs:
- ✅ Open-source packages from official repositories
- ✅ Well-known, trusted packages (FastAPI, React, etc.)
- ✅ Packages listed in requirements.txt and package.json
- ✅ System packages from official repos (apt/yum)

The script does NOT:
- ❌ Modify system configuration
- ❌ Install untrusted packages
- ❌ Change existing files (except installing to venv)
- ❌ Require root except for system package installation

### Security Considerations

- Virtual environment isolates Python packages
- System packages only from official repositories
- No automatic execution of downloaded code
- All dependencies are pinned in requirements.txt
- You can review the script before running

---

## 🔄 Updating Dependencies

### Update Python Packages

```bash
# Activate venv
source /app/.venv/bin/activate

# Update all packages
cd /app/backend
pip install --upgrade -r requirements.txt

# Or update specific package
pip install --upgrade langchain

# Update requirements.txt
pip freeze > requirements.txt

# Restart services
./stop.sh
./run.sh
```

### Update Frontend Packages

```bash
# Update all packages
cd /app/frontend
yarn upgrade

# Or update specific package
yarn upgrade react

# Restart services
./stop.sh
./run.sh
```

---

## 📈 Performance Notes

### Installation Times

**First Run (Cold Install):**
- System packages: 1-2 minutes
- Python packages: 2-3 minutes
- Frontend packages: 1-2 minutes
- Service startup: 30-40 seconds
- **Total: 4-7 minutes**

**Subsequent Runs (Warm Start):**
- Dependency checks: 5 seconds
- Service startup: 30-40 seconds
- **Total: 35-45 seconds**

### Resource Usage During Installation

- **CPU**: 50-80% (during package compilation)
- **Memory**: 500MB-1GB
- **Disk I/O**: High (downloading and extracting)
- **Network**: 500MB-1GB download

### Tips for Faster Installation

1. **Pre-install system packages:**
   ```bash
   sudo apt-get install python3 nodejs mongodb redis-server
   ```

2. **Use local package cache:**
   ```bash
   pip install -r requirements.txt --cache-dir ~/.cache/pip
   ```

3. **Parallel installations:**
   - The script already optimizes this where possible

---

## ✅ Summary

### What You Get

- ✅ **One-command setup** - Just run `./run.sh`
- ✅ **Automatic dependency installation** - No manual steps
- ✅ **Virtual environment** - Isolated Python packages
- ✅ **All services started** - MongoDB, Redis, Backend, Frontend, Celery
- ✅ **Health checks** - Automatic verification
- ✅ **Error handling** - Clear messages if something fails
- ✅ **Logging** - All logs in one place

### Quick Commands

```bash
# Start everything (auto-install missing deps)
./run.sh

# Stop everything
./stop.sh

# Test dependencies
./test_dependencies.sh

# View logs
tail -f logs/backend.log
tail -f logs/frontend.log

# Check status
curl http://localhost:8001/docs
curl http://localhost:3000
```

---

**The auto-installation makes NeuralStark deployment as simple as running one command! 🎉**
