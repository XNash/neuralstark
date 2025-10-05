# NeuralStark Shell Scripts Documentation

## Overview
This document describes the shell scripts available for managing the NeuralStark application services. All scripts have been updated (Version 3.0) to work seamlessly with the Kubernetes + Supervisor environment.

## Available Scripts

### 1. `run.sh` - Quick Start Script
**Purpose:** Fast, simple way to start all services with minimal output.

**What it does:**
- Creates required directories
- Starts Redis (if not running)
- Starts Celery worker
- Restarts backend and frontend via supervisor
- Shows service status summary

**Usage:**
```bash
./run.sh
```

**Best for:** Quick development restarts and everyday use.

---

### 2. `start_services.sh` - Comprehensive Start Script
**Purpose:** Detailed startup with health checks and verbose output.

**What it does:**
- Creates all required directories
- Installs and starts Redis (if needed)
- Verifies MongoDB connection
- Starts Celery worker with monitoring
- Restarts supervisor services (backend, frontend)
- Performs health checks on all services
- Provides detailed status summary and access points

**Usage:**
```bash
./start_services.sh
```

**Best for:** First-time setup, troubleshooting, or when you want detailed feedback.

---

### 3. `stop.sh` - Quick Stop Script
**Purpose:** Fast way to stop Celery worker (main non-supervisor service).

**What it does:**
- Stops Celery worker
- Cleans up PID files
- Provides info about supervisor-managed services

**Usage:**
```bash
./stop.sh
```

**Best for:** Quick cleanup of Celery between restarts.

---

### 4. `stop_services.sh` - Interactive Stop Script
**Purpose:** Comprehensive shutdown with user prompts.

**What it does:**
- Stops Celery worker
- Prompts to stop supervisor services (backend, frontend)
- Prompts to stop Redis
- Shows final status of all services

**Usage:**
```bash
./stop_services.sh
```

**Best for:** Complete shutdown or when you want control over what stops.

---

### 5. `scripts/start_celery.sh` - Celery-Only Script
**Purpose:** Start only the Celery worker service.

**What it does:**
- Stops existing Celery workers
- Starts new Celery worker with optimized settings

**Usage:**
```bash
./scripts/start_celery.sh
```

**Best for:** Restarting just the Celery worker without affecting other services.

---

## Service Architecture

### Supervisor-Managed Services
These services are automatically managed by supervisor and will auto-restart if they crash:
- **Backend** (FastAPI on port 8001)
- **Frontend** (React + Vite on port 3000)
- **MongoDB** (on port 27017)

**Control commands:**
```bash
sudo supervisorctl status              # Check status
sudo supervisorctl restart backend     # Restart backend
sudo supervisorctl restart frontend    # Restart frontend
sudo supervisorctl restart all         # Restart all
sudo supervisorctl stop backend        # Stop backend
```

### Manually-Managed Services
These services are started by the shell scripts:
- **Redis** (on port 6379) - Message broker for Celery
- **Celery Worker** - Background task processor

---

## Service Ports

| Service   | Port  | URL                          |
|-----------|-------|------------------------------|
| Frontend  | 3000  | http://localhost:3000        |
| Backend   | 8001  | http://localhost:8001        |
| API Docs  | 8001  | http://localhost:8001/docs   |
| MongoDB   | 27017 | mongodb://localhost:27017    |
| Redis     | 6379  | redis://localhost:6379       |

---

## Log Files

### Supervisor Logs
- Backend: `/var/log/supervisor/backend.err.log`
- Backend output: `/var/log/supervisor/backend.out.log`
- Frontend: `/var/log/supervisor/frontend.err.log`
- Frontend output: `/var/log/supervisor/frontend.out.log`
- MongoDB: `/var/log/mongodb.err.log`

### Manual Service Logs
- Celery Worker: `/var/log/celery_worker.log`

### View logs:
```bash
# Backend logs
tail -f /var/log/supervisor/backend.err.log

# Frontend logs
tail -f /var/log/supervisor/frontend.err.log

# Celery logs
tail -f /var/log/celery_worker.log

# All backend logs together
tail -f /var/log/supervisor/backend.*.log
```

---

## Common Workflows

### Starting the Application (First Time)
```bash
./start_services.sh
```

### Daily Development Start
```bash
./run.sh
```

### Restart After Code Changes
Backend has hot-reload, but if you need to restart:
```bash
sudo supervisorctl restart backend
```

Frontend also has hot-reload via Vite HMR.

### Restart Celery After Changes
```bash
pkill -f "celery.*worker"
./scripts/start_celery.sh
```

### Check Service Status
```bash
sudo supervisorctl status
pgrep -f "celery.*worker" && echo "Celery running" || echo "Celery not running"
redis-cli ping
```

### Stop Everything
```bash
./stop_services.sh
# Follow the interactive prompts
```

### Emergency Stop (Force)
```bash
pkill -9 -f "celery.*worker"
sudo supervisorctl stop all
redis-cli shutdown
```

---

## Troubleshooting

### Service Won't Start
1. Check the logs: `tail -50 /var/log/supervisor/[service].err.log`
2. Check supervisor status: `sudo supervisorctl status`
3. Restart services: `sudo supervisorctl restart all`

### Celery Issues
1. Check Redis is running: `redis-cli ping` (should return "PONG")
2. Check Celery logs: `tail -50 /var/log/celery_worker.log`
3. Restart Celery: `pkill -f celery && ./scripts/start_celery.sh`

### Port Already in Use
```bash
# Find process using port 8001
lsof -i:8001
# Kill it
fuser -k 8001/tcp
```

### Dependencies Missing
```bash
cd /app/backend
/root/.venv/bin/pip install -r requirements.txt
```

---

## Key Features of Updated Scripts

✅ **Supervisor Compatible** - Work with Kubernetes supervisor setup  
✅ **Color-Coded Output** - Easy to read status messages  
✅ **Health Checks** - Verify services are actually working  
✅ **Error Handling** - Clear error messages with helpful hints  
✅ **Idempotent** - Safe to run multiple times  
✅ **Non-Destructive** - Don't interfere with supervisor services  

---

## Environment Variables

The scripts respect existing environment variables and don't modify `.env` files. Key variables:
- `PYTHONPATH` - Set to `/app` for Python module resolution
- Backend URL and ports are configured in supervisor

---

## Version History

**Version 3.0** (January 2025)
- Complete rewrite for Kubernetes + Supervisor compatibility
- Removed manual uvicorn/vite management
- Added comprehensive health checks
- Improved error handling and user feedback
- Added interactive stop script

**Version 2.0** (October 2024)
- Added robust error handling
- Improved service verification

**Version 1.0** (Initial)
- Basic service management
- Manual process control

---

## Support

If you encounter issues:
1. Check the logs in `/var/log/`
2. Verify supervisor status: `sudo supervisorctl status`
3. Ensure Redis is running: `redis-cli ping`
4. Check if ports are available: `lsof -i:8001` and `lsof -i:3000`

For persistent issues, check the main application README.md for more information.
