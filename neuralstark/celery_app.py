from celery import Celery
from celery.schedules import crontab
from neuralstark.config import settings
from neuralstark.document_parser import parse_document
import os
import time
import logging
import json
import datetime
from typing import Dict, Any, Optional

# LangChain imports are moved into functions to support lazy loading
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

celery_app = Celery(
    "neuralstark_tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    include=['neuralstark.celery_app']
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
)

# --- Lazy Initializers for LangChain Components ---

def get_embeddings():
    """Lazy initialization of embeddings."""
    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL_NAME, 
        model_kwargs={'device': 'cpu'}, 
        encode_kwargs={'batch_size': settings.EMBEDDING_BATCH_SIZE}
    )

def get_text_splitter():
    """Get text splitter instance."""
    return RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# --- Celery Tasks ---

@celery_app.task(bind=True, name='neuralstark.celery_app.process_document_task')
def process_document_task(self, file_path: str, event_type: str, metadata_override: Optional[Dict[str, Any]] = None):
    """Celery task to process document changes."""
    logging.info(f"Processing document: {file_path} (Event: {event_type})")
    
    try:
        embeddings = get_embeddings()
        text_splitter = get_text_splitter()
        vector_store = Chroma(persist_directory=settings.CHROMA_DB_PATH, embedding_function=embeddings)
        normalized_file_path = os.path.abspath(file_path)

        if event_type == "deleted":
            vector_store.delete(ids=[normalized_file_path])
            logging.info(f"Successfully removed {file_path} from ChromaDB.")
            return {"status": "deleted", "file_path": file_path}

        start_time = time.time()
        parsed_result = parse_document(file_path)
        
        if not parsed_result:
            logging.warning(f"Could not extract text or metadata from {file_path}.")
            return {"status": "failed_extraction", "file_path": file_path}

        extracted_text, extracted_metadata = parsed_result
        logging.info(f"Document parsing for {file_path} took {time.time() - start_time:.4f} seconds.")

        if extracted_text:
            source_type = "unknown"
            if normalized_file_path.startswith(os.path.abspath(settings.INTERNAL_KNOWLEDGE_BASE_PATH)):
                source_type = "internal"
            elif normalized_file_path.startswith(os.path.abspath(settings.EXTERNAL_KNOWLEDGE_BASE_PATH)):
                source_type = "external"

            if event_type == "modified":
                vector_store.delete(ids=[normalized_file_path])

            texts = text_splitter.split_text(extracted_text)
            
            base_metadata = {
                "source": normalized_file_path,
                "file_name": os.path.basename(file_path),
                "event_type": event_type,
                "source_type": source_type,
            }
            base_metadata.update(extracted_metadata)
            if metadata_override:
                base_metadata.update(metadata_override)

            metadatas = [base_metadata for _ in texts]

            vector_store.add_texts(texts=texts, metadatas=metadatas, ids=[normalized_file_path] * len(texts))
            logging.info(f"Indexed {len(texts)} chunks from {file_path} into ChromaDB.")
            return {"status": "indexed", "file_path": file_path, "chunks_indexed": len(texts)}
        else:
            logging.warning(f"Could not extract text from {file_path}.")
            return {"status": "failed_extraction", "file_path": file_path}
            
    except Exception as e:
        logging.error(f"Task error processing {file_path}: {e}", exc_info=True)
        self.retry(exc=e, countdown=5, max_retries=3)

@celery_app.task(name='neuralstark.celery_app.run_scheduled_report')
def run_scheduled_report(report_config: Dict[str, Any]):
    """Executes a scheduled report by calling the appropriate tool."""
    tool_name = report_config.get("tool_name")
    tool_input = report_config.get("tool_input")
    
    if tool_name == "FinancialReviewGenerator":
        from neuralstark.main import generate_financial_review_pdf
        result = generate_financial_review_pdf(json.dumps(tool_input))
    elif tool_name == "CanvasGenerator":
        from neuralstark.main import generate_canvas_preview
        result = generate_canvas_preview(json.dumps(tool_input))
    else:
        result = f"Error: Tool '{tool_name}' not found or not supported for scheduling."
    
    logging.info(f"Executed scheduled report '{report_config.get('name')}': {result}")
    return {"status": "executed", "report_name": report_config.get('name'), "result": result}

@celery_app.task(name='neuralstark.celery_app.check_schedules')
def check_schedules():
    """Periodically checks for and runs scheduled reports."""
    try:
        with open("neuralstark/scheduled_reports.json", "r+") as f:
            schedules = json.load(f)
            now = datetime.datetime.utcnow()
            updated = False
            for schedule in schedules:
                last_run = datetime.datetime.fromisoformat(schedule.get("last_run", "1970-01-01T00:00:00"))
                interval_minutes = schedule.get("interval_minutes", 60)
                
                if (now - last_run).total_seconds() / 60 >= interval_minutes:
                    run_scheduled_report.delay(schedule)
                    schedule["last_run"] = now.isoformat()
                    updated = True
            
            if updated:
                f.seek(0)
                json.dump(schedules, f, indent=4)
                f.truncate()
    except FileNotFoundError:
        logging.warning("scheduled_reports.json not found. No schedules to run.")
    except Exception as e:
        logging.error(f"Error checking schedules: {e}")

# Add the periodic task to the Celery beat schedule
celery_app.add_periodic_task(60.0, check_schedules.s(), name='check for scheduled reports every minute')