# NeuralStark - Kubernetes/Container Deployment Guide

This guide is specifically for the **Kubernetes/containerized environment** where services are managed by `supervisord`.

## 🚀 Quick Start (Kubernetes Environment)

### Current Status
✅ **All services are running and functional!**

The application is already set up and running with:
- MongoDB, Backend, and Frontend managed by supervisor (auto-start)
- Redis and Celery started manually

### Access the Application
- **Frontend**: https://python-error-fix.preview.emergentagent.com
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

## 📋 Service Management

### Supervisor-Managed Services (Auto-start)

These services start automatically when the container starts:

```bash
# Check status of all services
sudo supervisorctl status

# Restart individual services
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
sudo supervisorctl restart mongodb

# Restart all services
sudo supervisorctl restart all

# Stop/Start services
sudo supervisorctl stop backend
sudo supervisorctl start backend
```

### Additional Services (Redis & Celery)

For Redis and Celery, use the provided helper scripts:

```bash
# Start Redis and Celery
./start_additional_services.sh

# Stop Redis and Celery
./stop_additional_services.sh
```

Or manually:

```bash
# Start Redis
redis-server --daemonize yes --bind 127.0.0.1

# Start Celery
cd /app
export PYTHONPATH=/app:$PYTHONPATH
nohup celery -A backend.celery_app worker --loglevel=info --concurrency=2 \
    --max-tasks-per-child=50 > /var/log/celery_worker.log 2>&1 &

# Stop Celery
pkill -f "celery.*worker"

# Stop Redis
redis-cli shutdown
```

## 🔍 Monitoring & Logs

### Check Service Status
```bash
# Quick status check
echo "MongoDB:" && mongosh --quiet --eval "db.serverStatus().ok"
echo "Redis:" && redis-cli ping
echo "Backend:" && curl -s -I http://localhost:8001/docs | head -1
echo "Frontend:" && curl -s -I http://localhost:3000 | head -1
echo "Celery:" && pgrep -f "celery.*worker" | wc -l
```

### View Logs
```bash
# Supervisor-managed service logs
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/backend.out.log
tail -f /var/log/supervisor/frontend.err.log
tail -f /var/log/supervisor/frontend.out.log
tail -f /var/log/mongodb.err.log

# Additional service logs
tail -f /var/log/celery_worker.log
```

## 🛠️ Troubleshooting

### Backend Not Starting
```bash
# Check logs
tail -n 100 /var/log/supervisor/backend.err.log

# Restart backend
sudo supervisorctl restart backend

# Check if port is in use
lsof -i:8001
```

### Frontend Not Loading
```bash
# Check logs
tail -n 50 /var/log/supervisor/frontend.out.log

# Restart frontend
sudo supervisorctl restart frontend

# Check if port is in use
lsof -i:3000
```

### Redis Connection Issues
```bash
# Check if Redis is running
redis-cli ping

# Start Redis if not running
./start_additional_services.sh

# Or manually
redis-server --daemonize yes --bind 127.0.0.1
```

### Celery Worker Not Processing
```bash
# Check Celery status
pgrep -f "celery.*worker"

# View Celery logs
tail -f /var/log/celery_worker.log

# Restart Celery
./stop_additional_services.sh
./start_additional_services.sh
```

### Document Processing Not Working
```bash
# Ensure all services are running
sudo supervisorctl status
redis-cli ping
pgrep -f "celery.*worker"

# Check if knowledge base directories exist
ls -la /app/backend/knowledge_base/internal
ls -la /app/backend/knowledge_base/external

# Check ChromaDB
ls -la /app/chroma_db
```

## 📦 Dependencies

All Python dependencies are in `/app/backend/requirements.txt` and are already installed.

To reinstall or add new dependencies:
```bash
cd /app/backend
pip install -r requirements.txt
pip freeze > requirements.txt  # Update after installing new packages
sudo supervisorctl restart backend
```

Frontend dependencies (Node.js):
```bash
cd /app/frontend
yarn install
sudo supervisorctl restart frontend
```

## 🔧 Configuration

### Backend Configuration
Configuration is in `/app/backend/config.py` and can be overridden with environment variables:

- `LLM_MODEL` - Default: "gemini-2.5-flash"
- `LLM_API_KEY` - Google Generative AI API key
- `EMBEDDING_MODEL_NAME` - Default: "all-MiniLM-L6-v2"
- `REDIS_HOST` - Default: "localhost"
- `REDIS_PORT` - Default: 6379
- `CHROMA_DB_PATH` - Default: "/app/chroma_db"

### Knowledge Base Paths
- Internal documents: `/app/backend/knowledge_base/internal`
- External documents: `/app/backend/knowledge_base/external`

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Chat with AI agent |
| `/documents` | GET | List indexed documents |
| `/documents/upload` | POST | Upload new document |
| `/documents/content` | GET | Get document content |
| `/documents/delete` | POST | Delete document |
| `/knowledge_base/reset` | POST | Reset knowledge base |
| `/docs` | GET | API documentation (Swagger) |

Visit http://localhost:8001/docs for interactive API documentation.

## ⚠️ Important Notes

### About run.sh and stop.sh
The `run.sh` and `stop.sh` scripts in the root directory are designed for **standalone server deployments** and will **not work correctly** in this Kubernetes environment because:

1. Supervisor already manages MongoDB, Backend, and Frontend
2. The scripts would try to start duplicate instances
3. Port conflicts would occur

**Use the supervisor commands and helper scripts instead.**

### Persistence
- MongoDB data is persisted by the container
- ChromaDB vector store is in `/app/chroma_db`
- Uploaded documents are in `/app/backend/knowledge_base/`

### Resource Usage
- The application uses ML models (SentenceTransformer) which requires significant memory
- Backend startup takes 20-30 seconds while loading models
- Monitor resource usage with `top` or `htop`

## 🎯 Testing the Application

### 1. Upload a Document
```bash
curl -X POST "http://localhost:8001/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.pdf" \
  -F "source_type=internal"
```

### 2. List Documents
```bash
curl http://localhost:8001/documents
```

### 3. Chat with AI
```bash
curl -X POST "http://localhost:8001/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, what can you do?",
    "session_id": "test-session"
  }'
```

### 4. Access Frontend
Open your browser to:
https://python-error-fix.preview.emergentagent.com

## 🚀 Production Recommendations

For a production deployment in Kubernetes:

1. **Use Kubernetes Services** for Redis instead of local instance
2. **Add Celery to supervisor** config for auto-start
3. **Configure persistent volumes** for:
   - MongoDB data
   - ChromaDB vector store
   - Knowledge base directories
4. **Set up health checks** in Kubernetes
5. **Configure resource limits** (memory, CPU)
6. **Use secrets** for API keys instead of environment variables
7. **Enable monitoring** and alerting

## 📞 Support

For issues specific to this deployment:
1. Check logs in `/var/log/supervisor/` and `/var/log/celery_worker.log`
2. Verify all services are running with the status check commands above
3. Ensure Redis is running before starting Celery
4. See `DEPLOYMENT_STATUS.md` for detailed setup information

For general NeuralStark questions, refer to the main `README.md`.

---

**Current Deployment Status**: ✅ Fully functional and running
