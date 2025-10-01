import time
import logging
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from neuralstark.config import settings
from neuralstark.celery_app import process_document_task # Import the Celery task

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

class DocumentEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            logging.info(f"New file created: {event.src_path}")
            process_document_task.delay(event.src_path, "created")

    def on_modified(self, event):
        if not event.is_directory:
            logging.info(f"File modified: {event.src_path}")
            process_document_task.delay(event.src_path, "modified")

    def on_deleted(self, event):
        if not event.is_directory:
            logging.info(f"File deleted: {event.src_path}")
            process_document_task.delay(event.src_path, "deleted")

# Global observer instance to manage its lifecycle
observer_instance = None

def start_watcher_in_background():
    global observer_instance
    
    internal_path = settings.INTERNAL_KNOWLEDGE_BASE_PATH
    external_path = settings.EXTERNAL_KNOWLEDGE_BASE_PATH

    # Ensure directories exist before watching
    os.makedirs(internal_path, exist_ok=True)
    os.makedirs(external_path, exist_ok=True)

    event_handler = DocumentEventHandler()
    observer_instance = Observer()
    
    observer_instance.schedule(event_handler, internal_path, recursive=True)
    logging.info(f"Watching internal directory: {internal_path}")

    observer_instance.schedule(event_handler, external_path, recursive=True)
    logging.info(f"Watching external directory: {external_path}")

    observer_instance.start()

def stop_watcher():
    global observer_instance
    if observer_instance:
        observer_instance.stop()
        observer_instance.join()
        logging.info("Watcher stopped.")

if __name__ == "__main__":
    # This block is for testing the watcher independently
    # In a real FastAPI app, the watcher would be started as a background task
    print(f"Starting watcher for: {settings.KNOWLEDGE_BASE_PATH}")
    start_watcher_in_background()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_watcher()

