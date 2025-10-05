# NeuralStark - Quick Start Guide

## Prerequisites

Before running NeuralStark, ensure you have:

- ✅ **Python 3.8+** - `python3 --version`
- ✅ **Node.js 16+** - `node --version`  
- ✅ **Redis** - Message broker for Celery
- ✅ **MongoDB** - Database (optional for basic testing)

### Install Redis & MongoDB

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server mongodb
```

**macOS:**
```bash
brew install redis mongodb-community
brew services start redis
brew services start mongodb-community
```

**CentOS/RHEL:**
```bash
sudo yum install redis mongodb-org
sudo systemctl start redis
sudo systemctl start mongod
```

---

## 🚀 Start the Application

```bash
# Make scripts executable (one time only)
chmod +x run.sh stop.sh

# Start all services
./run.sh
```

**What happens:**
1. ✅ Creates required directories
2. ✅ Starts MongoDB (if installed)
3. ✅ Starts Redis
4. ✅ Starts Celery worker (background tasks)
5. ✅ Starts FastAPI Backend (port 8001)
6. ✅ Starts React Frontend (port 3000)

**Startup time:** ~20-30 seconds (backend loads ML models)

---

## 🌐 Access the Application

Once started:

- **Frontend (Main App)**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

---

## 🛑 Stop the Application

```bash
./stop.sh
```

You'll be prompted:
- **Press 'n'** to keep Redis/MongoDB running (faster next startup)
- **Press 'y'** to stop everything

---

## 📝 View Logs

All logs are in the `logs/` directory:

```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs  
tail -f logs/frontend.log

# Celery worker logs
tail -f logs/celery_worker.log

# MongoDB logs (if started by script)
tail -f logs/mongodb.log
```

---

## ⚠️ Common Issues

### Backend Takes Long to Start

**Normal behavior!** Backend loads ML models (SentenceTransformer) which takes 10-20 seconds.

Wait for the message:
```
✓ Backend started on port 8001
```

### Port Already in Use

```bash
# Check what's using the port
lsof -i:8001  # Backend
lsof -i:3000  # Frontend

# Kill the process
kill -9 <PID>

# Or let the script handle it
./stop.sh
./run.sh
```

### Redis Not Installed

```bash
# The script will show installation command
# Ubuntu/Debian:
sudo apt-get install redis-server

# macOS:
brew install redis
```

### Permission Denied

```bash
# Make scripts executable
chmod +x run.sh stop.sh

# Ensure you're in the project directory
cd /path/to/neuralstark
./run.sh
```

### Frontend Dependencies Missing

First run will auto-install dependencies. If issues occur:

```bash
cd frontend
npm install  # or: yarn install
cd ..
./run.sh
```

### Backend Dependencies Missing

```bash
cd backend
pip install -r requirements.txt
cd ..
./run.sh
```

---

## 🔧 Development Tips

### Hot Reload

Both services support hot reload:
- **Backend**: Edit `.py` files → auto-restart
- **Frontend**: Edit `.js`/`.jsx` files → auto-refresh browser

### Restart Individual Services

**Backend only:**
```bash
pkill -f "uvicorn.*server:app"
cd backend && uvicorn server:app --host 0.0.0.0 --port 8001 --reload &
```

**Frontend only:**
```bash
pkill -f vite
cd frontend && npm start &
```

**Celery only:**
```bash
pkill -f "celery.*worker"
celery -A backend.celery_app worker --loglevel=info &
```

### Check Services Status

```bash
# All services
ps aux | grep -E "uvicorn|vite|celery|redis|mongod"

# Ports in use
lsof -i:3000 -i:8001 -i:6379 -i:27017
```

---

## 📁 Project Structure

```
neuralstark/
├── run.sh                    # 🚀 Start script
├── stop.sh                   # 🛑 Stop script
├── logs/                     # 📝 Log files
│   ├── backend.log
│   ├── frontend.log
│   ├── celery_worker.log
│   └── mongodb.log
├── backend/                  # FastAPI backend
│   ├── server.py
│   ├── main.py
│   ├── requirements.txt
│   └── canvas_templates.json
├── frontend/                 # React frontend
│   ├── package.json
│   └── src/
└── README.md
```

---

## ✅ Verify Installation

After running `./run.sh`, check:

1. **Frontend loads**: Open http://localhost:3000
2. **Backend responds**: `curl http://localhost:8001/health`
3. **Redis works**: `redis-cli ping` (should return PONG)
4. **Services running**:
   ```
   ✓ MongoDB     - Running on port 27017
   ✓ Redis       - Running on port 6379
   ✓ Celery      - Running
   ✓ Backend     - Running on port 8001 (healthy)
   ✓ Frontend    - Running on port 3000
   ```

---

## 💡 Tips

- **First run**: Takes longer due to dependency installation
- **Keep Redis running**: Much faster restarts
- **Use logs**: Check `logs/` for debugging
- **No sudo needed**: Scripts run with user permissions
- **Virtual env**: Auto-detected if present (.venv, venv)

---

## 🆘 Need Help?

1. Check logs in `logs/` directory
2. Verify all prerequisites are installed
3. Try stopping and restarting: `./stop.sh` then `./run.sh`
4. Check port availability: `lsof -i:8001 -i:3000`

---

**Ready to go!** 🎉

```bash
./run.sh
# Wait ~20 seconds
# Open http://localhost:3000
```
