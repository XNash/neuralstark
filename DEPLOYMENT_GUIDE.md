# NeuralStark Deployment Guide

## Quick Start

### Prerequisites
Ensure you have the following installed:
- **Python 3.8+** (`python3 --version`)
- **Node.js 16+** (`node --version`)
- **Redis** (message broker for Celery)
- **MongoDB** (database)

### Installation

#### Ubuntu/Debian
```bash
# Install Redis
sudo apt-get update
sudo apt-get install redis-server

# Install MongoDB
sudo apt-get install mongodb

# Start services
sudo systemctl start redis-server
sudo systemctl start mongodb
```

#### macOS
```bash
# Install via Homebrew
brew install redis mongodb-community

# Start services
brew services start redis
brew services start mongodb-community
```

#### CentOS/RHEL
```bash
# Install Redis
sudo yum install redis

# Install MongoDB (requires repository setup)
sudo yum install mongodb-org

# Start services
sudo systemctl start redis
sudo systemctl start mongod
```

---

## Running the Application

### Start All Services
```bash
./run.sh
```

This will:
1. Create required directories
2. Start MongoDB (if not running)
3. Start Redis (if not running)
4. Start Celery worker
5. Start FastAPI backend (port 8001)
6. Start React frontend (port 3000)

### Stop Services
```bash
./stop.sh
```

You'll be prompted whether to stop Redis and MongoDB (they can stay running for next use).

---

## Access Points

Once started, access the application at:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

---

## Logs

All logs are stored in the `logs/` directory:

```bash
# View backend logs
tail -f logs/backend.log

# View frontend logs
tail -f logs/frontend.log

# View Celery logs
tail -f logs/celery_worker.log

# View MongoDB logs (if started by script)
tail -f logs/mongodb.log
```

---

## Troubleshooting

### Port Already in Use

If you see "port already in use" errors:

```bash
# Find what's using port 8001 (backend)
lsof -i:8001

# Find what's using port 3000 (frontend)
lsof -i:3000

# Kill process on port
kill -9 <PID>
```

### Redis Not Starting

```bash
# Check if Redis is running
redis-cli ping

# Should return: PONG

# Start manually if needed
redis-server --daemonize yes
```

### MongoDB Not Starting

```bash
# Check if MongoDB is running
mongosh --eval "db.runCommand({ ping: 1 })"

# Start manually
mongod --bind_ip_all &
```

### Permission Denied Errors

The scripts no longer require sudo! If you see permission errors:

1. Make sure scripts are executable:
   ```bash
   chmod +x run.sh stop.sh
   ```

2. Check that you can write to the project directory

### Python Virtual Environment

If you're using a virtual environment:

```bash
# Activate your virtual environment first
source venv/bin/activate  # or .venv/bin/activate

# Then run the script
./run.sh
```

The scripts will automatically detect and use your virtual environment.

### Missing Dependencies

#### Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Frontend Dependencies
```bash
cd frontend
npm install  # or: yarn install
```

---

## Development Mode

Both backend and frontend run in development mode with hot-reload:

- **Backend**: Changes to Python files automatically reload the server
- **Frontend**: Changes to React files automatically refresh the browser

---

## Production Deployment

For production, consider:

1. **Use a process manager**:
   - systemd (Linux)
   - PM2 (Node.js apps)
   - supervisord (cross-platform)

2. **Configure environment variables**:
   - Set `REACT_APP_BACKEND_URL` for frontend
   - Set `MONGO_URL` for backend
   - Set database credentials

3. **Use a reverse proxy**:
   - nginx or Apache
   - Configure SSL/TLS certificates

4. **Build frontend for production**:
   ```bash
   cd frontend
   npm run build
   ```

5. **Run backend with more workers**:
   ```bash
   uvicorn server:app --host 0.0.0.0 --port 8001 --workers 4
   ```

---

## System Requirements

### Minimum
- 2 CPU cores
- 4GB RAM
- 10GB disk space

### Recommended
- 4 CPU cores
- 8GB RAM
- 20GB disk space
- SSD storage

---

## Security Notes

1. **Change default ports** in production
2. **Configure MongoDB authentication**
3. **Set up firewall rules**
4. **Use environment variables** for secrets
5. **Enable HTTPS** for production

---

## Support

If you encounter issues:

1. Check the logs in `logs/` directory
2. Ensure all prerequisites are installed
3. Verify services are running on correct ports
4. Check firewall settings

---

## Scripts Overview

### run.sh Features:
✅ No sudo required  
✅ Uses local `logs/` directory  
✅ Auto-detects virtual environments  
✅ Checks prerequisites  
✅ Health checks for all services  
✅ Color-coded status output  
✅ Works on Ubuntu, macOS, CentOS  

### stop.sh Features:
✅ Graceful shutdown  
✅ Force-kill fallback  
✅ Interactive prompts  
✅ Preserves Redis/MongoDB by default  
✅ Shows final status  

---

## Common Commands

```bash
# Start everything
./run.sh

# Stop application services (keep Redis/MongoDB)
./stop.sh
# Press 'n' when prompted

# Stop everything including Redis/MongoDB
./stop.sh
# Press 'y' when prompted

# Check service status
ps aux | grep -E "uvicorn|vite|celery|redis|mongod"

# Restart backend only
pkill -f "uvicorn.*server:app"
# Then let run.sh start it, or:
cd backend && uvicorn server:app --host 0.0.0.0 --port 8001 --reload &

# Restart frontend only
pkill -f vite
cd frontend && npm start &
```

---

## File Structure

```
neuralstark/
├── run.sh                    # Start all services
├── stop.sh                   # Stop all services
├── logs/                     # Log files (created automatically)
│   ├── backend.log
│   ├── frontend.log
│   ├── celery_worker.log
│   └── mongodb.log
├── backend/                  # FastAPI backend
│   ├── server.py
│   ├── requirements.txt
│   └── ...
├── frontend/                 # React frontend
│   ├── package.json
│   ├── src/
│   └── ...
└── README.md
```

---

## Environment Variables

Create a `.env` file if you need custom configuration:

### Backend (.env in backend/)
```bash
MONGO_URL=mongodb://localhost:27017/neuralstark
REDIS_URL=redis://localhost:6379
```

### Frontend (.env in frontend/)
```bash
REACT_APP_BACKEND_URL=http://localhost:8001
```

---

**Version**: 4.1  
**Last Updated**: January 2025  
**Compatibility**: Ubuntu, Debian, CentOS, RHEL, macOS
