# NeuralStark - Portable Deployment Guide

This document ensures NeuralStark works in **any environment** without manual intervention.

---

## 🎯 Goal

Make NeuralStark deployable in any environment (local, Docker, Kubernetes, VMs, cloud) with:
- ✅ Automated directory creation
- ✅ Automatic dependency installation
- ✅ Built-in error handling
- ✅ Environment validation
- ✅ Self-healing capabilities

---

## 🔧 Changes Made for Portability

### 1. Automated Directory Creation

#### In `run.sh` (Line 43)
```bash
mkdir -p backend/knowledge_base/internal backend/knowledge_base/external chroma_db logs 2>/dev/null
```
**Effect:** Automatically creates all required directories on every startup

#### In `backend/main.py` (Startup Lifespan)
```python
# Ensure required directories exist
os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
os.makedirs(settings.INTERNAL_KNOWLEDGE_BASE_PATH, exist_ok=True)
os.makedirs(settings.EXTERNAL_KNOWLEDGE_BASE_PATH, exist_ok=True)
```
**Effect:** Backend creates directories even if startup scripts weren't used

#### In `backend/celery_app.py` (Line 67)
```python
# Ensure the ChromaDB directory exists on startup
os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
```
**Effect:** Celery worker creates ChromaDB directory before processing documents

---

### 2. New Setup Validation Script

**File:** `setup.sh`

**Purpose:** Pre-flight validation before deployment

**What it checks:**
- ✅ Creates required directories
- ✅ Validates Python 3.8+ installation
- ✅ Validates Node.js 16+ installation
- ✅ Checks Redis availability
- ✅ Checks MongoDB availability
- ✅ Verifies Python dependencies
- ✅ Verifies frontend dependencies
- ✅ Validates directory permissions
- ✅ Checks system resources

**Usage:**
```bash
./setup.sh
```

---

### 3. Comprehensive Documentation

| Document | Purpose |
|----------|---------|
| `INSTALLATION_GUIDE.md` | Step-by-step installation for any environment |
| `DEPLOYMENT_CHECKLIST.md` | Verification checklist for deployments |
| `PORTABLE_DEPLOYMENT.md` | This file - portability guide |
| `FIXES_APPLIED.md` | Record of fixes applied to resolve issues |

---

## 📦 What's Automated

### Directory Creation
- **When:** Every time `run.sh` is executed
- **Where:** Project root level
- **Directories:**
  - `backend/knowledge_base/internal/`
  - `backend/knowledge_base/external/`
  - `chroma_db/`
  - `logs/`

### Dependency Installation (via run.sh)
- **Python packages:** Auto-installed from `requirements.txt`
- **Frontend packages:** Auto-installed via yarn
- **Redis:** Auto-installation attempted on Ubuntu/Debian/macOS
- **MongoDB:** Auto-installation attempted on Ubuntu/Debian/macOS

### Service Management (via run.sh)
- **Redis:** Auto-starts if installed
- **MongoDB:** Auto-starts if installed
- **Celery:** Auto-starts with optimal settings
- **Backend:** Auto-starts with uvicorn
- **Frontend:** Auto-starts with vite

---

## 🚀 Deployment in Different Environments

### Local Development (Linux/macOS)

```bash
# 1. Clone repository
git clone <repository-url>
cd neuralstark

# 2. Run setup
./setup.sh

# 3. Start services
./run.sh

# ✅ Done! All directories created automatically
```

---

### Docker Container

**Dockerfile example:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    redis-server \
    mongodb \
    nodejs \
    npm

# Copy application
COPY . /app

# Install dependencies
RUN pip install -r backend/requirements.txt
RUN cd frontend && npm install -g yarn && yarn install

# Directories will be created automatically by the application
# But you can also create them in Dockerfile:
RUN mkdir -p chroma_db logs backend/knowledge_base/internal backend/knowledge_base/external

# Start services
CMD ["./run.sh"]
```

**docker-compose.yml example:**
```yaml
version: '3.8'

services:
  redis:
    image: redis:latest
    ports:
      - "6379:6379"
  
  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
  
  neuralstark:
    build: .
    ports:
      - "3000:3000"
      - "8001:8001"
    volumes:
      - ./chroma_db:/app/chroma_db
      - ./logs:/app/logs
      - ./backend/knowledge_base:/app/backend/knowledge_base
    depends_on:
      - redis
      - mongodb
    environment:
      - REDIS_HOST=redis
      - MONGO_URL=mongodb://mongodb:27017

volumes:
  mongodb_data:
```

---

### Kubernetes Deployment

**Key considerations:**
1. Use PersistentVolumes for data directories
2. Configure environment variables via ConfigMap
3. Ensure init containers create directories if needed

**Example PersistentVolume:**
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: neuralstark-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

**Example Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: neuralstark
spec:
  replicas: 1
  selector:
    matchLabels:
      app: neuralstark
  template:
    metadata:
      labels:
        app: neuralstark
    spec:
      # Init container to ensure directories exist
      initContainers:
      - name: init-dirs
        image: busybox
        command: ['sh', '-c', 'mkdir -p /app/chroma_db /app/logs /app/backend/knowledge_base/internal /app/backend/knowledge_base/external']
        volumeMounts:
        - name: data
          mountPath: /app
      
      containers:
      - name: backend
        image: neuralstark:latest
        ports:
        - containerPort: 8001
        - containerPort: 3000
        volumeMounts:
        - name: data
          mountPath: /app/chroma_db
          subPath: chroma_db
        - name: data
          mountPath: /app/logs
          subPath: logs
        - name: data
          mountPath: /app/backend/knowledge_base
          subPath: knowledge_base
        env:
        - name: REDIS_HOST
          value: "redis-service"
        - name: MONGO_URL
          value: "mongodb://mongodb-service:27017"
      
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: neuralstark-data
```

---

### Cloud VM (AWS EC2, Google Compute, Azure VM)

```bash
# 1. SSH into VM
ssh user@vm-ip

# 2. Install prerequisites (if not already installed)
sudo apt-get update
sudo apt-get install -y python3 python3-pip nodejs npm git

# 3. Clone repository
git clone <repository-url>
cd neuralstark

# 4. Run setup and start
./setup.sh
./run.sh

# ✅ Directories created automatically!
```

---

### Shared/Multi-User Server

```bash
# Use virtual environment to avoid conflicts
cd neuralstark

# Setup will use local .venv
./setup.sh

# Run will auto-detect .venv
./run.sh
```

---

## 🔍 Critical Files for Portability

### Must-Have Scripts

1. **`run.sh`** - Universal startup script
   - Creates directories automatically
   - Installs dependencies
   - Starts all services
   
2. **`setup.sh`** - Validation script
   - Verifies environment
   - Creates directories
   - Checks dependencies

3. **`stop.sh`** - Universal shutdown script
   - Stops all services cleanly

### Must-Have Code

1. **`backend/main.py`** - FastAPI app
   - Creates directories on startup (lines 342-344)
   
2. **`backend/celery_app.py`** - Celery worker
   - Creates ChromaDB directory (line 67)
   
3. **`backend/config.py`** - Configuration
   - Environment variable fallbacks
   - Sensible defaults

---

## ✅ Portability Checklist

### Before Deploying to New Environment:

- [ ] `run.sh` has directory creation (line 43)
- [ ] `backend/main.py` has directory creation in lifespan
- [ ] `backend/celery_app.py` has directory creation (line 67)
- [ ] `setup.sh` exists and is executable
- [ ] `INSTALLATION_GUIDE.md` exists
- [ ] `DEPLOYMENT_CHECKLIST.md` exists
- [ ] All dependencies in `backend/requirements.txt`
- [ ] All dependencies in `frontend/package.json`

### After Deploying:

- [ ] Run `./setup.sh` - should pass all checks
- [ ] Run `./run.sh` - should start without errors
- [ ] Check `curl http://localhost:8001/api/health` - should return OK
- [ ] Check `curl http://localhost:8001/api/documents` - should NOT show ChromaDB errors
- [ ] Check logs for any errors

---

## 🐛 Common Issues (Now Fixed)

### Issue 1: ChromaDB "Could not connect to tenant"
**Original Cause:** Missing `chroma_db/` directory

**Fix Applied:**
- ✅ `run.sh` creates directory on startup
- ✅ `backend/main.py` creates directory in lifespan
- ✅ `backend/celery_app.py` creates directory before use

**Result:** Directory always exists, error eliminated

---

### Issue 2: "Unable to open database file"
**Original Cause:** Missing directory or permission issues

**Fix Applied:**
- ✅ Automated directory creation with proper permissions
- ✅ setup.sh validates permissions
- ✅ Application creates directory with exist_ok=True

**Result:** Always works, even if manually deleted

---

### Issue 3: Redis/MongoDB Not Available
**Original Cause:** Services not installed or not running

**Fix Applied:**
- ✅ `run.sh` attempts auto-installation
- ✅ `setup.sh` detects and warns if missing
- ✅ Clear instructions in INSTALLATION_GUIDE.md

**Result:** User gets clear guidance on what's needed

---

## 📊 Testing Portability

### Test in Fresh Environment

```bash
# 1. Start with clean slate
docker run -it ubuntu:22.04 bash

# 2. Install only git
apt-get update && apt-get install -y git

# 3. Clone and setup
git clone <repository-url>
cd neuralstark
chmod +x setup.sh run.sh
./setup.sh

# 4. Follow any warnings from setup.sh
# Install Redis, MongoDB, etc. as instructed

# 5. Start application
./run.sh

# 6. Verify
curl http://localhost:8001/api/health
curl http://localhost:8001/api/documents
```

---

## 🎓 Best Practices for Maintainers

### When Adding New Features:

1. **Never hardcode paths** - use settings from `config.py`
2. **Always use `os.makedirs(..., exist_ok=True)`** for directories
3. **Add directory creation to `run.sh`** if new directories needed
4. **Update `setup.sh`** to validate new requirements
5. **Document in `INSTALLATION_GUIDE.md`**

### When Modifying Startup:

1. **Test in fresh environment** (Docker container recommended)
2. **Ensure directories created before services start**
3. **Update documentation** if steps change

### When Changing Dependencies:

1. **Update `requirements.txt`** or `package.json`
2. **Update `setup.sh`** validation checks
3. **Document in `INSTALLATION_GUIDE.md`**

---

## 📝 Summary

NeuralStark is now fully portable and will work in any environment because:

1. ✅ **Automated directory creation** in 3 places (run.sh, main.py, celery_app.py)
2. ✅ **Environment validation** via setup.sh
3. ✅ **Comprehensive documentation** for all deployment scenarios
4. ✅ **Self-healing** - services create directories if missing
5. ✅ **Clear error messages** - users know what's wrong
6. ✅ **Dependency automation** - run.sh handles installation

**Result:** Clone → Setup → Run → Works! 🎉

---

## 🔗 Related Documents

- [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) - Complete installation guide
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Pre/post deployment checks
- [FIXES_APPLIED.md](FIXES_APPLIED.md) - Record of fixes
- [README.md](README.md) - Main documentation

---

**Last Updated:** October 5, 2025  
**Version:** 4.2 (Portable Edition)
