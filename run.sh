#!/bin/bash

###########################################
# NeuralStark - Universal Run Script
# Version: 5.0 - Auto-install dependencies
###########################################

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "  🚀 Starting NeuralStark"
echo "  Auto-installing missing dependencies"
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
# 2. Setup Virtual Environment
###########################################
print_status info "Setting up Python virtual environment..."

# Check if venv exists
if [ -d "$SCRIPT_DIR/.venv" ]; then
    print_status success "Virtual environment found (.venv)"
elif [ -d "/root/.venv" ]; then
    # Use /root/.venv directly without creating symlink (avoids Git issues)
    print_status success "Virtual environment found (/root/.venv)"
else
    # Create new venv
    print_status warn "Creating new virtual environment..."
    python3 -m venv "$SCRIPT_DIR/.venv"
    print_status success "Virtual environment created"
fi

# Activate venv
if [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
    print_status success "Virtual environment activated"
    PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python3"
    PIP_BIN="$SCRIPT_DIR/.venv/bin/pip"
elif [ -f "/root/.venv/bin/activate" ]; then
    source "/root/.venv/bin/activate"
    print_status success "Virtual environment activated (/root/.venv)"
    PYTHON_BIN="/root/.venv/bin/python3"
    PIP_BIN="/root/.venv/bin/pip"
else
    print_status warn "Using system Python"
    PYTHON_BIN="python3"
    PIP_BIN="pip3"
fi

###########################################
# 3. Check and Install System Prerequisites
###########################################
print_status info "Checking system prerequisites..."

# Python
if ! command -v python3 &>/dev/null; then
    print_status error "Python 3 not found. Installing..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get update -qq && sudo apt-get install -y python3 python3-pip python3-venv
    elif command -v yum &>/dev/null; then
        sudo yum install -y python3 python3-pip
    else
        print_status error "Cannot install Python. Please install manually."
        exit 1
    fi
fi

# Node.js
if ! command -v node &>/dev/null; then
    print_status error "Node.js not found. Installing..."
    if command -v apt-get &>/dev/null; then
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt-get install -y nodejs
    elif command -v yum &>/dev/null; then
        curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
        sudo yum install -y nodejs
    else
        print_status error "Cannot install Node.js. Please install manually."
        exit 1
    fi
fi

print_status success "System prerequisites OK (Python $(python3 --version | awk '{print $2}'), Node $(node --version))"

###########################################
# 4. Install Python Dependencies
###########################################
print_status info "Installing Python dependencies..."

cd "$SCRIPT_DIR/backend"

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    print_status error "requirements.txt not found!"
    exit 1
fi

# Always try to install/update dependencies
print_status info "Installing packages from requirements.txt..."
$PIP_BIN install --upgrade pip setuptools wheel -q 2>/dev/null
$PIP_BIN install -r requirements.txt -q 2>/dev/null

# Verify key packages
if $PYTHON_BIN -c "import fastapi" 2>/dev/null && \
   $PYTHON_BIN -c "import celery" 2>/dev/null && \
   $PYTHON_BIN -c "import chromadb" 2>/dev/null && \
   $PYTHON_BIN -c "import langchain" 2>/dev/null; then
    print_status success "Python dependencies installed successfully"
else
    print_status warn "Some dependencies may be missing, trying to fix..."
    
    # Install critical packages individually
    $PIP_BIN install -q fastapi uvicorn celery redis langchain langchain-google-genai \
        chromadb sentence-transformers langchain-huggingface langchain-chroma \
        pypdf python-docx pandas openpyxl reportlab pytesseract Pillow \
        watchdog python-dotenv pydantic-settings aiohttp 2>/dev/null
    
    print_status success "Critical packages installed"
fi

cd "$SCRIPT_DIR"

###########################################
# 5. Install Frontend Dependencies
###########################################
print_status info "Installing frontend dependencies..."

cd "$SCRIPT_DIR/frontend"

# Check if package.json exists
if [ ! -f "package.json" ]; then
    print_status error "package.json not found!"
    exit 1
fi

# Install yarn if not available
if ! command -v yarn &>/dev/null; then
    print_status warn "Yarn not found, installing..."
    npm install -g yarn 2>/dev/null || sudo npm install -g yarn 2>/dev/null
fi

# Install dependencies if node_modules doesn't exist or is incomplete
if [ ! -d "node_modules" ] || [ ! -d "node_modules/react" ]; then
    print_status info "Installing frontend packages (this may take a few minutes)..."
    if command -v yarn &>/dev/null; then
        yarn install --silent 2>/dev/null || yarn install
    else
        npm install --silent 2>/dev/null || npm install
    fi
    print_status success "Frontend dependencies installed"
else
    print_status success "Frontend dependencies already installed"
fi

cd "$SCRIPT_DIR"

###########################################
# 6. Check and Install MongoDB
###########################################
print_status info "Checking MongoDB..."

if lsof -i:27017 &>/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":27017 "; then
    print_status success "MongoDB already running on port 27017"
elif command -v mongod &>/dev/null; then
    # MongoDB installed, try to start it
    if [ -w /var/log ]; then
        nohup mongod --bind_ip_all --dbpath /tmp/mongodb_data > "$LOG_DIR/mongodb.log" 2>&1 &
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
    print_status warn "MongoDB not installed. Attempting to install..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get update -qq
        sudo apt-get install -y mongodb 2>/dev/null || sudo apt-get install -y mongodb-org 2>/dev/null
    elif command -v yum &>/dev/null; then
        sudo yum install -y mongodb-org 2>/dev/null
    fi
    
    # Try to start after installation
    if command -v mongod &>/dev/null; then
        nohup mongod --bind_ip_all > "$LOG_DIR/mongodb.log" 2>&1 &
        sleep 3
        print_status success "MongoDB installed and started"
    else
        print_status error "Failed to install MongoDB. Please install manually."
    fi
fi

###########################################
# 7. Check and Install Redis
###########################################
print_status info "Checking Redis..."

if redis-cli ping &>/dev/null; then
    print_status success "Redis already running on port 6379"
else
    if ! command -v redis-server &>/dev/null; then
        print_status warn "Redis not found. Installing..."
        if command -v apt-get &>/dev/null; then
            sudo apt-get update -qq
            sudo apt-get install -y redis-server 2>/dev/null
        elif command -v yum &>/dev/null; then
            sudo yum install -y redis 2>/dev/null
        elif command -v brew &>/dev/null; then
            brew install redis 2>/dev/null
        else
            print_status error "Cannot install Redis. Please install manually."
            exit 1
        fi
    fi
    
    # Start Redis
    redis-server --daemonize yes --bind 127.0.0.1 2>/dev/null || \
    redis-server --daemonize yes 2>/dev/null
    sleep 2
    
    if redis-cli ping &>/dev/null; then
        print_status success "Redis installed and started on port 6379"
    else
        print_status error "Redis failed to start"
        exit 1
    fi
fi

###########################################
# 8. Start Celery Worker
###########################################
print_status info "Starting Celery worker..."

# Stop existing workers
pkill -9 -f "celery.*worker" 2>/dev/null
sleep 1

# Set Python path
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Find celery binary
if [ -f "$SCRIPT_DIR/.venv/bin/celery" ]; then
    CELERY_BIN="$SCRIPT_DIR/.venv/bin/celery"
elif [ -f "/root/.venv/bin/celery" ]; then
    CELERY_BIN="/root/.venv/bin/celery"
else
    CELERY_BIN="celery"
fi

# Check if celery is available
if ! command -v $CELERY_BIN &>/dev/null && ! $PYTHON_BIN -c "import celery" 2>/dev/null; then
    print_status warn "Celery not found, installing..."
    $PIP_BIN install -q celery redis
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
    # Don't exit, continue with other services
fi

###########################################
# 9. Start Backend (FastAPI)
###########################################
print_status info "Starting Backend..."

# Check if backend is already running
if lsof -i:8001 &>/dev/null 2>&1; then
    print_status warn "Port 8001 already in use"
    if curl -s -m 2 http://localhost:8001/docs &>/dev/null; then
        print_status success "Backend already running on port 8001"
    else
        print_status error "Port 8001 occupied by another process. Trying to kill..."
        pkill -f "uvicorn.*server:app" 2>/dev/null
        sleep 2
    fi
fi

# Only start if not already running
if ! lsof -i:8001 &>/dev/null 2>&1; then
    cd "$SCRIPT_DIR/backend"
    
    # Find uvicorn
    if [ -f "$SCRIPT_DIR/.venv/bin/uvicorn" ]; then
        UVICORN_BIN="$SCRIPT_DIR/.venv/bin/uvicorn"
    elif [ -f "/root/.venv/bin/uvicorn" ]; then
        UVICORN_BIN="/root/.venv/bin/uvicorn"
    else
        UVICORN_BIN="uvicorn"
    fi
    
    # Start backend
    nohup $UVICORN_BIN server:app \
        --host 0.0.0.0 \
        --port 8001 \
        --reload \
        > "$LOG_DIR/backend.log" 2>&1 &
    
    print_status info "Waiting for backend to load (loading ML models, 20-30s)..."
    
    # Wait up to 40 seconds for backend to be ready
    for i in {1..40}; do
        sleep 1
        if lsof -i:8001 &>/dev/null 2>&1; then
            if curl -s -m 2 http://localhost:8001/docs &>/dev/null; then
                print_status success "Backend started on port 8001"
                break
            fi
        fi
        if [ $i -eq 40 ]; then
            print_status warn "Backend may still be loading"
            print_status info "Check logs: tail -f $LOG_DIR/backend.log"
        fi
    done
fi

cd "$SCRIPT_DIR"

###########################################
# 10. Start Frontend (React + Vite)
###########################################
print_status info "Starting Frontend..."

# Check if frontend is already running
if lsof -i:3000 &>/dev/null 2>&1; then
    print_status warn "Port 3000 already in use"
    if curl -s -m 2 -I http://localhost:3000 &>/dev/null; then
        print_status success "Frontend already running on port 3000"
    else
        print_status error "Port 3000 occupied by another process. Trying to kill..."
        pkill -f "vite.*3000" 2>/dev/null
        pkill -f "node.*vite" 2>/dev/null
        sleep 2
    fi
fi

# Only start if not already running
if ! lsof -i:3000 &>/dev/null 2>&1; then
    cd "$SCRIPT_DIR/frontend"
    
    # Start frontend
    if command -v yarn &>/dev/null; then
        nohup yarn start > "$LOG_DIR/frontend.log" 2>&1 &
    else
        nohup npm start > "$LOG_DIR/frontend.log" 2>&1 &
    fi
    
    print_status info "Waiting for frontend to start..."
    
    # Wait up to 15 seconds for frontend to be ready
    for i in {1..15}; do
        sleep 1
        if lsof -i:3000 &>/dev/null 2>&1; then
            print_status success "Frontend started on port 3000"
            break
        fi
        if [ $i -eq 15 ]; then
            print_status warn "Frontend may not have started"
            print_status info "Check logs: tail -f $LOG_DIR/frontend.log"
        fi
    done
fi

cd "$SCRIPT_DIR"

###########################################
# 11. Final Status Summary
###########################################
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
    WORKER_COUNT=$(pgrep -f "celery.*worker" | wc -l)
    echo -e "${GREEN}✓${NC} Celery      - Running ($WORKER_COUNT workers)"
else
    echo -e "${YELLOW}⚠${NC} Celery      - Not running"
fi

# Backend
if lsof -i:8001 &>/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":8001 "; then
    if curl -s -m 2 http://localhost:8001/docs &>/dev/null; then
        echo -e "${GREEN}✓${NC} Backend     - Running on port 8001 (healthy)"
    else
        echo -e "${YELLOW}⚠${NC} Backend     - Running on port 8001 (still loading)"
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
    echo -e "${GREEN}✓ All critical services running!${NC}"
    echo ""
    print_status info "🌐 Application: http://localhost:3000"
    print_status info "🔌 Backend API: http://localhost:8001"
    print_status info "📚 API Docs:    http://localhost:8001/docs"
    echo ""
    print_status info "📁 Logs directory: $LOG_DIR"
    print_status info "🛑 To stop: ./stop.sh"
    echo ""
    print_status success "NeuralStark is ready! 🎉"
else
    echo -e "${YELLOW}⚠ Some services failed to start${NC}"
    echo ""
    print_status info "Check logs:"
    print_status info "  Backend:  tail -f $LOG_DIR/backend.log"
    print_status info "  Frontend: tail -f $LOG_DIR/frontend.log"
    print_status info "  Celery:   tail -f $LOG_DIR/celery_worker.log"
    echo ""
    print_status info "Try running again or check the logs for errors"
fi

echo "=========================================="
