#!/bin/bash

###########################################
# NeuralStark - Universal Run Script
# Works in any standard Linux environment
# Version: 4.1 - No sudo required
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

# Create local logs directory
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

###########################################
# 1. Setup Directories
###########################################
print_status info "Setting up directories..."
mkdir -p backend/knowledge_base/internal backend/knowledge_base/external chroma_db 2>/dev/null
print_status success "Directories ready"

###########################################
# 2. Check Prerequisites
###########################################
print_status info "Checking prerequisites..."

if ! command -v python3 &>/dev/null; then
    print_status error "Python 3 not found. Please install Python 3."
    exit 1
fi

if ! command -v node &>/dev/null; then
    print_status error "Node.js not found. Please install Node.js."
    exit 1
fi

print_status success "Prerequisites OK (Python 3, Node.js)"

###########################################
# 3. Start MongoDB
###########################################
print_status info "Starting MongoDB..."

# Check if port is in use
if lsof -i:27017 &>/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":27017 "; then
    print_status success "MongoDB already running on port 27017"
elif command -v mongod &>/dev/null; then
    # Try to start MongoDB
    if [ -w /var/log ]; then
        mongod --fork --logpath /var/log/mongodb.log --bind_ip_all 2>/dev/null || \
        nohup mongod --bind_ip_all > "$LOG_DIR/mongodb.log" 2>&1 &
    else
        nohup mongod --bind_ip_all > "$LOG_DIR/mongodb.log" 2>&1 &
    fi
    sleep 3
    
    if lsof -i:27017 &>/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":27017 "; then
        print_status success "MongoDB started on port 27017"
    else
        print_status warn "MongoDB may not have started (check $LOG_DIR/mongodb.log)"
    fi
else
    print_status warn "MongoDB not installed - application may not work correctly"
fi

###########################################
# 4. Start Redis
###########################################
print_status info "Starting Redis..."

if redis-cli ping &>/dev/null; then
    print_status success "Redis already running on port 6379"
else
    if ! command -v redis-server &>/dev/null; then
        print_status error "Redis not found. Please install Redis:"
        print_status info "  Ubuntu/Debian: sudo apt-get install redis-server"
        print_status info "  CentOS/RHEL:   sudo yum install redis"
        print_status info "  macOS:         brew install redis"
        exit 1
    fi
    
    redis-server --daemonize yes --bind 127.0.0.1 2>/dev/null || \
    redis-server --daemonize yes 2>/dev/null
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

# Find Python executable
if [ -d "$SCRIPT_DIR/.venv" ]; then
    PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python"
    CELERY_BIN="$SCRIPT_DIR/.venv/bin/celery"
elif [ -d "/root/.venv" ]; then
    PYTHON_BIN="/root/.venv/bin/python"
    CELERY_BIN="/root/.venv/bin/celery"
elif [ -d "$SCRIPT_DIR/venv" ]; then
    PYTHON_BIN="$SCRIPT_DIR/venv/bin/python"
    CELERY_BIN="$SCRIPT_DIR/venv/bin/celery"
else
    PYTHON_BIN="python3"
    CELERY_BIN="celery"
fi

# Start Celery
nohup $CELERY_BIN -A backend.celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    --max-tasks-per-child=50 \
    > "$LOG_DIR/celery_worker.log" 2>&1 &

sleep 4

if pgrep -f "celery.*worker" &>/dev/null; then
    print_status success "Celery worker started"
else
    print_status error "Celery failed to start"
    print_status info "Check logs: tail -f $LOG_DIR/celery_worker.log"
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

# Find uvicorn
if [ -d "$SCRIPT_DIR/.venv" ]; then
    UVICORN_BIN="$SCRIPT_DIR/.venv/bin/uvicorn"
elif [ -d "/root/.venv" ]; then
    UVICORN_BIN="/root/.venv/bin/uvicorn"
elif [ -d "$SCRIPT_DIR/venv" ]; then
    UVICORN_BIN="$SCRIPT_DIR/venv/bin/uvicorn"
else
    UVICORN_BIN="uvicorn"
fi

# Start backend
nohup $UVICORN_BIN server:app \
    --host 0.0.0.0 \
    --port 8001 \
    --reload \
    > "$LOG_DIR/backend.log" 2>&1 &

sleep 4

if lsof -i:8001 &>/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":8001 "; then
    print_status success "Backend started on port 8001"
else
    print_status error "Backend failed to start"
    print_status info "Check logs: tail -f $LOG_DIR/backend.log"
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
    print_status warn "Installing frontend dependencies (this may take a few minutes)..."
    if command -v yarn &>/dev/null; then
        yarn install
    else
        npm install
    fi
fi

# Start frontend
if command -v yarn &>/dev/null; then
    nohup yarn start > "$LOG_DIR/frontend.log" 2>&1 &
else
    nohup npm start > "$LOG_DIR/frontend.log" 2>&1 &
fi

print_status info "Waiting for frontend to start..."
sleep 8

if lsof -i:3000 &>/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":3000 "; then
    print_status success "Frontend started on port 3000"
else
    print_status warn "Frontend may not have started"
    print_status info "Check logs: tail -f $LOG_DIR/frontend.log"
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
if lsof -i:27017 &>/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":27017 "; then
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
if lsof -i:8001 &>/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":8001 "; then
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
if lsof -i:3000 &>/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":3000 "; then
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
    print_status info "🌐 Application: http://localhost:3000"
    print_status info "🔌 Backend API: http://localhost:8001"
    print_status info "📚 API Docs:    http://localhost:8001/docs"
    echo ""
    print_status info "📁 Logs directory: $LOG_DIR"
    print_status info "🛑 To stop: ./stop.sh"
else
    echo -e "${YELLOW}⚠ Some services failed${NC}"
    echo ""
    print_status info "Check logs:"
    print_status info "  Backend:  tail -f $LOG_DIR/backend.log"
    print_status info "  Frontend: tail -f $LOG_DIR/frontend.log"
    print_status info "  Celery:   tail -f $LOG_DIR/celery_worker.log"
fi

echo "=========================================="