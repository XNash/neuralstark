"""
ChromaDB Singleton Manager for NeuralStark
Ensures only one ChromaDB client instance exists to prevent "different settings" errors
"""
import chromadb
import os
import logging
from threading import Lock
from typing import Optional
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from backend.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChromaDBManager:
    """Singleton manager for ChromaDB client to prevent multiple instances"""
    
    _instance: Optional['ChromaDBManager'] = None
    _lock: Lock = Lock()
    _client: Optional[chromadb.PersistentClient] = None
    _embeddings: Optional[HuggingFaceEmbeddings] = None
    _vector_store: Optional[Chroma] = None
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Only initialize once
        if not hasattr(self, '_initialized'):
            self._initialized = True
            logger.info("Initializing ChromaDB Manager (Singleton)")
    
    def get_embeddings(self) -> HuggingFaceEmbeddings:
        """Get or create embeddings instance (lazy loading)"""
        if self._embeddings is None:
            with self._lock:
                if self._embeddings is None:
                    logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
                    self._embeddings = HuggingFaceEmbeddings(
                        model_name=settings.EMBEDDING_MODEL_NAME,
                        model_kwargs={'device': 'cpu'},
                        encode_kwargs={
                            'batch_size': settings.EMBEDDING_BATCH_SIZE,
                            'normalize_embeddings': True
                        }
                    )
                    logger.info("✓ Embedding model loaded successfully")
        return self._embeddings
    
    def get_client(self) -> chromadb.PersistentClient:
        """Get or create ChromaDB client instance (singleton)"""
        if self._client is None:
            with self._lock:
                if self._client is None:
                    # Ensure directory exists
                    os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
                    
                    logger.info(f"Creating ChromaDB client at: {settings.CHROMA_DB_PATH}")
                    
                    # Create client with consistent settings
                    self._client = chromadb.PersistentClient(
                        path=settings.CHROMA_DB_PATH,
                        settings=chromadb.Settings(
                            anonymized_telemetry=False,
                            allow_reset=True,
                            is_persistent=True
                        )
                    )
                    logger.info("✓ ChromaDB client created successfully")
        
        return self._client
    
    def get_vector_store(self) -> Chroma:
        """Get or create LangChain Chroma vector store"""
        if self._vector_store is None:
            with self._lock:
                if self._vector_store is None:
                    client = self.get_client()
                    embeddings = self.get_embeddings()
                    
                    # Ensure collection exists
                    try:
                        collection = client.get_collection("knowledge_base_collection")
                        logger.info("Using existing ChromaDB collection")
                    except ValueError:
                        # Collection doesn't exist, create it
                        collection = client.create_collection(
                            name="knowledge_base_collection",
                            metadata={"hnsw:space": "cosine"}
                        )
                        logger.info("Created new ChromaDB collection")
                    
                    # Create LangChain wrapper
                    self._vector_store = Chroma(
                        client=client,
                        collection_name="knowledge_base_collection",
                        embedding_function=embeddings
                    )
                    logger.info("✓ Vector store initialized successfully")
        
        return self._vector_store
    
    def reset_vector_store(self):
        """Reset the vector store instance (call after clearing collection)"""
        with self._lock:
            self._vector_store = None
            logger.info("Vector store instance reset")
    
    def get_collection_info(self) -> dict:
        """Get information about the ChromaDB collection"""
        try:
            client = self.get_client()
            collection = client.get_collection("knowledge_base_collection")
            count = collection.count()
            
            info = {
                "count": count,
                "name": "knowledge_base_collection",
                "metadata": collection.metadata
            }
            
            if count > 0:
                # Get a sample
                sample = collection.get(limit=1, include=['documents', 'metadatas'])
                if sample['documents']:
                    info["sample_document"] = sample['documents'][0][:100] + "..."
            
            logger.info(f"Collection info: {count} documents")
            return info
            
        except ValueError:
            logger.warning("Collection does not exist")
            return {"count": 0, "exists": False}
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {"error": str(e)}
    
    def similarity_search_with_fallback(self, query: str, k: int = 5, filter: dict = None):
        """Perform similarity search with error handling and fallbacks"""
        vector_store = self.get_vector_store()
        
        try:
            # First try: search with score
            results = vector_store.similarity_search_with_score(query, k=k, filter=filter)
            logger.info(f"Search successful: found {len(results)} results")
            return results
            
        except Exception as e:
            logger.warning(f"similarity_search_with_score failed: {e}")
            
            try:
                # Second try: basic similarity search
                docs = vector_store.similarity_search(query, k=k, filter=filter)
                results = [(doc, 0.0) for doc in docs]  # Add dummy scores
                logger.info(f"Fallback search successful: found {len(results)} results")
                return results
                
            except Exception as e2:
                logger.error(f"All search methods failed: {e2}")
                return []
    
    def health_check(self) -> bool:
        """Check if ChromaDB is healthy and accessible"""
        try:
            client = self.get_client()
            client.heartbeat()  # Check if client is responsive
            
            # Try to get collection
            try:
                collection = client.get_collection("knowledge_base_collection")
                count = collection.count()
                logger.info(f"✓ ChromaDB health check passed ({count} documents)")
                return True
            except ValueError:
                logger.info("✓ ChromaDB healthy, collection not yet created")
                return True
                
        except Exception as e:
            logger.error(f"✗ ChromaDB health check failed: {e}")
            return False


# Global singleton instance
_chroma_manager = ChromaDBManager()


def get_chroma_manager() -> ChromaDBManager:
    """Get the global ChromaDB manager instance"""
    return _chroma_manager
