# Optimized Scripts Quick Guide

## Overview
Streamlined `run.sh` and `stop.sh` scripts for NeuralStark application management.

---

## 🚀 run.sh - Start Everything

### What it does:
1. ✅ Creates required directories
2. ✅ Starts Redis (installs if needed)
3. ✅ Starts Celery worker
4. ✅ Restarts backend and frontend via supervisor
5. ✅ Checks all service status with health verification

### Usage:
```bash
./run.sh
```

### Output:
- Color-coded status for each service
- Port information for all services
- Direct links to frontend, backend, and API docs
- Log file locations for troubleshooting

### Execution Time: ~15 seconds

---

## 🛑 stop.sh - Stop Services

### What it does:
1. ✅ Stops Celery worker (gracefully, then force if needed)
2. ✅ Cleans up PID files
3. ℹ️  Provides instructions for stopping supervisor services
4. ℹ️  Shows how to stop Redis if needed

### Usage:
```bash
./stop.sh
```

### Output:
- Confirmation of Celery shutdown
- Instructions for stopping other services
- Command examples for supervisor and Redis

### Execution Time: ~3 seconds

---

## Service Architecture

### Script-Managed (by run.sh/stop.sh):
- **Redis** - Port 6379 (message broker)
- **Celery** - Background task processor

### Supervisor-Managed (auto-restart):
- **Backend** - Port 8001 (FastAPI)
- **Frontend** - Port 3000 (React + Vite)
- **MongoDB** - Port 27017 (database)

---

## Quick Commands

### Start application
```bash
./run.sh
```

### Stop Celery only
```bash
./stop.sh
```

### Restart backend
```bash
sudo supervisorctl restart backend
```

### Restart frontend
```bash
sudo supervisorctl restart frontend
```

### Check all services
```bash
sudo supervisorctl status
```

### View logs
```bash
# Backend
tail -f /var/log/supervisor/backend.err.log

# Frontend
tail -f /var/log/supervisor/frontend.err.log

# Celery
tail -f /var/log/celery_worker.log
```

---

## Features

✅ **Fast** - Optimized for quick startup and shutdown  
✅ **Clear** - Color-coded output with emojis  
✅ **Smart** - Automatic Redis installation if needed  
✅ **Safe** - Graceful shutdown with force-kill fallback  
✅ **Informative** - Health checks and detailed status  
✅ **Helpful** - Includes all URLs and log locations  

---

## Access Points

After running `./run.sh`:

- 🌐 **Frontend**: http://localhost:3000
- 🔌 **Backend**: http://localhost:8001
- 📚 **API Docs**: http://localhost:8001/docs

---

## Troubleshooting

### Services won't start
```bash
# Check logs
tail -50 /var/log/supervisor/backend.err.log
tail -50 /var/log/celery_worker.log

# Restart supervisor services
sudo supervisorctl restart all
```

### Celery issues
```bash
# Check Redis
redis-cli ping

# Check Celery logs
tail -50 /var/log/celery_worker.log

# Restart Celery
./stop.sh && ./run.sh
```

### Port conflicts
```bash
# Check what's using a port
lsof -i:8001
lsof -i:3000

# Kill process on port
fuser -k 8001/tcp
```

---

## File Sizes
- `run.sh`: 4.7 KB
- `stop.sh`: 1.9 KB

Both scripts are executable and ready to use!
