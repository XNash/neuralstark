#!/bin/bash

###########################################
# NeuralStark - Service Stop Script
# Version: 3.0 (Supervisor Compatible)
# Updated: January 2025
###########################################

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  NeuralStark - Stopping Services"
echo "=========================================="
echo ""

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

###########################################
# Stop Celery Worker (Not managed by supervisor)
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
        print_success "Celery worker stopped"
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
# Optional: Stop Supervisor Services
###########################################
echo "Supervisor Services (managed by system):"
print_info "Backend and Frontend are managed by supervisor"
print_info "They will auto-restart if stopped"
echo ""

read -p "Do you want to stop supervisor services? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping supervisor services..."
    
    sudo supervisorctl stop backend > /dev/null 2>&1
    if sudo supervisorctl status backend | grep -q "STOPPED"; then
        print_success "Backend stopped"
    else
        print_warning "Backend may still be running"
    fi
    
    sudo supervisorctl stop frontend > /dev/null 2>&1
    if sudo supervisorctl status frontend | grep -q "STOPPED"; then
        print_success "Frontend stopped"
    else
        print_warning "Frontend may still be running"
    fi
    
    echo ""
    print_info "To restart: sudo supervisorctl start all"
else
    print_info "Supervisor services left running"
fi

echo ""

###########################################
# Optional: Stop Redis
###########################################
read -p "Do you want to stop Redis? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    redis-cli shutdown 2>/dev/null
    print_success "Redis stopped"
else
    print_info "Redis left running for next startup"
fi

echo ""

###########################################
# Verification
###########################################
echo "=========================================="
echo "  Service Status"
echo "=========================================="
echo ""

# Check Celery
CELERY_COUNT=$(pgrep -f "celery.*worker" | wc -l)
echo -n "Celery:       "
if [ "$CELERY_COUNT" -eq 0 ]; then
    print_success "Stopped"
else
    print_warning "$CELERY_COUNT processes still running"
fi

# Check supervisor services
echo -n "Backend:      "
if sudo supervisorctl status backend | grep -q "STOPPED"; then
    print_success "Stopped"
elif sudo supervisorctl status backend | grep -q "RUNNING"; then
    print_info "Running (managed by supervisor)"
else
    print_info "Status unknown"
fi

echo -n "Frontend:     "
if sudo supervisorctl status frontend | grep -q "STOPPED"; then
    print_success "Stopped"
elif sudo supervisorctl status frontend | grep -q "RUNNING"; then
    print_info "Running (managed by supervisor)"
else
    print_info "Status unknown"
fi

# Check Redis
echo -n "Redis:        "
if redis-cli ping 2>/dev/null | grep -q "PONG"; then
    print_info "Running"
else
    print_success "Stopped"
fi

# Check MongoDB
echo -n "MongoDB:      "
if sudo supervisorctl status mongodb | grep -q "RUNNING"; then
    print_info "Running (managed by supervisor)"
else
    print_success "Stopped/Not running"
fi

echo ""
echo "=========================================="
print_success "Service shutdown complete"
echo "=========================================="
echo ""
print_info "Note: Supervisor-managed services (backend, frontend, mongodb)"
print_info "      will auto-restart unless explicitly stopped via supervisor"
echo ""