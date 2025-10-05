# NeuralStark - One Command Setup

## 🎯 The Simplest Way to Run NeuralStark

Everything you need is now in **ONE command**: `./run.sh`

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd neuralstark

# Make script executable
chmod +x run.sh

# Run everything!
./run.sh
```

**That's literally it!** ✅

---

## 🎁 What `run.sh` Does For You

### Phase 1: Directory Setup
- Creates `chroma_db/` (for vector database)
- Creates `backend/knowledge_base/internal/` (for internal documents)
- Creates `backend/knowledge_base/external/` (for external documents)
- Creates `logs/` (for application logs)
- Sets proper permissions

### Phase 2: System Prerequisites
- Checks for Python 3.8+
- Checks for Node.js 16+
- Attempts to install if missing (on supported platforms)

### Phase 3: Virtual Environment
- Detects existing Python virtual environment
- Creates new one if doesn't exist
- Activates it automatically

### Phase 4: Python Dependencies
- Checks if packages already installed
- Installs from `requirements.txt` if needed
- Verifies critical packages (FastAPI, ChromaDB, LangChain, Celery, Redis)
- Installs missing critical packages individually if needed

### Phase 5: Frontend Dependencies
- Installs yarn if not available
- Checks if node_modules exists
- Runs `yarn install` (or `npm install`) if needed

### Phase 6: Redis Service
- Checks if Redis is running
- Starts Redis if installed but not running
- Attempts to install Redis if missing
- Verifies Redis is responding

### Phase 7: MongoDB Service
- Checks if MongoDB is running
- Starts MongoDB if installed but not running
- Attempts to install MongoDB if missing
- Creates data directory and starts service

### Phase 8: Celery Worker
- Stops any existing Celery workers
- Sets up Python path
- Starts new Celery worker with optimal settings
- Verifies worker is running

### Phase 9: Backend (FastAPI)
- Checks if port 8001 is available
- Starts uvicorn with FastAPI application
- Waits for ML models to load (20-30 seconds)
- Verifies backend is healthy

### Phase 10: Frontend (React + Vite)
- Checks if port 3000 is available
- Starts Vite dev server
- Waits for frontend to be ready
- Verifies frontend is responding

### Phase 11: Validation & Health Checks
- Tests Redis connection
- Tests MongoDB connection
- Checks Celery workers
- Tests backend health endpoint
- Tests ChromaDB connection
- Tests frontend accessibility
- Provides comprehensive status report

---

## 📊 Output Example

```bash
$ ./run.sh

==========================================
  🚀 NeuralStark Complete Setup & Start
  Version 6.0 - All-in-One Solution
==========================================

━━━ Phase 1: Directory Setup
ℹ Creating required directories...
✓ All required directories created
✓ Directory permissions set

━━━ Phase 2: System Prerequisites Check
ℹ Checking Python...
✓ Python 3.11.13 found
ℹ Checking Node.js...
✓ Node.js v20.19.5 found

━━━ Phase 3: Python Virtual Environment
ℹ Setting up Python virtual environment...
✓ Virtual environment found (.venv)
✓ Virtual environment activated

━━━ Phase 4: Python Dependencies
ℹ Checking Python dependencies...
✓ Key Python packages already installed

━━━ Phase 5: Frontend Dependencies
✓ Frontend dependencies already installed

━━━ Phase 6: Redis Service
ℹ Checking Redis...
✓ Redis already running on port 6379

━━━ Phase 7: MongoDB Service
ℹ Checking MongoDB...
✓ MongoDB already running on port 27017

━━━ Phase 8: Celery Worker
ℹ Starting Celery worker...
✓ Celery worker started

━━━ Phase 9: Backend Service
ℹ Starting Backend...
ℹ Waiting for backend to load (loading ML models, 20-30s)...
✓ Backend started on port 8001

━━━ Phase 10: Frontend Service
ℹ Starting Frontend...
ℹ Waiting for frontend to start...
✓ Frontend started on port 3000

━━━ Phase 11: Service Validation

ℹ Running health checks...

✓ Redis - Running on port 6379
✓ MongoDB - Running on port 27017
✓ Celery - Running (3 workers)
✓ Backend - Running on port 8001 (healthy)
✓ ChromaDB - Connected successfully
✓ Frontend - Running on port 3000

==========================================
  📊 Startup Summary
==========================================

✓ All services started successfully! 🎉

ℹ 🌐 Application URLs:
     Frontend:  http://localhost:3000
     Backend:   http://localhost:8001
     API Docs:  http://localhost:8001/docs

ℹ 📁 Logs directory: /app/logs
ℹ 🛑 To stop: ./stop.sh

✓ NeuralStark is ready! 🚀

==========================================
```

---

## ⚡ Performance

### First Time (Cold Start)
- **Time:** 2-5 minutes
- **Why:** Installing all dependencies
- **Network:** Requires internet connection for downloads

### Subsequent Runs (Warm Start)
- **Time:** 20-30 seconds
- **Why:** Only starting services, dependencies already installed
- **Network:** Not required if dependencies cached

---

## 🔧 What If Something Fails?

The script provides clear error messages and status codes:

### Errors (Red ✗)
- Critical issues that prevent services from starting
- Script exits with code 1
- Check logs for details

### Warnings (Yellow ⚠)
- Non-critical issues
- Application may still work
- Script continues and exits with code 0

### Example Error Handling
```bash
✗ Redis - Not running
ℹ Please install Redis manually: https://redis.io/download
```

### Example Warning Handling
```bash
⚠ MongoDB - Not running (optional)
ℹ Application will work but document storage may be limited
```

---

## 📝 Logs

All services log to the `logs/` directory:

```bash
# View logs in real-time
tail -f logs/backend.log
tail -f logs/frontend.log
tail -f logs/celery_worker.log
tail -f logs/mongodb.log
```

---

## 🛑 Stopping Services

Just run the stop script:

```bash
./stop.sh
```

---

## 🎓 Advanced Usage

### Run Specific Phases Only

If you want more control, you can still use individual commands:

```bash
# Just setup and validation
./setup.sh

# Just install dependencies (manual)
cd backend && pip install -r requirements.txt
cd frontend && yarn install

# Just start services (manual)
redis-server --daemonize yes
mongod --fork --logpath logs/mongodb.log
# ... etc
```

But honestly, **just use `./run.sh`** - it's easier! 😊

---

## 🌍 Platform Support

### ✅ Fully Automatic
- Ubuntu 20.04+
- Debian 11+
- macOS (with Homebrew)
- CentOS/RHEL 8+

### ✅ Semi-Automatic
- Other Linux distributions (may need manual dependency installation)
- Windows (via WSL)

### ✅ Container Platforms
- Docker (using Dockerfile)
- Kubernetes (using deployment manifests)
- Any container runtime

---

## 🔄 How It's Different From Before

### Old Way (Version 5.0)
```bash
# Step 1: Setup
./setup.sh

# Step 2: Start
./run.sh

# Issues:
# - Two separate steps
# - setup.sh didn't install dependencies
# - run.sh assumed dependencies were installed
# - Easy to forget setup.sh
```

### New Way (Version 6.0)
```bash
# One step - does everything!
./run.sh

# Benefits:
# - Single command
# - Validates environment
# - Installs dependencies
# - Creates directories
# - Starts services
# - Health checks
# - Clear status reporting
```

---

## 🎯 Design Philosophy

### Goals
1. **Simplicity:** One command to rule them all
2. **Robustness:** Handle missing dependencies gracefully
3. **Clarity:** Clear status messages and error reporting
4. **Speed:** Skip already-done steps (idempotent)
5. **Portability:** Work everywhere possible

### Principles
- **Fail Fast:** Stop on critical errors
- **Fail Gracefully:** Warn on non-critical issues
- **Be Informative:** Tell user what's happening
- **Be Helpful:** Suggest fixes for common problems
- **Be Smart:** Detect existing installations

---

## 🐛 Troubleshooting

### "Python not found"
**Solution:** Install Python 3.8+ manually, then re-run

### "Node.js not found"
**Solution:** Install Node.js 16+ manually, then re-run

### "Redis failed to install"
**Solution:** 
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Then re-run
./run.sh
```

### "Port 8001 already in use"
**Solution:**
```bash
# Kill existing process
lsof -ti:8001 | xargs kill -9

# Re-run
./run.sh
```

### "Backend still loading after 40 seconds"
**Reason:** Normal! ML models take time to load
**Solution:** Wait a bit more, check logs/backend.log

---

## 📚 Related Documentation

- [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) - Detailed installation guide
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Deployment verification
- [PORTABLE_DEPLOYMENT.md](PORTABLE_DEPLOYMENT.md) - Multi-platform deployment
- [README.md](README.md) - Main documentation

---

## ✅ Verification

After `./run.sh` completes, verify everything works:

```bash
# 1. Check health
curl http://localhost:8001/api/health
# Expected: {"status":"ok"}

# 2. Check ChromaDB
curl http://localhost:8001/api/documents
# Expected: {"indexed_documents":[]}

# 3. Check frontend
curl -I http://localhost:3000
# Expected: HTTP/1.1 200 OK

# 4. Open in browser
open http://localhost:3000
```

---

## 🎉 Summary

**Before:**
```bash
./setup.sh              # Validate
pip install -r ...      # Install backend
yarn install            # Install frontend
redis-server ...        # Start Redis
mongod ...              # Start MongoDB
celery ...              # Start Celery
uvicorn ...             # Start backend
yarn start              # Start frontend
# Check each service...
```

**Now:**
```bash
./run.sh               # ONE COMMAND! 🎉
```

**That's 8+ commands reduced to 1!**

---

**Version:** 6.0 (All-in-One Edition)  
**Last Updated:** October 5, 2025  
**Status:** Production Ready ✅
