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

    # Embedding settings - Using smaller model for disk space efficiency (384 dimensions)
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    EMBEDDING_API_KEY: str = os.getenv("EMBEDDING_API_KEY", "") # Not needed for local embeddings

    # ChromaDB settings - Use relative path from project root
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", str(PROJECT_ROOT / "chroma_db"))

    # Canvas settings
    CANVAS_TEMPLATES_PATH: str = os.getenv("CANVAS_TEMPLATES_PATH", "canvas_templates.json")

    # Embedding optimization - Adjusted for smaller model
    EMBEDDING_BATCH_SIZE: int = int(os.getenv("EMBEDDING_BATCH_SIZE", 8)) # Optimized for smaller model
    
    # OCR settings
    OCR_ENABLED: bool = os.getenv("OCR_ENABLED", "true").lower() == "true"
    OCR_LANGUAGES: str = os.getenv("OCR_LANGUAGES", "eng+fra") # English and French by default
    
    # RAG Optimization settings
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 1200)) # Increased for better semantic context
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 250)) # Increased overlap for continuity
    RETRIEVAL_K: int = int(os.getenv("RETRIEVAL_K", 10)) # Retrieve more candidates for reranking
    RETRIEVAL_SCORE_THRESHOLD: float = float(os.getenv("RETRIEVAL_SCORE_THRESHOLD", 0.3)) # Filter low-quality results
    RERANKER_MODEL: str = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2") # Cross-encoder for reranking
    RERANKER_TOP_K: int = int(os.getenv("RERANKER_TOP_K", 5)) # Return top 5 after reranking

settings = Settings()

# Automatically create required directories on import
def _ensure_directories_exist():
    """Ensure all required directories exist with proper permissions."""
    required_dirs = [
        settings.CHROMA_DB_PATH,
        settings.INTERNAL_KNOWLEDGE_BASE_PATH,
        settings.EXTERNAL_KNOWLEDGE_BASE_PATH,
    ]
    
    for dir_path in required_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        
    # Verify ChromaDB directory is writable
    chroma_path = Path(settings.CHROMA_DB_PATH)
    if not os.access(chroma_path, os.W_OK):
        try:
            # Try to make it writable
            os.chmod(chroma_path, 0o755)
        except Exception:
            pass  # If we can't change permissions, continue anyway

# Create directories when config is imported
_ensure_directories_exist()

# Print configuration on import (for debugging)
import sys
if __name__ != "__main__" and "pytest" not in sys.modules:
    print("📁 NeuralStark Configuration:")
    print(f"   ChromaDB Path: {settings.CHROMA_DB_PATH}")
    print(f"   Internal KB: {settings.INTERNAL_KNOWLEDGE_BASE_PATH}")
    print(f"   External KB: {settings.EXTERNAL_KNOWLEDGE_BASE_PATH}")
    print(f"   Embedding Model: {settings.EMBEDDING_MODEL_NAME}")
    print(f"   Reranker Model: {settings.RERANKER_MODEL}")
    print(f"   Chunk Size: {settings.CHUNK_SIZE} (Overlap: {settings.CHUNK_OVERLAP})")
    print(f"   Retrieval K: {settings.RETRIEVAL_K} -> Reranked Top K: {settings.RERANKER_TOP_K}")
