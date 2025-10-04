# NeuralStark

NeuralStark is a multi-platform AI assistant powered by **Xynorash**, an AI agent trained by NeuralStark to help professionals with their firm, societies, or work data. Xynorash provides intelligent assistance, manages knowledge bases, processes documents, and generates dynamic data visualizations.

## 🚀 Quick Start

### One-Command Setup

**🚀 New Robust Scripts (Tested & Verified):**
```bash
./start_services.sh  # Comprehensive startup with error handling
./stop_services.sh   # Clean shutdown
```

**Original Scripts:**
```bash
./run.sh   # Linux/macOS (basic startup)
./stop.sh  # Linux/macOS (basic stop)
```

**Windows:**
```cmd
run.bat    # Windows startup
stop.bat   # Windows stop
```

**Recommendation:** Use `start_services.sh` for better error handling and verification.

That's it! All services will start automatically. Access the application at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

### Stopping the Application

**Linux / macOS / WSL:**
```bash
./stop.sh
```

**Windows:**
```cmd
stop.bat
```

---

## ✨ Features

### 🤖 Intelligent AI Assistance (Xynorash)
- **RAG-based Conversational AI**: Context-aware responses based on your internal and external documents
- **Multilingual Support**: English and French language support
- **Tool-Use Capabilities**: Generate PDF reports (financial reviews, quotes) and create interactive data visualizations
- **Advanced OCR**: Extract text from images, scanned PDFs, and embedded images in documents

### 📁 Comprehensive Document Support
**Documents (15+ formats):**
- PDF (with OCR for scanned documents)
- MS Word: .doc (legacy), .docx (modern) with image OCR
- MS Excel: .xls (legacy), .xlsx (modern)
- OpenDocument: .odt
- Text: .txt, .md (Markdown)
- Data: .json, .csv

**Images (with OCR):**
- PNG, JPEG, TIFF, BMP, GIF
- Automatic text extraction from images
- Embedded images in PDFs and DOCX files

### 🔄 Automated Management
- **File System Watcher**: Monitors knowledge base directories for changes
- **Auto-indexing**: New, modified, or deleted documents automatically update the vector store
- **Background Processing**: Celery workers handle document processing asynchronously

### 📊 Dynamic Data Visualization
- Interactive canvas generation
- Multiple chart types (bar, pie, combo charts)
- Tables and dashboards
- Pure JSON output for frontend integration

### 🌐 Network Access
- **CORS Enabled**: No origin restrictions
- **All Hosts Allowed**: Access from any device on your network
- **Flexible Deployment**: Works with localhost, LAN, or public IPs

### ⚡ Resource Optimized
- Reduced memory footprint (75% reduction in embedding batch size)
- Optimized CPU usage with limited concurrency
- Worker recycling to prevent memory leaks
- Batch processing for large documents

---

## 🛠️ Technologies Used

### Frontend
- **React**: Modern UI library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool with hot reload
- **Tailwind CSS**: Utility-first CSS framework

### Backend
- **Python 3.9+**: Core language
- **FastAPI**: High-performance web framework
- **LangChain**: AI agent orchestration
- **Google Generative AI**: LLM (Gemini)
- **Hugging Face Embeddings**: Document embeddings
- **Celery**: Asynchronous task queue
- **Redis**: Message broker
- **ChromaDB**: Vector database
- **MongoDB**: Document storage

### OCR & Document Processing
- **Tesseract OCR**: Text extraction from images
- **pytesseract**: Python OCR interface
- **LibreOffice**: Legacy MS Office file conversion
- **pypdf**: PDF processing
- **python-docx**: DOCX processing
- **pandas**: Excel and CSV processing

---

## 📋 Prerequisites

### Required Software

- **Python 3.9+**: [Download Python](https://www.python.org/downloads/)
- **Node.js 18+**: [Download Node.js](https://nodejs.org/)
- **Redis**: Message broker for Celery
  - Linux: `sudo apt-get install redis-server`
  - macOS: `brew install redis`
  - Windows: [Download Redis](https://github.com/microsoftarchive/redis/releases)
- **MongoDB**: Database
  - Linux: `sudo apt-get install mongodb`
  - macOS: `brew install mongodb-community`
  - Windows: [Download MongoDB](https://www.mongodb.com/try/download/community)

### System Dependencies (Auto-installed by scripts)

- **Tesseract OCR**: For image text extraction
- **LibreOffice**: For .doc file conversion
- **poppler-utils**: For PDF processing

---

## 🎯 Getting Started

### Option 1: Quick Start (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd neuralstark
   ```

2. **Start the application**
   ```bash
   ./run.sh    # Linux/macOS
   run.bat     # Windows
   ```

3. **Access the application**
   - Open http://localhost:3000 in your browser

### Option 2: Manual Setup

If you prefer to start services individually:

#### Prerequisites
Ensure the following are installed:
- Python 3.9+
- Node.js 18+
- Redis
- MongoDB

#### Installation Commands

**Install Redis:**
```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y redis-server

# macOS
brew install redis

# Windows
# Download from: https://github.com/microsoftarchive/redis/releases
```

**Install MongoDB:**
```bash
# Ubuntu/Debian
sudo apt-get install -y mongodb

# macOS
brew install mongodb-community

# Windows
# Download from: https://www.mongodb.com/try/download/community
```

**Install System Dependencies (for OCR and document processing):**
```bash
# Ubuntu/Debian
sudo apt-get install -y tesseract-ocr poppler-utils libreoffice

# macOS
brew install tesseract poppler
```

#### Step-by-Step Startup

**1. Create Required Directories:**
```bash
cd /app
mkdir -p backend/knowledge_base/internal
mkdir -p backend/knowledge_base/external
mkdir -p chroma_db
```

**2. Install Python Dependencies:**
```bash
cd /app/backend
pip install -r requirements.txt
```

**3. Install Frontend Dependencies:**
```bash
cd /app/frontend
yarn install
```

**4. Start Redis:**
```bash
# Start Redis in background
redis-server --daemonize yes

# Verify Redis is running
redis-cli ping  # Should return "PONG"
```

**5. Start MongoDB:**
```bash
# Start MongoDB (if not already running via supervisor)
mongod --fork --logpath /var/log/mongodb.log --bind_ip_all

# Verify MongoDB is running
mongosh --eval "db.version()"  # Should return version number
```

**6. Start Celery Worker:**
```bash
cd /app
export PYTHONPATH=/app:$PYTHONPATH
nohup celery -A backend.celery_app worker \
  --loglevel=info \
  --concurrency=2 \
  --max-tasks-per-child=50 \
  > /var/log/celery_worker.log 2>&1 &

# Verify Celery is running
ps aux | grep celery
```

**7. Start Backend (FastAPI):**
```bash
cd /app/backend
nohup uvicorn server:app \
  --host 0.0.0.0 \
  --port 8001 \
  --reload \
  > /var/log/backend.log 2>&1 &

# Wait a few seconds, then verify
sleep 5
curl http://localhost:8001/health  # Should return {"status":"ok"}
```

**8. Start Frontend (React + Vite):**
```bash
cd /app/frontend
nohup yarn start > /var/log/frontend.log 2>&1 &

# Wait for frontend to start
sleep 8
curl -I http://localhost:3000  # Should return HTTP/1.1 200 OK
```

**9. Verify All Services:**
```bash
# Check Redis
redis-cli ping

# Check MongoDB
mongosh --eval "db.runCommand({ ping: 1 })"

# Check Celery
ps aux | grep celery | grep -v grep

# Check Backend
curl http://localhost:8001/health

# Check Frontend
curl -I http://localhost:3000
```

#### Stopping Services

```bash
# Stop Celery Worker
pkill -f "celery.*worker"

# Stop Backend
pkill -f "uvicorn.*server:app"

# Stop Frontend
pkill -f "vite"

# Optional: Stop Redis
redis-cli shutdown

# Optional: Stop MongoDB
mongod --shutdown
```

#### View Logs

```bash
# Backend logs
tail -f /var/log/backend.log

# Frontend logs
tail -f /var/log/frontend.log

# Celery logs
tail -f /var/log/celery_worker.log

# MongoDB logs
tail -f /var/log/mongodb.log
```

**📖 For comprehensive manual setup instructions with troubleshooting, see [MANUAL_SETUP.md](MANUAL_SETUP.md)**

For additional information, see [RUNNING_THE_APP.md](RUNNING_THE_APP.md).

---

## 📚 Project Structure

```
/app/
├── backend/                    # Backend API (renamed from neuralstark/)
│   ├── __init__.py            # Package initialization
│   ├── server.py              # Uvicorn entry point
│   ├── main.py                # FastAPI application
│   ├── config.py              # Configuration settings
│   ├── document_parser.py     # Document parsing with OCR
│   ├── celery_app.py          # Celery worker configuration
│   ├── watcher.py             # File system watcher
│   ├── requirements.txt       # Python dependencies
│   └── knowledge_base/
│       ├── internal/          # Internal documents
│       └── external/          # External documents
│
├── frontend/                  # React frontend
│   ├── src/                   # Source code
│   ├── public/                # Static assets
│   ├── package.json           # Node dependencies
│   └── vite.config.ts         # Vite configuration
│
├── chroma_db/                 # Vector database storage
├── scripts/                   # Utility scripts
│
├── run.sh                     # Linux/macOS startup script
├── run.bat                    # Windows startup script
├── stop.sh                    # Linux/macOS stop script
├── stop.bat                   # Windows stop script
│
├── README.md                  # This file
├── RUNNING_THE_APP.md         # Detailed running guide
├── STARTUP_SCRIPTS_README.md  # Quick reference
├── CHANGES.md                 # Technical changes
└── IMPLEMENTATION_COMPLETE.md # Implementation details
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory (optional):

```bash
# LLM Settings
LLM_API_KEY=your_gemini_api_key
LLM_MODEL=gemini-2.5-flash

# Embedding Settings
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
EMBEDDING_BATCH_SIZE=8

# OCR Settings
OCR_ENABLED=true
OCR_LANGUAGES=eng+fra

# Redis Settings
REDIS_HOST=localhost
REDIS_PORT=6379

# MongoDB Settings (if different)
# MONGO_URL=mongodb://localhost:27017

# Paths (defaults are set)
INTERNAL_KNOWLEDGE_BASE_PATH=/app/backend/knowledge_base/internal
EXTERNAL_KNOWLEDGE_BASE_PATH=/app/backend/knowledge_base/external
CHROMA_DB_PATH=/app/chroma_db
```

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome message |
| `/health` | GET | Health check |
| `/chat` | POST | Chat with AI agent |
| `/documents` | GET | List indexed documents |
| `/documents/upload` | POST | Upload new document |
| `/documents/content` | GET | Get document content |
| `/documents/delete` | POST | Delete document |
| `/knowledge_base/reset` | POST | Reset knowledge base |
| `/docs` | GET | Interactive API documentation |

For detailed API documentation, visit http://localhost:8001/docs after starting the backend.

---

## 🧪 Testing

### Backend Tests
```bash
# Run OCR and document parsing tests
python test_ocr.py
```

### Health Checks
```bash
# Backend health
curl http://localhost:8001/health

# List documents
curl http://localhost:8001/documents

# Check CORS
curl -H "Origin: http://example.com" -I http://localhost:8001/health
```

---

## 🌐 Network Access

The application is configured to allow access from any host:

### Local Access
- http://localhost:3000

### Network Access
1. Find your IP address:
   ```bash
   # Linux/macOS
   ip addr show
   # or
   ifconfig
   
   # Windows
   ipconfig
   ```

2. Access from any device on your network:
   - http://YOUR_IP:3000

### CORS Configuration
- **All origins allowed** (`*`)
- **All methods allowed** (GET, POST, PUT, DELETE, etc.)
- **All headers allowed**
- **Credentials supported**

---

## 🐛 Troubleshooting

### Services Won't Start

**Port already in use:**
```bash
# Linux/macOS
lsof -i :8001
kill -9 <PID>

# Windows
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

**Redis not running:**
```bash
redis-cli ping  # Should return "PONG"
# If not, start Redis:
redis-server --daemonize yes
```

**MongoDB not running:**
```bash
mongod --version
# Start MongoDB:
mongod --fork --logpath /var/log/mongodb.log --bind_ip_all
```

### Check Logs

**Linux/macOS:**
```bash
tail -f /var/log/backend.log
tail -f /var/log/frontend.log
tail -f /var/log/celery_worker.log
```

**Windows:**
Check the command windows opened by `run.bat`

### Common Issues

1. **CORS errors**: Ensure backend has latest changes, restart backend
2. **Frontend not loading**: Check if port 3000 is available
3. **OCR not working**: Verify Tesseract is installed: `tesseract --version`
4. **Documents not processing**: Check Celery worker logs

For detailed troubleshooting, see [RUNNING_THE_APP.md](RUNNING_THE_APP.md).

---

## 📖 Documentation

- **[QUICK_START_MANUAL.md](QUICK_START_MANUAL.md)**: ⚡ Quick reference for manual startup commands
- **[MANUAL_SETUP.md](MANUAL_SETUP.md)**: ⭐ Complete step-by-step manual setup guide with troubleshooting
- **[RUNNING_THE_APP.md](RUNNING_THE_APP.md)**: Comprehensive guide for running the application
- **[STARTUP_SCRIPTS_README.md](STARTUP_SCRIPTS_README.md)**: Quick reference for startup scripts
- **[CHANGES.md](CHANGES.md)**: Detailed list of all changes made
- **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)**: Complete implementation details

---

## 🚀 Deployment

### Development
The application is ready for development with hot-reload enabled for both frontend and backend.

### Production
For production deployment:

1. **Environment Variables**: Use production values
2. **Process Manager**: Use PM2, systemd, or supervisor
3. **Reverse Proxy**: Set up Nginx or Apache
4. **HTTPS**: Configure SSL certificates
5. **CORS**: Restrict origins to your domain
6. **Firewall**: Configure appropriate rules
7. **Monitoring**: Set up logging and monitoring

See [RUNNING_THE_APP.md](RUNNING_THE_APP.md) for production deployment details.

---

## 📝 Recent Changes

### Version 0.3.0 - Latest Updates

✅ **Backend Renamed**: `neuralstark/` → `backend/`  
✅ **Full MS Office Support**: .doc and .docx files with OCR  
✅ **Enhanced OCR**: Images, scanned PDFs, embedded images  
✅ **Resource Optimization**: 75% reduction in memory usage  
✅ **Network Access**: No host restrictions, CORS enabled  
✅ **Startup Scripts**: One-command setup for all platforms  

For detailed changes, see [CHANGES.md](CHANGES.md).

---

## 🤝 Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the `LICENSE` file for details.

---

## 🙏 Acknowledgments

- Google Generative AI for the powerful LLM
- Hugging Face for embeddings models
- The FastAPI and React communities
- Tesseract OCR project
- LangChain framework

---

## 📞 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check the documentation files
- Review the troubleshooting section

---

## 🎉 Get Started Now!

```bash
# Clone the repository
git clone <repository-url>
cd neuralstark

# Start the application
./run.sh    # Linux/macOS
run.bat     # Windows

# Open in browser
# http://localhost:3000
```

**Happy building with NeuralStark! 🚀**
