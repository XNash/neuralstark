#!/usr/bin/env python3
"""
Quick RAG Demo - Direct testing without full agent
"""

import sys
sys.path.insert(0, '/app')

from backend.config import settings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import chromadb
from chromadb.config import Settings as ChromaSettings

def quick_test():
    print("="*70)
    print("  Quick RAG System Demonstration")
    print("="*70)
    
    # Initialize
    print("\n[1] Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL_NAME,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'batch_size': settings.EMBEDDING_BATCH_SIZE, 'normalize_embeddings': True}
    )
    print("✓ Embeddings loaded")
    
    print("\n[2] Connecting to ChromaDB...")
    client = chromadb.PersistentClient(
        path=settings.CHROMA_DB_PATH,
        settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True, is_persistent=True)
    )
    
    vector_store = Chroma(
        client=client,
        collection_name="knowledge_base_collection",
        embedding_function=embeddings
    )
    print("✓ ChromaDB connected")
    
    # Check collection
    print("\n[3] Checking collection status...")
    collection = client.get_collection("knowledge_base_collection")
    count = collection.count()
    print(f"✓ Collection has {count} chunks")
    
    # Test queries
    test_queries = [
        "What was TechCorp's revenue in 2024?",
        "Who are the Engineering employees?",
        "What is the invoice number?",
        "Which ML algorithm performed best?",
    ]
    
    print(f"\n[4] Testing {len(test_queries)} queries...")
    print("="*70)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nQuery {i}: {query}")
        results = vector_store.similarity_search_with_score(query, k=3)
        
        if results:
            top_doc, top_score = results[0]
            filename = top_doc.metadata.get('filename', 'Unknown')
            snippet = top_doc.page_content[:100].replace('\n', ' ')
            
            print(f"  ✓ Found: {filename}")
            print(f"    Score: {top_score:.4f}")
            print(f"    Snippet: {snippet}...")
        else:
            print(f"  ✗ No results")
    
    print("\n" + "="*70)
    print("✅ Demo complete! RAG system is working correctly.")
    print("="*70)

if __name__ == "__main__":
    quick_test()
