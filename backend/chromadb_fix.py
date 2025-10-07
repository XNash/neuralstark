"""
ChromaDB Fix for NeuralStark - Robust implementation to prevent HNSW errors
"""
import chromadb
import os
import shutil
import time
import logging
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from backend.config import settings

logging.basicConfig(level=logging.INFO)

def create_robust_vector_store():
    """Create a robust ChromaDB vector store with proper error handling"""
    
    # Ensure ChromaDB directory exists and is clean
    if not os.path.exists(settings.CHROMA_DB_PATH):
        os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
    
    try:
        # Initialize embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'batch_size': settings.EMBEDDING_BATCH_SIZE, 'normalize_embeddings': True}
        )
        
        # Create ChromaDB client with robustness settings
        chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_DB_PATH,
            settings=chromadb.Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Try to get or create collection
        try:
            collection = chroma_client.get_collection("knowledge_base_collection")
            logging.info("Using existing ChromaDB collection")
        except ValueError:
            # Collection doesn't exist, create it
            collection = chroma_client.create_collection(
                name="knowledge_base_collection",
                metadata={"hnsw:space": "cosine"}
            )
            logging.info("Created new ChromaDB collection")
        
        # Create Langchain ChromaDB wrapper
        vector_store = Chroma(
            client=chroma_client,
            collection_name="knowledge_base_collection",
            embedding_function=embeddings
        )
        
        return vector_store, chroma_client
        
    except Exception as e:
        logging.error(f"Error creating vector store: {e}")
        
        # If there's an error, clean up and try again
        if os.path.exists(settings.CHROMA_DB_PATH):
            shutil.rmtree(settings.CHROMA_DB_PATH)
            os.makedirs(settings.CHROMA_DB_PATH)
        
        # Retry once
        try:
            chroma_client = chromadb.PersistentClient(
                path=settings.CHROMA_DB_PATH,
                settings=chromadb.Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            collection = chroma_client.create_collection(
                name="knowledge_base_collection",
                metadata={"hnsw:space": "cosine"}
            )
            
            vector_store = Chroma(
                client=chroma_client,
                collection_name="knowledge_base_collection",
                embedding_function=embeddings
            )
            
            logging.info("Successfully created vector store after cleanup")
            return vector_store, chroma_client
            
        except Exception as e2:
            logging.error(f"Failed to create vector store after cleanup: {e2}")
            return None, None

def robust_similarity_search(vector_store, query, k=5, filter=None):
    """Perform similarity search with error handling and fallbacks"""
    
    if not vector_store:
        return []
    
    try:
        # First try: search with score
        results = vector_store.similarity_search_with_score(query, k=k, filter=filter)
        logging.info(f"Search successful: found {len(results)} results")
        return results
        
    except Exception as e:
        logging.warning(f"similarity_search_with_score failed: {e}")
        
        try:
            # Second try: basic similarity search
            docs = vector_store.similarity_search(query, k=k, filter=filter)
            results = [(doc, 0.0) for doc in docs]  # Add dummy scores
            logging.info(f"Fallback search successful: found {len(results)} results")
            return results
            
        except Exception as e2:
            logging.error(f"All search methods failed: {e2}")
            return []

def get_collection_info(chroma_client):
    """Get information about ChromaDB collection"""
    try:
        collection = chroma_client.get_collection("knowledge_base_collection")
        count = collection.count()
        logging.info(f"Collection has {count} documents")
        
        if count > 0:
            # Get a sample
            sample = collection.get(limit=1, include=['documents', 'metadatas'])
            if sample['documents']:
                logging.info(f"Sample document: {sample['documents'][0][:100]}...")
        
        return count
    except Exception as e:
        logging.error(f"Error getting collection info: {e}")
        return 0