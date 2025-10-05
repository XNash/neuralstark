#!/bin/bash

###########################################
# NeuralStark - Universal Run Script
# Works in any standard Linux environment
# Version: 4.0
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
echo ""

# Function to print status
print_status() {
    case $1 in
        success) echo -e "${GREEN}✓${NC} $2" ;;
        error)   echo -e "${RED}✗${NC} $2" ;;
        info)    echo -e "${BLUE}ℹ${NC} $2" ;;
        warn)    echo -e "${YELLOW}⚠${NC} $2" ;;
    esac
}

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

###########################################
# 1. Setup Directories
###########################################
print_status info "Setting up directories..."
mkdir -p backend/knowledge_base/internal backend/knowledge_base/external chroma_db /var/log 2>/dev/null
print_status success "Directories ready"

###########################################
# 2. Check Prerequisites
###########################################
print_status info "Checking prerequisites..."

if ! command -v python3 &>/dev/null; then
    print_status error "Python 3 not found"
    exit 1
fi

if ! command -v node &>/dev/null; then
    print_status error "Node.js not found"
    exit 1
fi

print_status success "Prerequisites OK"

###########################################
# 3. Start MongoDB
###########################################
print_status info "Starting MongoDB..."

if lsof -i:27017 &>/dev/null; then
    print_status success "MongoDB already running on port 27017"
else
    if command -v mongod &>/dev/null; then
        mongod --fork --logpath /var/log/mongodb.log --bind_ip_all 2>/dev/null || \
        nohup mongod --bind_ip_all > /var/log/mongodb.log 2>&1 &
        sleep 3
        
        if lsof -i:27017 &>/dev/null; then
            print_status success "MongoDB started on port 27017"
        else
            print_status warn "MongoDB may not have started (check /var/log/mongodb.log)"
        fi
    else
        print_status warn "MongoDB not installed - skipping"
    fi
fi

###########################################
# 4. Start Redis
###########################################
print_status info "Starting Redis..."

if redis-cli ping &>/dev/null; then
    print_status success "Redis already running on port 6379"
else
    # Install if needed
    if ! command -v redis-server &>/dev/null; then
        print_status warn "Redis not found, installing..."
        if command -v apt-get &>/dev/null; then
            apt-get update -qq && apt-get install -y redis-server -qq 2>/dev/null
        elif command -v yum &>/dev/null; then
            yum install -y redis -q 2>/dev/null
        fi
    fi
    
    redis-server --daemonize yes --bind 127.0.0.1 2>/dev/null
    sleep 2
    
    if redis-cli ping &>/dev/null; then
        print_status success "Redis started on port 6379"
    else
        print_status error "Redis failed to start"
        exit 1
    fi
fi

###########################################
# 5. Start Celery Worker
###########################################
print_status info "Starting Celery worker..."

# Stop existing workers
pkill -9 -f "celery.*worker" 2>/dev/null
rm -f /tmp/celery_worker.pid
sleep 1

# Set Python path
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Start Celery
nohup celery -A backend.celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    --max-tasks-per-child=50 \
    > /var/log/celery_worker.log 2>&1 &

sleep 4

if pgrep -f "celery.*worker" &>/dev/null; then
    print_status success "Celery worker started"
else
    print_status error "Celery failed to start (check /var/log/celery_worker.log)"
    exit 1
fi

###########################################
# 6. Start Backend (FastAPI)
###########################################
print_status info "Starting Backend..."

# Kill existing backend
pkill -f "uvicorn.*server:app" 2>/dev/null
sleep 1

cd "$SCRIPT_DIR/backend"

# Check if virtual environment exists
if [ -d "/root/.venv" ]; then
    PYTHON_BIN="/root/.venv/bin/python"
    UVICORN_BIN="/root/.venv/bin/uvicorn"
elif [ -d "venv" ]; then
    PYTHON_BIN="venv/bin/python"
    UVICORN_BIN="venv/bin/uvicorn"
else
    PYTHON_BIN="python3"
    UVICORN_BIN="uvicorn"
fi

# Start backend
nohup $UVICORN_BIN server:app \
    --host 0.0.0.0 \
    --port 8001 \
    --reload \
    > /var/log/backend.log 2>&1 &

sleep 4

if lsof -i:8001 &>/dev/null; then
    print_status success "Backend started on port 8001"
else
    print_status error "Backend failed to start (check /var/log/backend.log)"
    exit 1
fi

###########################################
# 7. Start Frontend (React + Vite)
###########################################
print_status info "Starting Frontend..."

cd "$SCRIPT_DIR/frontend"

# Kill existing frontend
pkill -f "vite.*3000" 2>/dev/null
pkill -f "node.*vite" 2>/dev/null
sleep 1

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_status warn "Installing frontend dependencies..."
    if command -v yarn &>/dev/null; then
        yarn install --silent
    else
        npm install --silent
    fi
fi

# Start frontend
nohup yarn start > /var/log/frontend.log 2>&1 &

print_status info "Waiting for frontend to start..."
sleep 8

if lsof -i:3000 &>/dev/null; then
    print_status success "Frontend started on port 3000"
else
    print_status error "Frontend failed to start (check /var/log/frontend.log)"
fi

###########################################
# 8. Status Summary
###########################################
cd "$SCRIPT_DIR"

echo ""
echo "=========================================="
echo "  📊 Service Status"
echo "=========================================="
echo ""

all_ok=true

# MongoDB
if lsof -i:27017 &>/dev/null; then
    echo -e "${GREEN}✓${NC} MongoDB     - Running on port 27017"
else
    echo -e "${YELLOW}⚠${NC} MongoDB     - Not running"
fi

# Redis
if redis-cli ping &>/dev/null; then
    echo -e "${GREEN}✓${NC} Redis       - Running on port 6379"
else
    echo -e "${RED}✗${NC} Redis       - Not running"
    all_ok=false
fi

# Celery
if pgrep -f "celery.*worker" &>/dev/null; then
    echo -e "${GREEN}✓${NC} Celery      - Running"
else
    echo -e "${RED}✗${NC} Celery      - Not running"
    all_ok=false
fi

# Backend
sleep 2
if lsof -i:8001 &>/dev/null; then
    if curl -s http://localhost:8001/health &>/dev/null; then
        echo -e "${GREEN}✓${NC} Backend     - Running on port 8001 (healthy)"
    else
        echo -e "${YELLOW}⚠${NC} Backend     - Running on port 8001 (starting up)"
    fi
else
    echo -e "${RED}✗${NC} Backend     - Not running"
    all_ok=false
fi

# Frontend
if lsof -i:3000 &>/dev/null; then
    echo -e "${GREEN}✓${NC} Frontend    - Running on port 3000"
else
    echo -e "${RED}✗${NC} Frontend    - Not running"
    all_ok=false
fi

echo ""
echo "=========================================="

if [ "$all_ok" = true ]; then
    echo -e "${GREEN}✓ All services running!${NC}"
    echo ""
    print_status info "🌐 Frontend:  http://localhost:3000"
    print_status info "🔌 Backend:   http://localhost:8001"
    print_status info "📚 API Docs:  http://localhost:8001/docs"
    echo ""
    print_status info "To stop all services: ./stop.sh"
else
    echo -e "${YELLOW}⚠ Some services failed${NC}"
    echo ""
    print_status info "Check logs in /var/log/"
    echo ""
    print_status info "Logs:"
    print_status info "  Backend:  tail -f /var/log/backend.log"
    print_status info "  Frontend: tail -f /var/log/frontend.log"
    print_status info "  Celery:   tail -f /var/log/celery_worker.log"
fi

echo "=========================================="