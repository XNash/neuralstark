#!/usr/bin/env python3
"""
Test RAG with the newly created documents
"""

import sys
import os
import time
sys.path.insert(0, '/app')

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from backend.config import settings
from backend.document_parser import parse_document
from langchain.text_splitter import RecursiveCharacterTextSplitter

def rebuild_index_with_new_docs():
    """Rebuild index focusing on new documents"""
    print("="*80)
    print("  Rebuilding RAG Index with New Documents")
    print("="*80)
    
    # Initialize embeddings
    print("\n[1] Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL_NAME,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'batch_size': settings.EMBEDDING_BATCH_SIZE, 'normalize_embeddings': True}
    )
    print("✓ Embeddings loaded")
    
    # Create ChromaDB client
    print("\n[2] Resetting ChromaDB collection...")
    client = chromadb.PersistentClient(
        path=settings.CHROMA_DB_PATH,
        settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True, is_persistent=True)
    )
    
    # Delete and recreate collection
    try:
        client.delete_collection("knowledge_base_collection")
        print("✓ Deleted old collection")
    except:
        pass
    
    collection = client.create_collection(
        name="knowledge_base_collection",
        metadata={"hnsw:space": "cosine"}
    )
    print("✓ Created new collection")
    
    # Text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        length_function=len
    )
    
    # Focus on the 4 new documents
    new_docs = [
        "sales_report_q4_2024.xlsx",
        "ai_chatbot_project_proposal.docx",
        "software_license_agreement.pdf",
        "restaurant_receipt_scan.pdf"
    ]
    
    print(f"\n[3] Indexing {len(new_docs)} new documents...")
    print("-" * 80)
    
    kb_path = settings.INTERNAL_KNOWLEDGE_BASE_PATH
    total_chunks = 0
    
    for filename in new_docs:
        file_path = os.path.join(kb_path, filename)
        
        if not os.path.exists(file_path):
            print(f"⚠ File not found: {filename}")
            continue
        
        print(f"\n📄 Processing: {filename}")
        
        try:
            # Parse document
            content = parse_document(file_path)
            
            if not content or not content.strip():
                print(f"  ⚠ No content extracted")
                continue
            
            print(f"  ✓ Extracted {len(content)} characters")
            
            # Split into chunks
            chunks = text_splitter.split_text(content)
            print(f"  ✓ Created {len(chunks)} chunks")
            
            # Add to collection
            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue
                
                embedding = embeddings.embed_query(chunk)
                
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
                total_chunks += 1
            
            print(f"  ✓ Indexed successfully")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print("\n" + "="*80)
    print(f"✅ Index rebuilt: {len(new_docs)} documents, {total_chunks} chunks")
    print("="*80)
    
    # Return vector store
    vector_store = Chroma(
        client=client,
        collection_name="knowledge_base_collection",
        embedding_function=embeddings
    )
    
    return vector_store

def test_new_documents(vector_store):
    """Test queries against new documents"""
    print("\n" + "="*80)
    print("  Testing RAG with Specific Questions")
    print("="*80)
    
    # Define test queries for each document type
    test_queries = [
        {
            "doc_type": "XLSX - Sales Report",
            "query": "What was the total Q4 sales amount in the sales report?",
            "expected_file": "sales_report_q4_2024.xlsx",
            "expected_answer": "1,549,000 or December as best month"
        },
        {
            "doc_type": "XLSX - Sales Report",
            "query": "Who was the top performing sales representative?",
            "expected_file": "sales_report_q4_2024.xlsx",
            "expected_answer": "Michael Chen"
        },
        {
            "doc_type": "XLSX - Sales Report", 
            "query": "Which product sold the most units?",
            "expected_file": "sales_report_q4_2024.xlsx",
            "expected_answer": "Wireless Earbuds with 5,620 units"
        },
        {
            "doc_type": "DOCX - Project Proposal",
            "query": "What is the budget for the AI chatbot project?",
            "expected_file": "ai_chatbot_project_proposal.docx",
            "expected_answer": "$450,000"
        },
        {
            "doc_type": "DOCX - Project Proposal",
            "query": "Who is the project manager for the AI chatbot?",
            "expected_file": "ai_chatbot_project_proposal.docx",
            "expected_answer": "Rebecca Foster"
        },
        {
            "doc_type": "DOCX - Project Proposal",
            "query": "What AI model will be used in the chatbot project?",
            "expected_file": "ai_chatbot_project_proposal.docx",
            "expected_answer": "GPT-4 Turbo"
        },
        {
            "doc_type": "PDF - Legal Contract",
            "query": "What is the software license agreement number?",
            "expected_file": "software_license_agreement.pdf",
            "expected_answer": "SLA-2024-7856"
        },
        {
            "doc_type": "PDF - Legal Contract",
            "query": "What is the total license fee in the agreement?",
            "expected_file": "software_license_agreement.pdf",
            "expected_answer": "$125,000"
        },
        {
            "doc_type": "PDF - Legal Contract",
            "query": "How many concurrent users are permitted in the license?",
            "expected_file": "software_license_agreement.pdf",
            "expected_answer": "500 users"
        },
        {
            "doc_type": "PDF OCR - Receipt",
            "query": "What is the receipt number from the restaurant?",
            "expected_file": "restaurant_receipt_scan.pdf",
            "expected_answer": "R-2024-08956"
        },
        {
            "doc_type": "PDF OCR - Receipt",
            "query": "What was the total amount on the restaurant receipt?",
            "expected_file": "restaurant_receipt_scan.pdf",
            "expected_answer": "$151.17"
        },
        {
            "doc_type": "PDF OCR - Receipt",
            "query": "Who was the server at the restaurant?",
            "expected_file": "restaurant_receipt_scan.pdf",
            "expected_answer": "Maria Rodriguez"
        },
    ]
    
    passed = 0
    total = len(test_queries)
    results = []
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{'─'*80}")
        print(f"Test {i}/{total}: {test['doc_type']}")
        print(f"{'─'*80}")
        print(f"❓ Query: {test['query']}")
        print(f"📄 Expected file: {test['expected_file']}")
        print(f"💡 Expected answer: {test['expected_answer']}")
        
        try:
            start_time = time.time()
            results_list = vector_store.similarity_search_with_score(test['query'], k=3)
            elapsed = time.time() - start_time
            
            if not results_list:
                print(f"❌ No results found")
                test['status'] = 'FAILED'
                test['reason'] = 'No results'
                results.append(test)
                continue
            
            # Get top result
            top_doc, top_score = results_list[0]
            top_filename = top_doc.metadata.get('filename', 'Unknown')
            content_snippet = top_doc.page_content[:200].replace('\n', ' ')
            
            print(f"\n📊 Results:")
            print(f"   Top match: {top_filename}")
            print(f"   Similarity score: {top_score:.4f}")
            print(f"   Response time: {elapsed:.3f}s")
            print(f"   Content: {content_snippet}...")
            
            # Check if correct file was retrieved
            if test['expected_file'] == top_filename:
                print(f"\n✅ PASS - Retrieved correct document!")
                passed += 1
                test['status'] = 'PASSED'
            else:
                print(f"\n⚠️  PARTIAL - Expected {test['expected_file']}, got {top_filename}")
                test['status'] = 'PARTIAL'
            
            test['retrieved_file'] = top_filename
            test['score'] = float(top_score)
            test['time'] = elapsed
            results.append(test)
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            test['status'] = 'ERROR'
            test['error'] = str(e)
            results.append(test)
    
    # Summary
    print("\n" + "="*80)
    print("  TEST SUMMARY")
    print("="*80)
    
    print(f"\n📈 Overall Results:")
    print(f"   Total tests: {total}")
    print(f"   Passed: {passed}")
    print(f"   Accuracy: {(passed/total)*100:.1f}%")
    
    # Breakdown by document type
    print(f"\n📊 Breakdown by Document Type:")
    
    doc_types = {}
    for test in results:
        dtype = test['doc_type'].split(' - ')[0]
        if dtype not in doc_types:
            doc_types[dtype] = {'passed': 0, 'total': 0}
        doc_types[dtype]['total'] += 1
        if test['status'] == 'PASSED':
            doc_types[dtype]['passed'] += 1
    
    for dtype, stats in doc_types.items():
        accuracy = (stats['passed']/stats['total'])*100 if stats['total'] > 0 else 0
        status = "✅" if accuracy == 100 else "⚠️" if accuracy >= 80 else "❌"
        print(f"   {status} {dtype}: {stats['passed']}/{stats['total']} ({accuracy:.0f}%)")
    
    if passed == total:
        print(f"\n🎉 PERFECT! All tests passed with 100% accuracy!")
    elif passed >= total * 0.8:
        print(f"\n✅ GOOD! Most tests passed ({(passed/total)*100:.0f}% accuracy)")
    else:
        print(f"\n⚠️  NEEDS IMPROVEMENT ({(passed/total)*100:.0f}% accuracy)")
    
    print("="*80)
    
    return results

def main():
    print("\n" + "╔" + "═"*78 + "╗")
    print("║" + " "*20 + "RAG TESTING WITH NEW DOCUMENTS" + " "*28 + "║")
    print("╚" + "═"*78 + "╝")
    
    # Rebuild index
    vector_store = rebuild_index_with_new_docs()
    
    # Wait a moment for indexing to settle
    time.sleep(2)
    
    # Test with queries
    results = test_new_documents(vector_store)
    
    # Save results
    import json
    with open('/app/new_docs_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: /app/new_docs_test_results.json")
    
    return results

if __name__ == "__main__":
    main()
