#!/bin/bash

###########################################
# NeuralStark - Optimized Run Script
# Version: 3.1
###########################################

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "  🚀 Starting NeuralStark"
echo "=========================================="

# Function to print status
print_status() {
    case $1 in
        success) echo -e "${GREEN}✓${NC} $2" ;;
        error)   echo -e "${RED}✗${NC} $2" ;;
        info)    echo -e "${BLUE}ℹ${NC} $2" ;;
        warn)    echo -e "${YELLOW}⚠${NC} $2" ;;
    esac
}

###########################################
# 1. Setup Directories
###########################################
mkdir -p /app/backend/knowledge_base/{internal,external} /app/chroma_db /var/log 2>/dev/null

###########################################
# 2. Start Redis
###########################################
if ! redis-cli ping &>/dev/null; then
    print_status info "Starting Redis..."
    
    # Install if needed
    if ! command -v redis-server &>/dev/null; then
        apt-get update -qq && apt-get install -y redis-server -qq 2>/dev/null
    fi
    
    redis-server --daemonize yes --bind 127.0.0.1 2>/dev/null
    sleep 2
fi

if redis-cli ping &>/dev/null; then
    print_status success "Redis running"
else
    print_status error "Redis failed to start"
    exit 1
fi

###########################################
# 3. Start Celery Worker
###########################################
print_status info "Starting Celery worker..."

# Stop existing workers
pkill -9 -f "celery.*worker" 2>/dev/null
rm -f /tmp/celery_worker.pid
sleep 1

# Start new worker
cd /app
export PYTHONPATH=/app:$PYTHONPATH
nohup celery -A backend.celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    --max-tasks-per-child=50 \
    > /var/log/celery_worker.log 2>&1 &

sleep 4

if pgrep -f "celery.*worker" &>/dev/null; then
    print_status success "Celery worker running"
else
    print_status error "Celery failed to start (check /var/log/celery_worker.log)"
    exit 1
fi

###########################################
# 4. Restart Supervisor Services
###########################################
print_status info "Restarting application services..."
sudo supervisorctl restart backend frontend &>/dev/null
sleep 5

###########################################
# 5. Status Check
###########################################
echo ""
echo "=========================================="
echo "  📊 Service Status"
echo "=========================================="

# Check each service
services_ok=true

# Redis
if redis-cli ping &>/dev/null; then
    echo -e "${GREEN}✓${NC} Redis       - Running on port 6379"
else
    echo -e "${RED}✗${NC} Redis       - Not running"
    services_ok=false
fi

# MongoDB
if sudo supervisorctl status mongodb | grep -q "RUNNING"; then
    echo -e "${GREEN}✓${NC} MongoDB     - Running on port 27017"
else
    echo -e "${YELLOW}⚠${NC} MongoDB     - Check supervisor status"
fi

# Celery
if pgrep -f "celery.*worker" &>/dev/null; then
    echo -e "${GREEN}✓${NC} Celery      - Running"
else
    echo -e "${RED}✗${NC} Celery      - Not running"
    services_ok=false
fi

# Backend
sleep 2
if sudo supervisorctl status backend | grep -q "RUNNING"; then
    if curl -s http://localhost:8001/health &>/dev/null; then
        echo -e "${GREEN}✓${NC} Backend     - Running on port 8001 (healthy)"
    else
        echo -e "${YELLOW}⚠${NC} Backend     - Running on port 8001 (starting up)"
    fi
else
    echo -e "${RED}✗${NC} Backend     - Not running"
    services_ok=false
fi

# Frontend
if sudo supervisorctl status frontend | grep -q "RUNNING"; then
    echo -e "${GREEN}✓${NC} Frontend    - Running on port 3000"
else
    echo -e "${RED}✗${NC} Frontend    - Not running"
    services_ok=false
fi

echo ""
echo "=========================================="

if [ "$services_ok" = true ]; then
    echo -e "${GREEN}✓ All services running!${NC}"
    echo ""
    print_status info "🌐 Frontend:  http://localhost:3000"
    print_status info "🔌 Backend:   http://localhost:8001"
    print_status info "📚 API Docs:  http://localhost:8001/docs"
    echo ""
    print_status info "📝 Logs: tail -f /var/log/celery_worker.log"
else
    echo -e "${RED}⚠ Some services failed to start${NC}"
    echo ""
    print_status info "Check logs:"
    print_status info "  Backend:  tail -f /var/log/supervisor/backend.err.log"
    print_status info "  Frontend: tail -f /var/log/supervisor/frontend.err.log"
    print_status info "  Celery:   tail -f /var/log/celery_worker.log"
fi

echo "=========================================="