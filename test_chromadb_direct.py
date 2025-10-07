#!/usr/bin/env python3
"""
Direct ChromaDB test - bypass API to test data retrieval
"""
import sys
sys.path.insert(0, '/app')

from backend.config import settings
import chromadb
from langchain_huggingface import HuggingFaceEmbeddings

print("=" * 70)
print("Direct ChromaDB Data Retrieval Test")
print("=" * 70)
print()

# Create client directly
print("Creating ChromaDB client...")
client = chromadb.PersistentClient(
    path=settings.CHROMA_DB_PATH,
    settings=chromadb.Settings(
        anonymized_telemetry=False,
        allow_reset=True,
        is_persistent=True
    )
)
print("✓ Client created")
print()

# Get collection
print("Getting collection...")
try:
    collection = client.get_collection("knowledge_base_collection")
    doc_count = collection.count()
    print(f"✓ Collection found with {doc_count} chunks")
    print()
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Get sample documents
print("Retrieving sample documents...")
results = collection.get(limit=5, include=['documents', 'metadatas'])

if results['documents']:
    print(f"✓ Retrieved {len(results['documents'])} sample chunks")
    print()
    
    for i, (doc, meta) in enumerate(zip(results['documents'], results['metadatas']), 1):
        print(f"Sample {i}:")
        print(f"  File: {meta.get('file_name', 'Unknown')}")
        print(f"  Content preview: {doc[:150]}...")
        print()
else:
    print("❌ No documents found")
    sys.exit(1)

# Test search without embeddings
print("=" * 70)
print("Testing Search with Embeddings")
print("=" * 70)
print()

print("Loading embeddings model...")
embeddings = HuggingFaceEmbeddings(
    model_name=settings.EMBEDDING_MODEL_NAME,
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'batch_size': 8, 'normalize_embeddings': True}
)
print("✓ Embeddings loaded")
print()

# Embed query
query = "What is the annual revenue?"
print(f"Query: '{query}'")
print("Creating query embedding...")
query_embedding = embeddings.embed_query(query)
print(f"✓ Query embedded (dimension: {len(query_embedding)})")
print()

# Search
print("Searching collection...")
search_results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3,
    include=['documents', 'metadatas', 'distances']
)

if search_results['documents'] and search_results['documents'][0]:
    docs = search_results['documents'][0]
    metas = search_results['metadatas'][0]
    distances = search_results['distances'][0]
    
    print(f"✓ Found {len(docs)} results")
    print()
    
    for i, (doc, meta, dist) in enumerate(zip(docs, metas, distances), 1):
        print(f"Result {i} (distance: {dist:.4f}):")
        print(f"  File: {meta.get('file_name', 'Unknown')}")
        print(f"  Content: {doc[:200]}...")
        print()
    
    # Check if financial report is in results
    financial_found = any('financial' in m.get('file_name', '').lower() for m in metas)
    revenue_found = any('revenue' in d.lower() or '5,200,000' in d or '5.2' in d for d in docs)
    
    print("=" * 70)
    print("Accuracy Check")
    print("=" * 70)
    print(f"Financial document found: {'✅ YES' if financial_found else '❌ NO'}")
    print(f"Revenue data found: {'✅ YES' if revenue_found else '❌ NO'}")
    print()
    
    if financial_found and revenue_found:
        print("🎉 RAG RETRIEVAL WORKING - Data retrieved correctly!")
        sys.exit(0)
    else:
        print("⚠️  RAG needs tuning - correct data not in top results")
        sys.exit(1)
else:
    print("❌ No search results returned")
    sys.exit(1)
