from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
import os
import datetime
import time # Import time module for performance monitoring
import logging # Import logging module
import shutil # For file operations
import chromadb # For clearing the vector store
from typing import Optional # For optional parameters

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

from neuralstark.config import settings
from .watcher import start_watcher_in_background, stop_watcher
from neuralstark.celery_app import process_document_task # Import Celery task
from neuralstark.document_parser import parse_document # Import parse_document for content retrieval

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

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

        file_name = f"financial_review_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"
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

        file_name = f"quote_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"
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
def create_bar_chart_data(data: dict, labels_key: str, values_key: str, chart_label: str) -> dict:
    """Helper function to create bar chart data for the canvas."""
    return {
        "type": "bar_chart",
        "data": {
            "labels": data.get(labels_key, []),
            "datasets": [
                {
                    "label": chart_label,
                    "data": data.get(values_key, [])
                }
            ]
        }
    }

def generate_canvas_preview(data: str) -> dict:
    """Generates a visual canvas preview for data.
    Input should be a JSON string containing the data and a 'canvas_type' (e.g., {"canvas_type": "financial_summary", "data": {"revenue": 5000000, "profit": 1000000}}).
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

        canvas = {
            "type": "container",
            "layout": "vertical",
            "children": []
        }

        if canvas_type == "financial_summary":
            canvas["children"].append({"type": "header", "text": "Financial Summary"})
            canvas["children"].append({"type": "key_value_pairs", "data": canvas_data})
            # Add a bar chart for financial summary
            chart_data = create_bar_chart_data(
                data=canvas_data,
                labels_key=list(canvas_data.keys()),
                values_key=list(canvas_data.values()),
                chart_label="Amount (in currency)"
            )
            canvas["children"].append(chart_data)

        # Add more canvas types here (e.g., for quotes, document previews)

        end_time = time.time()
        logging.info(f"Canvas generation for '{canvas_type}' took {end_time - start_time:.4f} seconds.")
        return {"canvas": canvas}

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
        final_answer = f"Answer: {response["result"]}\nSources: {sources}"
    else:
        final_answer = f"Answer: {response["result"]}\nSources: None"

    end_time = time.time()
    logging.info(f"Knowledge base search for '{query}' took {end_time - start_time:.4f} seconds.")
    return final_answer

# Define the tools for the agent
tools = [
    Tool(
        name="FinancialReviewGenerator",
        func=generate_financial_review_pdf,
        description="Useful for generating financial review PDF reports. Input should be a JSON string containing financial data (e.g., {\"company\": \"ABC Corp\", \"revenue\": \"$1M\", \"profit\": \"$200K\"})."
    ),
    Tool(
        name="QuoteGenerator",
        func=generate_quote_pdf,
        description="Useful for generating quote PDF documents. Input should be a JSON string containing quote details (e.g., {\"item\": \"Service A\", \"price\": \"$500\", \"client\": \"Client X\"})."
    ),
    Tool(
        name="KnowledgeBaseSearch",
        func=_run_knowledge_base_search,
        description="This is the primary tool for finding information. Always use this tool first if the question requires retrieving any kind of information, whether it's general knowledge or details from indexed documents. It can optionally filter by 'source_type' (e.g., 'internal' or 'external'). Input should be a JSON string with 'query' and optional 'source_type' (e.g., {\"query\": \"How to cook rice?\", \"source_type\": \"external\"})."
    ),
    Tool(
        name="CanvasGenerator",
        func=generate_canvas_preview,
        description="Useful for generating a visual canvas preview of data. Use this tool when the user asks for a summary, a graph, or a visual representation of information. Input should be a JSON string with 'canvas_type' and 'data' (e.g., {\"canvas_type\": \"financial_summary\", \"data\": {\"revenue\": 5000000, \"profit\": 1000000}})."
    )
]

# Get the prompt for the ReAct agent
# Customize the prompt to emphasize KnowledgeBaseSearch priority
prompt_template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

When generating financial reviews or quotes, if you need specific data (like company name, revenue, profit, item, price, client), first try to find it using the KnowledgeBaseSearch tool. If you cannot find the necessary information, ask the user for it.

Begin!

Question: {input}
Thought:{agent_scratchpad}"""
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

class ChatRequest(BaseModel):
    query: str

class DeleteRequest(BaseModel):
    file_path: str

@app.get("/")
async def read_root():
    return {"message": "Welcome to NeuralStark API!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

from fastapi.responses import JSONResponse # Add this import

# ... (rest of the file) ...

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    print(f"Received chat query: {request.query}")
    start_time = time.time()
    try:
        # The agent will decide whether to use a tool or answer directly
        response = agent_executor.invoke({"input": request.query})
        
        output_content = response["output"]
        
        # Attempt to parse the output_content as JSON, as it might be a tool's JSON output
        try:
            parsed_output = json.loads(output_content)
            if isinstance(parsed_output, dict) and "canvas" in parsed_output:
                # If it's a canvas object, return it directly as part of the response
                return JSONResponse(content={"response": parsed_output})
            else:
                # If it's a valid JSON but not a canvas, return it as is
                return JSONResponse(content={"response": output_content})
        except json.JSONDecodeError:
            # If it's not a valid JSON, treat it as a regular string message
            return JSONResponse(content={"response": output_content})
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/documents")
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
        return {"error": str(e)}, 500

@app.post("/documents/upload")
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

@app.get("/documents/content")
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

@app.post("/documents/delete")
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

@app.post("/knowledge_base/reset")
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
