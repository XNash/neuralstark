#!/bin/bash

###########################################
# NeuralStark - Optimized Stop Script
# Version: 3.1
###########################################

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "  🛑 Stopping NeuralStark"
echo "=========================================="
echo ""

# Function to print status
print_status() {
    case $1 in
        success) echo -e "${GREEN}✓${NC} $2" ;;
        info)    echo -e "${BLUE}ℹ${NC} $2" ;;
        warn)    echo -e "${YELLOW}⚠${NC} $2" ;;
    esac
}

###########################################
# Stop Celery Worker
###########################################
print_status info "Stopping Celery worker..."

if pgrep -f "celery.*worker" &>/dev/null; then
    pkill -f "celery.*worker" 2>/dev/null
    sleep 2
    
    # Force kill if still running
    if pgrep -f "celery.*worker" &>/dev/null; then
        pkill -9 -f "celery.*worker" 2>/dev/null
        sleep 1
    fi
    
    if ! pgrep -f "celery.*worker" &>/dev/null; then
        print_status success "Celery stopped"
    else
        print_status warn "Celery may still be running"
    fi
else
    print_status info "Celery not running"
fi

# Clean up PID file
rm -f /tmp/celery_worker.pid 2>/dev/null

echo ""
echo "=========================================="
print_status success "Celery services stopped"
echo "=========================================="
echo ""

# Information about supervisor services
print_status info "Note: Backend, Frontend, and MongoDB are managed by supervisor"
print_status info "      and will continue running unless explicitly stopped."
echo ""

print_status info "To stop supervisor services:"
echo "      sudo supervisorctl stop backend frontend"
echo ""

print_status info "To stop Redis:"
echo "      redis-cli shutdown"
echo ""

print_status info "To restart everything:"
echo "      ./run.sh"
echo ""