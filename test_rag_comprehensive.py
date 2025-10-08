#!/usr/bin/env python3
"""
Comprehensive RAG Testing Script for NeuralStark
Tests document retrieval accuracy, ChromaDB health, and fixes issues
"""

import sys
import os
import json
import time
import traceback
from pathlib import Path

# Add backend to path
sys.path.insert(0, '/app')

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from backend.config import settings
from backend.document_parser import parse_document
from langchain.text_splitter import RecursiveCharacterTextSplitter


class RAGTester:
    def __init__(self):
        self.results = {
            "chromadb_health": None,
            "documents_indexed": [],
            "test_queries": [],
            "accuracy_score": 0.0,
            "errors": [],
            "warnings": []
        }
        
    def print_header(self, text):
        print(f"\n{'='*70}")
        print(f"  {text}")
        print(f"{'='*70}\n")
    
    def print_status(self, status, message):
        symbols = {"success": "✓", "error": "✗", "warning": "⚠", "info": "ℹ"}
        print(f"{symbols.get(status, '•')} {message}")
    
    def test_chromadb_health(self):
        """Test ChromaDB connection and health"""
        self.print_header("Phase 1: ChromaDB Health Check")
        
        try:
            # Test 1: Directory exists and is writable
            chroma_path = Path(settings.CHROMA_DB_PATH)
            if not chroma_path.exists():
                os.makedirs(chroma_path, exist_ok=True)
                self.print_status("warning", f"Created ChromaDB directory: {chroma_path}")
            else:
                self.print_status("success", f"ChromaDB directory exists: {chroma_path}")
            
            # Check if writable
            test_file = chroma_path / ".write_test"
            try:
                test_file.touch()
                test_file.unlink()
                self.print_status("success", "ChromaDB directory is writable")
            except Exception as e:
                self.print_status("error", f"ChromaDB directory not writable: {e}")
                self.results["errors"].append(f"ChromaDB directory not writable: {e}")
                return False
            
            # Test 2: Create client
            try:
                client = chromadb.PersistentClient(
                    path=str(chroma_path),
                    settings=ChromaSettings(
                        anonymized_telemetry=False,
                        allow_reset=True,
                        is_persistent=True
                    )
                )
                client.heartbeat()
                self.print_status("success", "ChromaDB client created and responsive")
            except Exception as e:
                self.print_status("error", f"ChromaDB client creation failed: {e}")
                self.results["errors"].append(f"ChromaDB client failed: {e}")
                return False
            
            # Test 3: Check collection
            try:
                collections = client.list_collections()
                collection_names = [c.name for c in collections]
                self.print_status("info", f"Found {len(collections)} collection(s): {collection_names}")
                
                if "knowledge_base_collection" in collection_names:
                    collection = client.get_collection("knowledge_base_collection")
                    count = collection.count()
                    self.print_status("success", f"Knowledge base collection has {count} chunks")
                    
                    # Get metadata
                    if count > 0:
                        sample = collection.get(limit=3, include=['documents', 'metadatas'])
                        unique_sources = set()
                        for meta in sample['metadatas']:
                            if 'source' in meta:
                                unique_sources.add(os.path.basename(meta['source']))
                        self.print_status("info", f"Sample sources: {', '.join(list(unique_sources)[:3])}")
                else:
                    self.print_status("warning", "Knowledge base collection does not exist yet")
                    self.results["warnings"].append("Collection not created yet")
            
            except Exception as e:
                self.print_status("error", f"Collection check failed: {e}")
                self.results["errors"].append(f"Collection check failed: {e}")
                traceback.print_exc()
                return False
            
            self.results["chromadb_health"] = "healthy"
            return True
            
        except Exception as e:
            self.print_status("error", f"ChromaDB health check failed: {e}")
            self.results["chromadb_health"] = "failed"
            self.results["errors"].append(str(e))
            traceback.print_exc()
            return False
    
    def rebuild_index(self):
        """Rebuild the entire ChromaDB index from scratch"""
        self.print_header("Phase 2: Rebuilding ChromaDB Index")
        
        try:
            # Initialize embeddings
            self.print_status("info", "Loading embedding model...")
            embeddings = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL_NAME,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={
                    'batch_size': settings.EMBEDDING_BATCH_SIZE,
                    'normalize_embeddings': True
                }
            )
            self.print_status("success", "Embedding model loaded")
            
            # Create/reset ChromaDB client
            self.print_status("info", "Creating ChromaDB client...")
            client = chromadb.PersistentClient(
                path=settings.CHROMA_DB_PATH,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=True
                )
            )
            
            # Delete existing collection if it exists
            try:
                client.delete_collection("knowledge_base_collection")
                self.print_status("info", "Deleted existing collection")
            except:
                pass
            
            # Create new collection
            collection = client.create_collection(
                name="knowledge_base_collection",
                metadata={"hnsw:space": "cosine"}
            )
            self.print_status("success", "Created new collection")
            
            # Create text splitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                length_function=len
            )
            
            # Index all documents
            documents_processed = 0
            chunks_created = 0
            
            for kb_type in ["internal", "external"]:
                kb_path = settings.INTERNAL_KNOWLEDGE_BASE_PATH if kb_type == "internal" else settings.EXTERNAL_KNOWLEDGE_BASE_PATH
                
                if not os.path.exists(kb_path):
                    continue
                
                for filename in os.listdir(kb_path):
                    file_path = os.path.join(kb_path, filename)
                    
                    if not os.path.isfile(file_path):
                        continue
                    
                    self.print_status("info", f"Processing: {filename}")
                    
                    try:
                        # Parse document
                        content = parse_document(file_path)
                        
                        if not content or not content.strip():
                            self.print_status("warning", f"  No content extracted from {filename}")
                            continue
                        
                        # Split into chunks
                        chunks = text_splitter.split_text(content)
                        self.print_status("info", f"  Created {len(chunks)} chunks")
                        
                        # Create embeddings and add to collection
                        for i, chunk in enumerate(chunks):
                            if not chunk.strip():
                                continue
                            
                            embedding = embeddings.embed_query(chunk)
                            
                            collection.add(
                                embeddings=[embedding],
                                documents=[chunk],
                                metadatas=[{
                                    "source": file_path,
                                    "source_type": kb_type,
                                    "chunk_index": i,
                                    "filename": filename
                                }],
                                ids=[f"{filename}_{i}_{int(time.time())}"]
                            )
                            chunks_created += 1
                        
                        documents_processed += 1
                        self.results["documents_indexed"].append(filename)
                        self.print_status("success", f"  Indexed: {filename}")
                        
                    except Exception as e:
                        self.print_status("error", f"  Failed to process {filename}: {e}")
                        self.results["errors"].append(f"Failed to process {filename}: {e}")
            
            self.print_status("success", f"Index rebuilt: {documents_processed} documents, {chunks_created} chunks")
            return True
            
        except Exception as e:
            self.print_status("error", f"Index rebuild failed: {e}")
            self.results["errors"].append(f"Index rebuild failed: {e}")
            traceback.print_exc()
            return False
    
    def test_retrieval_accuracy(self):
        """Test retrieval accuracy with various queries"""
        self.print_header("Phase 3: Testing RAG Retrieval Accuracy")
        
        # Define test queries with expected documents
        test_queries = [
            {
                "query": "What information is in the test text file?",
                "expected_docs": ["test_text.txt"],
                "description": "Simple text file retrieval"
            },
            {
                "query": "What data is in the spreadsheet?",
                "expected_docs": ["test_spreadsheet.xlsx", "test_spreadsheet.csv"],
                "description": "Spreadsheet data retrieval"
            },
            {
                "query": "What is in the PDF document?",
                "expected_docs": ["test_document.pdf"],
                "description": "PDF document retrieval"
            },
            {
                "query": "What content is in the Word document?",
                "expected_docs": ["test_document.docx"],
                "description": "DOCX document retrieval"
            },
            {
                "query": "What is in the markdown file?",
                "expected_docs": ["test_markdown.md"],
                "description": "Markdown file retrieval"
            },
            {
                "query": "What JSON data do you have?",
                "expected_docs": ["test_data.json"],
                "description": "JSON file retrieval"
            }
        ]
        
        try:
            # Initialize
            embeddings = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL_NAME,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={
                    'batch_size': settings.EMBEDDING_BATCH_SIZE,
                    'normalize_embeddings': True
                }
            )
            
            client = chromadb.PersistentClient(
                path=settings.CHROMA_DB_PATH,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=True
                )
            )
            
            vector_store = Chroma(
                client=client,
                collection_name="knowledge_base_collection",
                embedding_function=embeddings
            )
            
            # Test each query
            correct_retrievals = 0
            total_tests = len(test_queries)
            
            for test in test_queries:
                self.print_status("info", f"Testing: {test['description']}")
                self.print_status("info", f"  Query: {test['query']}")
                
                try:
                    # Perform retrieval
                    results = vector_store.similarity_search_with_score(
                        test['query'],
                        k=5
                    )
                    
                    if not results:
                        self.print_status("error", "  No results found")
                        test["status"] = "failed"
                        test["retrieved_docs"] = []
                        continue
                    
                    # Extract source documents
                    retrieved_sources = []
                    for doc, score in results:
                        source = doc.metadata.get('source', '')
                        filename = os.path.basename(source)
                        retrieved_sources.append(filename)
                        self.print_status("info", f"    Found: {filename} (score: {score:.4f})")
                    
                    # Check if expected docs were retrieved
                    found_expected = any(expected in retrieved_sources for expected in test['expected_docs'])
                    
                    if found_expected:
                        self.print_status("success", f"  ✓ Retrieved expected document(s)")
                        correct_retrievals += 1
                        test["status"] = "passed"
                    else:
                        self.print_status("error", f"  ✗ Did not retrieve expected document(s): {test['expected_docs']}")
                        test["status"] = "failed"
                    
                    test["retrieved_docs"] = retrieved_sources[:3]
                    
                except Exception as e:
                    self.print_status("error", f"  Query failed: {e}")
                    test["status"] = "error"
                    test["error"] = str(e)
                
                self.results["test_queries"].append(test)
                print()
            
            # Calculate accuracy
            accuracy = (correct_retrievals / total_tests) * 100 if total_tests > 0 else 0
            self.results["accuracy_score"] = accuracy
            
            self.print_status("info", f"Accuracy: {correct_retrievals}/{total_tests} ({accuracy:.1f}%)")
            
            if accuracy == 100:
                self.print_status("success", "🎉 Perfect accuracy achieved!")
            elif accuracy >= 80:
                self.print_status("warning", "Good accuracy, but room for improvement")
            else:
                self.print_status("error", "Low accuracy - needs investigation")
            
            return accuracy >= 80
            
        except Exception as e:
            self.print_status("error", f"Retrieval testing failed: {e}")
            self.results["errors"].append(f"Retrieval testing failed: {e}")
            traceback.print_exc()
            return False
    
    def generate_report(self):
        """Generate final report"""
        self.print_header("Final Report")
        
        print(f"ChromaDB Health: {self.results['chromadb_health']}")
        print(f"Documents Indexed: {len(self.results['documents_indexed'])}")
        print(f"Retrieval Accuracy: {self.results['accuracy_score']:.1f}%")
        print(f"Errors: {len(self.results['errors'])}")
        print(f"Warnings: {len(self.results['warnings'])}")
        
        if self.results['errors']:
            print("\nErrors encountered:")
            for error in self.results['errors']:
                print(f"  • {error}")
        
        if self.results['warnings']:
            print("\nWarnings:")
            for warning in self.results['warnings']:
                print(f"  • {warning}")
        
        # Save detailed report
        report_path = "/app/rag_test_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nDetailed report saved to: {report_path}")


def main():
    print("="*70)
    print("  NeuralStark RAG Comprehensive Testing")
    print("="*70)
    
    tester = RAGTester()
    
    # Phase 1: Health check
    if not tester.test_chromadb_health():
        print("\n⚠️  ChromaDB health check failed. Attempting to rebuild...")
        if not tester.rebuild_index():
            print("\n❌ Failed to rebuild index. Please check errors above.")
            tester.generate_report()
            return 1
    
    # Check if documents are indexed
    try:
        client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        collection = client.get_collection("knowledge_base_collection")
        doc_count = collection.count()
        
        if doc_count == 0:
            print("\n⚠️  No documents indexed. Rebuilding index...")
            if not tester.rebuild_index():
                print("\n❌ Failed to rebuild index.")
                tester.generate_report()
                return 1
    except:
        print("\n⚠️  Cannot access collection. Rebuilding index...")
        if not tester.rebuild_index():
            print("\n❌ Failed to rebuild index.")
            tester.generate_report()
            return 1
    
    # Phase 2: Test retrieval
    tester.test_retrieval_accuracy()
    
    # Generate report
    tester.generate_report()
    
    # Return status
    if tester.results["accuracy_score"] >= 100 and len(tester.results["errors"]) == 0:
        print("\n✅ All tests passed! RAG system is working perfectly.")
        return 0
    elif tester.results["accuracy_score"] >= 80:
        print("\n⚠️  Tests passed with warnings. System is functional but could be improved.")
        return 0
    else:
        print("\n❌ Tests failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
