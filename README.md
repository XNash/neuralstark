# NeuralStark

NeuralStark is a multi-platform AI assistant designed to provide intelligent assistance, manage knowledge bases, and process documents. It features a web-based frontend built with React and a powerful Python backend handling AI/ML tasks, document parsing, and data management.

## Features

*   **Intelligent AI Assistance:** Leverage AI/ML capabilities for various tasks.
*   **Knowledge Base Management:** Organize and query internal and external documents.
*   **Document Parsing:** Process and extract information from various document formats (PDF, DOCX, ODT, XLSX, etc.).
*   **Web User Interface:** Intuitive and responsive frontend for interaction.
*   **Asynchronous Task Processing:** Utilizes Celery for background tasks.

## Technologies Used

### Frontend
*   **React:** A JavaScript library for building user interfaces.
*   **TypeScript:** A typed superset of JavaScript that compiles to plain JavaScript.
*   **Vite:** A fast build tool for modern web projects.
*   **Tailwind CSS:** A utility-first CSS framework for rapid UI development.

### Backend
*   **Python:** The primary language for backend logic and AI/ML.
*   **Flask/FastAPI (assumed):** Web framework for building APIs.
*   **Celery:** An asynchronous task queue/job queue based on distributed message passing.
*   **ChromaDB:** An open-source embedding database for AI applications.
*   **Other Libraries:** `requirements.txt` contains specific dependencies for document parsing, AI models, etc.

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

Create a `.env` file in the `neuralstark/neuralstark/` directory. You might need to add specific configurations here, such as API keys, database connection strings, or other settings required by the application. Refer to `config.py` for expected variables.

```
# Example .env content (adjust as needed)
# DATABASE_URL=sqlite:///./chroma.sqlite3
# CELERY_BROKER_URL=redis://localhost:6379/0
# CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

#### Running the Backend Application

```bash
python main.py
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

celery -A celery_app worker -l info
```
If you need to run Celery Beat for scheduled tasks:
```bash
celery -A celery_app beat -l info
```

### 3. Frontend Setup

Navigate to the frontend directory and install its dependencies.

```bash
cd ../frontend # From neuralstark/neuralstark, go back to neuralstark/frontend
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

Once both the backend and frontend servers are running, open your web browser and navigate to the address provided by the frontend development server (e.g., `http://localhost:5173`). You can then interact with the NeuralStark AI assistant through the web interface.

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## License

This project is licensed under the [MIT License](LICENSE) - see the `LICENSE` file for details.
