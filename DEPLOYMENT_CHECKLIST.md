# NeuralStark - Deployment Checklist

Use this checklist to ensure NeuralStark is properly configured in any environment.

---

## Pre-Deployment Checklist

### ✅ System Prerequisites

- [ ] **Python 3.8+** installed and accessible
  ```bash
  python3 --version  # Should show 3.8 or higher
  ```

- [ ] **Node.js 16+** installed and accessible
  ```bash
  node --version  # Should show v16 or higher
  ```

- [ ] **pip** (Python package manager) available
  ```bash
  pip --version  # or pip3 --version
  ```

- [ ] **yarn** or **npm** (Node package manager) available
  ```bash
  yarn --version  # or npm --version
  ```

---

### ✅ Required Services

- [ ] **Redis** installed and running (required for Celery)
  ```bash
  # Install if missing
  sudo apt-get install redis-server  # Ubuntu/Debian
  brew install redis                  # macOS
  
  # Start Redis
  redis-server --daemonize yes
  
  # Verify
  redis-cli ping  # Should return "PONG"
  ```

- [ ] **MongoDB** installed and running (recommended)
  ```bash
  # Install if missing
  sudo apt-get install mongodb        # Ubuntu/Debian
  brew install mongodb-community      # macOS
  
  # Start MongoDB
  mongod --fork --logpath /tmp/mongodb.log --bind_ip_all
  
  # Verify
  mongosh --eval "db.version()"  # Should show version
  ```

---

### ✅ Required Directories

**CRITICAL:** These directories must exist before starting the application.

- [ ] `chroma_db/` directory exists
  ```bash
  mkdir -p chroma_db
  ls -ld chroma_db/  # Should show directory with write permissions
  ```

- [ ] `backend/knowledge_base/internal/` directory exists
  ```bash
  mkdir -p backend/knowledge_base/internal
  ```

- [ ] `backend/knowledge_base/external/` directory exists
  ```bash
  mkdir -p backend/knowledge_base/external
  ```

- [ ] `logs/` directory exists
  ```bash
  mkdir -p logs
  ```

**⚠️ WARNING:** Missing `chroma_db/` will cause:
```
ERROR: Could not connect to tenant default_tenant
ERROR: unable to open database file
```

---

### ✅ Directory Permissions

- [ ] All directories are writable
  ```bash
  chmod 755 chroma_db
  chmod 755 logs
  chmod -R 755 backend/knowledge_base
  ```

- [ ] Script files are executable
  ```bash
  chmod +x run.sh stop.sh setup.sh
  ```

---

### ✅ Python Dependencies

- [ ] `requirements.txt` exists in `backend/` directory
  ```bash
  ls -l backend/requirements.txt
  ```

- [ ] Python dependencies installed
  ```bash
  pip install -r backend/requirements.txt
  ```

- [ ] Key packages can be imported
  ```bash
  python3 -c "import fastapi"      # Should exit without error
  python3 -c "import chromadb"     # Should exit without error
  python3 -c "import langchain"    # Should exit without error
  python3 -c "import celery"       # Should exit without error
  python3 -c "import redis"        # Should exit without error
  ```

---

### ✅ Frontend Dependencies

- [ ] `package.json` exists in `frontend/` directory
  ```bash
  ls -l frontend/package.json
  ```

- [ ] Frontend dependencies installed
  ```bash
  cd frontend
  yarn install  # or npm install
  ```

- [ ] `node_modules/` directory exists
  ```bash
  ls -ld frontend/node_modules/
  ```

---

### ✅ Configuration Files

- [ ] `backend/config.py` exists
  ```bash
  ls -l backend/config.py
  ```

- [ ] Canvas templates exist (optional but recommended)
  ```bash
  ls -l backend/canvas_templates.json  # or canvas_templates.json
  ```

- [ ] Environment variables configured (optional)
  ```bash
  # Create .env in backend/ if needed
  # See INSTALLATION_GUIDE.md for template
  ```

---

## Deployment Steps

### Step 1: Run Setup Validation

- [ ] Run setup script
  ```bash
  ./setup.sh
  ```

- [ ] All checks pass (no critical errors)

---

### Step 2: Start Services

- [ ] Services started successfully
  ```bash
  ./run.sh
  ```

- [ ] No errors in startup output

- [ ] Wait 20-30 seconds for backend to load ML models

---

### Step 3: Verify Services

#### Redis
- [ ] Redis is running
  ```bash
  redis-cli ping
  # Expected: PONG
  ```

#### MongoDB
- [ ] MongoDB is running
  ```bash
  mongosh --eval "db.version()"
  # Expected: Version number
  # OR
  lsof -i:27017  # Should show mongod process
  ```

#### Celery Worker
- [ ] Celery worker is running
  ```bash
  ps aux | grep celery | grep -v grep
  # Expected: celery worker processes
  ```

#### Backend API
- [ ] Backend is running on port 8001
  ```bash
  lsof -i:8001  # Should show python/uvicorn process
  ```

- [ ] Health endpoint responds
  ```bash
  curl http://localhost:8001/api/health
  # Expected: {"status":"ok"}
  ```

- [ ] Documents endpoint works (ChromaDB test)
  ```bash
  curl http://localhost:8001/api/documents
  # Expected: {"indexed_documents":[]}
  # NOT: ChromaDB error messages
  ```

- [ ] Chat endpoint works
  ```bash
  curl -X POST http://localhost:8001/api/chat \
    -H "Content-Type: application/json" \
    -d '{"query":"Hello"}'
  # Expected: JSON response from AI
  ```

#### Frontend
- [ ] Frontend is running on port 3000
  ```bash
  lsof -i:3000  # Should show node/vite process
  ```

- [ ] Frontend responds to HTTP requests
  ```bash
  curl -I http://localhost:3000
  # Expected: HTTP/1.1 200 OK
  ```

---

### Step 4: Access Application

- [ ] Frontend accessible in browser
  ```
  Open: http://localhost:3000
  ```

- [ ] Backend API docs accessible
  ```
  Open: http://localhost:8001/docs
  ```

- [ ] Can interact with chat interface (if testing manually)

---

## Post-Deployment Verification

### ✅ Log Files Check

- [ ] Backend logs exist and show no errors
  ```bash
  tail -20 logs/backend.log
  # OR
  tail -20 /var/log/supervisor/backend.out.log
  ```

- [ ] Frontend logs exist
  ```bash
  tail -20 logs/frontend.log
  ```

- [ ] Celery logs exist
  ```bash
  tail -20 logs/celery_worker.log
  ```

---

### ✅ Functional Tests

- [ ] Upload a test document
  ```bash
  # Create a test file
  echo "This is a test document" > backend/knowledge_base/internal/test.txt
  
  # Wait 5-10 seconds for processing
  
  # Check if indexed
  curl http://localhost:8001/api/documents
  # Should include test.txt in the list
  ```

- [ ] Query the knowledge base
  ```bash
  curl -X POST http://localhost:8001/api/chat \
    -H "Content-Type: application/json" \
    -d '{"query":"What is in the test document?"}'
  # Should return relevant information
  ```

---

## Troubleshooting Checklist

### If Backend Fails to Start

- [ ] Port 8001 not already in use
  ```bash
  lsof -i:8001
  # If occupied: kill -9 <PID>
  ```

- [ ] Python dependencies installed
  ```bash
  pip list | grep fastapi
  pip list | grep chromadb
  ```

- [ ] `chroma_db/` directory exists
  ```bash
  ls -ld chroma_db/
  ```

- [ ] Check backend error logs
  ```bash
  tail -50 logs/backend.log
  # OR
  tail -50 /var/log/supervisor/backend.err.log
  ```

---

### If ChromaDB Errors Occur

- [ ] `chroma_db/` directory exists and is writable
  ```bash
  mkdir -p chroma_db
  chmod 755 chroma_db
  ```

- [ ] `backend/knowledge_base/internal/` exists
  ```bash
  mkdir -p backend/knowledge_base/internal
  ```

- [ ] `backend/knowledge_base/external/` exists
  ```bash
  mkdir -p backend/knowledge_base/external
  ```

- [ ] Restart backend after creating directories
  ```bash
  pkill -f "uvicorn.*server:app"
  cd backend && uvicorn server:app --host 0.0.0.0 --port 8001 &
  ```

---

### If Celery Worker Fails

- [ ] Redis is running
  ```bash
  redis-cli ping
  ```

- [ ] Redis connection settings correct in config
  ```bash
  grep REDIS backend/config.py
  ```

- [ ] PYTHONPATH is set
  ```bash
  export PYTHONPATH=$PWD:$PYTHONPATH
  ```

- [ ] Check celery logs
  ```bash
  tail -50 logs/celery_worker.log
  ```

---

### If Frontend Fails

- [ ] Port 3000 not already in use
  ```bash
  lsof -i:3000
  ```

- [ ] Node modules installed
  ```bash
  ls frontend/node_modules/
  ```

- [ ] Check frontend logs
  ```bash
  tail -50 logs/frontend.log
  ```

---

## Environment-Specific Notes

### Docker/Containers
- [ ] Volumes mounted for: `chroma_db/`, `backend/knowledge_base/`, `logs/`
- [ ] Redis and MongoDB accessible via network
- [ ] Ports 3000, 8001 exposed

### Kubernetes
- [ ] PersistentVolumes for data directories
- [ ] Services for Redis and MongoDB
- [ ] ConfigMaps for environment variables

### Shared/Multi-User Servers
- [ ] Using virtual environment (`.venv`)
- [ ] Not installing packages globally
- [ ] Custom ports if defaults occupied

---

## Final Verification

### All Systems Go ✅

If all items below are checked, deployment is successful:

- [ ] ✅ All required directories exist
- [ ] ✅ Redis running and responding
- [ ] ✅ MongoDB running (or skip if not needed)
- [ ] ✅ Celery worker running
- [ ] ✅ Backend healthy: `curl http://localhost:8001/api/health` → `{"status":"ok"}`
- [ ] ✅ Documents API works: `curl http://localhost:8001/api/documents` → No errors
- [ ] ✅ Frontend accessible: `http://localhost:3000` loads
- [ ] ✅ No errors in logs

**If any item is unchecked, review the troubleshooting section above or consult INSTALLATION_GUIDE.md**

---

## Quick Reference Commands

```bash
# Setup and validation
./setup.sh

# Start all services
./run.sh

# Stop all services
./stop.sh

# Check service status
ps aux | grep -E "(uvicorn|celery|vite|redis|mongod)" | grep -v grep

# Check logs
tail -f logs/backend.log
tail -f logs/frontend.log
tail -f logs/celery_worker.log

# Health checks
curl http://localhost:8001/api/health
curl http://localhost:8001/api/documents
curl -I http://localhost:3000
redis-cli ping
```

---

**Deployment Date:** _______________________

**Environment:** _______________________

**Deployed By:** _______________________

**Notes:** 
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
