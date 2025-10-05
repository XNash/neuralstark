#!/bin/bash

###########################################
# Dependency Test Script
# Verifies all dependencies are installed
###########################################

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "  🔍 Testing NeuralStark Dependencies"
echo "=========================================="
echo ""

passed=0
failed=0

test_check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((passed++))
    else
        echo -e "${RED}✗${NC} $1"
        ((failed++))
    fi
}

echo "System Prerequisites:"
echo "--------------------"

command -v python3 &>/dev/null
test_check "Python 3"

command -v node &>/dev/null
test_check "Node.js"

command -v npm &>/dev/null || command -v yarn &>/dev/null
test_check "npm or yarn"

echo ""
echo "System Services:"
echo "----------------"

command -v mongod &>/dev/null || lsof -i:27017 &>/dev/null 2>&1
test_check "MongoDB (installed or running)"

command -v redis-server &>/dev/null || redis-cli ping &>/dev/null 2>&1
test_check "Redis (installed or running)"

echo ""
echo "Virtual Environment:"
echo "--------------------"

[ -d "/root/.venv" ] || [ -d "/app/.venv" ]
test_check "venv directory exists"

if [ -f "/app/.venv/bin/python3" ] || [ -f "/root/.venv/bin/python3" ]; then
    echo -e "${GREEN}✓${NC} Python in venv"
    ((passed++))
    
    # Test Python packages
    echo ""
    echo "Python Packages:"
    echo "----------------"
    
    if [ -f "/app/.venv/bin/python3" ]; then
        PYTHON_BIN="/app/.venv/bin/python3"
    else
        PYTHON_BIN="/root/.venv/bin/python3"
    fi
    
    $PYTHON_BIN -c "import fastapi" 2>/dev/null
    test_check "fastapi"
    
    $PYTHON_BIN -c "import uvicorn" 2>/dev/null
    test_check "uvicorn"
    
    $PYTHON_BIN -c "import celery" 2>/dev/null
    test_check "celery"
    
    $PYTHON_BIN -c "import redis" 2>/dev/null
    test_check "redis"
    
    $PYTHON_BIN -c "import langchain" 2>/dev/null
    test_check "langchain"
    
    $PYTHON_BIN -c "import langchain_google_genai" 2>/dev/null
    test_check "langchain-google-genai"
    
    $PYTHON_BIN -c "import chromadb" 2>/dev/null
    test_check "chromadb"
    
    $PYTHON_BIN -c "import sentence_transformers" 2>/dev/null
    test_check "sentence-transformers"
    
    $PYTHON_BIN -c "import langchain_huggingface" 2>/dev/null
    test_check "langchain-huggingface"
    
    $PYTHON_BIN -c "from reportlab.lib.pagesizes import letter" 2>/dev/null
    test_check "reportlab"
    
    $PYTHON_BIN -c "import pandas" 2>/dev/null
    test_check "pandas"
    
    $PYTHON_BIN -c "import watchdog" 2>/dev/null
    test_check "watchdog"
else
    echo -e "${RED}✗${NC} Python in venv"
    ((failed++))
fi

echo ""
echo "Frontend Dependencies:"
echo "----------------------"

[ -d "/app/frontend/node_modules" ]
test_check "node_modules directory"

[ -f "/app/frontend/node_modules/react/package.json" ]
test_check "react"

[ -f "/app/frontend/node_modules/vite/package.json" ]
test_check "vite"

echo ""
echo "Project Structure:"
echo "------------------"

[ -d "/app/backend/knowledge_base/internal" ]
test_check "internal knowledge base directory"

[ -d "/app/backend/knowledge_base/external" ]
test_check "external knowledge base directory"

[ -d "/app/chroma_db" ]
test_check "chroma_db directory"

[ -f "/app/backend/requirements.txt" ]
test_check "requirements.txt"

[ -f "/app/frontend/package.json" ]
test_check "package.json"

echo ""
echo "Scripts:"
echo "--------"

[ -x "/app/run.sh" ]
test_check "run.sh (executable)"

[ -x "/app/stop.sh" ]
test_check "stop.sh (executable)"

echo ""
echo "=========================================="
echo "  📊 Test Results"
echo "=========================================="
echo ""

total=$((passed + failed))
percentage=$((passed * 100 / total))

echo -e "Passed: ${GREEN}$passed${NC}/$total"
echo -e "Failed: ${RED}$failed${NC}/$total"
echo -e "Success Rate: ${BLUE}$percentage%${NC}"
echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}✓ All dependencies are installed!${NC}"
    echo ""
    echo "You can now run: ./run.sh"
    exit 0
else
    echo -e "${YELLOW}⚠ Some dependencies are missing${NC}"
    echo ""
    echo "Run './run.sh' to auto-install missing dependencies"
    exit 1
fi
