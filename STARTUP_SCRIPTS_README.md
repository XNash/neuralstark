# Startup Scripts - Quick Reference

## 🚀 Quick Start

### For Linux / macOS / WSL
```bash
./run.sh    # Start all services
./stop.sh   # Stop all services
```

### For Windows
```cmd
run.bat     # Start all services
stop.bat    # Stop all services
```

---

## 📋 What Gets Started

### Services Started by run.sh / run.bat:

1. **Redis** (Port 6379)
   - Message broker for Celery
   - Required for background task processing

2. **MongoDB** (Port 27017)
   - Database for application data
   - Stores documents and metadata

3. **Celery Worker** (2 workers)
   - Background task processor
   - Handles document parsing and OCR
   - Resource-optimized configuration

4. **Backend API** (Port 8001)
   - FastAPI server
   - RESTful API endpoints
   - **CORS enabled for all origins**

5. **Frontend** (Port 3000)
   - React application with Vite
   - **Accessible from any host (0.0.0.0)**
   - Hot module reloading enabled

---

## 🌐 Network Access (No Restrictions)

### Backend Configuration ✅
```python
# CORS middleware configured to allow ALL origins
allow_origins = ["*"]
allow_methods = ["*"]
allow_headers = ["*"]
allow_credentials = True
```

### Frontend Configuration ✅
```typescript
// Vite server configured to listen on all interfaces
server: {
  host: '0.0.0.0',  // Allows access from any IP
  port: 3000
}
```

### Access Points
- **Local**: http://localhost:3000
- **LAN**: http://192.168.x.x:3000 (your local IP)
- **Network**: http://your-ip-address:3000

---

## 📊 Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Main web interface |
| Backend API | http://localhost:8001 | REST API |
| API Docs | http://localhost:8001/docs | Interactive API documentation |
| Health Check | http://localhost:8001/health | Backend health status |
| Documents | http://localhost:8001/documents | List indexed documents |

---

## 📝 Script Features

### run.sh / run.bat Features:
✅ Checks for required dependencies  
✅ Starts services in correct order  
✅ Waits for services to be ready  
✅ Provides status feedback  
✅ Logs service output  
✅ Auto-installs frontend dependencies if missing  
✅ Creates log files for debugging  

### stop.sh / stop.bat Features:
✅ Gracefully stops all services  
✅ Cleans up background processes  
✅ Preserves Redis and MongoDB data  
✅ Safe to run multiple times  

---

## 🔧 Log Files (Linux/macOS)

```bash
/var/log/backend.log         # Backend API logs
/var/log/frontend.log        # Frontend build/runtime logs
/var/log/celery_worker.log   # Celery worker logs
/var/log/mongodb.log         # MongoDB logs
```

View logs in real-time:
```bash
tail -f /var/log/backend.log
```

---

## 🪟 Windows Notes

- Services run in separate command windows
- Each window shows real-time logs
- Close windows to stop services
- Alternatively, run `stop.bat` to stop all

---

## 🔍 Verify Services are Running

### Quick Check
```bash
# Check all ports
netstat -an | grep -E "3000|8001|6379|27017"  # Linux/macOS
netstat -an | findstr "3000 8001 6379 27017"  # Windows
```

### Health Checks
```bash
# Backend health
curl http://localhost:8001/health

# Frontend (returns HTML)
curl -I http://localhost:3000

# Redis
redis-cli ping

# MongoDB
mongo --eval "db.version()"
```

---

## ⚙️ Configuration Changes Made

### Backend (backend/main.py)
```python
# Added CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # ← No restrictions
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend (frontend/vite.config.ts)
```typescript
server: {
  host: '0.0.0.0',  // ← Listen on all interfaces
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8001',
      changeOrigin: true,
    },
  },
}
```

---

## 🐛 Troubleshooting

### Services Won't Start

**Issue**: Port already in use
```bash
# Find and kill process on port 8001
lsof -i :8001          # Linux/macOS
kill -9 <PID>

netstat -ano | findstr :8001  # Windows
taskkill /PID <PID> /F
```

**Issue**: Redis not installed
```bash
# Install Redis
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis                  # macOS
# Windows: Download from GitHub
```

**Issue**: MongoDB not found
```bash
# Install MongoDB
sudo apt-get install mongodb        # Ubuntu/Debian
brew install mongodb-community      # macOS
# Windows: Download from MongoDB website
```

### CORS Errors

If you still see CORS errors:
1. Verify backend has latest changes: `grep -n "CORSMiddleware" /app/backend/main.py`
2. Restart backend: `sudo supervisorctl restart backend`
3. Clear browser cache
4. Check browser console for specific error

### Frontend Not Accessible from Network

1. Check firewall rules:
```bash
sudo ufw allow 3000  # Ubuntu/Debian
```

2. Verify Vite config:
```bash
grep -n "host:" /app/frontend/vite.config.ts
```

3. Check your local IP:
```bash
ip addr show        # Linux
ifconfig            # macOS
ipconfig            # Windows
```

---

## 📦 What's Included

### Files Created:
- `run.sh` - Linux/macOS startup script
- `run.bat` - Windows startup script
- `stop.sh` - Linux/macOS stop script
- `stop.bat` - Windows stop script
- `RUNNING_THE_APP.md` - Detailed guide
- `STARTUP_SCRIPTS_README.md` - This file

### Changes Made:
- ✅ Added CORS middleware to backend
- ✅ Configured Vite to allow all hosts
- ✅ Fixed backend port reference (8000 → 8001)
- ✅ Created comprehensive startup scripts
- ✅ Added service verification checks

---

## 🎯 Next Steps

1. **Start the application**:
   ```bash
   ./run.sh    # or run.bat on Windows
   ```

2. **Open in browser**:
   - http://localhost:3000

3. **Test from another device** (optional):
   - Find your IP: `ip addr show` or `ipconfig`
   - Open: http://YOUR_IP:3000

4. **Upload documents**:
   - Use the "Fichiers" menu
   - Upload PDF, DOCX, DOC, images, etc.
   - OCR will extract text automatically

5. **Chat with AI**:
   - Use the "Chat" interface
   - Ask questions about uploaded documents

---

## 💡 Pro Tips

- Use `sudo supervisorctl status` to check all services (if using supervisor)
- Keep Redis and MongoDB running between sessions for faster startups
- Check `/var/log/` for detailed error messages
- Use `tmux` or `screen` to keep services running in background
- For production, consider using Docker Compose for easier deployment

---

## ✅ Verification Checklist

After running the startup script, verify:

- [ ] Redis is running on port 6379
- [ ] MongoDB is running on port 27017
- [ ] Celery worker is processing tasks
- [ ] Backend returns `{"status":"ok"}` at http://localhost:8001/health
- [ ] Frontend loads at http://localhost:3000
- [ ] Can upload a test file
- [ ] Can chat with the AI

---

## 🎉 Success!

If all services started successfully, you should see:

```
==========================================
  All Services Started Successfully!
==========================================

Service Status:
  - Redis:      Running on port 6379
  - MongoDB:    Running on port 27017
  - Celery:     Running (2 workers)
  - Backend:    http://localhost:8001
  - Frontend:   http://localhost:3000

Application is ready to use!
==========================================
```

**Enjoy using NeuralStark! 🚀**

---

*For detailed technical documentation, see:*
- `/app/CHANGES.md` - All changes made
- `/app/IMPLEMENTATION_COMPLETE.md` - Complete implementation details
- `/app/RUNNING_THE_APP.md` - Comprehensive running guide
