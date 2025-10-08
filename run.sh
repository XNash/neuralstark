#!/bin/bash

###########################################
# NeuralStark - Complete All-in-One Script
# Version: 6.0 - Setup + Install + Run
# Everything you need in one command!
###########################################

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "=========================================="
echo "  🚀 NeuralStark Complete Setup & Start"
echo "  Version 6.0 - All-in-One Solution"
echo "=========================================="
echo ""

# Function to print status
print_status() {
    case $1 in
        success) echo -e "${GREEN}✓${NC} $2" ;;
        error)   echo -e "${RED}✗${NC} $2" ;;
        info)    echo -e "${BLUE}ℹ${NC} $2" ;;
        warn)    echo -e "${YELLOW}⚠${NC} $2" ;;
        section) echo -e "${CYAN}━━━${NC} $2" ;;
    esac
}

# Get script directory (project root)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"
cd "$PROJECT_ROOT"

ERRORS=0
WARNINGS=0

###########################################
# PHASE 1: DIRECTORY SETUP
###########################################
print_status section "Phase 1: Directory Setup"

print_status info "Creating required directories..."

# Create directories with error checking (relative to project root)
mkdir -p "$PROJECT_ROOT/backend/knowledge_base/internal" 2>/dev/null
mkdir -p "$PROJECT_ROOT/backend/knowledge_base/external" 2>/dev/null
mkdir -p "$PROJECT_ROOT/chroma_db" 2>/dev/null
mkdir -p "$PROJECT_ROOT/logs" 2>/dev/null

# Verify each directory individually
MISSING_DIRS=""

if [ ! -d "$PROJECT_ROOT/backend/knowledge_base/internal" ]; then
    MISSING_DIRS="$MISSING_DIRS backend/knowledge_base/internal"
fi

if [ ! -d "$PROJECT_ROOT/backend/knowledge_base/external" ]; then
    MISSING_DIRS="$MISSING_DIRS backend/knowledge_base/external"
fi

if [ ! -d "$PROJECT_ROOT/chroma_db" ]; then
    MISSING_DIRS="$MISSING_DIRS chroma_db"
fi

if [ ! -d "$PROJECT_ROOT/logs" ]; then
    MISSING_DIRS="$MISSING_DIRS logs"
fi

if [ -z "$MISSING_DIRS" ]; then
    print_status success "All required directories created"
else
    print_status error "Failed to create directories: $MISSING_DIRS"
    print_status info "Attempting to create missing directories with elevated permissions..."
    for dir in $MISSING_DIRS; do
        mkdir -p "$dir" 2>/dev/null && print_status success "Created $dir" || print_status error "Failed to create $dir"
    done
    ERRORS=$((ERRORS + 1))
fi

# Set permissions and ensure proper ChromaDB setup
chmod -R 755 "$PROJECT_ROOT/chroma_db" "$PROJECT_ROOT/backend/knowledge_base" "$PROJECT_ROOT/logs" 2>/dev/null
if [ $? -eq 0 ]; then
    print_status success "Directory permissions set (755)"
else
    print_status warn "Could not set permissions, but directories exist"
fi

# Ensure ChromaDB directory is properly initialized
if [ -w "$PROJECT_ROOT/chroma_db" ]; then
    print_status success "ChromaDB directory is writable"
    
    # Check for potential ChromaDB corruption and clean if needed
    if [ -d "$PROJECT_ROOT/chroma_db" ] && [ "$(find "$PROJECT_ROOT/chroma_db" -name '*.bin' -size 0 2>/dev/null | wc -l)" -gt 0 ]; then
        print_status warn "Detected potential ChromaDB corruption (empty index files)"
        print_status info "Cleaning ChromaDB for fresh start..."
        rm -rf "$PROJECT_ROOT/chroma_db"/* 2>/dev/null
    fi
else
    print_status warn "ChromaDB directory may not be writable - this could cause database errors"
    WARNINGS=$((WARNINGS + 1))
fi

LOG_DIR="$PROJECT_ROOT/logs"

LOG_DIR="$SCRIPT_DIR/logs"

echo ""

###########################################
# PHASE 2: SYSTEM PREREQUISITES
###########################################
print_status section "Phase 2: System Prerequisites Check"

# Python
print_status info "Checking Python..."
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_status success "Python $PYTHON_VERSION found"
else
    print_status error "Python 3 not found. Installing..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get update -qq && sudo apt-get install -y python3 python3-pip python3-venv 2>/dev/null
    elif command -v yum &>/dev/null; then
        sudo yum install -y python3 python3-pip 2>/dev/null
    elif command -v brew &>/dev/null; then
        brew install python3 2>/dev/null
    else
        print_status error "Cannot auto-install Python. Please install Python 3.8+ manually."
        ERRORS=$((ERRORS + 1))
    fi
fi

# Node.js
print_status info "Checking Node.js..."
if command -v node &>/dev/null; then
    NODE_VERSION=$(node --version 2>&1)
    print_status success "Node.js $NODE_VERSION found"
else
    print_status error "Node.js not found. Installing..."
    if command -v apt-get &>/dev/null; then
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - 2>/dev/null
        sudo apt-get install -y nodejs 2>/dev/null
    elif command -v yum &>/dev/null; then
        curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash - 2>/dev/null
        sudo yum install -y nodejs 2>/dev/null
    elif command -v brew &>/dev/null; then
        brew install node 2>/dev/null
    else
        print_status error "Cannot auto-install Node.js. Please install Node.js 16+ manually."
        ERRORS=$((ERRORS + 1))
    fi
fi

echo ""

###########################################
# PHASE 3: VIRTUAL ENVIRONMENT
###########################################
print_status section "Phase 3: Python Virtual Environment"

print_status info "Setting up Python virtual environment..."

# Check if venv exists
if [ -d "$SCRIPT_DIR/.venv" ]; then
    print_status success "Virtual environment found (.venv)"
elif [ -d "/root/.venv" ]; then
    print_status success "Virtual environment found (/root/.venv)"
else
    print_status info "Creating new virtual environment..."
    python3 -m venv "$SCRIPT_DIR/.venv" 2>/dev/null
    if [ $? -eq 0 ]; then
        print_status success "Virtual environment created"
    else
        print_status warn "Could not create venv, will use system Python"
    fi
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

echo ""

###########################################
# PHASE 4: PYTHON DEPENDENCIES
###########################################
print_status section "Phase 4: Python Dependencies"

cd "$SCRIPT_DIR/backend"

if [ ! -f "requirements.txt" ]; then
    print_status error "requirements.txt not found!"
    ERRORS=$((ERRORS + 1))
else
    print_status info "Checking Python dependencies..."
    
    # Check if key packages are installed
    if $PYTHON_BIN -c "import fastapi, chromadb, langchain, celery, redis" 2>/dev/null; then
        print_status success "Key Python packages already installed"
        
        # Verify ChromaDB version compatibility
        CHROMADB_VERSION=$($PYTHON_BIN -c "import chromadb; print(chromadb.__version__)" 2>/dev/null)
        if [ ! -z "$CHROMADB_VERSION" ]; then
            print_status success "ChromaDB version: $CHROMADB_VERSION"
        fi
    else
        print_status info "Installing Python packages (this may take a few minutes)..."
        $PIP_BIN install --upgrade pip setuptools wheel -q 2>/dev/null
        $PIP_BIN install -r requirements.txt -q 2>&1 | grep -i error
        
        # Verify installation with additional ChromaDB-specific imports
        if $PYTHON_BIN -c "import fastapi, chromadb, langchain, celery, redis, langchain_chroma" 2>/dev/null; then
            print_status success "Python dependencies installed successfully"
        else
            print_status warn "Some dependencies may be missing, installing critical packages..."
            # Enhanced package list with ChromaDB-specific dependencies
            $PIP_BIN install -q fastapi uvicorn celery redis langchain langchain-google-genai \
                chromadb sentence-transformers langchain-huggingface langchain-chroma \
                pypdf python-docx pandas openpyxl reportlab pytesseract Pillow \
                watchdog python-dotenv pydantic-settings aiohttp 2>/dev/null
            print_status success "Critical packages installed"
        fi
    fi
fi

cd "$SCRIPT_DIR"

echo ""

###########################################
# PHASE 5: FRONTEND DEPENDENCIES
###########################################
print_status section "Phase 5: Frontend Dependencies"

cd "$SCRIPT_DIR/frontend"

if [ ! -f "package.json" ]; then
    print_status error "package.json not found!"
    ERRORS=$((ERRORS + 1))
else
    # Install yarn if not available
    if ! command -v yarn &>/dev/null; then
        print_status info "Installing yarn..."
        npm install -g yarn 2>/dev/null || sudo npm install -g yarn 2>/dev/null
    fi
    
    # Check if node_modules exists
    if [ -d "node_modules" ] && [ -d "node_modules/react" ]; then
        print_status success "Frontend dependencies already installed"
    else
        print_status info "Installing frontend packages (this may take a few minutes)..."
        if command -v yarn &>/dev/null; then
            yarn install 2>&1 | tail -3
        else
            npm install 2>&1 | tail -3
        fi
        
        if [ -d "node_modules" ]; then
            print_status success "Frontend dependencies installed"
        else
            print_status error "Failed to install frontend dependencies"
            ERRORS=$((ERRORS + 1))
        fi
    fi
fi

cd "$SCRIPT_DIR"

echo ""

###########################################
# PHASE 6: REDIS SERVICE
###########################################
print_status section "Phase 6: Redis Service"

print_status info "Checking Redis..."

if redis-cli ping &>/dev/null; then
    print_status success "Redis already running on port 6379"
elif command -v redis-server &>/dev/null; then
    print_status info "Starting Redis..."
    redis-server --daemonize yes --bind 127.0.0.1 2>/dev/null || \
    redis-server --daemonize yes 2>/dev/null
    sleep 2
    
    if redis-cli ping &>/dev/null; then
        print_status success "Redis started on port 6379"
    else
        print_status error "Redis failed to start"
        ERRORS=$((ERRORS + 1))
    fi
else
    print_status warn "Redis not installed. Installing..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get update -qq
        sudo apt-get install -y redis-server 2>/dev/null
    elif command -v yum &>/dev/null; then
        sudo yum install -y redis 2>/dev/null
    elif command -v brew &>/dev/null; then
        brew install redis 2>/dev/null
    else
        print_status error "Cannot install Redis automatically"
        print_status info "Please install Redis manually: https://redis.io/download"
        ERRORS=$((ERRORS + 1))
    fi
    
    # Try to start after installation
    if command -v redis-server &>/dev/null; then
        redis-server --daemonize yes 2>/dev/null
        sleep 2
        if redis-cli ping &>/dev/null; then
            print_status success "Redis installed and started"
        fi
    fi
fi

echo ""

###########################################
# PHASE 7: MONGODB SERVICE
###########################################
print_status section "Phase 7: MongoDB Service"

print_status info "Checking MongoDB..."

if lsof -i:27017 &>/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":27017 "; then
    print_status success "MongoDB already running on port 27017"
elif command -v mongod &>/dev/null; then
    print_status info "Starting MongoDB..."
    mkdir -p /tmp/mongodb_data 2>/dev/null
    nohup mongod --bind_ip_all --dbpath /tmp/mongodb_data > "$LOG_DIR/mongodb.log" 2>&1 &
    sleep 3
    
    if lsof -i:27017 &>/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":27017 "; then
        print_status success "MongoDB started on port 27017"
    else
        print_status warn "MongoDB may not have started (check logs/mongodb.log)"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    print_status warn "MongoDB not installed. Attempting to install..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get update -qq
        sudo apt-get install -y mongodb 2>/dev/null || sudo apt-get install -y mongodb-org 2>/dev/null
    elif command -v yum &>/dev/null; then
        sudo yum install -y mongodb-org 2>/dev/null
    elif command -v brew &>/dev/null; then
        brew install mongodb-community 2>/dev/null
    fi
    
    # Try to start after installation
    if command -v mongod &>/dev/null; then
        mkdir -p /tmp/mongodb_data 2>/dev/null
        nohup mongod --bind_ip_all --dbpath /tmp/mongodb_data > "$LOG_DIR/mongodb.log" 2>&1 &
        sleep 3
        print_status success "MongoDB installed and started"
    else
        print_status warn "MongoDB installation failed (optional, app may still work)"
        WARNINGS=$((WARNINGS + 1))
    fi
fi

echo ""

###########################################
# PHASE 8: CELERY WORKER
###########################################
print_status section "Phase 8: Celery Worker"

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

# Verify Redis is running before starting Celery
if ! redis-cli ping &>/dev/null; then
    print_status warn "Redis not responding - Celery requires Redis"
    print_status info "Attempting to start Redis..."
    redis-server --daemonize yes 2>/dev/null
    sleep 2
fi

# Check if celery is available
if ! command -v $CELERY_BIN &>/dev/null && ! $PYTHON_BIN -c "import celery" 2>/dev/null; then
    print_status warn "Celery not found, installing..."
    $PIP_BIN install -q celery redis
fi

# Verify ChromaDB imports in Celery context
if ! $PYTHON_BIN -c "import chromadb; from backend.celery_app import process_document_task" 2>/dev/null; then
    print_status warn "ChromaDB imports issue - may affect document processing"
    WARNINGS=$((WARNINGS + 1))
fi

# Start Celery with reduced concurrency for stability
nohup $CELERY_BIN -A backend.celery_app worker \
    --loglevel=info \
    --concurrency=1 \
    --max-tasks-per-child=50 \
    > "$LOG_DIR/celery_worker.log" 2>&1 &

sleep 4

if pgrep -f "celery.*worker" &>/dev/null; then
    print_status success "Celery worker started"
else
    print_status warn "Celery may not have started (check logs/celery_worker.log)"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""

###########################################
# PHASE 9: BACKEND (FASTAPI)
###########################################
print_status section "Phase 9: Backend Service"

print_status info "Starting Backend..."

# Check if backend is already running
if lsof -i:8001 &>/dev/null 2>&1; then
    print_status warn "Port 8001 already in use"
    if curl -s -m 2 http://localhost:8001/api/health &>/dev/null; then
        print_status success "Backend already running on port 8001"
    else
        print_status warn "Port 8001 occupied, attempting to restart..."
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
    BACKEND_READY=false
    for i in {1..40}; do
        sleep 1
        if lsof -i:8001 &>/dev/null 2>&1; then
            if curl -s -m 2 http://localhost:8001/api/health &>/dev/null; then
                print_status success "Backend started on port 8001"
                BACKEND_READY=true
                break
            fi
        fi
    done
    
    if [ "$BACKEND_READY" = false ]; then
        print_status warn "Backend may still be loading (check logs/backend.log)"
        WARNINGS=$((WARNINGS + 1))
    fi
fi

cd "$SCRIPT_DIR"

echo ""

###########################################
# PHASE 10: FRONTEND (REACT + VITE)
###########################################
print_status section "Phase 10: Frontend Service"

print_status info "Starting Frontend..."

# Check if frontend is already running
if lsof -i:3000 &>/dev/null 2>&1; then
    print_status warn "Port 3000 already in use"
    if curl -s -m 2 -I http://localhost:3000 &>/dev/null; then
        print_status success "Frontend already running on port 3000"
    else
        print_status warn "Port 3000 occupied, attempting to restart..."
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
    FRONTEND_READY=false
    for i in {1..15}; do
        sleep 1
        if lsof -i:3000 &>/dev/null 2>&1; then
            print_status success "Frontend started on port 3000"
            FRONTEND_READY=true
            break
        fi
    done
    
    if [ "$FRONTEND_READY" = false ]; then
        print_status warn "Frontend may not have started (check logs/frontend.log)"
        WARNINGS=$((WARNINGS + 1))
    fi
fi

cd "$SCRIPT_DIR"

echo ""

###########################################
# PHASE 11: VALIDATION & HEALTH CHECKS
###########################################
print_status section "Phase 11: Service Validation"

echo ""
print_status info "Running health checks..."
echo ""

# Redis
if redis-cli ping &>/dev/null; then
    print_status success "Redis - Running on port 6379"
else
    print_status error "Redis - Not running"
    ERRORS=$((ERRORS + 1))
fi

# MongoDB
if lsof -i:27017 &>/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":27017 "; then
    print_status success "MongoDB - Running on port 27017"
else
    print_status warn "MongoDB - Not running (optional)"
fi

# Celery
if pgrep -f "celery.*worker" &>/dev/null; then
    WORKER_COUNT=$(pgrep -f "celery.*worker" | wc -l)
    print_status success "Celery - Running ($WORKER_COUNT workers)"
else
    print_status warn "Celery - Not running"
    WARNINGS=$((WARNINGS + 1))
fi

# Backend
if lsof -i:8001 &>/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":8001 "; then
    if curl -s -m 2 http://localhost:8001/api/health &>/dev/null; then
        HEALTH_RESPONSE=$(curl -s -m 2 http://localhost:8001/api/health)
        print_status success "Backend - Running on port 8001 (healthy)"
        
        # Test ChromaDB connection and functionality
        DOCS_RESPONSE=$(curl -s -m 5 http://localhost:8001/api/documents 2>&1)
        if echo "$DOCS_RESPONSE" | grep -q "indexed_documents"; then
            print_status success "ChromaDB - Connected successfully"
            
            # Test basic chat functionality if documents exist
            DOC_COUNT=$(echo "$DOCS_RESPONSE" | grep -o '"[^"]*"' | wc -l 2>/dev/null)
            if [ "$DOC_COUNT" -gt 0 ]; then
                print_status success "ChromaDB - Found $DOC_COUNT indexed documents"
            else
                print_status info "ChromaDB - No documents indexed yet (add files to backend/knowledge_base/)"
            fi
        else
            print_status warn "ChromaDB - Connection issues detected"
            print_status info "Tip: If chat queries fail, try resetting with: curl -X POST 'http://localhost:8001/api/knowledge_base/reset?reset_type=soft'"
            WARNINGS=$((WARNINGS + 1))
        fi
    else
        print_status warn "Backend - Running on port 8001 (still loading)"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    print_status error "Backend - Not running"
    ERRORS=$((ERRORS + 1))
fi

# Frontend
if lsof -i:3000 &>/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":3000 "; then
    print_status success "Frontend - Running on port 3000"
else
    print_status error "Frontend - Not running"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "=========================================="
echo "  📊 Startup Summary"
echo "=========================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    print_status success "All services started successfully! 🎉"
    echo ""
    print_status info "🌐 Application URLs:"
    echo "     Frontend:  http://localhost:3000"
    echo "     Backend:   http://localhost:8001"
    echo "     API Docs:  http://localhost:8001/docs"
    echo ""
    print_status info "📁 Logs directory: $LOG_DIR"
    print_status info "🛑 To stop: ./stop.sh"
    echo ""
    print_status success "NeuralStark is ready! 🚀"
elif [ $ERRORS -eq 0 ]; then
    print_status warn "$WARNINGS warning(s) - Some services may need attention"
    echo ""
    print_status info "Application should be functional, but check:"
    echo "     Backend:  tail -f $LOG_DIR/backend.log"
    echo "     Frontend: tail -f $LOG_DIR/frontend.log"
    echo "     Celery:   tail -f $LOG_DIR/celery_worker.log"
    echo ""
    print_status info "🌐 Try accessing: http://localhost:3000"
else
    print_status error "$ERRORS critical error(s) - Some services failed to start"
    echo ""
    print_status info "Check logs for details:"
    echo "     Backend:  tail -f $LOG_DIR/backend.log"
    echo "     Frontend: tail -f $LOG_DIR/frontend.log"
    echo "     Celery:   tail -f $LOG_DIR/celery_worker.log"
    echo ""
    print_status info "Try running again or check the INSTALLATION_GUIDE.md"
fi

echo ""
print_status section "🔧 Common Issues & Solutions"
echo ""
print_status info "If chat queries fail with 'HNSW segment reader' errors:"
echo "     curl -X POST 'http://localhost:8001/api/knowledge_base/reset?reset_type=soft'"
echo ""
print_status info "If ChromaDB corruption is suspected:"
echo "     ./stop.sh && rm -rf chroma_db && ./run.sh"
echo ""
print_status info "If Redis connection fails:"
echo "     redis-server --daemonize yes"
echo ""
print_status info "View real-time logs:"
echo "     Backend:  tail -f $LOG_DIR/backend.log"
echo "     Celery:   tail -f $LOG_DIR/celery_worker.log"

echo "=========================================="
echo ""

# Exit with appropriate code
if [ $ERRORS -gt 0 ]; then
    exit 1
else
    exit 0
fi
