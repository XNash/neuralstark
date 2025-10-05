# ChromaDB Database Fix Notes

## Issue Summary
**Date**: October 5, 2025  
**Status**: ✅ RESOLVED

### Problem
The NeuralStark backend was throwing ChromaDB database errors:
```
Error listing documents: Could not connect to tenant default_tenant. Are you sure it exists?
Error listing documents: error returned from database: (code: 14) unable to open database file
```

### Root Cause
Two critical directories were missing:
1. `/app/chroma_db/` - ChromaDB's database storage directory
2. `/app/backend/knowledge_base/external/` - External knowledge base documents directory

### Solution Applied

#### 1. Created Missing Directories
```bash
mkdir -p /app/chroma_db
mkdir -p /app/backend/knowledge_base/external
chmod -R 755 /app/chroma_db /app/backend/knowledge_base
```

#### 2. Updated `run.sh` Script (Phase 1)
Enhanced directory creation with:
- Individual directory verification
- Better error reporting
- Write permission checks for ChromaDB directory
- Retry logic if initial creation fails

Key improvements in `/app/run.sh` lines 41-99:
- Added detailed directory existence checks
- Added writable directory verification
- Added better error messages
- Added warning if ChromaDB directory is not writable

#### 3. Updated README.md
Enhanced the "Common Issues" section with:
- Clear explanation of the cause
- Manual fix commands
- Better troubleshooting guidance

### Verification

All services now working correctly:
```bash
✓ ChromaDB database file created: /app/chroma_db/chroma.sqlite3
✓ Backend API health check: http://localhost:8001/api/health → {"status":"ok"}
✓ Documents endpoint: http://localhost:8001/api/documents → {"indexed_documents":[]}
✓ Frontend dashboard: http://localhost:3000 → Loading correctly
```

### Prevention

The issue is now prevented by:

1. **Automatic Directory Creation**: The `run.sh` script creates all required directories at startup
2. **Permission Verification**: The script verifies that directories are writable
3. **Application Startup**: The `main.py` lifespan event also creates directories (line 342-344)
4. **Documentation**: README.md now includes manual fix instructions

### Testing Commands

To verify the fix is working:
```bash
# Check directories exist
ls -la /app/chroma_db
ls -la /app/backend/knowledge_base/external

# Test backend health
curl http://localhost:8001/api/health

# Test ChromaDB connection
curl http://localhost:8001/api/documents

# Check ChromaDB database file exists
ls -la /app/chroma_db/chroma.sqlite3
```

### Future Recommendations

1. **Always use `./run.sh`**: This script ensures all directories are created before services start
2. **Don't start services manually**: Starting uvicorn directly may skip directory creation
3. **Check logs**: If errors occur, check `logs/backend.log` for details
4. **Verify permissions**: Ensure the user running the script has write access to `/app/`

### Related Files Modified

1. `/app/run.sh` - Enhanced directory creation and verification (lines 41-99)
2. `/app/README.md` - Updated troubleshooting section (lines 627-634)
3. `/app/CHROMADB_FIX_NOTES.md` - This documentation file

---

## Technical Details

### ChromaDB Requirements
ChromaDB (used as the vector database for document embeddings) requires:
- A writable directory to store its SQLite database
- The directory must exist before ChromaDB client initialization
- Default path: `/app/chroma_db` (configurable via `CHROMA_DB_PATH` environment variable)

### Database File Structure
```
/app/chroma_db/
└── chroma.sqlite3      # Main ChromaDB database file (created automatically)
```

### Knowledge Base Structure
```
/app/backend/knowledge_base/
├── internal/           # Internal documents (processed by file watcher)
└── external/          # External documents (processed by file watcher)
```

### Application Flow
1. `run.sh` creates directories (Phase 1)
2. Backend starts with `uvicorn server:app`
3. `main.py` lifespan event verifies directories (line 342-344)
4. File watcher monitors knowledge base directories
5. ChromaDB client initializes with persistent directory
6. Documents endpoint queries ChromaDB database

---

**Note**: This fix ensures the application works correctly whether started via `./run.sh` or manually with `uvicorn`.

---

## Embedding Dimension Mismatch Fix

### New Issue: Embedding Dimension Mismatch
**Date**: October 5, 2025  
**Status**: ✅ SOLUTION PROVIDED

### Error Message
```
chromadb.errors.InvalidArgumentError: Collection expecting embedding with dimension of 384, got 1024
```

### Root Cause
This error occurs when the embedding model changes but ChromaDB still has collections created with the old model:

1. **Old Model**: `all-MiniLM-L6-v2` produces 384-dimensional embeddings
2. **New Model**: `BAAI/bge-m3` produces 1024-dimensional embeddings

ChromaDB collections are tied to the embedding dimension they were created with and cannot handle dimension mismatches.

### Solution: Reset ChromaDB

To fix this error, you need to reset the ChromaDB vector store:

#### Option 1: Quick Reset (Delete and Recreate)

```bash
# 1. Stop all services
./stop.sh

# 2. Backup your ChromaDB (optional but recommended)
cp -r chroma_db chroma_db_backup_$(date +%Y%m%d_%H%M%S)

# 3. Delete the ChromaDB directory
rm -rf chroma_db

# 4. Recreate the directory
mkdir -p chroma_db
chmod 755 chroma_db

# 5. Restart services (will recreate ChromaDB with correct dimensions)
./run.sh
```

#### Option 2: Python Reset Script

Create a file `reset_chromadb.py` in `/app/` with the following content:

```python
#!/usr/bin/env python3
import os
import shutil
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))
from backend.config import settings

def reset_chromadb():
    """Reset ChromaDB to fix embedding dimension mismatch."""
    chroma_path = settings.CHROMA_DB_PATH
    
    print(f"📁 ChromaDB Path: {chroma_path}")
    print(f"🤖 Embedding Model: {settings.EMBEDDING_MODEL_NAME}")
    print()
    
    # Confirm
    response = input("⚠️  Delete ChromaDB and reindex all documents? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Cancelled")
        return
    
    # Delete
    if os.path.exists(chroma_path):
        print(f"🗑️  Deleting {chroma_path}")
        shutil.rmtree(chroma_path)
    
    # Recreate
    os.makedirs(chroma_path, exist_ok=True)
    print(f"✅ Created fresh ChromaDB directory")
    print()
    print("📝 Next: Restart services with ./run.sh")

if __name__ == "__main__":
    reset_chromadb()
```

Then run:
```bash
python reset_chromadb.py
```

### What Happens After Reset?

1. **Services Restart**: ChromaDB creates a new collection with the correct embedding dimension (1024)
2. **Auto-Reindexing**: The file watcher automatically reindexes all documents from:
   - `/app/backend/knowledge_base/internal/`
   - `/app/backend/knowledge_base/external/`
3. **New Embeddings**: All documents are re-embedded using `BAAI/bge-m3`

### Verification

Check that reindexing is working:

```bash
# Watch Celery logs for reindexing progress
tail -f logs/celery_worker.log

# Check indexed documents
curl http://localhost:8001/api/documents

# Verify no errors in backend
tail -f logs/backend.log | grep -i error
```

### Prevention

To avoid this issue in the future:

1. **Don't change embedding models** once you have indexed documents
2. **If you must change models**, always reset ChromaDB first
3. **Keep backups** of your ChromaDB directory before making changes

### Configuration Check

Verify your current embedding model in `/app/backend/config.py`:

```python
# Line 32
EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-m3")
```

### Model Comparison

| Model | Dimensions | Quality | Speed |
|-------|-----------|---------|-------|
| all-MiniLM-L6-v2 | 384 | Good | Fast |
| BAAI/bge-m3 | 1024 | Better | Slower |

The `BAAI/bge-m3` model provides better semantic understanding but requires more resources.
