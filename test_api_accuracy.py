#!/usr/bin/env python3
"""
Test API accuracy to ensure it matches standalone RAG tests
Tests both agent-based and direct RAG endpoints
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8001/api"
TIMEOUT = 120  # 2 minutes for agent-based queries

def print_header(text):
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")

def print_status(status, message):
    symbols = {"success": "✓", "error": "✗", "warning": "⚠", "info": "ℹ"}
    print(f"{symbols.get(status, '•')} {message}")

def test_health():
    """Test backend health"""
    print_header("Testing Backend Health")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_status("success", "Backend is healthy")
            return True
        else:
            print_status("error", f"Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_status("error", f"Cannot connect to backend: {e}")
        return False

def test_documents_list():
    """Test document listing"""
    print_header("Testing Document Listing")
    
    try:
        response = requests.get(f"{BASE_URL}/documents", timeout=10)
        if response.status_code == 200:
            data = response.json()
            docs = data.get("indexed_documents", [])
            print_status("success", f"Found {len(docs)} indexed documents")
            
            # Check if our test documents are there
            test_docs = [
                "sales_report_q4_2024.xlsx",
                "ai_chatbot_project_proposal.docx",
                "software_license_agreement.pdf",
                "restaurant_receipt_scan.pdf"
            ]
            
            found_docs = []
            for test_doc in test_docs:
                for doc in docs:
                    if test_doc in doc:
                        found_docs.append(test_doc)
                        break
            
            print_status("info", f"Test documents found: {len(found_docs)}/{len(test_docs)}")
            for doc in found_docs:
                print(f"   • {doc}")
            
            return len(found_docs) == len(test_docs)
        else:
            print_status("error", f"Failed to list documents: {response.status_code}")
            return False
    except Exception as e:
        print_status("error", f"Document listing failed: {e}")
        return False

def test_direct_rag_endpoint(query, expected_keywords, expected_doc, description):
    """Test direct RAG endpoint (bypasses agent)"""
    print(f"\n{'─'*80}")
    print(f"TEST: {description}")
    print(f"{'─'*80}")
    print(f"Query: {query}")
    print(f"Expected doc: {expected_doc}")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/rag/direct",
            json={"query": query},
            timeout=60
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("response", "")
            
            print_status("success", f"Response received in {elapsed:.2f}s")
            
            # Check if expected document is in sources
            if expected_doc in answer:
                print_status("success", f"✓ Contains expected document: {expected_doc}")
                correct_doc = True
            else:
                print_status("warning", f"⚠ Expected document not found in response")
                correct_doc = False
            
            # Check for expected keywords
            keywords_found = []
            for keyword in expected_keywords:
                if keyword.lower() in answer.lower():
                    keywords_found.append(keyword)
            
            if keywords_found:
                print_status("info", f"Keywords found: {', '.join(keywords_found)}")
            
            # Show answer excerpt
            answer_clean = answer.replace("Answer: ", "").split("\nSources:")[0]
            print(f"\nAnswer excerpt: {answer_clean[:150]}...")
            
            if "Sources:" in answer:
                sources = answer.split("Sources:")[1].strip()
                print(f"Sources: {sources}")
            
            return correct_doc
        else:
            print_status("error", f"Query failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print_status("error", f"Request failed: {e}")
        return False

def test_agent_endpoint(query, expected_doc, description):
    """Test agent-based endpoint"""
    print(f"\n{'─'*80}")
    print(f"TEST (Agent): {description}")
    print(f"{'─'*80}")
    print(f"Query: {query}")
    print(f"Expected doc: {expected_doc}")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"query": query},
            timeout=TIMEOUT
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            answer = str(data.get("response", ""))
            
            print_status("success", f"Response received in {elapsed:.2f}s")
            
            # Check if expected document is mentioned
            if expected_doc.lower() in answer.lower():
                print_status("success", f"✓ Contains expected document: {expected_doc}")
                correct_doc = True
            else:
                print_status("warning", f"⚠ Expected document not explicitly mentioned")
                correct_doc = False
            
            # Show answer excerpt
            print(f"\nAnswer excerpt: {str(answer)[:200]}...")
            
            return correct_doc
        else:
            print_status("error", f"Query failed: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print_status("error", f"Request timed out after {TIMEOUT}s")
        return False
    except Exception as e:
        print_status("error", f"Request failed: {e}")
        return False

def run_comprehensive_tests():
    """Run all API accuracy tests"""
    print("\n" + "╔" + "═"*78 + "╗")
    print("║" + " "*22 + "API ACCURACY TESTING" + " "*35 + "║")
    print("╚" + "═"*78 + "╝")
    
    # Health check
    if not test_health():
        print("\n❌ Backend not available. Please start the backend first.")
        return False
    
    # Document check
    if not test_documents_list():
        print("\n⚠️  Test documents not fully indexed. Results may vary.")
    
    # Define test cases (same as standalone tests)
    test_cases = [
        {
            "query": "What was the total Q4 sales amount in the sales report?",
            "expected_keywords": ["1,549,000", "sales", "Q4"],
            "expected_doc": "sales_report_q4_2024.xlsx",
            "description": "XLSX - Total Sales Query"
        },
        {
            "query": "Who was the top performing sales representative?",
            "expected_keywords": ["Michael Chen", "sales rep"],
            "expected_doc": "sales_report_q4_2024.xlsx",
            "description": "XLSX - Sales Rep Query"
        },
        {
            "query": "What is the budget for the AI chatbot project?",
            "expected_keywords": ["450,000", "budget", "chatbot"],
            "expected_doc": "ai_chatbot_project_proposal.docx",
            "description": "DOCX - Budget Query"
        },
        {
            "query": "Who is the project manager for the AI chatbot?",
            "expected_keywords": ["Rebecca Foster", "project manager"],
            "expected_doc": "ai_chatbot_project_proposal.docx",
            "description": "DOCX - Project Manager Query"
        },
        {
            "query": "What is the software license agreement number?",
            "expected_keywords": ["SLA-2024-7856", "agreement"],
            "expected_doc": "software_license_agreement.pdf",
            "description": "PDF - Agreement Number Query"
        },
        {
            "query": "What is the total license fee in the agreement?",
            "expected_keywords": ["125,000", "license fee"],
            "expected_doc": "software_license_agreement.pdf",
            "description": "PDF - License Fee Query"
        },
        {
            "query": "What is the receipt number from the restaurant?",
            "expected_keywords": ["R-2024-08956", "receipt"],
            "expected_doc": "restaurant_receipt_scan.pdf",
            "description": "PDF OCR - Receipt Number Query"
        },
        {
            "query": "Who was the server at the restaurant?",
            "expected_keywords": ["Maria Rodriguez", "server"],
            "expected_doc": "restaurant_receipt_scan.pdf",
            "description": "PDF OCR - Server Name Query"
        },
    ]
    
    # Test Direct RAG Endpoint
    print_header("Testing Direct RAG Endpoint (No Agent)")
    direct_passed = 0
    direct_total = len(test_cases)
    
    for test in test_cases:
        if test_direct_rag_endpoint(
            test["query"],
            test["expected_keywords"],
            test["expected_doc"],
            test["description"]
        ):
            direct_passed += 1
        time.sleep(1)  # Small delay between requests
    
    direct_accuracy = (direct_passed / direct_total) * 100
    
    # Test Agent Endpoint (optional - takes longer)
    print("\n" + "="*80)
    print("Would you like to test the agent-based endpoint?")
    print("Note: This takes longer (1-2 min per query) as the agent needs to decide.")
    print("="*80)
    
    # For automated testing, we'll test just 2 queries with agent
    print("\nTesting 2 sample queries with agent endpoint...")
    
    agent_test_cases = test_cases[:2]  # Just test first 2
    agent_passed = 0
    agent_total = len(agent_test_cases)
    
    for test in agent_test_cases:
        if test_agent_endpoint(
            test["query"],
            test["expected_doc"],
            test["description"]
        ):
            agent_passed += 1
        time.sleep(2)
    
    agent_accuracy = (agent_passed / agent_total) * 100 if agent_total > 0 else 0
    
    # Summary
    print_header("TEST SUMMARY")
    
    print("\n📊 Direct RAG Endpoint Results:")
    print(f"   Tests run: {direct_total}")
    print(f"   Passed: {direct_passed}")
    print(f"   Accuracy: {direct_accuracy:.1f}%")
    
    if direct_accuracy == 100:
        print_status("success", "🎉 Perfect accuracy on direct RAG endpoint!")
    elif direct_accuracy >= 80:
        print_status("success", "✅ Good accuracy on direct RAG endpoint")
    else:
        print_status("warning", "⚠️  Direct RAG accuracy below 80%")
    
    if agent_total > 0:
        print("\n📊 Agent-Based Endpoint Results:")
        print(f"   Tests run: {agent_total}")
        print(f"   Passed: {agent_passed}")
        print(f"   Accuracy: {agent_accuracy:.1f}%")
        
        if agent_accuracy == 100:
            print_status("success", "🎉 Perfect accuracy on agent endpoint!")
        elif agent_accuracy >= 80:
            print_status("success", "✅ Good accuracy on agent endpoint")
        else:
            print_status("warning", "⚠️  Agent accuracy below 80%")
    
    print("\n" + "="*80)
    
    if direct_accuracy >= 90:
        print("\n✅ API ACCURACY TEST PASSED!")
        print("The API has the same high accuracy as standalone RAG tests.")
        return True
    else:
        print("\n⚠️  API accuracy needs improvement")
        print("Consider using direct RAG endpoint for guaranteed accuracy.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
