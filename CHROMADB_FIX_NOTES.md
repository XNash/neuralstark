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
