#!/usr/bin/env python3
"""
Robust ChromaDB Fix Script for NeuralStark
Addresses HNSW segment reader errors and ensures reliable RAG functionality
"""

import os
import sys
import shutil
import chromadb
from pathlib import Path
import logging

# Add the project root to the Python path
sys.path.insert(0, '/app')

from backend.config import settings
from backend.celery_app import get_embeddings, get_text_splitter
from backend.document_parser import parse_document
from langchain_chroma import Chroma

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_chromadb_completely():
    """Completely clean ChromaDB directory and recreate"""
    print("🧹 Cleaning ChromaDB completely...")
    
    if os.path.exists(settings.CHROMA_DB_PATH):
        shutil.rmtree(settings.CHROMA_DB_PATH)
        print(f"   Removed {settings.CHROMA_DB_PATH}")
    
    # Recreate directory
    os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
    os.chmod(settings.CHROMA_DB_PATH, 0o755)
    print(f"   Recreated {settings.CHROMA_DB_PATH}")

def initialize_chromadb_collection():
    """Initialize ChromaDB with proper configuration"""
    print("🔧 Initializing ChromaDB collection...")
    
    try:
        # Create client with persistent storage
        client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        
        # Delete collection if it exists
        try:
            client.delete_collection("knowledge_base_collection")
            print("   Deleted existing collection")
        except ValueError:
            pass  # Collection doesn't exist
        
        # Create new collection with proper settings
        collection = client.create_collection(
            name="knowledge_base_collection",
            metadata={"hnsw:space": "cosine"},  # Explicitly set distance metric
        )
        
        print("   ✅ Collection created successfully")
        return client, collection
        
    except Exception as e:
        print(f"   ❌ Error initializing ChromaDB: {e}")
        return None, None

def reindex_all_documents():
    """Re-index all documents in the knowledge base"""
    print("📚 Re-indexing all documents...")
    
    embeddings = get_embeddings()
    text_splitter = get_text_splitter()
    
    # Initialize ChromaDB
    client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
    vector_store = Chroma(
        client=client,
        embedding_function=embeddings,
        collection_name="knowledge_base_collection"
    )
    
    # Find all documents
    documents_to_process = []
    for kb_dir in [settings.INTERNAL_KNOWLEDGE_BASE_PATH, settings.EXTERNAL_KNOWLEDGE_BASE_PATH]:
        if os.path.exists(kb_dir):
            for root, dirs, files in os.walk(kb_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    documents_to_process.append(file_path)
    
    print(f"   Found {len(documents_to_process)} documents to process")
    
    processed_count = 0
    failed_count = 0
    
    for file_path in documents_to_process:
        try:
            print(f"   Processing: {os.path.basename(file_path)}")
            
            # Extract text
            extracted_text = parse_document(file_path)
            
            if extracted_text and extracted_text.strip():
                # Split into chunks
                texts = text_splitter.split_text(extracted_text)
                texts = [text for text in texts if text and text.strip()]
                
                if texts:
                    # Determine source type
                    source_type = "internal" if settings.INTERNAL_KNOWLEDGE_BASE_PATH in file_path else "external"
                    
                    # Prepare metadata
                    metadatas = [{
                        "source": os.path.abspath(file_path),
                        "file_name": os.path.basename(file_path),
                        "source_type": source_type,
                        "timestamp": os.path.getmtime(file_path),
                        "chunk_index": i
                    } for i in range(len(texts))]
                    
                    # Add to ChromaDB
                    vector_store.add_texts(texts=texts, metadatas=metadatas)
                    processed_count += 1
                    print(f"     ✅ Indexed {len(texts)} chunks")
                else:
                    print(f"     ⚠️  No content after chunking")
            else:
                print(f"     ⚠️  No text extracted")
                
        except Exception as e:
            print(f"     ❌ Error processing {file_path}: {e}")
            failed_count += 1
    
    print(f"   📊 Processing complete: {processed_count} succeeded, {failed_count} failed")
    return processed_count

def test_chromadb_search():
    """Test ChromaDB search functionality"""
    print("🔍 Testing ChromaDB search...")
    
    try:
        embeddings = get_embeddings()
        client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        vector_store = Chroma(
            client=client,
            embedding_function=embeddings,
            collection_name="knowledge_base_collection"
        )
        
        # Test basic retrieval
        results = vector_store.similarity_search("test document", k=5)
        print(f"   Found {len(results)} documents for 'test document'")
        
        if results:
            print(f"   First result: {results[0].page_content[:100]}...")
            print("   ✅ Search working correctly")
            return True
        else:
            print("   ⚠️  No results found")
            return False
            
    except Exception as e:
        print(f"   ❌ Search test failed: {e}")
        return False

def main():
    """Main function to fix ChromaDB issues"""
    print("🚀 Starting robust ChromaDB fix...")
    print("=" * 50)
    
    # Step 1: Clean ChromaDB
    clean_chromadb_completely()
    
    # Step 2: Initialize collection
    client, collection = initialize_chromadb_collection()
    if not client:
        print("❌ Failed to initialize ChromaDB. Exiting.")
        return False
    
    # Step 3: Re-index documents
    processed = reindex_all_documents()
    
    # Step 4: Test search
    search_works = test_chromadb_search()
    
    print("=" * 50)
    if processed > 0 and search_works:
        print("✅ ChromaDB fix completed successfully!")
        print(f"   📚 {processed} documents indexed")
        print("   🔍 Search functionality verified")
        return True
    else:
        print("❌ ChromaDB fix encountered issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)