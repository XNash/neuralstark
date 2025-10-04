#!/bin/bash

###########################################
# NeuralStark - Service Stop Script
# Version: 2.0
# Tested: October 4, 2025
###########################################

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  NeuralStark - Stopping All Services"
echo "=========================================="
echo ""

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo "  $1"
}

###########################################
# Stop Celery Worker
###########################################
echo "Stopping Celery worker..."
if pgrep -f "celery.*worker" > /dev/null; then
    pkill -f "celery.*worker" 2>/dev/null
    sleep 2
    
    # Force kill if still running
    if pgrep -f "celery.*worker" > /dev/null; then
        print_warning "Celery not responding, force killing..."
        pkill -9 -f "celery.*worker" 2>/dev/null
        sleep 1
    fi
    
    if ! pgrep -f "celery.*worker" > /dev/null; then
        print_success "Celery stopped"
    else
        print_warning "Celery may still be running"
    fi
else
    print_info "Celery not running"
fi

# Clean up PID file
rm -f /tmp/celery_worker.pid

echo ""

###########################################
# Stop Backend
###########################################
echo "Stopping Backend..."
if pgrep -f "uvicorn.*server:app" > /dev/null; then
    pkill -f "uvicorn.*server:app" 2>/dev/null
    sleep 2
    
    # Force kill if still running
    if pgrep -f "uvicorn.*server:app" > /dev/null; then
        print_warning "Backend not responding, force killing..."
        pkill -9 -f "uvicorn.*server:app" 2>/dev/null
        sleep 1
    fi
    
    if ! pgrep -f "uvicorn.*server:app" > /dev/null; then
        print_success "Backend stopped"
    else
        print_warning "Backend may still be running"
    fi
else
    print_info "Backend not running"
fi

echo ""

###########################################
# Stop Frontend
###########################################
echo "Stopping Frontend..."
if pgrep -f "vite" > /dev/null || pgrep -f "node.*vite" > /dev/null; then
    pkill -f "vite" 2>/dev/null
    pkill -f "node.*vite" 2>/dev/null
    sleep 2
    
    # Force kill if still running
    if pgrep -f "vite" > /dev/null || pgrep -f "node.*vite" > /dev/null; then
        print_warning "Frontend not responding, force killing..."
        pkill -9 -f "vite" 2>/dev/null
        pkill -9 -f "node.*vite" 2>/dev/null
        sleep 1
    fi
    
    if ! pgrep -f "vite" > /dev/null && ! pgrep -f "node.*vite" > /dev/null; then
        print_success "Frontend stopped"
    else
        print_warning "Frontend may still be running"
    fi
else
    print_info "Frontend not running"
fi

echo ""

###########################################
# Optional: Stop Redis (commented out by default)
###########################################
# Uncomment to stop Redis
# echo "Stopping Redis..."
# redis-cli shutdown 2>/dev/null
# print_success "Redis stopped"
# echo ""

###########################################
# Optional: Stop MongoDB (commented out by default)
###########################################
# Uncomment to stop MongoDB
# echo "Stopping MongoDB..."
# mongod --shutdown 2>/dev/null
# print_success "MongoDB stopped"
# echo ""

###########################################
# Verification
###########################################
echo "=========================================="
echo "  Verification"
echo "=========================================="
echo ""

REMAINING=$(ps aux | grep -E "celery.*worker|uvicorn.*server|vite" | grep -v grep | grep -v "8010" | wc -l)

if [ "$REMAINING" -eq 0 ]; then
    print_success "All application services stopped"
else
    print_warning "$REMAINING processes still running"
    print_info "Run 'ps aux | grep -E \"celery|uvicorn|vite\"' to check"
fi

echo ""
print_info "Note: Redis and MongoDB are left running by default"
print_info "      (they can be reused for next startup)"
echo ""
echo "=========================================="
print_success "Service shutdown complete"
echo "=========================================="
