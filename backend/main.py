from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
import os
import datetime
import time # Import time module for performance monitoring
import logging # Import logging module
import shutil # For file operations
import chromadb # For clearing the vector store
from typing import Optional # For optional parameters
import json # For loading canvas templates

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain import hub

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from backend.config import settings
from .watcher import start_watcher_in_background, stop_watcher
from backend.celery_app import process_document_task # Import Celery task
from backend.document_parser import parse_document # Import parse_document for content retrieval

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# --- Load Canvas Templates on Startup ---
canvas_templates = {}
try:
    with open("canvas_templates.json", "r", encoding="utf-8") as f:
        canvas_templates = json.load(f)
except FileNotFoundError:
    logging.warning("canvas_templates.json not found. Canvas generation will be limited.")
except json.JSONDecodeError:
    logging.error("Error decoding canvas_templates.json. Canvas generation may fail.")

# --- PDF Generation Functions (Tools) ---
KNOWLEDGE_BASE_DIR = settings.INTERNAL_KNOWLEDGE_BASE_PATH # Use the configured path

def generate_financial_review_pdf(data: str) -> str:
    """Generates a financial review PDF report and saves it to the knowledge_base folder.
    Input should be a JSON string containing financial data (e.g., {"company": "ABC Corp", "revenue": "$1M", "profit": "$200K"}).
    Returns the absolute path to the generated PDF file.
    """
    start_time = time.time()
    try:
        # Ensure the knowledge_base directory exists
        os.makedirs(KNOWLEDGE_BASE_DIR, exist_ok=True)

        # Strip potential backticks from the input string
        data = data.strip('`')

        # Parse data (simple example, more robust parsing needed for real data)
        import json
        try:
            financial_data = json.loads(data)
        except json.JSONDecodeError:
            return f"Error: Invalid JSON input for financial review: {data}"

        file_name = f"financial_review_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = os.path.join(KNOWLEDGE_BASE_DIR, file_name)

        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("Financial Review Report", styles['h1']))
        story.append(Spacer(1, 0.2 * 2.54 * 72)) # 0.2 inch spacer

        for key, value in financial_data.items():
            story.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value}", styles['Normal']))
            story.append(Spacer(1, 0.1 * 2.54 * 72))

        doc.build(story)
        print(f"Generated financial review PDF: {file_path}")
        end_time = time.time()
        logging.info(f"Financial review PDF generation took {end_time - start_time:.4f} seconds.")
        return file_path
    except Exception as e:
        print(f"Error generating financial review PDF: {e}")
        return f"Error generating financial review PDF: {e}"

def generate_quote_pdf(quote_details: str) -> str:
    """Generates a quote PDF and saves it to the knowledge_base folder.
    Input should be a JSON string containing quote details (e.g., {"item": "Service A", "price": "$500", "client": "Client X"}).
    Returns the absolute path to the generated PDF file.
    """
    start_time = time.time()
    try:
        os.makedirs(KNOWLEDGE_BASE_DIR, exist_ok=True)

        # Strip potential backticks from the input string
        quote_details = quote_details.strip('`')

        import json
        try:
            details = json.loads(quote_details)
        except json.JSONDecodeError:
            return f"Error: Invalid JSON input for quote: {quote_details}"

        file_name = f"quote_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = os.path.join(KNOWLEDGE_BASE_DIR, file_name)

        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("Quotation", styles['h1']))
        story.append(Spacer(1, 0.2 * 2.54 * 72))

        for key, value in details.items():
            story.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value}", styles['Normal']))
            story.append(Spacer(1, 0.1 * 2.54 * 72))

        doc.build(story)
        print(f"Generated quote PDF: {file_path}")
        end_time = time.time()
        logging.info(f"Quote PDF generation took {end_time - start_time:.4f} seconds.")
        return file_path
    except Exception as e:
        print(f"Error generating quote PDF: {e}")
        return f"Error generating quote PDF: {e}"

# --- Canvas Tool Functions ---
def generate_canvas_preview(data: str) -> dict:
    """Generates a visual canvas preview for data using predefined templates.
    Input should be a JSON string containing the 'canvas_type' and the 'data' to populate the template.
    Example: {"canvas_type": "bar_chart", "data": {"title": "New Title", "data": [...]}}
    Returns a JSON object representing the canvas.
    """
    start_time = time.time()
    try:
        import json
        data = data.strip('`')
        parsed_data = json.loads(data)
        canvas_type = parsed_data.get("canvas_type")
        canvas_data = parsed_data.get("data")

        if not canvas_type or not canvas_data:
            return {"error": "Invalid input for canvas generation. 'canvas_type' and 'data' are required."}

        if canvas_type not in canvas_templates.get("visualization_formats", {}):
            return {"error": f"Canvas type '{canvas_type}' not found in templates."}

        import copy
        template = copy.deepcopy(canvas_templates["visualization_formats"][canvas_type])

        if "title" in canvas_data:
            template["title"] = canvas_data["title"]

        if canvas_type == "pie_chart":
            if "labels" in canvas_data and "datasets" in canvas_data:
                labels = canvas_data["labels"]
                dataset = canvas_data["datasets"][0] 
                template["data"] = [{"label": l, "value": v} for l, v in zip(labels, dataset["data"])]
        elif canvas_type == "bar_chart":
            if isinstance(canvas_data, list):
                template["data"] = canvas_data
            elif "labels" in canvas_data and "datasets" in canvas_data:
                labels = canvas_data["labels"]
                dataset = canvas_data["datasets"][0]
                template["data"] = [{"category": l, "value": v} for l, v in zip(labels, dataset["data"])]
        elif canvas_type == "table":
            if "headers" in canvas_data and "rows" in canvas_data:
                headers = canvas_data["headers"]
                rows = canvas_data["rows"]
                template["columns"] = [{"field": h.lower().replace(" ", "_"), "title": h} for h in headers]
                template["data"] = [dict(zip([c["field"] for c in template["columns"]], r)) for r in rows]

        if "axes" in canvas_data:
            if "x" in canvas_data["axes"] and "x" in template["axes"]:
                if "label" in canvas_data["axes"]["x"]:
                    template["axes"]["x"]["label"] = canvas_data["axes"]["x"]["label"]
            if "y" in canvas_data["axes"] and "y" in template["axes"]:
                if "label" in canvas_data["axes"]["y"]:
                    template["axes"]["y"]["label"] = canvas_data["axes"]["y"]["label"]

        elif canvas_type == "combo_chart":
            if "labels" in canvas_data and "series" in canvas_data:
                labels = canvas_data["labels"]
                series = canvas_data["series"]
                template["series"] = []
                for i, s in enumerate(series):
                    template["series"].append({
                        "name": s["name"],
                        "type": "column" if i == 0 else "line",
                        "axis": f"y{i+1}",
                        "data": [{"x": l, "y": v} for l, v in zip(labels, s["data"])]
                    })

        if "kpis" in canvas_data:
            template["kpis"] = canvas_data["kpis"]

        end_time = time.time()
        logging.info(f"Canvas generation for '{canvas_type}' took {end_time - start_time:.4f} seconds.")
        return {"canvas": template}

    except Exception as e:
        print(f"Error generating canvas preview: {e}")
        return {"error": f"Error generating canvas preview: {e}"}


# --- LangChain Setup ---
# Initialize embeddings for retrieval
embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL_NAME)

# Initialize LLM for chat and agent reasoning
llm = ChatGoogleGenerativeAI(model=settings.LLM_MODEL, google_api_key=settings.LLM_API_KEY)

# Custom Knowledge Base Search function to allow filtering by source_type
def _run_knowledge_base_search(input_json_string: str) -> str:
    """Performs a knowledge base search, optionally filtering by source_type (internal/external).
    Input should be a JSON string with 'query' and optional 'source_type' (e.g., {"query": "How to cook rice?", "source_type": "external"}).
    """
    start_time = time.time()
    print(f"Performing knowledge base search for input: {input_json_string}")
    
    import json
    try:
        parsed_input = json.loads(input_json_string)
        query = parsed_input.get("query")
        source_type = parsed_input.get("source_type")
    except json.JSONDecodeError:
        return f"Error: Invalid JSON input for KnowledgeBaseSearch: {input_json_string}"
    except AttributeError:
        return f"Error: Input for KnowledgeBaseSearch must be a JSON string: {input_json_string}"

    if not query:
        return "Error: 'query' key is missing in the input JSON for KnowledgeBaseSearch."

    # Re-initialize ChromaDB client to ensure it reads the latest state from disk
    # This is a temporary solution for development; for production, consider a more efficient refresh mechanism
    current_vector_store = Chroma(persist_directory=settings.CHROMA_DB_PATH, embedding_function=embeddings)

    # Build the filter for ChromaDB
    chroma_filter = {}
    if source_type and source_type in ["internal", "external"]:
        chroma_filter["source_type"] = source_type

    # Create a retriever with the filter
    search_kwargs = {}
    if chroma_filter:
        search_kwargs["filter"] = chroma_filter
    retriever = current_vector_store.as_retriever(search_kwargs=search_kwargs)
    
    # Create a temporary RAG chain for this specific query
    qa_chain_filtered = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    
    response = qa_chain_filtered.invoke({"query": query})
    
    # Format the response to include source documents for the agent
    valid_source_documents = [doc for doc in response["source_documents"] if doc.page_content is not None and doc.page_content.strip() != '']

    if valid_source_documents:
        sources = ", ".join([os.path.basename(doc.metadata["source"]) for doc in valid_source_documents])
        final_answer = f"Answer: {response['result']}\nSources: {sources}"
    else:
        final_answer = f"Answer: {response['result']}\nSources: None"

    end_time = time.time()
    logging.info(f"Knowledge base search for '{query}' took {end_time - start_time:.4f} seconds.")
    return final_answer

# Define the tools for the agent
tools = [
    Tool(
        name="FinancialReviewGenerator",
        func=generate_financial_review_pdf,
        description="Utile pour générer des rapports PDF de revue financière. L'entrée doit être une chaîne JSON contenant des données financières (par exemple, {\"company\": \"ABC Corp\", \"revenue\": \"$1M\", \"profit\": \"$200K\"})."
    ),
    Tool(
        name="QuoteGenerator",
        func=generate_quote_pdf,
        description="Utile pour générer des documents PDF de devis. L'entrée doit être une chaîne JSON contenant les détails du devis (par exemple, {\"item\": \"Service A\", \"price\": \"$500\", \"client\": \"Client X\"})."
    ),
    Tool(
        name="KnowledgeBaseSearch",
        func=_run_knowledge_base_search,
        description="Use this tool to answer questions from the knowledge base. You can also answer general questions if no relevant documents are found. Do NOT write code. Respond only with Action and Action Input."
    ),
    Tool(
        name="CanvasGenerator",
        func=generate_canvas_preview,
        description=f"Utile pour générer un aperçu visuel des données sur un canevas. Utilisez cet outil lorsque l'utilisateur demande un résumé, un graphique ou une représentation visuelle des informations. L'entrée doit être une chaîne JSON avec 'canvas_type' et 'data'. Les canvas_types disponibles sont : {list(canvas_templates.get('visualization_formats', {}).keys())}"
    )
]

# Get the prompt for the ReAct agent
# Customize the prompt to emphasize KnowledgeBaseSearch priority
prompt_template = """Vous êtes Xynorash, un agent IA entraîné par NeuralStark pour aider les professionnels avec les données de leur entreprise, société ou travail.

Vous avez accès aux outils suivants :
{tools}

Les noms des outils sont : {tool_names}

Répondez à la question de l'utilisateur. Si vous avez besoin d'informations supplémentaires, utilisez les outils à votre disposition. Une fois que vous avez suffisamment d'informations, fournissez une réponse finale et complète.

**Instructions Spéciales:**
*   Si vous utilisez un outil, l'observation de l'outil sera disponible pour votre prochaine pensée.
*   Si vous avez la réponse finale, commencez votre réponse par "Final Answer:".
*   Lorsque vous utilisez l'outil CanvasGenerator, votre réponse finale doit être uniquement l'objet JSON du canevas, sans aucun texte ou description supplémentaire.

Commencez !

Question : {input}
Pensée :{agent_scratchpad}"""
prompt = PromptTemplate.from_template(prompt_template)

# Create the agent
agent = create_react_agent(llm, tools, prompt)

# Create the agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# --- FastAPI App Setup ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    print("Starting NeuralStark API...")
    start_watcher_in_background()
    yield
    # Shutdown event
    print("Shutting down NeuralStark API...")
    stop_watcher()

app = FastAPI(
    title="NeuralStark API",
    description="AI Chat, Tool Usage, and Document Management System",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS - Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

class ChatRequest(BaseModel):
    query: str

class DeleteRequest(BaseModel):
    file_path: str

@app.get("/api")
@app.get("/api/")
async def read_root():
    return {"message": "Welcome to NeuralStark API!"}

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    print(f"Received chat query: {request.query}")
    start_time = time.time()
    try:
        # The agent will decide whether to use a tool or answer directly
        response = agent_executor.invoke({"input": request.query})
        end_time = time.time()
        logging.info(f"Overall chat response for '{request.query}' took {end_time - start_time:.4f} seconds.")

        # Try to parse the output as JSON if it's a string representation of a dict
        output = response["output"]
        try:
            # Using ast.literal_eval is safer than eval().
            import ast
            parsed_output = ast.literal_eval(output)
            
            # Ensure it's a valid JSON-serializable dictionary
            # This step is to be absolutely sure the frontend receives valid JSON
            import json
            json_string = json.dumps(parsed_output, ensure_ascii=False)
            final_response = json.loads(json_string)

            return {"response": final_response}
        except (ValueError, SyntaxError):
            # If it's not a dict string, return the original string output.
            return {"response": output}

    except Exception as e:
        error_message = str(e)
        print(f"Error in chat endpoint: {error_message}")
        
        # Handle specific quota exceeded errors with more user-friendly messages
        if "quota exceeded" in error_message.lower() or "429" in error_message:
            raise HTTPException(
                status_code=429, 
                detail="Service temporarily unavailable due to high demand. Please try again in a few minutes."
            )
        elif "api" in error_message.lower() and "key" in error_message.lower():
            raise HTTPException(
                status_code=503, 
                detail="AI service is currently unavailable. Please try again later."
            )
        else:
            raise HTTPException(status_code=500, detail="An error occurred while processing your request.")


@app.get("/api/documents")
async def list_documents():
    try:
        # Re-initialize ChromaDB client to ensure it reads the latest state from disk
        # This is a temporary solution for development; for production, consider a more efficient refresh mechanism
        current_vector_store = Chroma(persist_directory=settings.CHROMA_DB_PATH, embedding_function=embeddings)

        results = current_vector_store.get(include=['metadatas'])
        
        unique_sources = set()
        if results and 'metadatas' in results:
            for metadata in results['metadatas']:
                if 'source' in metadata:
                    unique_sources.add(metadata['source'])
        
        return {"indexed_documents": list(unique_sources)}
    except Exception as e:
        print(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/documents/upload")
async def upload_document(source_type: str = Form(...), file: UploadFile = File(...)):
    """Uploads a new document to the knowledge base for automatic processing and indexing."""
    if source_type not in ["internal", "external"]:
        raise HTTPException(status_code=400, detail="Invalid source_type. Must be 'internal' or 'external'.")

    target_dir = settings.INTERNAL_KNOWLEDGE_BASE_PATH if source_type == "internal" else settings.EXTERNAL_KNOWLEDGE_BASE_PATH
    os.makedirs(target_dir, exist_ok=True)

    file_path = os.path.join(target_dir, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Dispatch Celery task for processing
        process_document_task.delay(file_path, "created")

        return {"message": "File uploaded successfully. Processing started.", "file_path": file_path, "source_type": source_type}
    except Exception as e:
        logging.error(f"Error uploading file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")

@app.get("/api/documents/content")
async def get_document_content(file_path: str):
    """Retrieves the extracted text content of a specific document from the knowledge base."""
    # Basic security check: Ensure the file path is within the knowledge base directories
    abs_file_path = os.path.abspath(file_path)
    internal_kb_path = os.path.abspath(settings.INTERNAL_KNOWLEDGE_BASE_PATH)
    external_kb_path = os.path.abspath(settings.EXTERNAL_KNOWLEDGE_BASE_PATH)

    if not (abs_file_path.startswith(internal_kb_path) or abs_file_path.startswith(external_kb_path)):
        raise HTTPException(status_code=400, detail="File path is outside knowledge base directories.")

    if not os.path.exists(abs_file_path):
        raise HTTPException(status_code=404, detail="File not found.")

    try:
        content = parse_document(abs_file_path)
        if content is None:
            raise HTTPException(status_code=500, detail="Could not extract content from the file.")
        return {"file_path": file_path, "content": content}
    except Exception as e:
        logging.error(f"Error retrieving content for {file_path}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving content: {e}")

@app.post("/api/documents/delete")
async def delete_document(request: DeleteRequest):
    """Deletes a document from the knowledge base. This will also trigger its removal from the vector store."""
    # Basic security check: Ensure the file path is within the knowledge base directories
    abs_file_path = os.path.abspath(request.file_path)
    internal_kb_path = os.path.abspath(settings.INTERNAL_KNOWLEDGE_BASE_PATH)
    external_kb_path = os.path.abspath(settings.EXTERNAL_KNOWLEDGE_BASE_PATH)

    if not (abs_file_path.startswith(internal_kb_path) or abs_file_path.startswith(external_kb_path)):
        raise HTTPException(status_code=400, detail="File path is outside knowledge base directories.")

    if not os.path.exists(abs_file_path):
        raise HTTPException(status_code=404, detail="File not found.")

    try:
        os.remove(abs_file_path)
        # Watchdog will pick up the deletion and trigger the Celery task
        return {"message": "File deletion initiated. It will be removed from the knowledge base."}
    except Exception as e:
        logging.error(f"Error deleting file {request.file_path}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting file: {e}")

@app.post("/api/knowledge_base/reset")
async def reset_knowledge_base(reset_type: str):
    """Resets the knowledge base. 
    - 'hard': Deletes all files and clears the vector store.
    - 'soft': Re-indexes all existing files.
    """
    if reset_type not in ["hard", "soft"]:
        raise HTTPException(status_code=400, detail="Invalid reset_type. Must be 'hard' or 'soft'.")

    try:
        # Clear the ChromaDB vector store using the client API
        client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        # The default collection name used by LangChain's Chroma is "langchain"
        try:
            collection = client.get_collection("langchain")
            # Get all items in the collection to delete them by ID
            # This is safer than deleting and recreating the collection
            results = collection.get()
            if results["ids"]:
                collection.delete(ids=results["ids"])
            print("Successfully cleared ChromaDB collection.")
        except ValueError:
            # This error is raised if the collection does not exist, which is fine.
            print("ChromaDB collection not found, creating a new one.")

        if reset_type == "hard":
            # Delete all files in internal and external knowledge base directories
            for dir_path in [settings.INTERNAL_KNOWLEDGE_BASE_PATH, settings.EXTERNAL_KNOWLEDGE_BASE_PATH]:
                if os.path.exists(dir_path):
                    for filename in os.listdir(dir_path):
                        file_path = os.path.join(dir_path, filename)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
            return {"message": "Knowledge base has been hard reset. All files and embeddings have been deleted."}

        elif reset_type == "soft":
            # Re-index all existing files
            files_to_reindex = []
            for dir_path in [settings.INTERNAL_KNOWLEDGE_BASE_PATH, settings.EXTERNAL_KNOWLEDGE_BASE_PATH]:
                if os.path.exists(dir_path):
                    for filename in os.listdir(dir_path):
                        file_path = os.path.join(dir_path, filename)
                        if os.path.isfile(file_path):
                            files_to_reindex.append(file_path)
            
            for file_path in files_to_reindex:
                process_document_task.delay(file_path, "created")
            
            return {"message": f"Knowledge base has been soft reset. Re-indexing {len(files_to_reindex)} files."}

    except Exception as e:
        logging.error(f"Error resetting knowledge base: {e}")
        raise HTTPException(status_code=500, detail=f"Error resetting knowledge base: {e}")
