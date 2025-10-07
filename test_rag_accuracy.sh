#!/bin/bash
# Test RAG retrieval accuracy with known queries

echo "========================================================================"
echo "RAG Accuracy Testing - NeuralStark"
echo "========================================================================"
echo ""

# Test 1: Financial Query
echo "Test 1: Financial Query - Annual Revenue"
echo "Query: 'What is the annual revenue?'"
curl -s -X POST "http://localhost:8001/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the annual revenue?"}' | python3 -c "import sys, json; data=json.load(sys.stdin); print('Response:', data['response'][:500] if isinstance(data['response'], str) else 'Canvas response'); print()"

echo ""
echo "------------------------------------------------------------------------"
echo ""

# Test 2: Employee Count
echo "Test 2: Company Information - Employee Count"
echo "Query: 'How many employees does the company have?'"
curl -s -X POST "http://localhost:8001/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "How many employees does the company have?"}' | python3 -c "import sys, json; data=json.load(sys.stdin); print('Response:', data['response'][:500] if isinstance(data['response'], str) else 'Canvas response'); print()"

echo ""
echo "------------------------------------------------------------------------"
echo ""

# Test 3: Product Pricing
echo "Test 3: Product Query - AI Document Processor Price"
echo "Query: 'What is the price of AI Document Processor Pro?'"
curl -s -X POST "http://localhost:8001/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the price of AI Document Processor Pro?"}' | python3 -c "import sys, json; data=json.load(sys.stdin); print('Response:', data['response'][:500] if isinstance(data['response'], str) else 'Canvas response'); print()"

echo ""
echo "------------------------------------------------------------------------"
echo ""

# Test 4: HR Policy
echo "Test 4: HR Policy - Vacation Days"
echo "Query: 'How many vacation days do employees get?'"
curl -s -X POST "http://localhost:8001/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "How many vacation days do employees get?"}' | python3 -c "import sys, json; data=json.load(sys.stdin); print('Response:', data['response'][:500] if isinstance(data['response'], str) else 'Canvas response'); print()"

echo ""
echo "------------------------------------------------------------------------"
echo ""

# Test 5: Meeting Information
echo "Test 5: Meeting Notes - Board Meeting Date"
echo "Query: 'When was the board meeting held?'"
curl -s -X POST "http://localhost:8001/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "When was the board meeting held?"}' | python3 -c "import sys, json; data=json.load(sys.stdin); print('Response:', data['response'][:500] if isinstance(data['response'], str) else 'Canvas response'); print()"

echo ""
echo "------------------------------------------------------------------------"
echo ""

# Test 6: Sales Data
echo "Test 6: Sales Data - December Revenue"
echo "Query: 'What was the revenue in December?'"
curl -s -X POST "http://localhost:8001/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What was the revenue in December?"}' | python3 -c "import sys, json; data=json.load(sys.stdin); print('Response:', data['response'][:500] if isinstance(data['response'], str) else 'Canvas response'); print()"

echo ""
echo "========================================================================"
echo "Testing Complete"
echo "========================================================================"
