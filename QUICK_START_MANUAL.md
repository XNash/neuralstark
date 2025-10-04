# NeuralStark - Quick Start (Manual Commands)

This is a quick reference for manually starting NeuralStark services. For detailed troubleshooting, see [MANUAL_SETUP.md](MANUAL_SETUP.md).

---

## Prerequisites

Ensure the following are installed:
- Python 3.9+
- Node.js 18+
- Redis
- MongoDB
- Yarn

---

## Quick Setup

### 1. Create Required Directories

```bash
cd /app
mkdir -p backend/knowledge_base/internal backend/knowledge_base/external chroma_db
```

### 2. Install Dependencies

```bash
# Backend
cd /app/backend
pip install -r requirements.txt

# Frontend
cd /app/frontend
yarn install
```

---

## Start Services (One Command at a Time)

Copy and paste each command in order:

```bash
# 1. Start Redis
redis-server --daemonize yes && redis-cli ping

# 2. Verify MongoDB is running (usually auto-starts)
mongosh --eval "db.version()" --quiet

# 3. Start Celery Worker
cd /app && export PYTHONPATH=/app:$PYTHONPATH && \
nohup celery -A backend.celery_app worker --loglevel=info --concurrency=2 --max-tasks-per-child=50 > /var/log/celery_worker.log 2>&1 &

# 4. Start Backend (wait 3 seconds)
cd /app/backend && \
nohup uvicorn server:app --host 0.0.0.0 --port 8001 --reload > /var/log/backend.log 2>&1 &

# 5. Wait and verify backend
sleep 5 && curl http://localhost:8001/health

# 6. Start Frontend
cd /app/frontend && \
nohup yarn start > /var/log/frontend.log 2>&1 &

# 7. Wait and verify frontend
sleep 8 && curl -I http://localhost:3000
```

---

## Verify All Services

```bash
# Quick check all services
redis-cli ping && \
curl -s http://localhost:8001/health && \
curl -s -I http://localhost:3000 | grep HTTP && \
echo "✓ All services running!"
```

---

## Access Application

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8001/docs
- **Backend Health**: http://localhost:8001/health

---

## Stop Services

```bash
# Stop all application services
pkill -f "celery.*worker"
pkill -f "uvicorn.*server:app"
pkill -f "vite"

# Optionally stop databases
redis-cli shutdown
```

---

## View Logs

```bash
# Backend logs
tail -f /var/log/backend.log

# Frontend logs
tail -f /var/log/frontend.log

# Celery logs
tail -f /var/log/celery_worker.log
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find and kill process on port 8001
lsof -i :8001
kill -9 <PID>
```

### Service Won't Start

```bash
# Check logs for errors
tail -50 /var/log/backend.log
tail -50 /var/log/frontend.log
tail -50 /var/log/celery_worker.log
```

### Backend Error: "No such file or directory"

```bash
# Create missing directories
mkdir -p /app/backend/knowledge_base/internal
mkdir -p /app/backend/knowledge_base/external
```

---

## Complete Manual Setup

For comprehensive setup instructions, troubleshooting, and detailed explanations:

📖 **[Read MANUAL_SETUP.md](MANUAL_SETUP.md)**

---

## Service Status Commands

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

# All ports
netstat -tlnp | grep -E ":(6379|27017|8001|3000)"
```

---

**Need help?** Check [MANUAL_SETUP.md](MANUAL_SETUP.md) for detailed troubleshooting.

**Happy building with NeuralStark! 🚀**
