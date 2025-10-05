#!/bin/bash

###########################################
# NeuralStark - Quick Start Script
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
echo "  NeuralStark - Quick Start"
echo "=========================================="
echo ""

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Create required directories
print_info "Setting up directories..."
mkdir -p /app/backend/knowledge_base/internal
mkdir -p /app/backend/knowledge_base/external
mkdir -p /app/chroma_db
mkdir -p /var/log

# Start Redis if not running
print_info "Checking Redis..."
if ! redis-cli ping 2>/dev/null | grep -q "PONG"; then
    if ! command -v redis-server &> /dev/null; then
        print_info "Installing Redis..."
        apt-get update -qq && apt-get install -y redis-server -qq
    fi
    redis-server --daemonize yes --bind 127.0.0.1
    sleep 2
fi

if redis-cli ping 2>/dev/null | grep -q "PONG"; then
    print_success "Redis running"
else
    print_error "Redis failed to start"
    exit 1
fi

# Start Celery worker
print_info "Starting Celery worker..."
pkill -9 -f "celery.*worker" 2>/dev/null || true
sleep 1
rm -f /tmp/celery_worker.pid

cd /app
export PYTHONPATH=/app:$PYTHONPATH
nohup celery -A backend.celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    --max-tasks-per-child=50 \
    > /var/log/celery_worker.log 2>&1 &

sleep 4

if pgrep -f "celery.*worker" > /dev/null; then
    print_success "Celery worker running"
else
    print_error "Celery failed to start"
    exit 1
fi

# Restart supervisor services
print_info "Restarting application services..."
sudo supervisorctl restart backend frontend > /dev/null 2>&1

sleep 5

# Check status
echo ""
echo "=========================================="
echo "  Service Status"
echo "=========================================="
echo ""

if redis-cli ping 2>/dev/null | grep -q "PONG"; then
    echo -e "Redis:     ${GREEN}✓ Running${NC}"
else
    echo -e "Redis:     ${RED}✗ Not running${NC}"
fi

if sudo supervisorctl status mongodb | grep -q "RUNNING"; then
    echo -e "MongoDB:   ${GREEN}✓ Running${NC}"
else
    echo -e "MongoDB:   ${YELLOW}⚠ Check supervisor${NC}"
fi

if pgrep -f "celery.*worker" > /dev/null; then
    echo -e "Celery:    ${GREEN}✓ Running${NC}"
else
    echo -e "Celery:    ${RED}✗ Not running${NC}"
fi

if sudo supervisorctl status backend | grep -q "RUNNING"; then
    echo -e "Backend:   ${GREEN}✓ Running${NC} (http://localhost:8001)"
else
    echo -e "Backend:   ${RED}✗ Not running${NC}"
fi

if sudo supervisorctl status frontend | grep -q "RUNNING"; then
    echo -e "Frontend:  ${GREEN}✓ Running${NC} (http://localhost:3000)"
else
    echo -e "Frontend:  ${RED}✗ Not running${NC}"
fi

echo ""
echo "=========================================="
print_success "NeuralStark is ready!"
echo "=========================================="
echo ""
print_info "Access the application at: http://localhost:3000"
print_info "API documentation at: http://localhost:8001/docs"
echo ""
print_info "View logs:"
print_info "  • Backend:  tail -f /var/log/supervisor/backend.err.log"
print_info "  • Frontend: tail -f /var/log/supervisor/frontend.err.log"
print_info "  • Celery:   tail -f /var/log/celery_worker.log"
echo ""