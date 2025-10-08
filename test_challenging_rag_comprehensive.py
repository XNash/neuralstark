#!/usr/bin/env python3
"""
Comprehensive RAG Testing with Challenging Documents
Tests the RAG system with complex, realistic documents and challenging queries
"""

import requests
import json
import time
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple

BASE_URL = "http://localhost:8001/api"
TIMEOUT = 120

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")

def print_status(status: str, message: str):
    """Print status message with appropriate symbol"""
    symbols = {"success": "✓", "error": "✗", "warning": "⚠", "info": "ℹ"}
    print(f"{symbols.get(status, '•')} {message}")

def test_backend_health() -> bool:
    """Test if backend is healthy and responsive"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        return response.status_code == 200
    except Exception as e:
        print_status("error", f"Backend health check failed: {e}")
        return False

def test_chromadb_health() -> Dict[str, Any]:
    """Test ChromaDB health and robustness"""
    print_header("ChromaDB Health & Robustness Check")
    
    try:
        # Test basic health
        response = requests.get(f"{BASE_URL}/chromadb/health", timeout=30)
        if response.status_code == 200:
            health_data = response.json()
            health_status = health_data["health_check"]
            
            if health_status["healthy"]:
                print_status("success", "ChromaDB is healthy")
            else:
                print_status("warning", "ChromaDB has issues:")
                for issue in health_status.get("issues", []):
                    print(f"  - Issue: {issue}")
                for warning in health_status.get("warnings", []):
                    print(f"  - Warning: {warning}")
            
            # Display stats if available
            stats = health_status.get("stats", {})
            if stats:
                print_status("info", "ChromaDB Statistics:")
                for key, value in stats.items():
                    print(f"  - {key}: {value}")
            
            return health_data
        else:
            print_status("error", f"Health check failed: {response.status_code}")
            return {"healthy": False, "error": "API call failed"}
            
    except Exception as e:
        print_status("error", f"ChromaDB health check failed: {e}")
        return {"healthy": False, "error": str(e)}

def test_chromadb_backup() -> bool:
    """Test ChromaDB backup functionality"""
    print_header("ChromaDB Backup Test")
    
    try:
        response = requests.post(f"{BASE_URL}/chromadb/backup", timeout=60)
        if response.status_code == 200:
            backup_data = response.json()
            print_status("success", f"Backup created: {backup_data['backup_path']}")
            return True
        else:
            print_status("error", f"Backup failed: {response.status_code}")
            return False
    except Exception as e:
        print_status("error", f"Backup test failed: {e}")
        return False

def get_indexed_documents() -> List[str]:
    """Get list of indexed documents"""
    try:
        response = requests.get(f"{BASE_URL}/documents", timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data.get("indexed_documents", [])
        else:
            print_status("error", f"Failed to get documents: {response.status_code}")
            return []
    except Exception as e:
        print_status("error", f"Error getting documents: {e}")
        return []

def test_direct_rag_query(query: str, expected_keywords: List[str], description: str) -> Tuple[bool, Dict]:
    """Test direct RAG query with specific expectations"""
    print(f"\n{'─'*80}")
    print(f"TEST: {description}")
    print(f"{'─'*80}")
    print(f"Query: {query}")
    print(f"Expected keywords: {', '.join(expected_keywords)}")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/rag/direct",
            json={"query": query},
            timeout=TIMEOUT
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("response", "")
            
            print_status("success", f"Response received in {elapsed:.2f}s")
            
            # Check for expected keywords
            keywords_found = []
            for keyword in expected_keywords:
                if keyword.lower() in answer.lower():
                    keywords_found.append(keyword)
            
            accuracy = len(keywords_found) / len(expected_keywords) if expected_keywords else 1.0
            
            if accuracy >= 0.8:
                print_status("success", f"High accuracy: {accuracy:.1%} ({len(keywords_found)}/{len(expected_keywords)} keywords found)")
            elif accuracy >= 0.5:
                print_status("warning", f"Medium accuracy: {accuracy:.1%} ({len(keywords_found)}/{len(expected_keywords)} keywords found)")
            else:
                print_status("error", f"Low accuracy: {accuracy:.1%} ({len(keywords_found)}/{len(expected_keywords)} keywords found)")
            
            print(f"Keywords found: {', '.join(keywords_found)}")
            
            # Show answer excerpt
            answer_clean = answer.replace("Answer: ", "").split("\nSources:")[0]
            print(f"Answer excerpt: {answer_clean[:200]}...")
            
            if "Sources:" in answer:
                sources = answer.split("Sources:")[1].strip()
                print(f"Sources: {sources}")
            
            return accuracy >= 0.5, {
                "accuracy": accuracy,
                "keywords_found": keywords_found,
                "response_time": elapsed,
                "answer_length": len(answer_clean)
            }
            
        else:
            print_status("error", f"Query failed: {response.status_code}")
            return False, {"error": response.text[:200]}
            
    except Exception as e:
        print_status("error", f"Request failed: {e}")
        return False, {"error": str(e)}

def run_challenging_document_tests():
    """Run comprehensive tests with challenging documents"""
    print_header("CHALLENGING DOCUMENT RAG TESTING")
    
    # Check if backend is healthy
    if not test_backend_health():
        print("❌ Backend not available. Please start the backend first.")
        return False
    
    # Check ChromaDB health
    chromadb_health = test_chromadb_health()
    if not chromadb_health.get("healthy", False):
        print_status("warning", "ChromaDB issues detected. Attempting recovery...")
        
        # Try recovery
        try:
            recovery_response = requests.post(f"{BASE_URL}/chromadb/recovery", timeout=60)
            if recovery_response.status_code == 200:
                recovery_data = recovery_response.json()
                if recovery_data["status"] == "recovery_successful":
                    print_status("success", "ChromaDB recovery completed")
                else:
                    print_status("warning", f"Recovery result: {recovery_data['status']}")
            else:
                print_status("error", "Recovery failed")
        except Exception as e:
            print_status("error", f"Recovery attempt failed: {e}")
    
    # Test backup functionality
    backup_success = test_chromadb_backup()
    
    # Get indexed documents
    indexed_docs = get_indexed_documents()
    print_status("info", f"Found {len(indexed_docs)} indexed documents")
    
    if not indexed_docs:
        print_status("error", "No documents indexed. Please ensure documents are processed.")
        return False
    
    # Define challenging test cases based on our created documents
    test_cases = [
        # Financial Report Tests
        {
            "query": "What was NeuralCorp's total revenue in Q3 2024?",
            "expected_keywords": ["47.3 million", "revenue", "Q3 2024", "NeuralCorp"],
            "description": "Complex Financial Data - Revenue Query"
        },
        {
            "query": "What is NeuralCorp's EBITDA and net profit margin for Q3 2024?",
            "expected_keywords": ["12.4 million", "EBITDA", "18.7%", "profit margin"],
            "description": "Financial Metrics - EBITDA and Margins"
        },
        {
            "query": "Who are the CEO and CFO of NeuralCorp according to the financial report?",
            "expected_keywords": ["Alexandra Chen", "Robert Kumar", "CEO", "CFO"],
            "description": "Executive Leadership Identification"
        },
        
        # Technical Architecture Tests
        {
            "query": "What database technologies are used by the microservices architecture?",
            "expected_keywords": ["PostgreSQL", "MongoDB", "Redis", "ClickHouse", "Elasticsearch"],
            "description": "Technical Stack - Database Technologies"
        },
        {
            "query": "What is the port number for the AI inference engine service?",
            "expected_keywords": ["8003", "ai-inference-engine", "port"],
            "description": "Technical Configuration - Service Ports"
        },
        {
            "query": "What programming languages and frameworks are used in the microservices?",
            "expected_keywords": ["Java 17", "Python 3.11", "Node.js 18", "Go 1.21", "Spring Boot"],
            "description": "Technical Stack - Programming Languages"
        },
        
        # Excel/Spreadsheet Tests
        {
            "query": "Which departments are included in the employee performance data?",
            "expected_keywords": ["Engineering", "Sales", "Marketing", "Finance", "HR", "Operations"],
            "description": "Excel Data - Department Information"
        },
        {
            "query": "What financial metrics are tracked in the monthly projections?",
            "expected_keywords": ["Revenue_Target", "Operating_Expenses", "Customer_Acquisition_Cost", "Churn_Rate"],
            "description": "Excel Data - Financial Metrics"
        },
        
        # OCR Tests
        {
            "query": "What is the invoice number and total amount due in the NeuralCorp invoice?",
            "expected_keywords": ["INV-2024-45892", "125,388.75", "TOTAL AMOUNT DUE"],
            "description": "OCR Test - Invoice Information"
        },
        {
            "query": "Who attended the product strategy meeting and what were the key decisions?",
            "expected_keywords": ["Michael Chen", "Sarah Kim", "David Rodriguez", "AI Assistant", "Nov 15, 2024"],
            "description": "OCR Test - Meeting Notes"
        },
        
        # JSON Configuration Tests
        {
            "query": "What is the JWT secret key configuration in the microservices setup?",
            "expected_keywords": ["JWT_SECRET", "authentication", "environment_variables"],
            "description": "JSON Config - Security Settings"
        },
        {
            "query": "What ML models are configured in the AI inference service?",
            "expected_keywords": ["text_classification", "sentiment_analysis", "BERT", "batch_size"],
            "description": "JSON Config - ML Model Configuration"
        },
        
        # Markdown Documentation Tests
        {
            "query": "What are the rate limits for different API plan types?",
            "expected_keywords": ["Free Tier", "1,000", "Professional", "10,000", "Enterprise", "100,000"],
            "description": "Markdown Documentation - Rate Limits"
        },
        {
            "query": "What HTTP status codes does the NeuralCorp API return for errors?",
            "expected_keywords": ["400", "Bad Request", "401", "Unauthorized", "429", "Rate limit"],
            "description": "Markdown Documentation - Error Codes"
        },
        
        # Cross-Document Complex Queries
        {
            "query": "Based on all available information, what is NeuralCorp's technology stack and business performance?",
            "expected_keywords": ["microservices", "AI", "revenue", "growth", "Python", "Java"],
            "description": "Cross-Document Analysis - Technology & Business"
        },
        {
            "query": "What security measures and authentication methods does NeuralCorp implement?",
            "expected_keywords": ["JWT", "RS256", "TLS", "authentication", "rate limiting", "CORS"],
            "description": "Cross-Document Analysis - Security Measures"
        }
    ]
    
    # Run all test cases
    results = []
    total_tests = len(test_cases)
    passed_tests = 0
    total_response_time = 0
    
    print_header(f"Running {total_tests} Challenging RAG Tests")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}/{total_tests}]", end=" ")
        
        success, test_result = test_direct_rag_query(
            test_case["query"],
            test_case["expected_keywords"],
            test_case["description"]
        )
        
        if success:
            passed_tests += 1
        
        if "response_time" in test_result:
            total_response_time += test_result["response_time"]
        
        results.append({
            "test_case": test_case,
            "success": success,
            "result": test_result
        })
        
        time.sleep(1)  # Small delay between tests
    
    # Generate summary report
    print_header("TEST SUMMARY REPORT")
    
    accuracy = (passed_tests / total_tests) * 100
    avg_response_time = total_response_time / total_tests if total_tests > 0 else 0
    
    print(f"📊 Overall Results:")
    print(f"   Tests Run: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {total_tests - passed_tests}")
    print(f"   Accuracy: {accuracy:.1f}%")
    print(f"   Average Response Time: {avg_response_time:.2f}s")
    
    # Category breakdown
    categories = {}
    for result in results:
        description = result["test_case"]["description"]
        category = description.split(" - ")[0]
        if category not in categories:
            categories[category] = {"total": 0, "passed": 0}
        categories[category]["total"] += 1
        if result["success"]:
            categories[category]["passed"] += 1
    
    print(f"\n📋 Results by Category:")
    for category, stats in categories.items():
        category_accuracy = (stats["passed"] / stats["total"]) * 100
        print(f"   {category}: {stats['passed']}/{stats['total']} ({category_accuracy:.1f}%)")
    
    # Performance analysis
    response_times = [r["result"].get("response_time", 0) for r in results if "response_time" in r["result"]]
    if response_times:
        fastest = min(response_times)
        slowest = max(response_times)
        print(f"\n⚡ Performance Analysis:")
        print(f"   Fastest Query: {fastest:.2f}s")
        print(f"   Slowest Query: {slowest:.2f}s")
        print(f"   Average: {avg_response_time:.2f}s")
    
    # Overall assessment
    print(f"\n🎯 Overall Assessment:")
    if accuracy >= 90:
        print_status("success", f"EXCELLENT: {accuracy:.1f}% accuracy - RAG system performing exceptionally well!")
    elif accuracy >= 80:
        print_status("success", f"VERY GOOD: {accuracy:.1f}% accuracy - RAG system performing well")
    elif accuracy >= 70:
        print_status("warning", f"GOOD: {accuracy:.1f}% accuracy - RAG system needs minor improvements")
    elif accuracy >= 50:
        print_status("warning", f"FAIR: {accuracy:.1f}% accuracy - RAG system needs improvements")
    else:
        print_status("error", f"POOR: {accuracy:.1f}% accuracy - RAG system needs significant improvements")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if accuracy < 80:
        print("   - Consider reindexing documents with better chunking")
        print("   - Adjust retrieval parameters (k, score threshold)")
        print("   - Review document quality and preprocessing")
    
    if avg_response_time > 5:
        print("   - Optimize retrieval performance")
        print("   - Consider reducing reranking candidates")
        print("   - Check system resource utilization")
    
    if len(indexed_docs) < 10:
        print("   - Add more diverse test documents")
        print("   - Ensure all document formats are supported")
    
    # Save detailed results
    results_file = "/app/challenging_rag_test_results.json"
    try:
        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "accuracy": accuracy,
                    "avg_response_time": avg_response_time,
                    "timestamp": time.time()
                },
                "categories": categories,
                "detailed_results": results,
                "indexed_documents": indexed_docs
            }, f, indent=2)
        print(f"\n📄 Detailed results saved to: {results_file}")
    except Exception as e:
        print_status("warning", f"Could not save results file: {e}")
    
    print("\n" + "="*80)
    
    return accuracy >= 70  # Consider 70% as passing threshold

if __name__ == "__main__":
    success = run_challenging_document_tests()
    sys.exit(0 if success else 1)