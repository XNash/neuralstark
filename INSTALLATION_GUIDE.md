# NeuralStark - Complete Installation Guide

## For Any Environment (Ubuntu, Debian, macOS, CentOS)

This guide ensures NeuralStark works correctly in any environment.

---

## Quick Start (Automated)

### One Command Does Everything!

```bash
chmod +x run.sh
./run.sh
```

**That's it!** The `run.sh` script is now an all-in-one solution that handles:
- ✅ Directory creation (chroma_db, logs, knowledge_base folders)
- ✅ Virtual environment setup
- ✅ System prerequisite validation (Python, Node.js)
- ✅ Python dependency installation (from requirements.txt)
- ✅ Frontend dependency installation (yarn/npm)
- ✅ Redis installation and startup (if missing)
- ✅ MongoDB installation and startup (if missing)
- ✅ Celery worker startup
- ✅ Backend (FastAPI) startup
- ✅ Frontend (React/Vite) startup
- ✅ Health checks and validation

### Optional: Pre-Flight Validation

If you want to check your environment before starting services:
```bash
chmod +x setup.sh
./setup.sh
```

This validates the environment but doesn't start services. However, **it's completely optional** because `run.sh` does everything!

---

## Manual Installation (If Automated Fails)

### Prerequisites

#### 1. Python 3.8+ (Required)
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv

# macOS
brew install python3

# CentOS/RHEL
sudo yum install -y python3 python3-pip
```

#### 2. Node.js 16+ (Required)
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS
brew install node

# CentOS/RHEL
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo yum install -y nodejs
```

#### 3. Redis (Required for Celery)
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y redis-server

# macOS
brew install redis

# CentOS/RHEL
sudo yum install -y redis

# Start Redis
redis-server --daemonize yes

# Verify
redis-cli ping  # Should return "PONG"
```

#### 4. MongoDB (Recommended)
```bash
# Ubuntu/Debian
sudo apt-get install -y mongodb

# macOS
brew install mongodb-community

# CentOS/RHEL
sudo yum install -y mongodb-org

# Start MongoDB
mongod --fork --logpath /tmp/mongodb.log --bind_ip_all

# Verify
mongosh --eval "db.version()"
```

---

## Directory Structure Setup

### Create Required Directories (CRITICAL)
```bash
cd /path/to/neuralstark

# Create all required directories
mkdir -p backend/knowledge_base/internal
mkdir -p backend/knowledge_base/external
mkdir -p chroma_db
mkdir -p logs

# Verify directories exist
ls -la backend/knowledge_base/
ls -la chroma_db/
ls -la logs/
```

**Why these directories are needed:**
- `backend/knowledge_base/internal/` - Internal documents for the AI
- `backend/knowledge_base/external/` - External documents for the AI
- `chroma_db/` - **CRITICAL** - ChromaDB vector database storage
- `logs/` - Application logs

**⚠️ IMPORTANT:** Missing `chroma_db/` directory will cause:
```
ERROR: Could not connect to tenant default_tenant
ERROR: unable to open database file
```

---

## Python Dependencies

### Install Backend Dependencies
```bash
cd backend

# Method 1: Using virtual environment (Recommended)
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Method 2: System-wide installation
pip3 install -r requirements.txt

# Verify installation
python3 -c "import fastapi, chromadb, langchain, celery, redis"
```

### Key Packages in requirements.txt:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `chromadb==1.1.1` - Vector database (version specific)
- `langchain` - AI framework
- `celery` - Task queue
- `redis==5.0.1` - Message broker
- `sentence-transformers` - Embeddings
- `pytesseract` - OCR (optional)

---

## Frontend Dependencies

### Install Frontend Dependencies
```bash
cd frontend

# Install yarn if not available
npm install -g yarn

# Install dependencies
yarn install

# Verify installation
ls node_modules/react
```

---

## Environment Configuration (Optional)

### Create .env file in backend/ (Optional)
```bash
cd backend
cat > .env << 'EOF'
# LLM Settings
LLM_API_KEY=your_gemini_api_key_here
LLM_MODEL=gemini-2.5-flash

# Embedding Settings
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
EMBEDDING_BATCH_SIZE=8

# OCR Settings
OCR_ENABLED=true
OCR_LANGUAGES=eng+fra

# Redis Settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# MongoDB Settings (if different from default)
# MONGO_URL=mongodb://localhost:27017

# Paths (defaults work for standard setup)
INTERNAL_KNOWLEDGE_BASE_PATH=/app/backend/knowledge_base/internal
EXTERNAL_KNOWLEDGE_BASE_PATH=/app/backend/knowledge_base/external
CHROMA_DB_PATH=/app/chroma_db
EOF
```

**Note:** Default values in `config.py` work for most setups. `.env` file is optional.

---

## Starting Services

### Method 1: Automated (Recommended)
```bash
./run.sh
```

### Method 2: Manual Startup

#### 1. Start Redis
```bash
redis-server --daemonize yes
redis-cli ping  # Verify: Should return "PONG"
```

#### 2. Start MongoDB
```bash
mongod --fork --logpath logs/mongodb.log --bind_ip_all
```

#### 3. Start Celery Worker
```bash
cd /path/to/neuralstark
export PYTHONPATH=$PWD:$PYTHONPATH

celery -A backend.celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    --max-tasks-per-child=50 \
    > logs/celery_worker.log 2>&1 &
```

#### 4. Start Backend
```bash
cd backend
uvicorn server:app \
    --host 0.0.0.0 \
    --port 8001 \
    --reload \
    > ../logs/backend.log 2>&1 &

# Wait for ML models to load (20-30 seconds)
sleep 30

# Verify
curl http://localhost:8001/api/health
```

#### 5. Start Frontend
```bash
cd frontend
yarn start > ../logs/frontend.log 2>&1 &

# Wait for frontend to start (5-10 seconds)
sleep 10

# Verify
curl -I http://localhost:3000
```

---

## Verification Checklist

### ✅ Run These Commands to Verify Everything Works

```bash
# 1. Check Redis
redis-cli ping
# Expected: PONG

# 2. Check MongoDB
mongosh --eval "db.version()"
# Expected: Version number

# 3. Check Celery
ps aux | grep celery | grep -v grep
# Expected: Running processes

# 4. Check Backend Health
curl http://localhost:8001/api/health
# Expected: {"status":"ok"}

# 5. Check Documents API (ChromaDB)
curl http://localhost:8001/api/documents
# Expected: {"indexed_documents":[]}
# If you see ChromaDB errors, check that chroma_db/ directory exists

# 6. Check Frontend
curl -I http://localhost:3000
# Expected: HTTP/1.1 200 OK

# 7. Test Chat Endpoint
curl -X POST http://localhost:8001/api/chat \
    -H "Content-Type: application/json" \
    -d '{"query":"Hello"}'
# Expected: JSON response from AI
```

---

## Common Issues & Solutions

### Issue 1: ChromaDB Errors
```
ERROR: Could not connect to tenant default_tenant
ERROR: unable to open database file
```

**Solution:**
```bash
# Ensure directory exists
mkdir -p chroma_db

# Check permissions
chmod 755 chroma_db

# Restart backend
pkill -f "uvicorn.*server:app"
cd backend && uvicorn server:app --host 0.0.0.0 --port 8001 &
```

### Issue 2: Redis Connection Refused
```
ERROR: Connection refused (redis)
```

**Solution:**
```bash
# Install Redis
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis                  # macOS

# Start Redis
redis-server --daemonize yes

# Verify
redis-cli ping
```

### Issue 3: Port Already in Use
```
ERROR: Address already in use (port 8001 or 3000)
```

**Solution:**
```bash
# Find and kill process
lsof -ti:8001 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend

# Or use stop script
./stop.sh
```

### Issue 4: Backend Takes Too Long to Start
```
Backend is loading...
```

**This is normal!** The backend loads ML models which takes 20-30 seconds on first startup.

**Wait for:**
```
INFO: Application startup complete.
```

### Issue 5: Permission Denied
```bash
# Make scripts executable
chmod +x run.sh stop.sh setup.sh

# Fix directory permissions
chmod -R 755 chroma_db logs backend/knowledge_base
```

---

## Stopping Services

### Method 1: Automated
```bash
./stop.sh
```

### Method 2: Manual
```bash
# Stop Backend
pkill -f "uvicorn.*server:app"

# Stop Frontend
pkill -f "vite"

# Stop Celery
pkill -f "celery.*worker"

# Stop Redis (optional)
redis-cli shutdown

# Stop MongoDB (optional)
mongod --shutdown
```

---

## Environment-Specific Notes

### Docker/Container Environments
If running in Docker or Kubernetes:
1. Ensure volumes are mounted for persistent data:
   - `/app/chroma_db`
   - `/app/backend/knowledge_base`
   - `/app/logs`

2. Redis and MongoDB should be accessible via network

3. Environment variables should be set via ConfigMap or .env

### Shared/Multi-User Environments
1. Use virtual environment for Python (`.venv`)
2. Don't install packages system-wide
3. Use local Redis/MongoDB if possible
4. Set custom ports if defaults are taken

### Low-Resource Environments
In `backend/config.py` or `.env`, adjust:
```bash
EMBEDDING_BATCH_SIZE=4  # Reduce from 8
```

In Celery command, adjust:
```bash
celery -A backend.celery_app worker --concurrency=1  # Reduce from 2
```

---

## Access Points

Once everything is running:

- **Frontend UI:** http://localhost:3000
- **Backend API:** http://localhost:8001
- **API Documentation:** http://localhost:8001/docs
- **Health Check:** http://localhost:8001/api/health

---

## Log Files

Check logs if something goes wrong:

```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log

# Celery logs
tail -f logs/celery_worker.log

# MongoDB logs (if started manually)
tail -f logs/mongodb.log
```

---

## Support

For issues:
1. Run `./setup.sh` to validate environment
2. Check logs in `logs/` directory
3. Verify all directories exist
4. Ensure Redis and MongoDB are running
5. Check firewall/port availability

---

## Summary: Critical Steps for Any Environment

1. ✅ **Create directories:** `chroma_db/`, `backend/knowledge_base/internal/`, `backend/knowledge_base/external/`, `logs/`
2. ✅ **Install Redis:** Required for Celery
3. ✅ **Install MongoDB:** Recommended
4. ✅ **Install Python dependencies:** `pip install -r backend/requirements.txt`
5. ✅ **Install frontend dependencies:** `cd frontend && yarn install`
6. ✅ **Start services:** Use `./run.sh` or start manually
7. ✅ **Verify:** Check health endpoints and logs

**The most common issue is missing `chroma_db/` directory - always create it first!**
