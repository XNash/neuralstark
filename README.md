# NeuralStark

NeuralStark is a multi-platform AI assistant powered by **Xynorash**, an AI agent trained by NeuralStark to help professionals with their firm, societies, or work data. Xynorash provides intelligent assistance, manages knowledge bases, processes documents, and generates dynamic data visualizations.

> **⚡ NEW in v6.0:** One-command setup! Just run `./run.sh` (Linux/macOS) or `run_windows.bat` (Windows) and everything is handled automatically - setup, installation, and startup. No manual steps needed!

## 🚀 Quick Start

### One-Command Setup & Start

**Linux / macOS:**

```bash
# Make executable (first time only)
chmod +x run.sh stop.sh

# Start everything (setup + install + run)
./run.sh

# Stop services
./stop.sh
```

**Windows:**

```cmd
# Start everything (setup + install + run)
run_windows.bat

# Stop services
stop_windows.bat
```

**That's it!** The startup script handles everything:
- ✅ Creates all required directories (`chroma_db/`, `logs/`, etc.)
- ✅ Sets up Python virtual environment
- ✅ Validates system prerequisites (Python, Node.js)
- ✅ Installs missing dependencies (Redis, MongoDB if needed)
- ✅ Installs Python packages from requirements.txt
- ✅ Installs frontend dependencies (yarn/npm)
- ✅ Starts Redis, MongoDB, Celery, Backend, Frontend
- ✅ Performs health checks on all services
- ✅ Works on Ubuntu, Debian, CentOS, macOS, **and Windows**

**Startup time:** ~2-5 minutes first time (installs dependencies), ~20-30 seconds after that

> **💡 TIP for Linux/macOS:** You can also run `./setup.sh` first to validate your environment before starting services, but it's optional - `run.sh` does everything!
> 
> **💡 TIP for Windows:** See [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for detailed Windows setup instructions and troubleshooting

### Access the Application

Once started:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

### View Logs

All logs are in the local `logs/` directory:
```bash
tail -f logs/backend.log
tail -f logs/frontend.log
tail -f logs/celery_worker.log
```

---

## ✨ Features

### 🎨 User Interface
- **Light/Dark Theme Toggle**: Seamlessly switch between light and dark modes with automatic theme persistence
  - Theme preference saved in localStorage
  - Auto-detects system theme preference on first visit
  - Elegant Moon/Sun icon toggle in the sidebar
- **File Type Filtering**: Smart file organization with category-based filtering
  - Filter by "Tous" (All), "Documents", "Feuilles de calcul" (Spreadsheets), or "Images"
  - Real-time count display for each file category
  - Extension-based automatic categorization (PDF, DOCX, XLSX, PNG, etc.)

### 🤖 Intelligent AI Assistance (Xynorash)
- **RAG-based Conversational AI**: Context-aware responses based on your internal and external documents
- **Multilingual Support**: English and French language support
- **Tool-Use Capabilities**: Generate PDF reports (financial reviews, quotes) and create interactive data visualizations
- **Advanced OCR**: Extract text from images, scanned PDFs, and embedded images in documents

#### AI Agent Tools
The Xynorash AI agent uses the following specialized tools:

1. **KnowledgeBaseSearch**: Answers questions from the knowledge base and can also answer general questions if no relevant documents are found. Does not write code.
2. **FinancialReviewGenerator**: Generates financial review PDF reports with company data, revenue, and profit information.
3. **QuoteGenerator**: Creates professional quote/quotation PDF documents with item details, pricing, and client information.
4. **CanvasGenerator**: Generates interactive data visualizations including bar charts, pie charts, combo charts, tables, and dashboards.

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
- **Lucide React**: Beautiful icon library
- **Theme System**: CSS variables for light/dark mode theming
- **Context API**: State management for theme and app state

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

- **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
- **Node.js 16+**: [Download Node.js](https://nodejs.org/)
- **Redis**: Message broker for Celery (required)
- **MongoDB**: Database (recommended)

### Installation

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server mongodb
```

**macOS:**
```bash
brew install redis mongodb-community
brew services start redis
brew services start mongodb-community
```

**CentOS/RHEL:**
```bash
sudo yum install redis mongodb-org
sudo systemctl start redis
sudo systemctl start mongod
```

### Optional System Dependencies

- **Tesseract OCR**: For image text extraction
- **LibreOffice**: For legacy .doc file conversion
- **poppler-utils**: For advanced PDF processing

These are optional and can be installed later if needed.

---

## 🎯 Getting Started

### Quick Start (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd neuralstark
   ```

2. **Install prerequisites** (if not already installed)
   ```bash
   # Ubuntu/Debian
   sudo apt-get install redis-server mongodb
   
   # macOS
   brew install redis mongodb-community
   ```

3. **Make scripts executable**
   ```bash
   chmod +x run.sh stop.sh
   ```

4. **Start the application**
   ```bash
   ./run.sh
   ```
   
   Wait ~20-30 seconds for backend to load ML models.

5. **Access the application**
   - Open http://localhost:3000 in your browser

### Manual Setup

If you prefer to start services individually or need more control:

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
# Using automated scripts (logs in local directory)
tail -f logs/backend.log
tail -f logs/frontend.log
tail -f logs/celery_worker.log

# Or system logs (if started manually)
tail -f /var/log/backend.log
tail -f /var/log/frontend.log
tail -f /var/log/celery_worker.log
```

**📖 For detailed setup and troubleshooting:**
- [QUICK_START.md](QUICK_START.md) - Simple quick start guide
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Complete deployment documentation

---

## 📚 Project Structure

```
neuralstark/
├── backend/                    # Backend API
│   ├── __init__.py            # Package initialization
│   ├── server.py              # Uvicorn entry point
│   ├── main.py                # FastAPI application
│   ├── config.py              # Configuration settings
│   ├── document_parser.py     # Document parsing with OCR
│   ├── celery_app.py          # Celery worker configuration
│   ├── watcher.py             # File system watcher
│   ├── requirements.txt       # Python dependencies
│   ├── canvas_templates.json  # Visualization templates
│   └── knowledge_base/
│       ├── internal/          # Internal documents
│       └── external/          # External documents
│
├── frontend/                  # React frontend
│   ├── src/                   # Source code
│   │   ├── components/        # React components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Chat.tsx
│   │   │   ├── Files.tsx      # File management with type filtering
│   │   │   ├── Sidebar.tsx    # Navigation with theme toggle
│   │   │   ├── ThemeToggle.tsx # Theme switcher component
│   │   │   └── ui/            # Reusable UI components
│   │   ├── contexts/          # React contexts
│   │   │   └── ThemeContext.tsx # Theme state management
│   │   ├── lib/               # Utility libraries
│   │   ├── App.tsx            # Main application component
│   │   ├── main.tsx           # Application entry point
│   │   └── index.css          # Global styles with theme variables
│   ├── public/                # Static assets
│   ├── package.json           # Node dependencies
│   ├── tailwind.config.js     # Tailwind with dark mode support
│   └── vite.config.ts         # Vite configuration
│
├── logs/                      # Application logs (created on first run)
│   ├── backend.log
│   ├── frontend.log
│   ├── celery_worker.log
│   └── mongodb.log
│
├── chroma_db/                 # Vector database storage
├── scripts/                   # Utility scripts
│
├── run.sh                     # Universal startup script (Linux/macOS)
├── stop.sh                    # Universal stop script (Linux/macOS)
├── run_windows.bat            # Universal startup script (Windows)
├── stop_windows.bat           # Universal stop script (Windows)
│
├── README.md                  # This file
├── WINDOWS_SETUP.md           # Windows setup guide
├── QUICK_START.md             # Quick start guide
├── DEPLOYMENT_GUIDE.md        # Complete deployment guide
└── canvas_templates.json      # Visualization templates
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

### Backend Takes Long to Start

**This is normal!** The backend loads ML models (SentenceTransformer) which takes 10-20 seconds on first startup.

Wait for:
```
✓ Backend started on port 8001
```

### Port Already in Use

```bash
# Find what's using the port
lsof -i:8001  # Backend
lsof -i:3000  # Frontend

# Kill the process
kill -9 <PID>

# Or use the stop script
./stop.sh
./run.sh
```

### Redis Not Running

```bash
# Check Redis
redis-cli ping  # Should return "PONG"

# Install Redis (if not installed)
# Ubuntu/Debian:
sudo apt-get install redis-server

# macOS:
brew install redis

# Start Redis
redis-server --daemonize yes
```

### MongoDB Not Running

```bash
# Check MongoDB
mongosh --eval "db.version()"

# Install if needed (see Prerequisites section)

# Start MongoDB
mongod --fork --logpath logs/mongodb.log --bind_ip_all
```

### Check Logs

All logs are in the `logs/` directory:

```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log

# Celery logs
tail -f logs/celery_worker.log
```

### Permission Denied

```bash
# Make scripts executable
chmod +x run.sh stop.sh

# Ensure you're in project directory
cd /path/to/neuralstark
./run.sh
```

### Common Issues

1. **ChromaDB Errors** ("Could not connect to tenant" or "unable to open database file"):
   - **Cause**: Missing `chroma_db/` or `backend/knowledge_base/external/` directories
   - **Solution**: Run `./run.sh` which automatically creates all required directories
   - **Manual fix**: 
     ```bash
     mkdir -p chroma_db backend/knowledge_base/internal backend/knowledge_base/external
     chmod -R 755 chroma_db backend/knowledge_base
     ```
   - Ensure `chroma_db/` directory exists and is writable before starting the backend

2. **Embedding Dimension Mismatch** ("Collection expecting embedding with dimension of 384, got 1024"):
   - **Cause**: ChromaDB collection was created with a different embedding model
   - **Solution**: Reset ChromaDB to recreate with correct dimensions
   - **Quick fix**:
     ```bash
     ./stop.sh
     rm -rf chroma_db
     mkdir -p chroma_db
     ./run.sh
     ```
   - Documents will be automatically reindexed
   - See [CHROMADB_FIX_NOTES.md](CHROMADB_FIX_NOTES.md) for detailed instructions
   
3. **Backend loading**: Wait 20-30 seconds for ML models to load

4. **Port conflicts**: Use `./stop.sh` then `./run.sh`

5. **Redis missing**: Install Redis (see Prerequisites)

6. **Logs location**: Check `logs/` directory in project root

7. **Dependencies**: Run `pip install -r backend/requirements.txt`

For comprehensive troubleshooting, see:
- **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** - Complete installation for any environment
- **[setup.sh](setup.sh)** - Automated setup validation script
- [QUICK_START.md](QUICK_START.md) - Quick start guide
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Deployment documentation

---

## 📖 Documentation

- **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)**: 🔧 **Complete installation guide for any environment**
- **[setup.sh](setup.sh)**: ✅ Automated setup validation and environment check
- **[QUICK_START.md](QUICK_START.md)**: ⚡ Simple quick start guide with common issues
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**: ⭐ Complete deployment documentation
- **[README.md](README.md)**: 📘 This file - comprehensive overview

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

### Version 4.2 - Enhanced User Interface

✅ **Theme Toggle**: Light/Dark mode with localStorage persistence  
✅ **File Type Filters**: Category-based file filtering (All, Documents, Spreadsheets, Images)  
✅ **Smart Categorization**: Automatic file type detection by extension  
✅ **Real-time Counts**: Display file counts for each category  
✅ **Enhanced UX**: Empty state handling for filtered results  

### Version 4.1 - Universal Deployment Scripts

✅ **Universal Scripts**: Work on any Linux environment (no sudo required)  
✅ **Local Logs**: All logs in `logs/` directory  
✅ **Canvas Templates**: Included in backend configuration  
✅ **Smart Detection**: Auto-finds virtual environments  
✅ **Cross-Platform**: Ubuntu, Debian, CentOS, macOS support  
✅ **Health Checks**: Comprehensive service verification  
✅ **User-Friendly**: Clear error messages with solutions  

### Previous Updates (Version 0.3.0)

✅ **Backend Renamed**: `neuralstark/` → `backend/`  
✅ **Full MS Office Support**: .doc and .docx files with OCR  
✅ **Enhanced OCR**: Images, scanned PDFs, embedded images  
✅ **Resource Optimization**: 75% reduction in memory usage  
✅ **Network Access**: No host restrictions, CORS enabled

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
# 1. Clone the repository
git clone <repository-url>
cd neuralstark

# 2. Install prerequisites (if needed)
# Ubuntu/Debian:
sudo apt-get install redis-server mongodb

# macOS:
brew install redis mongodb-community

# 3. Make scripts executable
chmod +x run.sh stop.sh

# 4. Start the application
./run.sh

# 5. Wait ~20 seconds for backend to load ML models

# 6. Open in browser
# http://localhost:3000
```

**Features:**
- 🚀 No sudo required for scripts
- 📝 Logs in local `logs/` directory
- ✅ Works on any Linux distribution
- 🔄 Hot reload for development
- 📊 20+ visualization templates included

**Happy building with NeuralStark! 🚀**
