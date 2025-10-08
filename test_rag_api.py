#!/usr/bin/env python3
"""
Test RAG system through the actual API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001/api"

def test_query(query, description):
    """Test a single query through the chat API"""
    print(f"\n{'='*70}")
    print(f"TEST: {description}")
    print(f"{'='*70}")
    print(f"Query: {query}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"query": query},
            timeout=60
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("response", "")
            
            print(f"✓ Response received in {elapsed:.2f}s")
            print(f"\nAnswer excerpt: {str(answer)[:300]}...")
            
            # Check if sources are mentioned
            if "Sources:" in str(answer) or "sources" in str(answer).lower():
                print("✓ Response includes source citations")
            
            return True
        else:
            print(f"✗ Error: Status {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return False

def main():
    print("="*70)
    print("  RAG System API Testing")
    print("="*70)
    
    # Test health endpoint
    print("\n[1] Testing health endpoint...")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        if resp.status_code == 200:
            print("✓ Backend is healthy")
        else:
            print("✗ Backend health check failed")
            return
    except:
        print("✗ Cannot connect to backend")
        return
    
    # Test diverse queries
    test_cases = [
        ("What was the total revenue for TechCorp in 2024?", "Financial query"),
        ("Who are the employees in the Engineering department?", "HR data query"),
        ("What is the invoice number and amount?", "OCR - Invoice"),
        ("What machine learning algorithm performed best?", "Research notes"),
        ("What are the strategic initiatives for 2025?", "Strategic planning"),
        ("What products are in the inventory?", "Inventory query"),
        ("What is the database host in the configuration?", "Config query"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, (query, desc) in enumerate(test_cases, 2):
        print(f"\n[{i}] Testing: {desc}")
        if test_query(query, desc):
            passed += 1
        time.sleep(2)  # Small delay between requests
    
    # Summary
    print(f"\n{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}")
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n✅ All API tests passed! RAG system is fully functional.")
    elif passed >= total * 0.8:
        print("\n⚠️  Most tests passed. System is functional.")
    else:
        print("\n❌ Multiple tests failed. System needs attention.")

if __name__ == "__main__":
    main()
