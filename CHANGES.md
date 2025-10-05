# NeuralStark Backend Improvements - Implementation Summary

## Latest Changes (January 2025)

### AI Agent Tool Description Update ✅
- **Updated KnowledgeBaseSearch tool description**: Changed to be more clear and concise
  - New description: "Use this tool to answer questions from the knowledge base. You can also answer general questions if no relevant documents are found. Do NOT write code. Respond only with Action and Action Input."
  - Previous description was in French and less specific about code generation
- **Files modified**: `/app/backend/main.py`, `/app/README.md`
- **Documentation updated**: Added AI Agent Tools section to README

---

## Changes Implemented

### 1. Directory Restructuring ✅
- **Renamed**: `neuralstark/` → `backend/`
- **Updated all imports**: Changed from `neuralstark.*` to `backend.*` across all files
- **Updated paths**: Modified default paths in config.py to use absolute paths
- **Created server.py**: Entry point for uvicorn compatible with supervisor configuration

### 2. Enhanced Document Support ✅

#### MS Office File Support
- **Added .doc support**: Uses LibreOffice headless conversion to .docx format
- **Enhanced .docx support**: Already supported, now with image extraction
- **Excel support**: .xls and .xlsx formats already supported

#### OCR Integration
- **Standalone image files**: Supports .png, .jpg, .jpeg, .tiff, .tif, .bmp, .gif
- **PDF OCR**: 
  - Extracts text from standard PDFs
  - OCRs scanned pages with minimal text
  - Extracts and OCRs embedded images
- **DOCX OCR**: Extracts and OCRs embedded images
- **OCR Languages**: English and French (configurable)

#### Technical Implementation
- **pytesseract**: Core OCR engine using Tesseract
- **Pillow**: Image processing
- **pdf2image**: PDF to image conversion for OCR
- **LibreOffice**: .doc to .docx conversion

### 3. Resource Optimization ✅

#### Memory Optimization
- **Reduced embedding batch size**: 32 → 8 (75% reduction)
- **Lazy loading**: Embeddings model only loaded when needed
- **Worker recycling**: Celery workers restart after 50 tasks to free memory
- **Batch processing**: Large documents (>1000 chunks) processed in batches of 100

#### CPU Optimization
- **Reduced concurrency**: Celery workers limited to 2 concurrent tasks
- **Optimized chunking**: Reduced chunk size (1000 → 800) and overlap (200 → 150)
- **Task prefetching**: Workers fetch one task at a time
- **Time limits**: Soft limit (5 min) and hard limit (10 min) per task

#### Performance Settings
```python
EMBEDDING_BATCH_SIZE = 8  # Down from 32
chunk_size = 800          # Down from 1000
chunk_overlap = 150       # Down from 200
worker_concurrency = 2    # Limited concurrent tasks
worker_max_tasks_per_child = 50  # Auto-restart for memory
```

### 4. Configuration Updates ✅

#### New Settings in config.py
```python
OCR_ENABLED = True              # Enable/disable OCR
OCR_LANGUAGES = "eng+fra"       # OCR languages
EMBEDDING_BATCH_SIZE = 8        # Reduced for memory
```

#### Absolute Paths
```python
INTERNAL_KNOWLEDGE_BASE_PATH = "/app/backend/knowledge_base/internal"
EXTERNAL_KNOWLEDGE_BASE_PATH = "/app/backend/knowledge_base/external"
CHROMA_DB_PATH = "/app/chroma_db"
```

### 5. System Dependencies Installed ✅
- tesseract-ocr (OCR engine)
- tesseract-ocr-eng (English language pack)
- tesseract-ocr-fra (French language pack)
- libreoffice (Document conversion)
- poppler-utils (PDF utilities)
- redis-server (Message broker for Celery)

### 6. Python Dependencies Added ✅
```
pytesseract          # OCR interface
Pillow              # Image processing
pdf2image           # PDF to image conversion
opencv-python-headless  # Image processing utilities
```

## File Changes Summary

### Modified Files
1. `/app/backend/main.py` - Fixed f-string syntax errors
2. `/app/backend/config.py` - Added OCR settings, optimized batch size, absolute paths
3. `/app/backend/watcher.py` - Updated imports
4. `/app/backend/celery_app.py` - Complete rewrite with optimizations
5. `/app/backend/document_parser.py` - Complete rewrite with OCR support
6. `/app/backend/requirements.txt` - Added OCR dependencies
7. `/app/frontend/package.json` - Added "start" script, date-fns dependency

### New Files Created
1. `/app/backend/server.py` - Uvicorn entry point
2. `/app/backend/__init__.py` - Package initialization
3. `/app/scripts/start_celery.sh` - Celery worker startup script

### Directories Created
1. `/app/backend/knowledge_base/internal/` - Internal documents
2. `/app/backend/knowledge_base/external/` - External documents
3. `/app/chroma_db/` - Vector database storage

## Supported File Formats

### Documents (with OCR where applicable)
- ✅ .txt - Plain text
- ✅ .pdf - PDF with text extraction and OCR
- ✅ .doc - MS Word (via LibreOffice conversion)
- ✅ .docx - MS Word with image OCR
- ✅ .odt - OpenDocument Text
- ✅ .md - Markdown

### Spreadsheets
- ✅ .csv - CSV files
- ✅ .xls - Excel (legacy)
- ✅ .xlsx - Excel (modern)

### Images (OCR)
- ✅ .png - PNG images
- ✅ .jpg/.jpeg - JPEG images
- ✅ .tiff/.tif - TIFF images
- ✅ .bmp - Bitmap images
- ✅ .gif - GIF images

### Data
- ✅ .json - JSON files

## Performance Improvements

### Before Optimization
- CPU Usage: ~100%
- Embedding Batch Size: 32
- Chunk Size: 1000
- No worker limits

### After Optimization
- CPU Usage: Reduced through concurrency limits
- Embedding Batch Size: 8 (75% reduction)
- Chunk Size: 800 (20% reduction)
- Worker Limits: 2 concurrent, max 50 tasks per child

## Testing Recommendations

### Test OCR Functionality
1. Upload a scanned PDF to verify OCR on PDF pages
2. Upload an image file (.png/.jpg) with text
3. Upload a .docx with embedded images
4. Upload a .doc file to verify LibreOffice conversion

### Test Resource Usage
1. Monitor CPU: `top -p $(pgrep -f "celery|uvicorn")`
2. Monitor memory: `free -h`
3. Check Celery logs: `tail -f /var/log/celery_worker.log`
4. Check backend logs: `tail -f /var/log/supervisor/backend.out.log`

### Test Document Processing
1. Upload documents via the web interface
2. Verify documents appear in `/documents` endpoint
3. Test chat queries against uploaded documents
4. Verify source attribution in responses

## Services Status

```bash
# Check all services
sudo supervisorctl status

# Expected output:
# backend    RUNNING
# frontend   RUNNING
# mongodb    RUNNING

# Restart services if needed
sudo supervisorctl restart backend
sudo supervisorctl restart frontend

# Check Celery worker
ps aux | grep celery
```

## API Endpoints

All backend endpoints remain the same:
- `GET /health` - Health check
- `POST /chat` - Chat with AI agent
- `GET /documents` - List indexed documents
- `POST /documents/upload` - Upload new document
- `GET /documents/content` - Get document content
- `POST /documents/delete` - Delete document
- `POST /knowledge_base/reset` - Reset knowledge base

## Notes

1. **API Prefix**: All backend routes must use `/api` prefix for proper routing
2. **OCR Languages**: Default to English and French, configurable via `OCR_LANGUAGES`
3. **Resource Limits**: Celery tasks have 5-minute soft limit, 10-minute hard limit
4. **Batch Processing**: Documents with >1000 chunks processed in batches
5. **Worker Recycling**: Workers restart after 50 tasks to prevent memory leaks

## Rollback Instructions

If issues arise, the old files are preserved:
- `/app/backend/celery_app_old.py`
- `/app/backend/document_parser_old.py`

To rollback:
```bash
cd /app/backend
mv celery_app.py celery_app_new.py
mv celery_app_old.py celery_app.py
mv document_parser.py document_parser_new.py
mv document_parser_old.py document_parser.py
sudo supervisorctl restart backend
```
