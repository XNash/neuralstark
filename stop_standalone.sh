#!/bin/bash

###########################################
# NeuralStark - Standalone Stop Script
# Version: 5.0
###########################################

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================="
echo "  🛑 Stopping NeuralStark (Standalone)"
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
# 1. Stop Frontend
###########################################
print_status info "Stopping Frontend..."

if pgrep -f "vite.*3000" &>/dev/null || pgrep -f "node.*vite" &>/dev/null; then
    pkill -f "vite.*3000" 2>/dev/null
    pkill -f "node.*vite" 2>/dev/null
    sleep 2
    
    # Force kill if needed
    if pgrep -f "vite" &>/dev/null; then
        pkill -9 -f "vite" 2>/dev/null
        sleep 1
    fi
    
    if ! pgrep -f "vite" &>/dev/null; then
        print_status success "Frontend stopped"
        ((stopped_count++))
    else
        print_status warn "Frontend may still be running"
    fi
else
    print_status info "Frontend not running"
fi

###########################################
# 2. Stop Backend
###########################################
print_status info "Stopping Backend..."

# Only stop if not managed by supervisor
if ! sudo supervisorctl status backend 2>/dev/null | grep -q "RUNNING"; then
    if pgrep -f "uvicorn.*server:app" &>/dev/null; then
        pkill -f "uvicorn.*server:app" 2>/dev/null
        sleep 2
        
        # Force kill if needed
        if pgrep -f "uvicorn.*server:app" &>/dev/null; then
            pkill -9 -f "uvicorn.*server:app" 2>/dev/null
            sleep 1
        fi
        
        if ! pgrep -f "uvicorn.*server:app" &>/dev/null; then
            print_status success "Backend stopped"
            ((stopped_count++))
        else
            print_status warn "Backend may still be running"
        fi
    else
        print_status info "Backend not running"
    fi
else
    print_status info "Backend managed by supervisor (not stopped)"
fi

###########################################
# 3. Stop Celery Worker
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
# 4. Stop Redis
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
# 5. Stop MongoDB (optional)
###########################################
echo ""
read -p "Stop MongoDB? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Only stop if not managed by supervisor
    if ! sudo supervisorctl status mongodb 2>/dev/null | grep -q "RUNNING"; then
        if lsof -i:27017 &>/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":27017 "; then
            print_status info "Stopping MongoDB..."
            if command -v mongod &>/dev/null; then
                mongod --shutdown 2>/dev/null || pkill -f mongod 2>/dev/null
            else
                pkill -f mongod 2>/dev/null
            fi
            sleep 2
            
            if ! lsof -i:27017 &>/dev/null 2>&1 && ! netstat -tuln 2>/dev/null | grep -q ":27017 "; then
                print_status success "MongoDB stopped"
                ((stopped_count++))
            fi
        fi
    else
        print_status info "MongoDB managed by supervisor (not stopped)"
    fi
else
    print_status info "Keeping MongoDB running"
fi

###########################################
# 6. Final Status
###########################################
echo ""
echo "=========================================="
echo "  📊 Final Status"
echo "=========================================="
echo ""

# Check remaining processes
if pgrep -f "vite" &>/dev/null; then
    echo -e "${YELLOW}⚠${NC} Frontend    - Still running"
else
    echo -e "${GREEN}✓${NC} Frontend    - Stopped"
fi

if pgrep -f "uvicorn.*server:app" &>/dev/null; then
    if sudo supervisorctl status backend 2>/dev/null | grep -q "RUNNING"; then
        echo -e "${BLUE}ℹ${NC} Backend     - Running (managed by supervisor)"
    else
        echo -e "${YELLOW}⚠${NC} Backend     - Still running"
    fi
else
    echo -e "${GREEN}✓${NC} Backend     - Stopped"
fi

if pgrep -f "celery.*worker" &>/dev/null; then
    echo -e "${YELLOW}⚠${NC} Celery      - Still running"
else
    echo -e "${GREEN}✓${NC} Celery      - Stopped"
fi

if redis-cli ping &>/dev/null; then
    echo -e "${BLUE}ℹ${NC} Redis       - Running"
else
    echo -e "${GREEN}✓${NC} Redis       - Stopped"
fi

if lsof -i:27017 &>/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":27017 "; then
    if sudo supervisorctl status mongodb 2>/dev/null | grep -q "RUNNING"; then
        echo -e "${BLUE}ℹ${NC} MongoDB     - Running (managed by supervisor)"
    else
        echo -e "${BLUE}ℹ${NC} MongoDB     - Running"
    fi
else
    echo -e "${GREEN}✓${NC} MongoDB     - Stopped"
fi

echo ""
echo "=========================================="

if [ "$stopped_count" -gt 0 ]; then
    print_status success "Stopped $stopped_count service(s)"
else
    print_status info "No services were stopped"
fi

echo "=========================================="
echo ""
print_status info "To start services: ./run_standalone.sh"
echo ""
