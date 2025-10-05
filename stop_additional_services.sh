#!/bin/bash

###########################################
# NeuralStark - Stop Additional Services
# For Kubernetes/Supervisor Environment
# Stops Redis and Celery only
###########################################

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================="
echo "  🛑 Stopping Additional Services"
echo "  (Redis & Celery)"
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

stopped_count=0

###########################################
# 1. Stop Celery Worker
###########################################
print_status info "Stopping Celery worker..."

if pgrep -f "celery.*worker" &>/dev/null; then
    pkill -f "celery.*worker" 2>/dev/null
    sleep 2
    
    # Force kill if needed
    if pgrep -f "celery.*worker" &>/dev/null; then
        pkill -9 -f "celery.*worker" 2>/dev/null
        sleep 1
    fi
    
    if ! pgrep -f "celery.*worker" &>/dev/null; then
        print_status success "Celery stopped"
        ((stopped_count++))
    else
        print_status warn "Celery may still be running"
    fi
else
    print_status info "Celery not running"
fi

# Clean up PID file
rm -f /tmp/celery_worker.pid 2>/dev/null

###########################################
# 2. Stop Redis
###########################################
print_status info "Stopping Redis..."

if redis-cli ping &>/dev/null; then
    redis-cli shutdown 2>/dev/null
    sleep 1
    if ! redis-cli ping &>/dev/null; then
        print_status success "Redis stopped"
        ((stopped_count++))
    else
        print_status warn "Redis may still be running"
    fi
else
    print_status info "Redis not running"
fi

###########################################
# 3. Final Status
###########################################
echo ""
echo "=========================================="
echo "  📊 Final Status"
echo "=========================================="
echo ""

if pgrep -f "celery.*worker" &>/dev/null; then
    echo -e "${YELLOW}⚠${NC} Celery      - Still running"
else
    echo -e "${GREEN}✓${NC} Celery      - Stopped"
fi

if redis-cli ping &>/dev/null; then
    echo -e "${YELLOW}⚠${NC} Redis       - Still running"
else
    echo -e "${GREEN}✓${NC} Redis       - Stopped"
fi

echo ""
echo "=========================================="

if [ "$stopped_count" -gt 0 ]; then
    print_status success "Stopped $stopped_count service(s)"
else
    print_status info "No services were running"
fi

echo "=========================================="
echo ""
print_status info "Note: MongoDB, Backend, and Frontend are managed by supervisor"
print_status info "Use 'sudo supervisorctl' to control those services"
echo ""
