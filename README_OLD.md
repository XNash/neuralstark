# NeuralStark

NeuralStark is a multi-platform AI assistant powered by **Xynorash**, an AI agent trained by NeuralStark to help professionals with their firm, societies, or work data. Xynorash provides intelligent assistance, manages knowledge bases, processes documents, and generates dynamic data visualizations.

## Features

*   **Intelligent AI Assistance (Xynorash)**:
    *   **RAG-based Conversational AI**: Xynorash leverages Retrieval-Augmented Generation (RAG) to provide context-aware and accurate responses based on your internal and external documents.
    *   **Multilingual Support**: Configured to understand and respond in French, facilitating seamless interaction.
    *   **Tool-Use Capabilities**: Xynorash can utilize specialized tools for tasks like generating PDF reports (financial reviews, quotes) and creating interactive data visualizations.
*   **Comprehensive Knowledge Base Management**:
    *   **Multi-format Document Processing**: Automatically processes and extracts information from a wide range of document formats including PDF, DOCX, ODT, XLSX, CSV, Markdown, and JSON.
    *   **Automated Management**: Features a file system watcher that monitors knowledge base directories for new, modified, or deleted documents, ensuring the vector store is always up-to-date.
*   **Dynamic Data Visualization**:
    *   **Interactive Canvas Generation**: Generate various types of charts (bar, pie, combo charts), tables, and dashboards directly from your data. The `CanvasGenerator` tool provides pure JSON output for seamless frontend integration.
*   **Web User Interface**: An intuitive and responsive frontend built with React for easy interaction with Xynorash.
*   **Asynchronous Task Processing**: Utilizes Celery for efficient background tasks, ensuring the application remains responsive during heavy workloads like document indexing.

## Technologies Used

### Frontend
*   **React:** A JavaScript library for building user interfaces.
*   **TypeScript:** A typed superset of JavaScript that compiles to plain JavaScript.
*   **Vite:** A fast build tool for modern web projects.
*   **Tailwind CSS:** A utility-first CSS framework for rapid UI development.

### Backend
*   **Python:** The primary language for backend logic and AI/ML.
*   **FastAPI:** A modern, high-performance web framework for building APIs.
*   **LangChain:** The framework used for orchestrating the AI agent, integrating LLMs, tools, and the knowledge base.
*   **Google Generative AI**: Powers the Large Language Model (LLM) for conversational AI and reasoning.
*   **Hugging Face Embeddings**: Used for generating document embeddings for semantic search.
*   **Celery:** An asynchronous task queue/job queue based on distributed message passing, with Redis as the message broker.
*   **ChromaDB:** An open-source embedding database for AI applications.
*   **Other Libraries:** `requirements.txt` contains specific dependencies for document parsing (e.g., `pypdf`, `python-docx`, `odfdo`, `pandas`), PDF generation (`reportlab`), etc.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

*   **Git:** For cloning the repository.
*   **Node.js & npm (or Yarn):** For the frontend development.
    *   [Download Node.js](https://nodejs.org/)
*   **Python 3.9+ & pip:** For the backend development.
    *   [Download Python](https://www.python.org/downloads/)

## Getting Started

Follow these steps to get NeuralStark up and running on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/neuralstark.git
cd neuralstark
```

### 2. Backend Setup

Navigate to the backend directory, set up a virtual environment, and install dependencies.

```bash
cd neuralstark/neuralstark
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

#### Environment Variables

Create a `.env` file in the `neuralstark/neuralstark/` directory. This file will store sensitive information and configuration settings.

```
# Example .env content
LLM_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY"
LLM_MODEL="gemini-pro" # Or another suitable Gemini model
EMBEDDING_MODEL_NAME="sentence-transformers/all-MiniLM-L6-v2" # Or another suitable embedding model
REDIS_HOST="localhost"
REDIS_PORT=6379
REDIS_DB=0
INTERNAL_KNOWLEDGE_BASE_PATH="./knowledge_base/internal"
EXTERNAL_KNOWLEDGE_BASE_PATH="./knowledge_base/external"
CHROMA_DB_PATH="./chroma_db"
```

#### Running the Backend Application

```bash
uvicorn neuralstark.main:app --reload
```
This will start the main backend API server.

#### Running the Celery Worker

In a separate terminal, activate the virtual environment and start the Celery worker:

```bash
cd neuralstark/neuralstark
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

celery -A neuralstark.celery_app worker -l info
```
If you need to run Celery Beat for scheduled tasks:
```bash
celery -A neuralstark.celery_app beat -l info
```

### 3. Frontend Setup

Navigate to the frontend directory and install its dependencies.

```bash
cd frontend # From the project root
npm install # or yarn install
```

#### Running the Frontend Development Server

```bash
npm run dev # or yarn dev
```
This will start the frontend development server, usually accessible at `http://localhost:5173` (or another port as indicated in your terminal).

## Project Structure

*   `chroma_db/`: Local storage for the ChromaDB vector database.
*   `frontend/`: Contains the React.js application, including components, assets, and build configurations.
*   `neuralstark/`: Houses the Python backend, Celery configurations, document parsing logic, and the knowledge base.
    *   `knowledge_base/`: Stores internal and external documents used by the AI assistant.
    *   `venv/`: Python virtual environment.
*   `NeuralStark_Files/`, `NeuralStark_Full/`, `test_files/`: Example or test data directories.

## Usage

Once both the backend and frontend servers are running, open your web browser and navigate to the address provided by the frontend development server (e.g., `http://localhost:5173`). You can then interact with **Xynorash**, the NeuralStark AI assistant, through the web interface.

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## License

This project is licensed under the [MIT License](LICENSE) - see the `LICENSE` file for details.
