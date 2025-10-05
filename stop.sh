#!/bin/bash

###########################################
# NeuralStark - Quick Stop Script
# Version: 3.0 (Supervisor Compatible)
# Updated: January 2025
###########################################

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "  NeuralStark - Quick Stop"
echo "=========================================="
echo ""

# Stop Celery worker (not managed by supervisor)
echo "Stopping Celery worker..."
if pgrep -f "celery.*worker" > /dev/null; then
    pkill -9 -f "celery.*worker" 2>/dev/null
    sleep 1
    echo -e "${GREEN}✓${NC} Celery stopped"
else
    echo -e "${YELLOW}⚠${NC} Celery not running"
fi

rm -f /tmp/celery_worker.pid

echo ""
echo "=========================================="
echo -e "${GREEN}✓${NC} Services stopped"
echo "=========================================="
echo ""
echo "Note: Backend, Frontend, and MongoDB are managed by supervisor"
echo "      and will continue running unless explicitly stopped."
echo ""
echo "To stop supervisor services:"
echo "  sudo supervisorctl stop backend frontend"
echo ""
echo "To stop Redis:"
echo "  redis-cli shutdown"
echo ""