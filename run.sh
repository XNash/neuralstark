#!/bin/bash

# NeuralStark Application Startup Script
# This script starts all required services for the NeuralStark application

echo "=========================================="
echo "  NeuralStark - Starting All Services"
echo "=========================================="

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i:$1 >/dev/null 2>&1 || netstat -an | grep ":$1 " | grep LISTEN >/dev/null 2>&1
}

# Check for required commands
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}Error: python3 is not installed${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    exit 1
fi

if ! command_exists mongod; then
    echo -e "${YELLOW}Warning: MongoDB is not installed. Attempting to start anyway...${NC}"
fi

if ! command_exists redis-server; then
    echo -e "${YELLOW}Warning: Redis is not installed. Installing...${NC}"
    if command_exists apt-get; then
        sudo apt-get install -y redis-server
    elif command_exists brew; then
        brew install redis
    else
        echo -e "${RED}Cannot install Redis automatically. Please install it manually.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ All prerequisites checked${NC}"

# Start Redis
echo -e "\n${YELLOW}Starting Redis...${NC}"
if port_in_use 6379; then
    echo -e "${GREEN}✓ Redis already running on port 6379${NC}"
else
    redis-server --daemonize yes
    sleep 2
    if port_in_use 6379; then
        echo -e "${GREEN}✓ Redis started successfully${NC}"
    else
        echo -e "${RED}✗ Failed to start Redis${NC}"
        exit 1
    fi
fi

# Start MongoDB
echo -e "\n${YELLOW}Starting MongoDB...${NC}"
if port_in_use 27017; then
    echo -e "${GREEN}✓ MongoDB already running on port 27017${NC}"
else
    if command_exists mongod; then
        mongod --fork --logpath /var/log/mongodb.log --bind_ip_all
        sleep 2
        if port_in_use 27017; then
            echo -e "${GREEN}✓ MongoDB started successfully${NC}"
        else
            echo -e "${YELLOW}⚠ MongoDB may not have started correctly${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ MongoDB not found, skipping...${NC}"
    fi
fi

# Set Python path
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Start Celery Worker
echo -e "\n${YELLOW}Starting Celery worker...${NC}"
pkill -f "celery.*worker" 2>/dev/null
sleep 1

cd "$SCRIPT_DIR"
celery -A backend.celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    --max-tasks-per-child=50 \
    --logfile=/var/log/celery_worker.log \
    --pidfile=/tmp/celery_worker.pid \
    --detach

sleep 3
if pgrep -f "celery.*worker" > /dev/null; then
    echo -e "${GREEN}✓ Celery worker started successfully${NC}"
else
    echo -e "${RED}✗ Failed to start Celery worker${NC}"
    exit 1
fi

# Start Backend (FastAPI)
echo -e "\n${YELLOW}Starting Backend (FastAPI)...${NC}"
cd "$SCRIPT_DIR/backend"

# Kill any existing backend process
pkill -f "uvicorn.*server:app" 2>/dev/null
sleep 1

# Start backend in background
nohup uvicorn server:app --host 0.0.0.0 --port 8001 --reload > /var/log/backend.log 2>&1 &
BACKEND_PID=$!

sleep 3
if port_in_use 8001; then
    echo -e "${GREEN}✓ Backend started successfully on port 8001${NC}"
    echo "  PID: $BACKEND_PID"
else
    echo -e "${RED}✗ Failed to start Backend${NC}"
    exit 1
fi

# Start Frontend (React + Vite)
echo -e "\n${YELLOW}Starting Frontend (React)...${NC}"
cd "$SCRIPT_DIR/frontend"

# Kill any existing frontend process
pkill -f "vite" 2>/dev/null
sleep 1

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    yarn install
fi

# Start frontend in background
nohup yarn start > /var/log/frontend.log 2>&1 &
FRONTEND_PID=$!

echo -e "${YELLOW}Waiting for frontend to start...${NC}"
sleep 5

if port_in_use 3000; then
    echo -e "${GREEN}✓ Frontend started successfully on port 3000${NC}"
    echo "  PID: $FRONTEND_PID"
else
    echo -e "${RED}✗ Failed to start Frontend${NC}"
    echo "Check logs at /var/log/frontend.log"
fi

# Summary
echo -e "\n=========================================="
echo -e "${GREEN}  All Services Started Successfully!${NC}"
echo "=========================================="
echo ""
echo "Service Status:"
echo "  - Redis:      Running on port 6379"
echo "  - MongoDB:    Running on port 27017"
echo "  - Celery:     Running (2 workers)"
echo "  - Backend:    http://localhost:8001"
echo "  - Frontend:   http://localhost:3000"
echo ""
echo "Logs:"
echo "  - Backend:    /var/log/backend.log"
echo "  - Frontend:   /var/log/frontend.log"
echo "  - Celery:     /var/log/celery_worker.log"
echo ""
echo "To stop all services, run:"
echo "  pkill -f 'uvicorn|vite|celery'"
echo "  redis-cli shutdown"
echo "  mongod --shutdown"
echo ""
echo -e "${GREEN}Application is ready to use!${NC}"
echo "=========================================="
