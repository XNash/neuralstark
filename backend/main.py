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

# Cross-encoder for reranking
from sentence_transformers import CrossEncoder

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from backend.config import settings
from .watcher import start_watcher_in_background, stop_watcher
from backend.celery_app import process_document_task, process_document_sync # Import Celery task and sync fallback
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



# --- Helper Function for Document Processing ---
def dispatch_document_processing(file_path: str, event_type: str):
    """
    Try to dispatch document processing to Celery. 
    If Celery/Redis is not available, process synchronously.
    """
    try:
        # Try to dispatch to Celery
        process_document_task.delay(file_path, event_type)
        logging.info(f"Dispatched {file_path} to Celery worker")
        return {"status": "dispatched_async", "file_path": file_path}
    except Exception as e:
        # Celery/Redis not available, process synchronously
        logging.warning(f"Celery not available ({str(e)}), processing synchronously")
        result = process_document_sync(file_path, event_type)
        logging.info(f"Processed {file_path} synchronously: {result}")
        return result

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
# Initialize embeddings for retrieval with optimized settings
logging.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}...")
embeddings = HuggingFaceEmbeddings(
    model_name=settings.EMBEDDING_MODEL_NAME,
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'batch_size': settings.EMBEDDING_BATCH_SIZE, 'normalize_embeddings': True}
)
logging.info("✓ Embedding model loaded successfully")

# Initialize cross-encoder for reranking
logging.info(f"Loading reranker model: {settings.RERANKER_MODEL}...")
reranker = CrossEncoder(settings.RERANKER_MODEL)
logging.info("✓ Reranker model loaded successfully")

# Initialize LLM for chat and agent reasoning
llm = ChatGoogleGenerativeAI(model=settings.LLM_MODEL, google_api_key=settings.LLM_API_KEY)

# Import robust ChromaDB utilities
from backend.chromadb_fix import create_robust_vector_store, robust_similarity_search, get_collection_info

# Custom Knowledge Base Search function with improved retrieval and reranking
def _run_knowledge_base_search(input_json_string: str) -> str:
    """Performs an optimized knowledge base search with reranking for better accuracy.
    Input should be a JSON string with 'query' and optional 'source_type' (e.g., {"query": "How to cook rice?", "source_type": "external"}).
    """
    start_time = time.time()
    logging.info(f"Performing knowledge base search for input: {input_json_string}")
    
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

    # Create robust vector store with error handling
    try:
        # Try to create/get existing vector store
        chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_DB_PATH,
            settings=chromadb.Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        current_vector_store = Chroma(
            client=chroma_client,
            embedding_function=embeddings,
            collection_name="knowledge_base_collection"
        )
        
        # Check if collection has documents
        doc_count = get_collection_info(chroma_client)
        if doc_count == 0:
            logging.warning("No documents found in ChromaDB collection")
            return "Answer: No documents are currently indexed in the knowledge base. Please upload some documents first.\nSources: None"
            
    except Exception as e:
        logging.error(f"Error initializing ChromaDB: {e}")
        # Try to create a fresh vector store
        current_vector_store, chroma_client = create_robust_vector_store()
        
        if not current_vector_store:
            return "Answer: Unable to access the knowledge base due to technical issues. Please try again or contact support.\nSources: None"

    # Build the filter for ChromaDB
    chroma_filter = {}
    if source_type and source_type in ["internal", "external"]:
        chroma_filter["source_type"] = source_type

    logging.info(f"Retrieving top {settings.RETRIEVAL_K} candidates...")
    logging.info(f"Using ChromaDB path: {settings.CHROMA_DB_PATH}")
    logging.info(f"Collection name: knowledge_base_collection")
    logging.info(f"Query: {query}")
    retrieval_start = time.time()
    
    # Use robust similarity search with multiple fallbacks
    candidate_docs = robust_similarity_search(
        current_vector_store, 
        query, 
        k=settings.RETRIEVAL_K,
        filter=chroma_filter if chroma_filter else None
    )
    
    logging.info(f"Retrieved {len(candidate_docs)} candidates in {time.time() - retrieval_start:.4f}s")
    
    if not candidate_docs:
        logging.warning("No documents found in knowledge base for this query")
        return "Answer: No relevant information found in the knowledge base for this query.\nSources: None"
    
    # Step 2: Apply score threshold filtering
    filtered_docs = [(doc, score) for doc, score in candidate_docs if score <= (1 - settings.RETRIEVAL_SCORE_THRESHOLD)]
    
    if not filtered_docs:
        logging.warning(f"All documents filtered out by score threshold ({settings.RETRIEVAL_SCORE_THRESHOLD})")
        filtered_docs = candidate_docs[:3]  # Keep top 3 if all filtered
    
    logging.info(f"After score filtering: {len(filtered_docs)} documents remain")
    
    # Filter out documents with None or empty page_content
    filtered_docs = [(doc, score) for doc, score in filtered_docs if doc.page_content and doc.page_content.strip()]
    
    if not filtered_docs:
        logging.warning("All documents have empty or None page_content")
        return "Answer: No relevant information found in the knowledge base for this query.\nSources: None"
    
    logging.info(f"After filtering out empty documents: {len(filtered_docs)} documents remain")
    
    # Step 3: Rerank using cross-encoder for better relevance
    rerank_start = time.time()
    query_doc_pairs = [[query, doc.page_content] for doc, _ in filtered_docs]
    
    try:
        rerank_scores = reranker.predict(query_doc_pairs)
        logging.info(f"Reranking completed in {time.time() - rerank_start:.4f}s")
        
        # Combine documents with rerank scores
        reranked_results = list(zip(filtered_docs, rerank_scores))
        # Sort by rerank score (higher is better for cross-encoder)
        reranked_results.sort(key=lambda x: x[1], reverse=True)
        
        # Take top K after reranking
        top_reranked = reranked_results[:settings.RERANKER_TOP_K]
        final_docs = [doc for (doc, _), _ in top_reranked]
        
        logging.info(f"Selected top {len(final_docs)} documents after reranking")
        logging.info(f"Rerank scores: {[float(score) for _, score in top_reranked]}")
    except Exception as e:
        logging.error(f"Error during reranking: {e}. Using original ranking.")
        final_docs = [doc for doc, _ in filtered_docs[:settings.RERANKER_TOP_K]]
    
    # Step 4: Build context from reranked documents
    context_parts = []
    sources = []
    for i, doc in enumerate(final_docs):
        # Skip documents with None or empty page_content
        if doc.page_content and doc.page_content.strip():
            context_parts.append(f"[Document {i+1}]\n{doc.page_content}\n")
            sources.append(os.path.basename(doc.metadata.get("source", "Unknown")))
    
    if not context_parts:
        logging.warning("No valid document content to build context")
        return "Answer: No relevant information found in the knowledge base for this query.\nSources: None"
    
    context = "\n".join(context_parts)
    
    # Step 5: Generate answer using LLM with improved context
    qa_prompt = f"""Utilisez les documents suivants pour répondre à la question. Si vous ne trouvez pas la réponse dans les documents, dites-le clairement.

Documents de référence:
{context}

Question: {query}

Réponse détaillée basée sur les documents ci-dessus:"""
    
    try:
        llm_start = time.time()
        answer = llm.invoke(qa_prompt)
        logging.info(f"LLM response generated in {time.time() - llm_start:.4f}s")
        
        result_text = answer.content if hasattr(answer, 'content') else str(answer)
    except Exception as e:
        logging.error(f"Error generating LLM response: {e}")
        result_text = "Error generating response from the retrieved documents."
    
    # Format final response
    unique_sources = list(dict.fromkeys(sources))  # Remove duplicates while preserving order
    final_answer = f"Answer: {result_text}\nSources: {', '.join(unique_sources)}"
    
    end_time = time.time()
    logging.info(f"Total knowledge base search for '{query}' took {end_time - start_time:.4f} seconds.")
    return final_answer

# Define the tools for the agent
tools = [
    Tool(
        name="FinancialReviewGenerator",
        func=generate_financial_review_pdf,
        description="Use this tool to generate financial review PDF reports. Input must be a JSON string with financial data. Example: {\"company\": \"ABC Corp\", \"revenue\": \"$1M\", \"profit\": \"$200K\"}. Respond only with Action and Action Input."
    ),
    Tool(
        name="QuoteGenerator",
        func=generate_quote_pdf,
        description="Use this tool to generate quote/quotation PDF documents. Input must be a JSON string with quote details. Example: {\"item\": \"Service A\", \"price\": \"$500\", \"client\": \"Client X\"}. Respond only with Action and Action Input."
    ),
    Tool(
        name="KnowledgeBaseSearch",
        func=_run_knowledge_base_search,
        description="Use this tool to answer questions from the knowledge base. You can also answer general questions if no relevant documents are found. Do NOT write code. Respond only with Action and Action Input."
    ),
    Tool(
        name="CanvasGenerator",
        func=generate_canvas_preview,
        description=f"Use this tool to generate interactive data visualizations and charts. Input must be a JSON string with 'canvas_type' and 'data'. Available types: {list(canvas_templates.get('visualization_formats', {}).keys())}. Respond only with Action and Action Input."
    )
]

# Get the prompt for the ReAct agent
# Optimized prompt for better RAG utilization and context understanding
prompt_template = """You are Xynorash, an AI agent trained by NeuralStark to help professionals with their firm, company, or work data.

You have access to the following tools:
{tools}

Tool names: {tool_names}

**Important Instructions:**
1. For ANY question requiring specific information, use KnowledgeBaseSearch tool first - it uses advanced semantic search with reranking.
2. Base your answers on information returned by tools, especially cited sources.
3. If knowledge base information is insufficient, you may supplement with general knowledge, but clearly mention this.
4. Always cite document sources used in your response.

**Response Format:**
*   When you use a tool, its observation will be available for your next thought.
*   Once you have sufficient information, begin your final response with "Final Answer:".
*   For CanvasGenerator tool, the final response must be only the canvas JSON object.

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
    
    # Ensure required directories exist
    os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
    os.makedirs(settings.INTERNAL_KNOWLEDGE_BASE_PATH, exist_ok=True)
    os.makedirs(settings.EXTERNAL_KNOWLEDGE_BASE_PATH, exist_ok=True)
    print(f"✓ Verified required directories exist")
    
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
        chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        current_vector_store = Chroma(
            client=chroma_client,
            embedding_function=embeddings,
            collection_name="knowledge_base_collection"
        )

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
        
        # Dispatch document processing (async if Celery available, sync otherwise)
        dispatch_document_processing(file_path, "created")
        
        return {"status": "success", "filename": file.filename, "source_type": source_type}
    except Exception as e:
        print(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
        # Use consistent collection name across the application
        try:
            collection = client.get_collection("knowledge_base_collection")
            # Get all items in the collection to delete them by ID
            # This is safer than deleting and recreating the collection
            results = collection.get()
            if results["ids"]:
                collection.delete(ids=results["ids"])
            logging.info("Successfully cleared ChromaDB collection.")
        except ValueError:
            # This error is raised if the collection does not exist, which is fine.
            logging.info("ChromaDB collection not found, creating a new one.")

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
                dispatch_document_processing(file_path, "created")
            
            return {"message": f"Knowledge base has been soft reset. Re-indexing {len(files_to_reindex)} files."}

    except Exception as e:
        logging.error(f"Error resetting knowledge base: {e}")
        raise HTTPException(status_code=500, detail=f"Error resetting knowledge base: {e}")