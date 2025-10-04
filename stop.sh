#!/bin/bash

# NeuralStark Application Stop Script
# This script stops all services for the NeuralStark application

echo "=========================================="
echo "  NeuralStark - Stopping All Services"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Stop Celery worker
echo -e "\n${YELLOW}Stopping Celery worker...${NC}"
pkill -f "celery.*worker"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Celery worker stopped${NC}"
else
    echo -e "${YELLOW}⚠ No Celery worker found${NC}"
fi

# Stop Backend
echo -e "\n${YELLOW}Stopping Backend...${NC}"
pkill -f "uvicorn.*server:app"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend stopped${NC}"
else
    echo -e "${YELLOW}⚠ No Backend process found${NC}"
fi

# Stop Frontend
echo -e "\n${YELLOW}Stopping Frontend...${NC}"
pkill -f "vite"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend stopped${NC}"
else
    echo -e "${YELLOW}⚠ No Frontend process found${NC}"
fi

# Optionally stop Redis (uncomment if needed)
# echo -e "\n${YELLOW}Stopping Redis...${NC}"
# redis-cli shutdown
# echo -e "${GREEN}✓ Redis stopped${NC}"

# Optionally stop MongoDB (uncomment if needed)
# echo -e "\n${YELLOW}Stopping MongoDB...${NC}"
# mongod --shutdown
# echo -e "${GREEN}✓ MongoDB stopped${NC}"

echo -e "\n=========================================="
echo -e "${GREEN}  All Services Stopped${NC}"
echo "=========================================="
