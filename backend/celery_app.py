from celery import Celery
from backend.config import settings
from backend.document_parser import parse_document
import chromadb
import os
import time
import logging

# LangChain imports for RAG
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

celery_app = Celery(
    "backend_tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
)

# Optimized Celery configuration for better resource usage
celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,  # Fetch one task at a time
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks to free memory
    task_soft_time_limit=300,  # 5 minutes soft limit
    task_time_limit=600,  # 10 minutes hard limit
)

# Lazy initialization of embeddings - only create when needed
_embeddings_instance = None
_text_splitter_instance = None

def get_embeddings():
    """Lazy load embeddings to save memory."""
    global _embeddings_instance
    if _embeddings_instance is None:
        logging.info(f"Initializing embeddings model: {settings.EMBEDDING_MODEL_NAME}...")
        _embeddings_instance = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'batch_size': settings.EMBEDDING_BATCH_SIZE, 'normalize_embeddings': True}
        )
        logging.info("✓ Embeddings model loaded successfully")
    return _embeddings_instance

def get_text_splitter():
    """Get or create text splitter instance with optimized chunking parameters."""
    global _text_splitter_instance
    if _text_splitter_instance is None:
        # Optimized chunking parameters for better semantic context preservation
        _text_splitter_instance = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,  # Increased from 800 to 1200 for better context
            chunk_overlap=settings.CHUNK_OVERLAP,  # Increased from 150 to 250 for continuity
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]  # Smart splitting by paragraphs, sentences, etc.
        )
        logging.info(f"✓ Text splitter initialized (chunk_size={settings.CHUNK_SIZE}, overlap={settings.CHUNK_OVERLAP})")
    return _text_splitter_instance

# Ensure the ChromaDB directory exists on startup
os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def process_document_task(self, file_path: str, event_type: str):
    """Celery task to process document changes with resource optimization."""
    print(f"Processing document: {file_path} (Event: {event_type})")
    
    try:
        # Initialize ChromaDB client inside the task to avoid file locking issues
        text_splitter = get_text_splitter()
        
        chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        vector_store = Chroma(
             client=chroma_client,
             embedding_function=get_embeddings(),
             collection_name="knowledge_base_collection"
        )

        # Normalize file_path for consistent ID generation
        normalized_file_path = os.path.abspath(file_path)

        # Determine if the file is internal or external
        source_type = "unknown"
        if normalized_file_path.startswith(os.path.abspath(settings.INTERNAL_KNOWLEDGE_BASE_PATH)):
            source_type = "internal"
        elif normalized_file_path.startswith(os.path.abspath(settings.EXTERNAL_KNOWLEDGE_BASE_PATH)):
            source_type = "external"

        if event_type == "deleted":
            print(f"Handling deletion for {file_path}. Removing from knowledge base.")
            try:
                vector_store.delete(where={"source": normalized_file_path})
                print(f"Successfully removed {file_path} from ChromaDB.")
                return {"status": "deleted", "file_path": file_path}
            except Exception as e:
                logging.error(f"Error during deletion for {file_path}: {e}")
                raise self.retry(exc=e)

        # For 'created' or 'modified' events
        start_time = time.time()
        extracted_text = parse_document(file_path)
        parsing_time = time.time() - start_time
        logging.info(f"Document parsing for {file_path} took {parsing_time:.4f} seconds.")

        if extracted_text:
            print(f"Successfully extracted text from {file_path}. Length: {len(extracted_text)} characters.")
            
            # If modified, delete existing chunks for this source first
            if event_type == "modified":
                print(f"Handling modification for {file_path}. Deleting old chunks from ChromaDB.")
                try:
                    vector_store.delete(where={"source": normalized_file_path})
                    print(f"Successfully deleted old chunks for {file_path}.")
                except Exception as e:
                    logging.warning(f"Error deleting old chunks for {file_path}: {e}")
                    # Continue to add new ones, but log the error

            # Split text into chunks with improved parameters
            texts = text_splitter.split_text(extracted_text)
            
            # Filter out empty or None chunks
            texts = [text for text in texts if text and text.strip()]
            
            if not texts:
                logging.warning(f"No valid text chunks after filtering empty content for {file_path}")
                return {"status": "no_content", "file_path": file_path}
            
            # Limit chunk size for very large documents to prevent memory issues
            if len(texts) > 1000:
                logging.warning(f"Document {file_path} has {len(texts)} chunks. Processing in batches.")
                # Process in batches
                batch_size = 100
                for i in range(0, len(texts), batch_size):
                    batch_texts = texts[i:i+batch_size]
                    metadatas = [{
                        "source": normalized_file_path,
                        "file_name": os.path.basename(file_path),
                        "event_type": event_type,
                        "timestamp": os.path.getmtime(file_path),
                        "source_type": source_type,
                        "batch": i // batch_size,
                        "chunk_index": i + j  # Add chunk index for ordering
                    } for j in range(len(batch_texts))]
                    
                    vector_store.add_texts(texts=batch_texts, metadatas=metadatas)
                    logging.info(f"Indexed batch {i // batch_size + 1} with {len(batch_texts)} chunks")
            else:
                # Prepare metadata for each chunk with enhanced information
                metadatas = [{
                    "source": normalized_file_path,
                    "file_name": os.path.basename(file_path),
                    "event_type": event_type,
                    "timestamp": os.path.getmtime(file_path),
                    "source_type": source_type,
                    "chunk_index": i  # Add chunk index for ordering
                } for i in range(len(texts))]

                # Add documents to ChromaDB
                start_time = time.time()
                vector_store.add_texts(texts=texts, metadatas=metadatas)
                indexing_time = time.time() - start_time
                logging.info(f"Indexing {len(texts)} chunks from {file_path} took {indexing_time:.4f} seconds.")
            
            print(f"Successfully indexed {len(texts)} chunks from {file_path} into ChromaDB.")
            return {"status": "indexed", "file_path": file_path, "chunks_indexed": len(texts)}
        else:
            print(f"Could not extract text from {file_path}.")
            return {"status": "failed_extraction", "file_path": file_path}
            
    except Exception as e:
        logging.error(f"Error processing {file_path}: {e}")
        raise self.retry(exc=e)



# Synchronous fallback function for when Celery/Redis is not available
def process_document_sync(file_path: str, event_type: str):
    """Process document synchronously without Celery (fallback for when Redis is unavailable)."""
    print(f"[SYNC] Processing document: {file_path} (Event: {event_type})")
    
    try:
        # Initialize ChromaDB client
        text_splitter = get_text_splitter()
        
        chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        vector_store = Chroma(
             client=chroma_client,
             embedding_function=get_embeddings(),
             collection_name="knowledge_base_collection"
        )

        # Normalize file_path for consistent ID generation
        normalized_file_path = os.path.abspath(file_path)

        # Determine if the file is internal or external
        source_type = "unknown"
        if normalized_file_path.startswith(os.path.abspath(settings.INTERNAL_KNOWLEDGE_BASE_PATH)):
            source_type = "internal"
        elif normalized_file_path.startswith(os.path.abspath(settings.EXTERNAL_KNOWLEDGE_BASE_PATH)):
            source_type = "external"

        if event_type == "deleted":
            print(f"[SYNC] Handling deletion for {file_path}. Removing from knowledge base.")
            try:
                vector_store.delete(where={"source": normalized_file_path})
                print(f"[SYNC] Successfully removed {file_path} from ChromaDB.")
                return {"status": "deleted", "file_path": file_path}
            except Exception as e:
                logging.error(f"[SYNC] Error during deletion for {file_path}: {e}")
                return {"status": "error", "file_path": file_path, "error": str(e)}

        # For 'created' or 'modified' events
        start_time = time.time()
        extracted_text = parse_document(file_path)
        parsing_time = time.time() - start_time
        logging.info(f"[SYNC] Document parsing for {file_path} took {parsing_time:.4f} seconds.")

        if extracted_text:
            print(f"[SYNC] Successfully extracted text from {file_path}. Length: {len(extracted_text)} characters.")
            
            # If modified, delete existing chunks for this source first
            if event_type == "modified":
                print(f"[SYNC] Handling modification for {file_path}. Deleting old chunks from ChromaDB.")
                try:
                    vector_store.delete(where={"source": normalized_file_path})
                    print(f"[SYNC] Successfully deleted old chunks for {file_path}.")
                except Exception as e:
                    logging.warning(f"[SYNC] Error deleting old chunks for {file_path}: {e}")

            # Split text into chunks
            texts = text_splitter.split_text(extracted_text)
            
            # Filter out empty or None chunks
            texts = [text for text in texts if text and text.strip()]
            
            if not texts:
                logging.warning(f"[SYNC] No valid text chunks after filtering empty content for {file_path}")
                return {"status": "no_content", "file_path": file_path}
            
            # Limit chunk size for very large documents
            if len(texts) > 1000:
                logging.warning(f"[SYNC] Document {file_path} has {len(texts)} chunks. Processing in batches.")
                batch_size = 100
                for i in range(0, len(texts), batch_size):
                    batch_texts = texts[i:i+batch_size]
                    metadatas = [{
                        "source": normalized_file_path,
                        "file_name": os.path.basename(file_path),
                        "event_type": event_type,
                        "timestamp": os.path.getmtime(file_path),
                        "source_type": source_type,
                        "batch": i // batch_size,
                        "chunk_index": i + j
                    } for j in range(len(batch_texts))]
                    
                    vector_store.add_texts(texts=batch_texts, metadatas=metadatas)
                    logging.info(f"[SYNC] Indexed batch {i // batch_size + 1} with {len(batch_texts)} chunks")
            else:
                # Prepare metadata for each chunk
                metadatas = [{
                    "source": normalized_file_path,
                    "file_name": os.path.basename(file_path),
                    "event_type": event_type,
                    "timestamp": os.path.getmtime(file_path),
                    "source_type": source_type,
                    "chunk_index": i
                } for i in range(len(texts))]

                # Add documents to ChromaDB
                start_time = time.time()
                vector_store.add_texts(texts=texts, metadatas=metadatas)
                indexing_time = time.time() - start_time
                logging.info(f"[SYNC] Indexing {len(texts)} chunks from {file_path} took {indexing_time:.4f} seconds.")
            
            print(f"[SYNC] Successfully indexed {len(texts)} chunks from {file_path} into ChromaDB.")
            return {"status": "indexed", "file_path": file_path, "chunks_indexed": len(texts)}
        else:
            print(f"[SYNC] Could not extract text from {file_path}.")
            return {"status": "failed_extraction", "file_path": file_path}
            
    except Exception as e:
        logging.error(f"[SYNC] Error processing {file_path}: {e}")
        return {"status": "error", "file_path": file_path, "error": str(e)}
