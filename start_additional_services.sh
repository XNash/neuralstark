#!/bin/bash

###########################################
# NeuralStark - Additional Services Script
# For Kubernetes/Supervisor Environment
# Starts Redis and Celery only
###########################################

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "  🚀 Starting Additional Services"
echo "  (Redis & Celery for NeuralStark)"
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

###########################################
# 1. Start Redis
###########################################
print_status info "Starting Redis..."

if redis-cli ping &>/dev/null; then
    print_status success "Redis already running on port 6379"
else
    if ! command -v redis-server &>/dev/null; then
        print_status error "Redis not found. Installing..."
        apt-get update > /dev/null 2>&1
        apt-get install -y redis-server > /dev/null 2>&1
    fi
    
    redis-server --daemonize yes --bind 127.0.0.1 2>/dev/null
    sleep 2
    
    if redis-cli ping &>/dev/null; then
        print_status success "Redis started on port 6379"
    else
        print_status error "Redis failed to start"
        exit 1
    fi
fi

###########################################
# 2. Start Celery Worker
###########################################
print_status info "Starting Celery worker..."

# Stop existing workers
pkill -9 -f "celery.*worker" 2>/dev/null
rm -f /tmp/celery_worker.pid
sleep 1

# Set Python path
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Start Celery
nohup celery -A backend.celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    --max-tasks-per-child=50 \
    > /var/log/celery_worker.log 2>&1 &

sleep 5

if pgrep -f "celery.*worker" &>/dev/null; then
    print_status success "Celery worker started"
else
    print_status error "Celery failed to start"
    print_status info "Check logs: tail -f /var/log/celery_worker.log"
    exit 1
fi

###########################################
# 3. Status Summary
###########################################
echo ""
echo "=========================================="
echo "  📊 Service Status"
echo "=========================================="
echo ""

# Redis
if redis-cli ping &>/dev/null; then
    echo -e "${GREEN}✓${NC} Redis       - Running on port 6379"
else
    echo -e "${RED}✗${NC} Redis       - Not running"
fi

# Celery
if pgrep -f "celery.*worker" &>/dev/null; then
    echo -e "${GREEN}✓${NC} Celery      - Running"
else
    echo -e "${RED}✗${NC} Celery      - Not running"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✓ Additional services started!${NC}"
echo ""
print_status info "📁 Celery logs: /var/log/celery_worker.log"
print_status info "🛑 To stop: ./stop_additional_services.sh"
echo "=========================================="
