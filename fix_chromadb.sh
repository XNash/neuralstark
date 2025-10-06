#!/bin/bash

###########################################
# NeuralStark ChromaDB Fix Script
# Fixes common ChromaDB HNSW index issues
###########################################

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "  🔧 NeuralStark ChromaDB Fix Script"
echo "  Resolves HNSW segment reader errors"
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

print_status info "Stopping all services..."

# Stop services
./stop.sh 2>/dev/null || {
    print_status warn "stop.sh not found, stopping services manually..."
    pkill -f "uvicorn.*server:app" 2>/dev/null
    pkill -f "celery.*worker" 2>/dev/null
    pkill -f "vite" 2>/dev/null
}

sleep 3

print_status info "Cleaning ChromaDB..."

# Remove corrupted ChromaDB
if [ -d "chroma_db" ]; then
    rm -rf chroma_db
    print_status success "Removed corrupted ChromaDB directory"
fi

# Recreate directory with proper permissions
mkdir -p chroma_db
chmod 755 chroma_db

print_status success "Recreated ChromaDB directory"

print_status info "Verifying Redis..."

# Ensure Redis is running
if ! redis-cli ping &>/dev/null; then
    print_status warn "Redis not running, starting..."
    if command -v redis-server &>/dev/null; then
        redis-server --daemonize yes
        sleep 2
        if redis-cli ping &>/dev/null; then
            print_status success "Redis started"
        else
            print_status error "Failed to start Redis"
            exit 1
        fi
    else
        print_status error "Redis not installed. Please install Redis first."
        exit 1
    fi
else
    print_status success "Redis is running"
fi

print_status info "Installing/updating Python dependencies..."

# Find Python and pip
if [ -f "/root/.venv/bin/python3" ]; then
    PYTHON_BIN="/root/.venv/bin/python3"
    PIP_BIN="/root/.venv/bin/pip"
elif [ -f "$SCRIPT_DIR/.venv/bin/python3" ]; then
    PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python3"
    PIP_BIN="$SCRIPT_DIR/.venv/bin/pip"
else
    PYTHON_BIN="python3"
    PIP_BIN="pip3"
fi

# Ensure key packages are installed
$PIP_BIN install -q chromadb langchain-chroma sentence-transformers redis celery 2>/dev/null

print_status success "Dependencies verified"

print_status info "Starting services..."

# Start services using supervisor if available, otherwise use run.sh
if command -v supervisorctl &>/dev/null; then
    print_status info "Using supervisor to restart services..."
    sudo supervisorctl restart backend frontend 2>/dev/null || {
        print_status warn "Supervisor not available, using run.sh..."
        ./run.sh
    }
else
    print_status info "Starting services with run.sh..."
    ./run.sh
fi

# Wait for backend to be ready
print_status info "Waiting for backend to initialize..."
sleep 15

# Check if services are running
if curl -s -m 5 http://localhost:8001/api/health &>/dev/null; then
    print_status success "Backend is running"
    
    # Test ChromaDB connection
    DOCS_RESPONSE=$(curl -s -m 5 http://localhost:8001/api/documents 2>&1)
    if echo "$DOCS_RESPONSE" | grep -q "indexed_documents"; then
        print_status success "ChromaDB connection verified"
        
        # Check if documents need to be re-indexed
        DOC_FILES=$(find backend/knowledge_base -name "*.pdf" -o -name "*.docx" -o -name "*.txt" -o -name "*.xlsx" 2>/dev/null | wc -l)
        if [ "$DOC_FILES" -gt 0 ]; then
            print_status info "Found $DOC_FILES documents that need re-indexing..."
            curl -s -X POST "http://localhost:8001/api/knowledge_base/reset?reset_type=soft" > /dev/null
            print_status success "Document re-indexing initiated"
        fi
        
    else
        print_status error "ChromaDB connection failed"
        exit 1
    fi
else
    print_status error "Backend failed to start"
    print_status info "Check logs: tail -f logs/backend.log"
    exit 1
fi

echo ""
echo "=========================================="
print_status success "ChromaDB Fix Complete! 🎉"
echo ""
print_status info "Test the fix:"
echo '     curl -X POST "http://localhost:8001/api/chat" \'
echo '       -H "Content-Type: application/json" \'
echo '       -d '"'"'{"query": "What documents do you have?"}'"'"
echo ""
print_status info "Access your application:"
echo "     Frontend: http://localhost:3000"
echo "     Backend:  http://localhost:8001"
echo "=========================================="