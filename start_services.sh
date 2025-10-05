#!/bin/bash

###########################################
# NeuralStark - Service Startup Script
# Version: 3.0 (Supervisor Compatible)
# Updated: January 2025
###########################################

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  NeuralStark - Starting All Services"
echo "=========================================="
echo ""

###########################################
# Function: Print colored messages
###########################################
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

###########################################
# 1. Create Required Directories
###########################################
echo "Step 1: Creating required directories..."
mkdir -p /app/backend/knowledge_base/internal
mkdir -p /app/backend/knowledge_base/external
mkdir -p /app/chroma_db
mkdir -p /var/log
print_success "Directories created"
echo ""

###########################################
# 2. Install and Start Redis
###########################################
echo "Step 2: Setting up Redis..."
if ! command -v redis-server &> /dev/null; then
    print_warning "Redis not found. Installing..."
    apt-get update -qq && apt-get install -y redis-server -qq
    print_success "Redis installed"
fi

if redis-cli ping 2>/dev/null | grep -q "PONG"; then
    print_success "Redis already running on port 6379"
else
    redis-server --daemonize yes --bind 127.0.0.1
    sleep 2
    if redis-cli ping 2>/dev/null | grep -q "PONG"; then
        print_success "Redis started successfully on port 6379"
    else
        print_error "Failed to start Redis"
        exit 1
    fi
fi
echo ""

###########################################
# 3. Verify MongoDB (Managed by Supervisor)
###########################################
echo "Step 3: Verifying MongoDB..."
if sudo supervisorctl status mongodb | grep -q "RUNNING"; then
    print_success "MongoDB running (managed by supervisor)"
elif mongosh --eval "db.runCommand({ ping: 1 }).ok" --quiet 2>/dev/null | grep -q "1"; then
    print_success "MongoDB running on port 27017"
else
    print_warning "MongoDB status unclear - supervisor will manage it"
fi
echo ""

###########################################
# 4. Start Celery Worker
###########################################
echo "Step 4: Starting Celery worker..."

# Stop existing Celery workers
if pgrep -f "celery.*worker" > /dev/null; then
    print_warning "Stopping existing Celery workers..."
    pkill -9 -f "celery.*worker" 2>/dev/null || true
    sleep 2
fi

# Clean up PID file
rm -f /tmp/celery_worker.pid

# Start Celery
cd /app
export PYTHONPATH=/app:$PYTHONPATH
nohup celery -A backend.celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    --max-tasks-per-child=50 \
    > /var/log/celery_worker.log 2>&1 &

# Wait and verify
sleep 5

CELERY_COUNT=$(pgrep -f "celery.*worker" | wc -l)
if [ "$CELERY_COUNT" -ge 1 ]; then
    print_success "Celery worker started ($CELERY_COUNT processes)"
else
    print_error "Failed to start Celery worker"
    print_info "Check logs: tail -f /var/log/celery_worker.log"
    exit 1
fi
echo ""

###########################################
# 5. Restart Supervisor Services
###########################################
echo "Step 5: Restarting supervisor services..."

# Restart backend
print_info "Restarting backend..."
sudo supervisorctl restart backend > /dev/null 2>&1
sleep 3

if sudo supervisorctl status backend | grep -q "RUNNING"; then
    print_success "Backend running on port 8001 (via supervisor)"
else
    print_error "Backend failed to start"
    print_info "Check logs: tail -f /var/log/supervisor/backend.err.log"
fi

# Restart frontend
print_info "Restarting frontend..."
sudo supervisorctl restart frontend > /dev/null 2>&1
sleep 5

if sudo supervisorctl status frontend | grep -q "RUNNING"; then
    print_success "Frontend running on port 3000 (via supervisor)"
else
    print_error "Frontend failed to start"
    print_info "Check logs: tail -f /var/log/supervisor/frontend.err.log"
fi

echo ""

###########################################
# 6. Health Checks
###########################################
echo "Step 6: Performing health checks..."

# Backend health check
print_info "Checking backend health..."
sleep 3
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    print_success "Backend API healthy (HTTP 200)"
elif [ "$HTTP_CODE" = "000" ]; then
    print_warning "Backend not yet responding (still starting up)"
else
    print_warning "Backend health check returned HTTP $HTTP_CODE"
fi

# Frontend health check
print_info "Checking frontend..."
sleep 2
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    print_success "Frontend accessible (HTTP 200)"
elif [ "$HTTP_CODE" = "000" ]; then
    print_warning "Frontend not yet responding (still starting up)"
else
    print_warning "Frontend returned HTTP $HTTP_CODE"
fi

echo ""

###########################################
# 7. Final Service Status
###########################################
echo "=========================================="
echo "  Service Status Summary"
echo "=========================================="
echo ""

# Redis
echo -n "Redis:        "
if redis-cli ping 2>/dev/null | grep -q "PONG"; then
    print_success "Running on port 6379"
else
    print_error "Not responding"
fi

# MongoDB
echo -n "MongoDB:      "
if sudo supervisorctl status mongodb | grep -q "RUNNING"; then
    print_success "Running on port 27017"
elif mongosh --eval "db.runCommand({ ping: 1 }).ok" --quiet 2>/dev/null | grep -q "1"; then
    print_success "Running on port 27017"
else
    print_error "Not responding"
fi

# Celery
echo -n "Celery:       "
CELERY_COUNT=$(pgrep -f "celery.*worker" | wc -l)
if [ "$CELERY_COUNT" -ge 1 ]; then
    print_success "Running ($CELERY_COUNT workers)"
else
    print_error "Not running"
fi

# Backend
echo -n "Backend:      "
if sudo supervisorctl status backend | grep -q "RUNNING"; then
    print_success "Running on port 8001"
else
    print_error "Not running"
fi

# Frontend
echo -n "Frontend:     "
if sudo supervisorctl status frontend | grep -q "RUNNING"; then
    print_success "Running on port 3000"
else
    print_error "Not running"
fi

echo ""
echo "=========================================="
echo "  All Services Started!"
echo "=========================================="
echo ""
print_info "Access Points:"
print_info "  • Frontend:   http://localhost:3000"
print_info "  • Backend:    http://localhost:8001"
print_info "  • API Docs:   http://localhost:8001/docs"
echo ""
print_info "Service Logs:"
print_info "  • Backend:    tail -f /var/log/supervisor/backend.err.log"
print_info "  • Frontend:   tail -f /var/log/supervisor/frontend.err.log"
print_info "  • Celery:     tail -f /var/log/celery_worker.log"
print_info "  • MongoDB:    tail -f /var/log/mongodb.err.log"
echo ""
print_info "Service Control:"
print_info "  • Restart all:      sudo supervisorctl restart all"
print_info "  • Restart backend:  sudo supervisorctl restart backend"
print_info "  • Restart frontend: sudo supervisorctl restart frontend"
print_info "  • Status check:     sudo supervisorctl status"
echo ""
print_success "System is ready to use!"
echo "=========================================="