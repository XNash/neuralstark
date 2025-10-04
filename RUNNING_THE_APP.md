# Running the NeuralStark Application

This guide explains how to start and stop the NeuralStark application using the provided scripts.

## Quick Start

### Linux / macOS / WSL

```bash
# Start all services
./run.sh

# Stop all services
./stop.sh
```

### Windows

```cmd
# Start all services
run.bat

# Stop all services
stop.bat
```

---

## What the Scripts Do

### run.sh / run.bat

The startup scripts automatically:

1. ✅ Check for required dependencies (Python, Node.js, Redis, MongoDB)
2. ✅ Start Redis server (message broker)
3. ✅ Start MongoDB (database)
4. ✅ Start Celery worker (background task processor)
5. ✅ Start Backend API (FastAPI on port 8001)
6. ✅ Start Frontend (React + Vite on port 3000)

### stop.sh / stop.bat

The stop scripts will:

1. ✅ Stop Celery worker
2. ✅ Stop Backend API
3. ✅ Stop Frontend
4. ⚠️ Keep Redis and MongoDB running (optional - can be uncommented)

---

## Prerequisites

### Required Software

#### Linux/macOS
```bash
# Python 3.9+
python3 --version

# Node.js 18+
node --version

# Redis
redis-server --version

# MongoDB
mongod --version
```

#### Windows
- **Python 3.9+**: [Download Python](https://www.python.org/downloads/)
- **Node.js 18+**: [Download Node.js](https://nodejs.org/)
- **Redis**: [Download Redis for Windows](https://github.com/microsoftarchive/redis/releases)
- **MongoDB**: [Download MongoDB](https://www.mongodb.com/try/download/community)

### Python Dependencies

The scripts assume dependencies are already installed. If not:

```bash
cd backend
pip install -r requirements.txt
```

### Frontend Dependencies

The scripts will automatically install frontend dependencies if not present:

```bash
cd frontend
yarn install
```

---

## Services and Ports

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend API | 8001 | http://localhost:8001 |
| MongoDB | 27017 | mongodb://localhost:27017 |
| Redis | 6379 | redis://localhost:6379 |

---

## Network Access Configuration

### ✅ Unlimited Host Access Enabled

Both backend and frontend are configured to **allow access from any host**:

#### Backend (FastAPI)
- **CORS enabled** with `allow_origins=["*"]`
- **All methods** allowed (GET, POST, PUT, DELETE, etc.)
- **All headers** allowed
- **Credentials** supported

```python
# In backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Frontend (Vite)
- **Host** set to `0.0.0.0` (listens on all interfaces)
- **Port** fixed to 3000
- **Proxy** configured for backend API

```typescript
// In frontend/vite.config.ts
server: {
  host: '0.0.0.0',  // Allow access from any host
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8001',
      changeOrigin: true,
    },
  },
}
```

### Accessing from Network

You can now access the application from other devices on your network:

```
Frontend:  http://<your-ip>:3000
Backend:   http://<your-ip>:8001
```

To find your IP address:
- **Linux/macOS**: `ifconfig` or `ip addr show`
- **Windows**: `ipconfig`

---

## Logs

### Linux/macOS

```bash
# Backend logs
tail -f /var/log/backend.log

# Frontend logs
tail -f /var/log/frontend.log

# Celery logs
tail -f /var/log/celery_worker.log
```

### Windows

Logs are displayed in the respective command windows that open when running `run.bat`.

---

## Manual Startup (Alternative)

If you prefer to start services manually:

### Backend
```bash
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend
```bash
cd frontend
yarn start
# or
npm run start
```

### Celery Worker
```bash
celery -A backend.celery_app worker --loglevel=info --concurrency=2
```

### Redis
```bash
redis-server
```

### MongoDB
```bash
mongod --bind_ip_all
```

---

## Troubleshooting

### Port Already in Use

If you get "port already in use" errors:

**Linux/macOS:**
```bash
# Find process using port 8001
lsof -i :8001

# Kill the process
kill -9 <PID>
```

**Windows:**
```cmd
# Find process using port 8001
netstat -ano | findstr :8001

# Kill the process
taskkill /PID <PID> /F
```

### Services Not Starting

1. **Check prerequisites**: Ensure Python, Node.js, Redis, and MongoDB are installed
2. **Check logs**: Review log files for error messages
3. **Check permissions**: Ensure scripts have execute permissions (Linux/macOS)
4. **Check dependencies**: Run `pip install -r backend/requirements.txt` and `yarn install` in frontend

### Backend Returns 500 Error

1. Check Redis is running: `redis-cli ping` (should return "PONG")
2. Check MongoDB is running: `mongo --eval "db.version()"`
3. Check Celery worker is running: `ps aux | grep celery`
4. Review backend logs for error details

### Frontend Can't Connect to Backend

1. Verify backend is running: `curl http://localhost:8001/health`
2. Check CORS configuration in `backend/main.py`
3. Check proxy configuration in `frontend/vite.config.ts`
4. Clear browser cache and reload

---

## Production Deployment

For production deployment, consider:

1. **Environment Variables**: Use `.env` files for configuration
2. **Process Manager**: Use PM2, systemd, or supervisor for service management
3. **Reverse Proxy**: Use Nginx or Apache as reverse proxy
4. **HTTPS**: Set up SSL certificates for secure connections
5. **CORS**: Restrict `allow_origins` to specific domains
6. **Firewall**: Configure firewall rules appropriately

---

## Service Management (Linux with Supervisor)

If using supervisor (as in the current setup):

```bash
# Start all services
sudo supervisorctl start all

# Stop all services
sudo supervisorctl stop all

# Restart a specific service
sudo supervisorctl restart backend
sudo supervisorctl restart frontend

# Check status
sudo supervisorctl status
```

---

## Health Checks

### Backend Health
```bash
curl http://localhost:8001/health
# Expected: {"status":"ok"}
```

### Frontend Access
```bash
curl http://localhost:3000
# Should return HTML content
```

### Check All Services
```bash
# Linux/macOS
./run.sh && sleep 10 && curl http://localhost:8001/health && curl -I http://localhost:3000

# Windows
run.bat
# Then manually check http://localhost:8001/health and http://localhost:3000
```

---

## Support

For issues or questions:

1. Check the logs in `/var/log/` (Linux/macOS) or command windows (Windows)
2. Review `/app/CHANGES.md` for recent changes
3. Review `/app/IMPLEMENTATION_COMPLETE.md` for technical details
4. Ensure all prerequisites are installed and up to date

---

## Summary

✅ **Easy to use**: Single command starts all services  
✅ **Cross-platform**: Works on Linux, macOS, and Windows  
✅ **Network accessible**: Can be accessed from any device on the network  
✅ **No restrictions**: CORS and host restrictions removed  
✅ **Auto-install**: Frontend dependencies installed automatically  
✅ **Graceful stop**: Stop scripts safely shut down all services

**Start the app now:**
```bash
./run.sh    # Linux/macOS
run.bat     # Windows
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

🚀 **Happy coding!**
