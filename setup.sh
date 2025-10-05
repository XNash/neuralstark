#!/bin/bash

###########################################
# NeuralStark - Environment Setup Script
# Run this once before starting the application
###########################################

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "  🔧 NeuralStark Setup & Validation"
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

ERRORS=0

###########################################
# 1. Create Required Directories
###########################################
print_status info "Creating required directories..."

mkdir -p backend/knowledge_base/internal 2>/dev/null
mkdir -p backend/knowledge_base/external 2>/dev/null
mkdir -p chroma_db 2>/dev/null
mkdir -p logs 2>/dev/null

# Verify directories were created
if [ -d "backend/knowledge_base/internal" ] && \
   [ -d "backend/knowledge_base/external" ] && \
   [ -d "chroma_db" ] && \
   [ -d "logs" ]; then
    print_status success "All required directories created"
else
    print_status error "Failed to create some directories"
    ERRORS=$((ERRORS + 1))
fi

###########################################
# 2. Check Python Installation
###########################################
print_status info "Checking Python installation..."

if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_status success "Python $PYTHON_VERSION found"
else
    print_status error "Python 3 not found. Please install Python 3.8+"
    ERRORS=$((ERRORS + 1))
fi

###########################################
# 3. Check Node.js Installation
###########################################
print_status info "Checking Node.js installation..."

if command -v node &>/dev/null; then
    NODE_VERSION=$(node --version 2>&1)
    print_status success "Node.js $NODE_VERSION found"
else
    print_status error "Node.js not found. Please install Node.js 16+"
    ERRORS=$((ERRORS + 1))
fi

###########################################
# 4. Check Redis
###########################################
print_status info "Checking Redis..."

if command -v redis-server &>/dev/null; then
    print_status success "Redis installed"
    
    # Try to ping Redis
    if redis-cli ping &>/dev/null 2>&1; then
        print_status success "Redis is running"
    else
        print_status warn "Redis installed but not running"
        print_status info "Start with: redis-server --daemonize yes"
    fi
else
    print_status warn "Redis not installed (required for Celery)"
    print_status info "Install with: sudo apt-get install redis-server (Ubuntu/Debian)"
    print_status info "           or: brew install redis (macOS)"
fi

###########################################
# 5. Check MongoDB
###########################################
print_status info "Checking MongoDB..."

if command -v mongod &>/dev/null; then
    print_status success "MongoDB installed"
    
    # Try to check if MongoDB is running
    if lsof -i:27017 &>/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":27017 "; then
        print_status success "MongoDB is running"
    else
        print_status warn "MongoDB installed but not running"
        print_status info "Start with: mongod --fork --logpath logs/mongodb.log --bind_ip_all"
    fi
else
    print_status warn "MongoDB not installed (recommended for document storage)"
    print_status info "Install with: sudo apt-get install mongodb (Ubuntu/Debian)"
    print_status info "           or: brew install mongodb-community (macOS)"
fi

###########################################
# 6. Check Backend Dependencies
###########################################
print_status info "Checking backend dependencies..."

if [ -f "backend/requirements.txt" ]; then
    print_status success "requirements.txt found"
    
    # Check if key packages are installed
    if python3 -c "import fastapi, chromadb, langchain, celery" 2>/dev/null; then
        print_status success "Key Python packages installed"
    else
        print_status warn "Some Python packages missing"
        print_status info "Install with: pip install -r backend/requirements.txt"
    fi
else
    print_status error "backend/requirements.txt not found"
    ERRORS=$((ERRORS + 1))
fi

###########################################
# 7. Check Frontend Dependencies
###########################################
print_status info "Checking frontend dependencies..."

if [ -f "frontend/package.json" ]; then
    print_status success "package.json found"
    
    if [ -d "frontend/node_modules" ]; then
        print_status success "node_modules directory exists"
    else
        print_status warn "node_modules not found"
        print_status info "Install with: cd frontend && yarn install"
    fi
else
    print_status error "frontend/package.json not found"
    ERRORS=$((ERRORS + 1))
fi

###########################################
# 8. Check Configuration Files
###########################################
print_status info "Checking configuration files..."

# Check for canvas templates
if [ -f "backend/canvas_templates.json" ] || [ -f "canvas_templates.json" ]; then
    print_status success "Canvas templates found"
else
    print_status warn "canvas_templates.json not found (optional for visualizations)"
fi

###########################################
# 9. Validate Directory Permissions
###########################################
print_status info "Validating directory permissions..."

if [ -w "chroma_db" ] && [ -w "logs" ] && \
   [ -w "backend/knowledge_base/internal" ] && \
   [ -w "backend/knowledge_base/external" ]; then
    print_status success "All directories are writable"
else
    print_status error "Some directories are not writable"
    print_status info "Fix with: chmod -R 755 chroma_db logs backend/knowledge_base"
    ERRORS=$((ERRORS + 1))
fi

###########################################
# 10. System Resources Check
###########################################
print_status info "Checking system resources..."

# Check available memory (Linux)
if command -v free &>/dev/null; then
    AVAILABLE_MEM_MB=$(free -m | awk 'NR==2{print $7}')
    if [ "$AVAILABLE_MEM_MB" -gt 500 ]; then
        print_status success "Sufficient memory available (${AVAILABLE_MEM_MB}MB)"
    else
        print_status warn "Low memory available (${AVAILABLE_MEM_MB}MB)"
    fi
fi

# Check disk space
if command -v df &>/dev/null; then
    AVAILABLE_DISK_GB=$(df -BG . | awk 'NR==2{print $4}' | sed 's/G//')
    if [ "$AVAILABLE_DISK_GB" -gt 1 ]; then
        print_status success "Sufficient disk space (${AVAILABLE_DISK_GB}GB available)"
    else
        print_status warn "Low disk space (${AVAILABLE_DISK_GB}GB available)"
    fi
fi

###########################################
# Summary
###########################################
echo ""
echo "=========================================="
echo "  📊 Setup Summary"
echo "=========================================="
echo ""

if [ $ERRORS -eq 0 ]; then
    print_status success "Setup validation passed!"
    echo ""
    print_status info "Next steps:"
    echo "  1. Install missing dependencies if any warnings shown above"
    echo "  2. Start services with: ./run.sh"
    echo "  3. Access application at: http://localhost:3000"
    echo ""
else
    print_status error "$ERRORS critical error(s) found"
    echo ""
    print_status info "Please fix the errors above before starting the application"
    echo ""
    exit 1
fi

echo "=========================================="
