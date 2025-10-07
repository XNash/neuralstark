#!/usr/bin/env python3
"""
Manual RAG test - Process documents and test retrieval
"""
import sys
sys.path.insert(0, '/app')

from backend.chromadb_manager import get_chroma_manager
from backend.document_parser import parse_document
from backend.config import settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

def process_and_index_documents():
    """Manually process and index test documents"""
    print("=" * 70)
    print("Manual Document Processing and Indexing")
    print("=" * 70)
    print()
    
    # Get ChromaDB manager
    print("Initializing ChromaDB Manager...")
    chroma_manager = get_chroma_manager()
    
    # Health check
    if not chroma_manager.health_check():
        print("❌ ChromaDB health check failed!")
        return False
    print("✓ ChromaDB is healthy")
    print()
    
    # Get vector store
    vector_store = chroma_manager.get_vector_store()
    print("✓ Vector store initialized")
    print()
    
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    print(f"✓ Text splitter ready (chunk_size={settings.CHUNK_SIZE}, overlap={settings.CHUNK_OVERLAP})")
    print()
    
    # Get all files in knowledge base
    kb_path = settings.INTERNAL_KNOWLEDGE_BASE_PATH
    files = [f for f in os.listdir(kb_path) if os.path.isfile(os.path.join(kb_path, f))]
    
    # Filter to only process our test documents
    test_docs = [
        'financial_report_2024.pdf',
        'product_catalog_2024.pdf',
        'employee_handbook.docx',
        'meeting_notes.docx',
        'sales_data_q4.xlsx',
        'inventory_status.xlsx',
        'company_overview.txt',
        'invoice_001.txt',
        'contact_info.png',
        'pricing_table.png'
    ]
    
    files = [f for f in files if f in test_docs]
    
    print(f"Found {len(files)} test documents to process")
    print()
    
    successful = 0
    failed = 0
    
    for i, filename in enumerate(files, 1):
        filepath = os.path.join(kb_path, filename)
        print(f"[{i}/{len(files)}] Processing: {filename}")
        
        try:
            # Parse document
            text = parse_document(filepath)
            
            if not text or not text.strip():
                print(f"  ⚠ No text extracted from {filename}")
                failed += 1
                continue
            
            print(f"  ✓ Extracted {len(text)} characters")
            
            # Split into chunks
            chunks = text_splitter.split_text(text)
            chunks = [c for c in chunks if c and c.strip()]
            
            if not chunks:
                print(f"  ⚠ No valid chunks after splitting")
                failed += 1
                continue
            
            print(f"  ✓ Split into {len(chunks)} chunks")
            
            # Create metadata
            metadatas = [{
                "source": filepath,
                "file_name": filename,
                "source_type": "internal",
                "chunk_index": idx
            } for idx in range(len(chunks))]
            
            # Add to vector store
            vector_store.add_texts(texts=chunks, metadatas=metadatas)
            print(f"  ✓ Indexed {len(chunks)} chunks")
            successful += 1
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed += 1
        
        print()
    
    print("=" * 70)
    print(f"Processing complete: {successful} successful, {failed} failed")
    print("=" * 70)
    print()
    
    # Verify indexing
    info = chroma_manager.get_collection_info()
    print(f"Total documents in ChromaDB: {info.get('count', 0)}")
    print()
    
    return successful > 0

if __name__ == "__main__":
    success = process_and_index_documents()
    sys.exit(0 if success else 1)
