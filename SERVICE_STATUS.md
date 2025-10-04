# NeuralStark - Current Service Status

**Last Updated:** $(date)
**Status:** ✅ All services running successfully

---

## Service Overview

| Service | Status | Port | Command to Check |
|---------|--------|------|------------------|
| Redis | ✅ Running | 6379 | `redis-cli ping` |
| MongoDB | ✅ Running | 27017 | `mongosh --eval "db.version()"` |
| Celery Worker | ✅ Running | N/A | `ps aux \| grep celery` |
| Backend API | ✅ Running | 8001 | `curl http://localhost:8001/health` |
| Frontend | ✅ Running | 3000 | `curl -I http://localhost:3000` |

---

## Access Points

- **Frontend Application**: http://localhost:3000
- **Backend API Documentation**: http://localhost:8001/docs
- **Backend Health Check**: http://localhost:8001/health
- **API Root**: http://localhost:8001/

---

## Verification Results

### 1. Redis Status
```
$ redis-cli ping
PONG
```
✅ **Status:** Healthy

### 2. MongoDB Status
```
$ mongosh --eval "db.version()" --quiet
7.0.24
```
✅ **Status:** Healthy

### 3. Celery Workers
```
$ ps aux | grep celery | grep -v grep | wc -l
3
```
✅ **Status:** 3 worker processes running (1 main + 2 workers)

### 4. Backend API
```
$ curl http://localhost:8001/health
{"status":"ok"}
```
✅ **Status:** Healthy

### 5. Frontend
```
$ curl -I http://localhost:3000
HTTP/1.1 200 OK
```
✅ **Status:** Healthy

---

## API Endpoints Tested

### Root Endpoint
```bash
$ curl http://localhost:8001/
{"message":"Welcome to NeuralStark API!"}
```
✅ **Working**

### Health Endpoint
```bash
$ curl http://localhost:8001/health
{"status":"ok"}
```
✅ **Working**

### Documents Endpoint
```bash
$ curl http://localhost:8001/documents
{"indexed_documents":[]}
```
✅ **Working**

---

## Log Locations

- Backend: `/var/log/backend.log`
- Frontend: `/var/log/frontend.log`
- Celery: `/var/log/celery_worker.log`
- MongoDB: `/var/log/mongodb.log`

---

## Quick Commands

### Check All Services
```bash
redis-cli ping && \
curl -s http://localhost:8001/health && \
curl -s -I http://localhost:3000 | grep HTTP && \
echo "✓ All services running!"
```

### View Logs
```bash
# Backend
tail -f /var/log/backend.log

# Frontend
tail -f /var/log/frontend.log

# Celery
tail -f /var/log/celery_worker.log
```

### Restart Services
```bash
# Backend
pkill -f "uvicorn.*server:app"
cd /app/backend && nohup uvicorn server:app --host 0.0.0.0 --port 8001 --reload > /var/log/backend.log 2>&1 &

# Frontend
pkill -f "vite"
cd /app/frontend && nohup yarn start > /var/log/frontend.log 2>&1 &

# Celery
pkill -f "celery.*worker"
cd /app && export PYTHONPATH=/app:$PYTHONPATH && \
nohup celery -A backend.celery_app worker --loglevel=info --concurrency=2 > /var/log/celery_worker.log 2>&1 &
```

---

## Setup Documentation

For manual setup instructions:
- **Quick Start**: [QUICK_START_MANUAL.md](QUICK_START_MANUAL.md)
- **Detailed Guide**: [MANUAL_SETUP.md](MANUAL_SETUP.md)
- **Main README**: [README.md](README.md)

---

**All services are operational and ready for use! 🚀**
