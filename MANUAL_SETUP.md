# NeuralStark - Manual Setup Guide

This guide provides detailed step-by-step instructions for manually starting all NeuralStark services without using automated scripts.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Dependencies](#system-dependencies)
3. [Project Dependencies](#project-dependencies)
4. [Directory Setup](#directory-setup)
5. [Starting Services](#starting-services)
6. [Verification](#verification)
7. [Stopping Services](#stopping-services)
8. [Troubleshooting](#troubleshooting)
9. [Service Management](#service-management)

---

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.9+ | Backend runtime |
| Node.js | 18+ | Frontend development |
| Redis | Latest | Message broker for Celery |
| MongoDB | 4.0+ | Document database |
| Yarn | 1.22+ | Frontend package manager |

### Installation by Platform

#### Ubuntu/Debian Linux

```bash
# Update package list
sudo apt-get update

# Install Python 3.9+
sudo apt-get install -y python3 python3-pip python3-venv

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Yarn
npm install -g yarn

# Install Redis
sudo apt-get install -y redis-server

# Install MongoDB
sudo apt-get install -y mongodb

# Verify installations
python3 --version
node --version
yarn --version
redis-server --version
mongod --version
```

#### macOS

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11

# Install Node.js
brew install node@18

# Install Yarn
npm install -g yarn

# Install Redis
brew install redis

# Install MongoDB
brew tap mongodb/brew
brew install mongodb-community

# Verify installations
python3 --version
node --version
yarn --version
redis-server --version
mongod --version
```

#### Windows

1. **Python**: Download from [python.org](https://www.python.org/downloads/)
2. **Node.js**: Download from [nodejs.org](https://nodejs.org/)
3. **Yarn**: Run `npm install -g yarn` in CMD/PowerShell
4. **Redis**: Download from [GitHub releases](https://github.com/microsoftarchive/redis/releases)
5. **MongoDB**: Download from [mongodb.com](https://www.mongodb.com/try/download/community)

---

## System Dependencies

Install system-level dependencies for OCR and document processing:

### Linux (Ubuntu/Debian)

```bash
sudo apt-get install -y \
  tesseract-ocr \
  tesseract-ocr-eng \
  tesseract-ocr-fra \
  poppler-utils \
  libreoffice \
  libreoffice-writer \
  libreoffice-calc
```

### macOS

```bash
brew install tesseract
brew install poppler
brew install --cask libreoffice
```

### Windows

- **Tesseract**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
- **Poppler**: Download from [poppler releases](https://github.com/oschwartz10612/poppler-windows/releases/)
- **LibreOffice**: Download from [libreoffice.org](https://www.libreoffice.org/download/)

---

## Project Dependencies

### Backend (Python)

```bash
# Navigate to backend directory
cd /app/backend

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python3 -c "import fastapi, uvicorn, celery, redis, langchain, chromadb" && echo "✓ All dependencies installed"
```

### Frontend (Node.js)

```bash
# Navigate to frontend directory
cd /app/frontend

# Install dependencies
yarn install

# Verify installation
yarn --version
```

---

## Directory Setup

Create required directories for the application:

```bash
# Navigate to project root
cd /app

# Create knowledge base directories
mkdir -p backend/knowledge_base/internal
mkdir -p backend/knowledge_base/external

# Create vector database directory
mkdir -p chroma_db

# Create log directory (if not exists)
sudo mkdir -p /var/log

# Set permissions (Linux/macOS)
chmod 755 backend/knowledge_base/internal
chmod 755 backend/knowledge_base/external
chmod 755 chroma_db

# Verify directory structure
ls -la backend/knowledge_base/
```

**Expected output:**
```
drwxr-xr-x internal/
drwxr-xr-x external/
```

---

## Starting Services

Start each service in the correct order:

### 1. Start Redis

Redis is required as a message broker for Celery.

```bash
# Start Redis in daemon mode
redis-server --daemonize yes

# Verify Redis is running
redis-cli ping
```

**Expected output:** `PONG`

**Alternative (foreground mode):**
```bash
# Start Redis in foreground (use separate terminal)
redis-server
```

### 2. Start MongoDB

MongoDB stores application data and document metadata.

```bash
# Start MongoDB
mongod --fork --logpath /var/log/mongodb.log --bind_ip_all

# Verify MongoDB is running
mongosh --eval "db.version()" --quiet
```

**Expected output:** Version number (e.g., `7.0.24`)

**Alternative (if mongod is already running):**
```bash
# Check if MongoDB is already running
pgrep -x mongod
```

### 3. Start Celery Worker

Celery processes background tasks like document parsing and OCR.

```bash
# Navigate to project root
cd /app

# Set Python path
export PYTHONPATH=/app:$PYTHONPATH

# Start Celery worker in background
nohup celery -A backend.celery_app worker \
  --loglevel=info \
  --concurrency=2 \
  --max-tasks-per-child=50 \
  > /var/log/celery_worker.log 2>&1 &

# Note the process ID
echo $!

# Wait a few seconds for startup
sleep 3

# Verify Celery is running
ps aux | grep "celery.*worker" | grep -v grep
```

**Expected output:** Should show 3 processes (1 main + 2 workers)

**Alternative (foreground mode):**
```bash
# Start Celery in foreground (use separate terminal)
cd /app
export PYTHONPATH=/app:$PYTHONPATH
celery -A backend.celery_app worker --loglevel=info --concurrency=2
```

### 4. Start Backend (FastAPI)

The backend API serves RESTful endpoints.

```bash
# Navigate to backend directory
cd /app/backend

# Start backend in background
nohup uvicorn server:app \
  --host 0.0.0.0 \
  --port 8001 \
  --reload \
  > /var/log/backend.log 2>&1 &

# Wait for backend to start
sleep 5

# Verify backend is running
curl http://localhost:8001/health
```

**Expected output:** `{"status":"ok"}`

**Alternative (foreground mode):**
```bash
# Start backend in foreground (use separate terminal)
cd /app/backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### 5. Start Frontend (React + Vite)

The frontend serves the web interface.

```bash
# Navigate to frontend directory
cd /app/frontend

# Start frontend in background
nohup yarn start > /var/log/frontend.log 2>&1 &

# Wait for frontend to start
sleep 8

# Verify frontend is running
curl -I http://localhost:3000
```

**Expected output:** `HTTP/1.1 200 OK`

**Alternative (foreground mode):**
```bash
# Start frontend in foreground (use separate terminal)
cd /app/frontend
yarn start
```

---

## Verification

Verify all services are running correctly:

### Quick Status Check

```bash
echo "=== NeuralStark Service Status ==="
echo ""
echo "1. Redis:"
redis-cli ping && echo "✓ Running" || echo "✗ Not running"
echo ""
echo "2. MongoDB:"
mongosh --eval "db.runCommand({ ping: 1 }).ok" --quiet && echo "✓ Running" || echo "✗ Not running"
echo ""
echo "3. Celery Workers:"
CELERY_COUNT=$(ps aux | grep "celery.*worker" | grep -v grep | wc -l)
echo "Workers: $CELERY_COUNT (expected: 3)"
echo ""
echo "4. Backend API:"
curl -s http://localhost:8001/health && echo " ✓ Running" || echo "✗ Not running"
echo ""
echo "5. Frontend:"
curl -s -I http://localhost:3000 | grep "HTTP" || echo "✗ Not running"
```

### Port Status Check

```bash
# Check all required ports
netstat -tlnp 2>/dev/null | grep -E ":(6379|27017|8001|3000)" || \
ss -tlnp | grep -E ":(6379|27017|8001|3000)"
```

**Expected output:**
```
tcp  0.0.0.0:6379   (redis)
tcp  0.0.0.0:27017  (mongod)
tcp  0.0.0.0:8001   (uvicorn)
tcp  0.0.0.0:3000   (vite)
```

### API Endpoint Tests

```bash
# Test root endpoint
curl http://localhost:8001/

# Test health endpoint
curl http://localhost:8001/health

# Test documents endpoint
curl http://localhost:8001/documents

# Test API documentation
curl -I http://localhost:8001/docs
```

### Frontend Access

Open your browser and navigate to:
- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8001/docs
- **Backend Health**: http://localhost:8001/health

---

## Stopping Services

Stop all services gracefully:

### Individual Services

```bash
# Stop Celery Worker
pkill -f "celery.*worker"
echo "✓ Celery stopped"

# Stop Backend
pkill -f "uvicorn.*server:app"
echo "✓ Backend stopped"

# Stop Frontend
pkill -f "vite"
echo "✓ Frontend stopped"

# Stop Redis (optional)
redis-cli shutdown
echo "✓ Redis stopped"

# Stop MongoDB (optional)
mongod --shutdown
echo "✓ MongoDB stopped"
```

### Stop All at Once

```bash
# Stop application services
pkill -f "celery.*worker"
pkill -f "uvicorn.*server:app"
pkill -f "vite"

# Optional: Stop databases
redis-cli shutdown
mongod --shutdown

echo "✓ All services stopped"
```

### Verify Services Stopped

```bash
ps aux | grep -E "celery|uvicorn|vite" | grep -v grep
# Should return empty
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Port Already in Use

**Problem:** Service won't start because port is already in use.

**Solution:**
```bash
# Find process using port 8001 (example)
lsof -i :8001  # Linux/macOS
netstat -ano | findstr :8001  # Windows

# Kill the process
kill -9 <PID>  # Linux/macOS
taskkill /PID <PID> /F  # Windows
```

#### 2. Redis Connection Error

**Problem:** Backend can't connect to Redis.

**Solution:**
```bash
# Check if Redis is running
redis-cli ping

# If not running, start Redis
redis-server --daemonize yes

# Check Redis logs
tail -f /var/log/redis/redis-server.log
```

#### 3. MongoDB Connection Error

**Problem:** Backend can't connect to MongoDB.

**Solution:**
```bash
# Check if MongoDB is running
pgrep mongod

# If not running, start MongoDB
mongod --fork --logpath /var/log/mongodb.log --bind_ip_all

# Check MongoDB logs
tail -f /var/log/mongodb.log
```

#### 4. Celery Worker Not Starting

**Problem:** Celery worker fails to start.

**Solution:**
```bash
# Check Celery logs
tail -50 /var/log/celery_worker.log

# Common fix: Ensure Redis is running
redis-cli ping

# Restart Celery
pkill -f "celery.*worker"
cd /app
export PYTHONPATH=/app:$PYTHONPATH
celery -A backend.celery_app worker --loglevel=info --concurrency=2
```

#### 5. Backend Startup Error (Knowledge Base)

**Problem:** Backend fails with "FileNotFoundError: No such file or directory"

**Solution:**
```bash
# Create missing directories
mkdir -p /app/backend/knowledge_base/internal
mkdir -p /app/backend/knowledge_base/external

# Restart backend
pkill -f "uvicorn.*server:app"
cd /app/backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

#### 6. Frontend Build Errors

**Problem:** Frontend fails to start or build.

**Solution:**
```bash
# Clear node modules and reinstall
cd /app/frontend
rm -rf node_modules yarn.lock
yarn install

# Start frontend
yarn start
```

#### 7. CORS Errors

**Problem:** Frontend can't communicate with backend.

**Solution:**
```bash
# Verify backend CORS settings
grep -A 10 "CORSMiddleware" /app/backend/main.py

# Restart backend
pkill -f "uvicorn.*server:app"
cd /app/backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

#### 8. OCR Not Working

**Problem:** Document text extraction fails.

**Solution:**
```bash
# Check if Tesseract is installed
tesseract --version

# Install Tesseract (Ubuntu/Debian)
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng

# Verify OCR languages
tesseract --list-langs
```

---

## Service Management

### View Logs

Monitor service logs in real-time:

```bash
# Backend logs
tail -f /var/log/backend.log

# Frontend logs
tail -f /var/log/frontend.log

# Celery logs
tail -f /var/log/celery_worker.log

# MongoDB logs
tail -f /var/log/mongodb.log

# Redis logs
tail -f /var/log/redis/redis-server.log

# View all logs simultaneously (requires multitail)
multitail /var/log/backend.log /var/log/frontend.log /var/log/celery_worker.log
```

### Check Service Status

```bash
# Redis
redis-cli ping

# MongoDB
mongosh --eval "db.runCommand({ ping: 1 })"

# Celery
ps aux | grep celery | grep -v grep

# Backend
curl http://localhost:8001/health

# Frontend
curl -I http://localhost:3000

# All services
ps aux | grep -E "redis|mongo|celery|uvicorn|vite" | grep -v grep
```

### Restart Services

```bash
# Restart Backend
pkill -f "uvicorn.*server:app"
cd /app/backend
nohup uvicorn server:app --host 0.0.0.0 --port 8001 --reload > /var/log/backend.log 2>&1 &

# Restart Frontend
pkill -f "vite"
cd /app/frontend
nohup yarn start > /var/log/frontend.log 2>&1 &

# Restart Celery
pkill -f "celery.*worker"
cd /app
export PYTHONPATH=/app:$PYTHONPATH
nohup celery -A backend.celery_app worker --loglevel=info --concurrency=2 > /var/log/celery_worker.log 2>&1 &
```

---

## Environment Variables

### Backend Configuration

Create `/app/backend/.env` (optional):

```bash
# LLM Settings
LLM_API_KEY=your_gemini_api_key
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

# MongoDB Settings
MONGO_URL=mongodb://localhost:27017

# Paths
INTERNAL_KNOWLEDGE_BASE_PATH=/app/backend/knowledge_base/internal
EXTERNAL_KNOWLEDGE_BASE_PATH=/app/backend/knowledge_base/external
CHROMA_DB_PATH=/app/chroma_db
```

### Frontend Configuration

Frontend uses environment variables from Vite config. No `.env` file needed for basic setup.

---

## Performance Tips

1. **Resource Optimization**:
   - Reduce Celery concurrency if low on memory: `--concurrency=1`
   - Adjust embedding batch size in backend config

2. **Production Settings**:
   - Remove `--reload` flag from uvicorn for production
   - Use `yarn build` instead of `yarn start` for production frontend

3. **Monitoring**:
   - Set up log rotation for `/var/log/*.log` files
   - Use `htop` or `top` to monitor resource usage

---

## Additional Resources

- **Main README**: [README.md](README.md)
- **Automated Scripts**: [STARTUP_SCRIPTS_README.md](STARTUP_SCRIPTS_README.md)
- **Running Guide**: [RUNNING_THE_APP.md](RUNNING_THE_APP.md)
- **API Documentation**: http://localhost:8001/docs (after starting backend)

---

## Quick Reference Card

### Start All Services

```bash
# 1. Start databases
redis-server --daemonize yes
mongod --fork --logpath /var/log/mongodb.log --bind_ip_all

# 2. Start application services
cd /app && export PYTHONPATH=/app:$PYTHONPATH
nohup celery -A backend.celery_app worker --loglevel=info --concurrency=2 > /var/log/celery_worker.log 2>&1 &
cd /app/backend && nohup uvicorn server:app --host 0.0.0.0 --port 8001 --reload > /var/log/backend.log 2>&1 &
cd /app/frontend && nohup yarn start > /var/log/frontend.log 2>&1 &
```

### Stop All Services

```bash
pkill -f "celery.*worker"
pkill -f "uvicorn.*server:app"
pkill -f "vite"
redis-cli shutdown
mongod --shutdown
```

### Check Status

```bash
redis-cli ping && curl http://localhost:8001/health && curl -I http://localhost:3000
```

---

**Happy building with NeuralStark! 🚀**

For questions or issues, refer to the [Troubleshooting](#troubleshooting) section or check the application logs.
