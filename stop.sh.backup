#!/bin/bash

###########################################
# NeuralStark - Universal Stop Script
# Works in any standard Linux environment
# Version: 4.1 - No sudo required
###########################################

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
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

echo ""
echo "=========================================="

###########################################
# 4. Optional Services (with prompt)
###########################################
print_status info "The following services can continue running:"
echo ""

# Check Redis
if redis-cli ping &>/dev/null; then
    echo "  • Redis (port 6379) - used by Celery"
fi

# Check MongoDB
if lsof -i:27017 &>/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":27017 "; then
    echo "  • MongoDB (port 27017) - database"
fi

echo ""
read -p "Stop Redis and MongoDB? (y/N): " -n 1 -r
echo ""
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Stop Redis
    if redis-cli ping &>/dev/null; then
        print_status info "Stopping Redis..."
        redis-cli shutdown 2>/dev/null
        sleep 1
        if ! redis-cli ping &>/dev/null; then
            print_status success "Redis stopped"
            ((stopped_count++))
        fi
    fi
    
    # Stop MongoDB
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
    print_status info "Keeping Redis and MongoDB running"
fi

###########################################
# 5. Final Status
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
    echo -e "${YELLOW}⚠${NC} Backend     - Still running"
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
    echo -e "${BLUE}ℹ${NC} MongoDB     - Running"
else
    echo -e "${GREEN}✓${NC} MongoDB     - Stopped"
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
print_status info "To start services: ./run.sh"
echo ""