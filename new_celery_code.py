from celery import Celery
from neuralstark.config import settings
from neuralstark.document_parser import parse_document
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

# Create Celery app with explicit task discovery
celery_app = Celery(
    "neuralstark_tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    include=['neuralstark.celery_app']  # Explicitly include this module
)

celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    # Add these Windows-specific configurations
    task_always_eager=False,
    task_eager_propagates=False,
    worker_pool='solo',  # Use solo pool for Windows
    # Alternative: use eventlet or gevent pool
    # worker_pool='eventlet',  # Uncomment if you have eventlet installed
    task_routes={
        'neuralstark.celery_app.process_document_task': {'queue': 'default'}
    },
    # Add task discovery settings
    task_create_missing_queues=True,
    task_default_queue='default',
    task_default_exchange='default',
    task_default_exchange_type='direct',
    task_default_routing_key='default',
)

# Initialize embeddings - moved inside a function to avoid import issues
def get_embeddings():
    """Lazy initialization of embeddings to avoid multiprocessing issues."""
    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL_NAME, 
        model_kwargs={'device': 'cpu'}, 
        encode_kwargs={'batch_size': settings.EMBEDDING_BATCH_SIZE}
    )

def get_text_splitter():
    """Get text splitter instance."""
    return RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# Ensure the ChromaDB directory exists on startup
os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)


@celery_app.task(bind=True, name='neuralstark.celery_app.process_document_task')
def process_document_task(self, file_path: str, event_type: str):
    """Celery task to process document changes."""
    print(f"Processing document: {file_path} (Event: {event_type})")
    
    try:
        # Initialize components inside the task to avoid multiprocessing issues
        embeddings = get_embeddings()
        text_splitter = get_text_splitter()
        
        # Initialize ChromaDB client inside the task
        vector_store = Chroma(persist_directory=settings.CHROMA_DB_PATH, embedding_function=embeddings)

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
                print(f"Error during deletion for {file_path}: {e}")
                self.retry(exc=e, countdown=5, max_retries=3)

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
                    print(f"Error deleting old chunks for {file_path}: {e}")
                    # Continue to add new ones, but log the error

            # Split text into chunks
            texts = text_splitter.split_text(extracted_text)
            
            # Prepare metadata for each chunk
            metadatas = [{
                "source": normalized_file_path,
                "file_name": os.path.basename(file_path),
                "event_type": event_type,
                "timestamp": os.path.getmtime(file_path), # Last modified timestamp
                "source_type": source_type # Add source type metadata
            } for _ in texts]

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
        print(f"Error processing {file_path}: {e}")
        logging.error(f"Task error: {e}", exc_info=True)
        self.retry(exc=e, countdown=5, max_retries=3)


# Autodiscover tasks
celery_app.autodiscover_tasks(['neuralstark'])

if __name__ == '__main__':
    celery_app.start()
