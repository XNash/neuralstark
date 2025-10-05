# NeuralStark - Complete Setup Guide

## 📦 Environment Overview

This NeuralStark installation can work in **two modes**:

### Mode 1: Kubernetes/Supervisor Environment (Current)
- ✅ **Currently Active**
- Services managed by `supervisord`
- MongoDB, Backend, Frontend auto-start
- Best for production containerized deployments

### Mode 2: Standalone Environment
- Use when running on a local machine or server
- Full control over all services
- Use the standalone scripts

---

## 🚀 Quick Start (Current Kubernetes Setup)

### Current Service Status
All services are **already running** via supervisor:

```bash
# Check status
sudo supervisorctl status
```

You should see:
- ✅ backend (RUNNING)
- ✅ frontend (RUNNING)  
- ✅ mongodb (RUNNING)

**Additional services (manually started):**
- ✅ Redis (port 6379)
- ✅ Celery workers (3 workers)

### Access the Application
- **Frontend**: https://python-error-fix.preview.emergentagent.com
- **Backend API**: http://localhost:8001/docs

---

## 🔧 Virtual Environment Setup

### Current venv Location
The virtual environment is at `/root/.venv` and is already:
- ✅ Created and activated for supervisor services
- ✅ All dependencies installed
- ✅ Linked to project directory as `/app/.venv`

### Activating venv Manually
```bash
source /app/.venv/bin/activate
# or
source /root/.venv/bin/activate
```

### Verify venv
```bash
which python3
# Should show: /root/.venv/bin/python3

pip list | grep fastapi
# Should show: fastapi 0.111.0
```

---

## 📁 Project Structure

```
/app/
├── .venv/                          # Symlink to /root/.venv
├── backend/                        # FastAPI backend
│   ├── knowledge_base/
│   │   ├── internal/              # Internal documents
│   │   └── external/              # External documents
│   ├── requirements.txt           # All dependencies (updated)
│   ├── server.py                  # Uvicorn entry point
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Configuration
│   ├── celery_app.py             # Celery configuration
│   └── watcher.py                # File system watcher
│
├── frontend/                      # React + Vite frontend
│   ├── src/
│   ├── package.json
│   └── node_modules/             # Already installed
│
├── chroma_db/                     # Vector database
├── logs/                          # Log files (if using standalone)
│
├── run.sh                         # Original run script
├── stop.sh                        # Original stop script
├── run_standalone.sh              # ✨ NEW: Fixed standalone script
├── stop_standalone.sh             # ✨ NEW: Fixed standalone script
├── start_additional_services.sh  # Start Redis & Celery
├── stop_additional_services.sh   # Stop Redis & Celery
│
├── README.md                      # Original documentation
├── README_KUBERNETES.md           # Kubernetes guide
├── DEPLOYMENT_STATUS.md           # Deployment details
└── SETUP_GUIDE.md                 # This file
```

---

## 🛠️ Service Management

### Option 1: Supervisor Commands (Recommended for Kubernetes)

For services managed by supervisor (Backend, Frontend, MongoDB):

```bash
# Check all services
sudo supervisorctl status

# Restart specific service
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
sudo supervisorctl restart mongodb

# Restart all
sudo supervisorctl restart all

# Stop/Start
sudo supervisorctl stop backend
sudo supervisorctl start backend

# View real-time logs
sudo supervisorctl tail -f backend stderr
sudo supervisorctl tail -f frontend stdout
```

### Option 2: Helper Scripts for Additional Services

For Redis and Celery:

```bash
# Start Redis and Celery
./start_additional_services.sh

# Stop Redis and Celery  
./stop_additional_services.sh
```

### Option 3: Standalone Scripts (For Development)

If you want full control without supervisor:

```bash
# Stop supervisor-managed services first (if needed)
sudo supervisorctl stop all

# Use standalone scripts
./run_standalone.sh    # Starts everything
./stop_standalone.sh   # Stops everything
```

---

## 📊 Monitoring

### Check All Services
```bash
# Quick health check
echo "=== Service Status ==="
echo "MongoDB:" && mongosh --quiet --eval "db.serverStatus().ok"
echo "Redis:" && redis-cli ping  
echo "Backend:" && curl -s -I http://localhost:8001/docs | head -1
echo "Frontend:" && curl -s -I http://localhost:3000 | head -1
echo "Celery:" && pgrep -f "celery.*worker" | wc -l
```

### View Logs

**Supervisor logs:**
```bash
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/backend.out.log
tail -f /var/log/supervisor/frontend.err.log
tail -f /var/log/mongodb.err.log
```

**Additional service logs:**
```bash
tail -f /var/log/celery_worker.log
```

**Standalone mode logs:**
```bash
tail -f logs/backend.log
tail -f logs/frontend.log
tail -f logs/celery_worker.log
```

---

## 🔍 Troubleshooting

### Issue: Backend won't start

```bash
# Check logs
tail -n 100 /var/log/supervisor/backend.err.log

# Check if models are loading (takes 20-30 seconds)
# Look for: "Load pretrained SentenceTransformer: all-MiniLM-L6-v2"

# Restart
sudo supervisorctl restart backend
```

### Issue: Missing Python dependencies

```bash
# Activate venv
source /app/.venv/bin/activate

# Install dependencies
cd /app/backend
pip install -r requirements.txt

# Restart backend
sudo supervisorctl restart backend
```

### Issue: Redis not running

```bash
# Check Redis
redis-cli ping

# Start Redis
./start_additional_services.sh

# Or manually
redis-server --daemonize yes --bind 127.0.0.1
```

### Issue: Celery not processing documents

```bash
# Check Celery is running
pgrep -f "celery.*worker"

# Check logs
tail -f /var/log/celery_worker.log

# Restart Celery
./stop_additional_services.sh
./start_additional_services.sh
```

### Issue: Port already in use

```bash
# Find what's using the port
lsof -i:8001  # Backend
lsof -i:3000  # Frontend
lsof -i:6379  # Redis
lsof -i:27017 # MongoDB

# Kill specific process
kill -9 <PID>

# Or stop all via supervisor
sudo supervisorctl stop all
```

---

## 🔄 Installing New Dependencies

### Python Dependencies

```bash
# Activate venv
source /app/.venv/bin/activate

# Install new package
cd /app/backend
pip install <package-name>

# Update requirements.txt
pip freeze > requirements.txt

# Restart backend
sudo supervisorctl restart backend
```

### Frontend Dependencies

```bash
cd /app/frontend

# Install with yarn (preferred)
yarn add <package-name>

# Or with npm
npm install <package-name>

# Restart frontend
sudo supervisorctl restart frontend
```

---

## 🌐 Configuration

### Backend Environment Variables

Edit `/app/backend/config.py` or set environment variables:

```bash
# LLM Settings
LLM_MODEL=gemini-2.5-flash
LLM_API_KEY=your_api_key_here

# Embedding Settings
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
EMBEDDING_BATCH_SIZE=8

# Redis Settings  
REDIS_HOST=localhost
REDIS_PORT=6379

# MongoDB Settings
MONGO_URL=mongodb://localhost:27017

# OCR Settings
OCR_ENABLED=true
OCR_LANGUAGES=eng+fra
```

After changing config:
```bash
sudo supervisorctl restart backend
```

---

## 📝 Important Notes

### About run.sh and stop.sh

The **original** `run.sh` and `stop.sh` scripts:
- ⚠️ Designed for standalone Linux servers
- ⚠️ Will conflict with supervisor in Kubernetes
- ⚠️ Don't use them in this environment

Use instead:
- ✅ `sudo supervisorctl` commands
- ✅ `run_standalone.sh` (if you stop supervisor)
- ✅ `start_additional_services.sh` for Redis/Celery

### Virtual Environment

- Located at `/root/.venv`
- Symlinked to `/app/.venv`
- Automatically used by supervisor
- All dependencies already installed
- 150+ packages installed including:
  - FastAPI, Uvicorn, Celery
  - LangChain, ChromaDB
  - Google Generative AI
  - Sentence Transformers
  - And many more...

### Data Persistence

- **MongoDB data**: Persisted by container
- **ChromaDB vectors**: `/app/chroma_db`
- **Documents**: `/app/backend/knowledge_base/`
- **Logs**: `/var/log/supervisor/` and `/var/log/`

---

## 🧪 Testing

### Test Backend API

```bash
# Health check (via docs page)
curl -s http://localhost:8001/docs | grep -q "swagger" && echo "✓ Backend OK"

# List documents
curl http://localhost:8001/documents

# Upload a document
curl -X POST http://localhost:8001/documents/upload \
  -F "file=@test.pdf" \
  -F "source_type=internal"
```

### Test Frontend

```bash
# Check frontend is serving
curl -s -I http://localhost:3000 | head -1

# Open in browser
# http://localhost:3000
```

### Test Celery

```bash
# Check workers
celery -A backend.celery_app inspect active

# Check worker status
pgrep -f "celery.*worker" && echo "✓ Celery running"
```

---

## 🚀 Summary

### Current Setup (Kubernetes Mode)

**Active Services:**
- ✅ MongoDB (supervisor) - Port 27017
- ✅ Backend (supervisor) - Port 8001  
- ✅ Frontend (supervisor) - Port 3000
- ✅ Redis (manual) - Port 6379
- ✅ Celery (manual) - 3 workers

**Management:**
```bash
# Supervisor services
sudo supervisorctl status
sudo supervisorctl restart backend

# Additional services
./start_additional_services.sh
./stop_additional_services.sh
```

**Virtual Environment:**
- Location: `/root/.venv` (linked to `/app/.venv`)
- All dependencies installed
- Auto-activated for supervisor services

**Everything is working and production-ready! 🎉**

For more details, see:
- `README_KUBERNETES.md` - Kubernetes-specific guide
- `DEPLOYMENT_STATUS.md` - Current deployment status
- `README.md` - Original documentation
