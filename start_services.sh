#!/bin/bash

###########################################
# NeuralStark - Robust Service Startup Script
# Version: 2.0
# Tested: October 4, 2025
###########################################

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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
    echo "  $1"
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
# 2. Start Redis
###########################################
echo "Step 2: Starting Redis..."
if redis-cli ping 2>/dev/null | grep -q "PONG"; then
    print_success "Redis already running"
else
    redis-server --daemonize yes
    sleep 2
    if redis-cli ping 2>/dev/null | grep -q "PONG"; then
        print_success "Redis started successfully"
    else
        print_error "Failed to start Redis"
        exit 1
    fi
fi
echo ""

###########################################
# 3. Verify MongoDB
###########################################
echo "Step 3: Verifying MongoDB..."
if mongosh --eval "db.runCommand({ ping: 1 }).ok" --quiet 2>/dev/null | grep -q "1"; then
    VERSION=$(mongosh --eval "db.version()" --quiet 2>/dev/null)
    print_success "MongoDB running (v$VERSION)"
else
    print_warning "MongoDB not accessible"
    print_info "Attempting to start MongoDB..."
    mongod --fork --logpath /var/log/mongodb.log --bind_ip_all 2>/dev/null || print_info "MongoDB may be managed by supervisor"
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
# 5. Start Backend (FastAPI)
###########################################
echo "Step 5: Starting Backend API..."

# Stop existing backend
if pgrep -f "uvicorn.*server:app.*8001" > /dev/null; then
    print_warning "Stopping existing backend..."
    pkill -9 -f "uvicorn.*server:app.*8001" 2>/dev/null || true
    sleep 2
fi

# Check if port 8001 is free
if lsof -i:8001 > /dev/null 2>&1 || netstat -tlnp 2>/dev/null | grep -q ":8001 "; then
    print_warning "Port 8001 in use, cleaning up..."
    fuser -k 8001/tcp 2>/dev/null || true
    sleep 2
fi

# Start backend
cd /app/backend
nohup uvicorn server:app \
    --host 0.0.0.0 \
    --port 8001 \
    --reload \
    > /var/log/backend.log 2>&1 &

# Wait and verify
sleep 5

if pgrep -f "uvicorn.*server:app" > /dev/null; then
    print_success "Backend process started"
else
    print_error "Backend process failed to start"
    print_info "Check logs: tail -f /var/log/backend.log"
    exit 1
fi

# Health check
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health 2>/dev/null)
if [ "$HTTP_CODE" = "200" ]; then
    print_success "Backend API healthy (HTTP 200)"
else
    print_error "Backend health check failed (HTTP $HTTP_CODE)"
    print_info "Check logs: tail -f /var/log/backend.log"
    exit 1
fi
echo ""

###########################################
# 6. Start Frontend (React + Vite)
###########################################
echo "Step 6: Starting Frontend..."

# Stop existing frontend
if pgrep -f "vite.*3000" > /dev/null || pgrep -f "node.*vite" > /dev/null; then
    print_warning "Stopping existing frontend..."
    pkill -9 -f "vite.*3000" 2>/dev/null || true
    pkill -9 -f "node.*vite" 2>/dev/null || true
    sleep 2
fi

# Check if port 3000 is free
if lsof -i:3000 > /dev/null 2>&1 || netstat -tlnp 2>/dev/null | grep -q ":3000 "; then
    print_warning "Port 3000 in use, cleaning up..."
    fuser -k 3000/tcp 2>/dev/null || true
    sleep 2
fi

# Check dependencies
if [ ! -d "/app/frontend/node_modules" ]; then
    print_warning "Installing frontend dependencies..."
    cd /app/frontend
    yarn install --silent
fi

# Start frontend
cd /app/frontend
nohup yarn start > /var/log/frontend.log 2>&1 &

# Wait and verify
print_info "Waiting for frontend to start (10 seconds)..."
sleep 10

if pgrep -f "vite.*3000" > /dev/null || pgrep -f "node.*vite" > /dev/null; then
    print_success "Frontend process started"
else
    print_error "Frontend process failed to start"
    print_info "Check logs: tail -f /var/log/frontend.log"
    exit 1
fi

# HTTP check
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null)
if [ "$HTTP_CODE" = "200" ]; then
    print_success "Frontend accessible (HTTP 200)"
else
    print_warning "Frontend returned HTTP $HTTP_CODE (may be normal during startup)"
fi
echo ""

###########################################
# 7. Final Verification
###########################################
echo "=========================================="
echo "  Service Verification"
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
if mongosh --eval "db.runCommand({ ping: 1 }).ok" --quiet 2>/dev/null | grep -q "1"; then
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
if curl -s http://localhost:8001/health 2>/dev/null | grep -q "ok"; then
    print_success "Running on port 8001"
else
    print_error "Not responding"
fi

# Frontend
echo -n "Frontend:     "
if curl -s -I http://localhost:3000 2>/dev/null | grep -q "HTTP"; then
    print_success "Running on port 3000"
else
    print_error "Not responding"
fi

echo ""
echo "=========================================="
echo "  All Services Started Successfully!"
echo "=========================================="
echo ""
print_info "Access points:"
print_info "  • Frontend:   http://localhost:3000"
print_info "  • Backend:    http://localhost:8001"
print_info "  • API Docs:   http://localhost:8001/docs"
echo ""
print_info "Logs:"
print_info "  • Backend:    tail -f /var/log/backend.log"
print_info "  • Frontend:   tail -f /var/log/frontend.log"
print_info "  • Celery:     tail -f /var/log/celery_worker.log"
echo ""
print_success "System is ready to use!"
echo "=========================================="
