import os
from pathlib import Path

# Get project root directory (parent of backend directory)
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent

class Settings:
    PROJECT_NAME: str = "NeuralStark API"
    PROJECT_VERSION: str = "0.3.0"

    # Redis settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))

    # Watchdog settings - Use relative paths from project root
    INTERNAL_KNOWLEDGE_BASE_PATH: str = os.getenv(
        "INTERNAL_KNOWLEDGE_BASE_PATH", 
        str(BACKEND_DIR / "knowledge_base" / "internal")
    )
    EXTERNAL_KNOWLEDGE_BASE_PATH: str = os.getenv(
        "EXTERNAL_KNOWLEDGE_BASE_PATH", 
        str(BACKEND_DIR / "knowledge_base" / "external")
    )

    # AI settings (for LLM chat model)
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.5-flash") # Default to a common chat model
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "AIzaSyDCzcuoGZpK0ZfS7G3iUydpv-4jFFfq7X0") # Generic API key for LLM

    # Embedding settings
    # EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-m3")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    EMBEDDING_API_KEY: str = os.getenv("EMBEDDING_API_KEY", "") # Not needed for local BGE-M3, but good for API-based embeddings

    # ChromaDB settings - Use relative path from project root
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", str(PROJECT_ROOT / "chroma_db"))

    # Canvas settings
    CANVAS_TEMPLATES_PATH: str = os.getenv("CANVAS_TEMPLATES_PATH", "canvas_templates.json")

    # Embedding optimization - Reduced for better resource usage
    EMBEDDING_BATCH_SIZE: int = int(os.getenv("EMBEDDING_BATCH_SIZE", 8)) # Reduced batch size for lower memory usage
    
    # OCR settings
    OCR_ENABLED: bool = os.getenv("OCR_ENABLED", "true").lower() == "true"
    OCR_LANGUAGES: str = os.getenv("OCR_LANGUAGES", "eng+fra") # English and French by default

settings = Settings()
