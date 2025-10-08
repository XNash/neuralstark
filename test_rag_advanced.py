#!/usr/bin/env python3
"""
Advanced RAG Testing with Diverse Documents and Complex Queries
Tests accuracy, relevance, and robustness of the RAG system
"""

import sys
import os
import json
import time
from pathlib import Path

sys.path.insert(0, '/app')

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from backend.config import settings
from backend.document_parser import parse_document
from langchain.text_splitter import RecursiveCharacterTextSplitter


class AdvancedRAGTester:
    def __init__(self):
        self.embeddings = None
        self.vector_store = None
        self.results = {
            "total_documents": 0,
            "total_chunks": 0,
            "test_results": [],
            "accuracy_score": 0.0,
            "avg_retrieval_time": 0.0,
            "errors": []
        }
        
    def print_header(self, text):
        print(f"\n{'='*80}")
        print(f"  {text}")
        print(f"{'='*80}\n")
    
    def print_status(self, status, message):
        symbols = {"success": "✓", "error": "✗", "warning": "⚠", "info": "ℹ"}
        print(f"{symbols.get(status, '•')} {message}")
    
    def rebuild_index(self):
        """Rebuild the ChromaDB index with all documents"""
        self.print_header("Rebuilding RAG Index")
        
        try:
            # Initialize embeddings
            self.print_status("info", "Loading embedding model...")
            self.embeddings = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL_NAME,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={
                    'batch_size': settings.EMBEDDING_BATCH_SIZE,
                    'normalize_embeddings': True
                }
            )
            self.print_status("success", "Embedding model loaded")
            
            # Create ChromaDB client
            client = chromadb.PersistentClient(
                path=settings.CHROMA_DB_PATH,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=True
                )
            )
            
            # Reset collection
            try:
                client.delete_collection("knowledge_base_collection")
            except:
                pass
            
            collection = client.create_collection(
                name="knowledge_base_collection",
                metadata={"hnsw:space": "cosine"}
            )
            self.print_status("success", "Created new collection")
            
            # Text splitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                length_function=len
            )
            
            # Index documents
            documents_processed = 0
            chunks_created = 0
            
            kb_path = settings.INTERNAL_KNOWLEDGE_BASE_PATH
            
            for filename in sorted(os.listdir(kb_path)):
                file_path = os.path.join(kb_path, filename)
                
                if not os.path.isfile(file_path):
                    continue
                
                self.print_status("info", f"Processing: {filename}")
                
                try:
                    content = parse_document(file_path)
                    
                    if not content or not content.strip():
                        self.print_status("warning", f"  No content extracted")
                        continue
                    
                    chunks = text_splitter.split_text(content)
                    
                    for i, chunk in enumerate(chunks):
                        if not chunk.strip():
                            continue
                        
                        embedding = self.embeddings.embed_query(chunk)
                        
                        collection.add(
                            embeddings=[embedding],
                            documents=[chunk],
                            metadatas=[{
                                "source": file_path,
                                "source_type": "internal",
                                "chunk_index": i,
                                "filename": filename
                            }],
                            ids=[f"{filename}_{i}_{int(time.time()*1000)}"]
                        )
                        chunks_created += 1
                    
                    documents_processed += 1
                    self.print_status("success", f"  Indexed: {len(chunks)} chunks")
                    
                except Exception as e:
                    self.print_status("error", f"  Failed: {e}")
            
            self.results["total_documents"] = documents_processed
            self.results["total_chunks"] = chunks_created
            
            # Create vector store
            self.vector_store = Chroma(
                client=client,
                collection_name="knowledge_base_collection",
                embedding_function=self.embeddings
            )
            
            self.print_status("success", f"Index complete: {documents_processed} docs, {chunks_created} chunks")
            return True
            
        except Exception as e:
            self.print_status("error", f"Index rebuild failed: {e}")
            return False
    
    def test_complex_queries(self):
        """Test with complex, diverse queries"""
        self.print_header("Testing Complex Queries")
        
        # Define comprehensive test queries
        test_queries = [
            {
                "query": "What was the total revenue for TechCorp in 2024?",
                "expected_keywords": ["12.5 million", "revenue", "2024"],
                "expected_docs": ["financial_report_2024.pdf"],
                "category": "Financial"
            },
            {
                "query": "What is the authentication API endpoint and what does it return?",
                "expected_keywords": ["POST", "/api/auth/login", "token"],
                "expected_docs": ["api_technical_spec.pdf"],
                "category": "Technical"
            },
            {
                "query": "Who are the employees in the Engineering department?",
                "expected_keywords": ["Alice Johnson", "David Brown", "Engineering"],
                "expected_docs": ["employee_database.xlsx"],
                "category": "HR Data"
            },
            {
                "query": "What products do we have in stock and their prices?",
                "expected_keywords": ["Laptop", "Mouse", "SKU"],
                "expected_docs": ["product_inventory.xlsx"],
                "category": "Inventory"
            },
            {
                "query": "What is the invoice number and amount due?",
                "expected_keywords": ["INV-2024-001", "5,450", "invoice"],
                "expected_docs": ["invoice_ocr_test.png"],
                "category": "OCR - Invoice"
            },
            {
                "query": "Who attended the Q4 planning meeting?",
                "expected_keywords": ["Sarah", "Mike", "Jennifer", "Tom"],
                "expected_docs": ["meeting_notes_ocr.png"],
                "category": "OCR - Meeting"
            },
            {
                "query": "What is the database configuration in the application?",
                "expected_keywords": ["db.example.com", "5432", "analytics_db"],
                "expected_docs": ["app_config.json"],
                "category": "Configuration"
            },
            {
                "query": "What machine learning algorithm performed best for churn prediction?",
                "expected_keywords": ["XGBoost", "84.7", "accuracy"],
                "expected_docs": ["research_notes.txt"],
                "category": "Research"
            },
            {
                "query": "What are the strategic initiatives for 2025?",
                "expected_keywords": ["Digital Transformation", "Market Expansion", "AI"],
                "expected_docs": ["financial_report_2024.pdf"],
                "category": "Strategic"
            },
            {
                "query": "What is the average employee salary?",
                "expected_keywords": ["salary", "average", "employee"],
                "expected_docs": ["employee_database.xlsx"],
                "category": "HR Analytics"
            }
        ]
        
        correct = 0
        total = len(test_queries)
        total_time = 0
        
        for i, test in enumerate(test_queries, 1):
            print(f"\n[Test {i}/{total}] {test['category']}")
            self.print_status("info", f"Query: {test['query']}")
            
            start_time = time.time()
            
            try:
                # Perform retrieval
                results = self.vector_store.similarity_search_with_score(
                    test['query'],
                    k=5
                )
                
                retrieval_time = time.time() - start_time
                total_time += retrieval_time
                
                if not results:
                    self.print_status("error", "No results found")
                    test["status"] = "failed"
                    test["reason"] = "No results"
                    self.results["test_results"].append(test)
                    continue
                
                # Get top document
                top_doc, top_score = results[0]
                top_filename = os.path.basename(top_doc.metadata.get('source', ''))
                
                self.print_status("info", f"Top result: {top_filename} (score: {top_score:.4f})")
                self.print_status("info", f"Retrieval time: {retrieval_time:.3f}s")
                
                # Check if expected document is in top results
                retrieved_files = [os.path.basename(doc.metadata.get('source', '')) for doc, _ in results]
                expected_found = any(exp in retrieved_files for exp in test['expected_docs'])
                
                # Check content relevance
                content_snippet = top_doc.page_content[:200]
                self.print_status("info", f"Content snippet: {content_snippet[:100]}...")
                
                if expected_found:
                    self.print_status("success", "✓ Retrieved expected document")
                    correct += 1
                    test["status"] = "passed"
                else:
                    self.print_status("warning", f"⚠ Expected {test['expected_docs']}, got {top_filename}")
                    test["status"] = "partial"
                
                test["retrieved_doc"] = top_filename
                test["score"] = float(top_score)
                test["retrieval_time"] = retrieval_time
                
            except Exception as e:
                self.print_status("error", f"Query failed: {e}")
                test["status"] = "error"
                test["error"] = str(e)
            
            self.results["test_results"].append(test)
        
        # Calculate metrics
        accuracy = (correct / total) * 100 if total > 0 else 0
        avg_time = total_time / total if total > 0 else 0
        
        self.results["accuracy_score"] = accuracy
        self.results["avg_retrieval_time"] = avg_time
        
        print(f"\n{'='*80}")
        self.print_status("info", f"Accuracy: {correct}/{total} ({accuracy:.1f}%)")
        self.print_status("info", f"Average retrieval time: {avg_time:.3f}s")
        
        if accuracy >= 90:
            self.print_status("success", "🎉 Excellent accuracy!")
        elif accuracy >= 70:
            self.print_status("warning", "⚠ Good accuracy, some improvements possible")
        else:
            self.print_status("error", "❌ Low accuracy, needs investigation")
        
        return accuracy >= 70
    
    def generate_report(self):
        """Generate detailed test report"""
        self.print_header("Test Report Summary")
        
        print(f"📊 Total Documents Indexed: {self.results['total_documents']}")
        print(f"📝 Total Chunks Created: {self.results['total_chunks']}")
        print(f"✅ Accuracy Score: {self.results['accuracy_score']:.1f}%")
        print(f"⚡ Avg Retrieval Time: {self.results['avg_retrieval_time']:.3f}s")
        
        # Category breakdown
        categories = {}
        for test in self.results['test_results']:
            cat = test['category']
            status = test['status']
            if cat not in categories:
                categories[cat] = {'passed': 0, 'failed': 0, 'partial': 0, 'error': 0}
            categories[cat][status] = categories[cat].get(status, 0) + 1
        
        print(f"\n📋 Results by Category:")
        for cat, stats in categories.items():
            total = sum(stats.values())
            passed = stats.get('passed', 0)
            print(f"  • {cat}: {passed}/{total} passed")
        
        # Save detailed report
        report_path = "/app/rag_advanced_test_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.print_status("success", f"Detailed report saved: {report_path}")


def main():
    print("="*80)
    print("  Advanced RAG Testing - Comprehensive Evaluation")
    print("="*80)
    
    tester = AdvancedRAGTester()
    
    # Rebuild index
    if not tester.rebuild_index():
        print("\n❌ Failed to rebuild index")
        return 1
    
    # Run tests
    if not tester.test_complex_queries():
        print("\n⚠️ Some tests failed")
    
    # Generate report
    tester.generate_report()
    
    # Final verdict
    if tester.results["accuracy_score"] >= 90:
        print("\n✅ RAG system is performing excellently!")
        return 0
    elif tester.results["accuracy_score"] >= 70:
        print("\n⚠️ RAG system is functional with room for improvement")
        return 0
    else:
        print("\n❌ RAG system needs significant improvements")
        return 1


if __name__ == "__main__":
    sys.exit(main())
