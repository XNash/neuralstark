# NeuralStark API Documentation for Frontend

This folder contains the OpenAPI (Swagger) specification for the NeuralStark API. This file (`openapi.json`) provides a machine-readable description of all the API's endpoints, their parameters, and expected responses.

## What is `openapi.json`?

`openapi.json` is a standard format for describing RESTful APIs. It allows various tools to understand your API without needing to access the source code.

## How to use it in your Frontend Application:

Frontend developers can use this `openapi.json` file with various tools and libraries to:

1.  **Generate API Client Code:** Many tools (e.g., OpenAPI Generator, Swagger Codegen) can automatically generate client-side code (in languages like JavaScript, TypeScript, Python, etc.) based on this specification. This saves time and reduces errors in manually writing API calls.

    *   **Example (using OpenAPI Generator CLI):**
        ```bash
        # Install OpenAPI Generator CLI (if not already installed)
        # npm install @openapitools/openapi-generator-cli -g

        # Generate TypeScript client for Fetch API
        openapi-generator-cli generate -i openapi.json -g typescript-fetch -o ./generated-client
        ```

2.  **Display Interactive API Documentation:** Tools like Swagger UI (which FastAPI uses by default) can render this `openapi.json` file into a beautiful, interactive documentation page.

3.  **Validate API Requests/Responses:** Ensure that your frontend is sending requests and receiving responses that conform to the API contract defined in this file.

4.  **Mock API Server:** Some tools can create a mock API server based on the OpenAPI spec, allowing frontend development to proceed even if the backend is not fully ready.

## API Endpoints Details:

---

### 1. `GET /` (Read Root)

*   **Purpose:** A basic endpoint to check if the API is running.
*   **Request:**
    *   **Method:** `GET`
    *   **Path:** `/`
    *   **Parameters:** None
*   **Response:**
    *   `200 OK`
        ```json
        {
          "message": "Welcome to NeuralStark API!"
        }
        ```

---


### 2. `GET /health` (Health Check)

*   **Purpose:** Verify the health and operational status of the API.
*   **Request:**
    *   **Method:** `GET`
    *   **Path:** `/health`
    *   **Parameters:** None
*   **Response:**
    *   `200 OK`
        ```json
        {
          "status": "ok"
        }
        ```

---


### 3. `POST /chat` (Chat Endpoint)

*   **Purpose:** The primary endpoint for AI chat interactions, leveraging RAG and AI tools.
*   **Request:**
    *   **Method:** `POST`
    *   **Path:** `/chat`
    *   **Content-Type:** `application/json`
    *   **Body (JSON):** `ChatRequest` schema
        ```json
        {
          "query": "string" // The user's question or command for the AI agent.
        }
        ```
        *   **Example Query:** `{"query": "Generate a financial review for Tech Innovations with revenue of $5M and profit of $1M."}`
        *   **Example Query:** `{"query": "How to cook rice?"}`
*   **Response:**
    *   `200 OK`
        ```json
        {
          "response": "string" // The AI agent's answer or tool execution result.
        }
        ```
    *   `422 Unprocessable Entity`: Validation error if `query` is missing or invalid.
    *   `500 Internal Server Error`: For other server-side errors during agent execution.

---


### 4. `GET /documents` (List Documents)

*   **Purpose:** Retrieve a list of all unique documents currently indexed in the knowledge base.
*   **Request:**
    *   **Method:** `GET`
    *   **Path:** `/documents`
    *   **Parameters:** None
*   **Response:**
    *   `200 OK`
        ```json
        {
          "indexed_documents": [
            "string" // Absolute path to an indexed document (e.g., "C:\\Users\\YourUser\\projects\\neuralstark\\neuralstark\\knowledge_base\\internal\\document.pdf")
          ]
        }
        ```
    *   `500 Internal Server Error`: For errors during document retrieval.

---


### 5. `POST /documents/upload` (Upload Document)

*   **Purpose:** Upload a new document to the knowledge base for automatic processing and indexing.
*   **Request:**
    *   **Method:** `POST`
    *   **Path:** `/documents/upload`
    *   **Content-Type:** `multipart/form-data`
    *   **Form Fields:**
        *   `file`: (File) The document file to upload. (Required)
        *   `source_type`: (string) The type of knowledge base to store the document in. Must be `internal` or `external`. (Required)
            *   **Example:** `internal`
    *   **Example Request (using curl):**
        ```bash
        curl -X POST "http://127.0.0.1:8000/documents/upload" \
             -H "accept: application/json" \
             -H "Content-Type: multipart/form-data" \
             -F "file=@/path/to/your/document.pdf;type=application/pdf" \
             -F "source_type=internal"
        ```
*   **Response:**
    *   `200 OK`: Successful upload.
        ```json
        {
          "message": "File uploaded successfully. Processing started.",
          "file_path": "string", // Absolute path where the file was saved.
          "source_type": "string" // The source type (internal/external).
        }
        ```
    *   `400 Bad Request`: If `source_type` is invalid or file is missing.
    *   `500 Internal Server Error`: For other server-side errors.

---


### 6. `GET /documents/content` (Retrieve Document Content)

*   **Purpose:** Get the extracted text content of a specific document from the knowledge base.
*   **Request:**
    *   **Method:** `GET`
    *   **Path:** `/documents/content`
    *   **Query Parameters:**
        *   `file_path`: (string) The absolute path of the document whose content is to be retrieved. (Required)
            *   **Example:** `C:\\Users\\YourUser\\projects\\neuralstark\\neuralstark\\knowledge_base\\internal\\document.pdf`
*   **Response:**
    *   `200 OK`: Successful retrieval.
        ```json
        {
          "file_path": "string",
          "content": "string" // The extracted text content of the document.
        }
        ```
    *   `404 Not Found`: If the `file_path` does not exist.
    *   `500 Internal Server Error`: For parsing errors or other server-side issues.

---


### 7. `DELETE /documents/delete` (Delete Document)

*   **Purpose:** Delete a document from the knowledge base. This will also trigger its removal from the vector store.
*   **Request:**
    *   **Method:** `DELETE`
    *   **Path:** `/documents/delete`
    *   **Query Parameters:**
        *   `file_path`: (string) The absolute path of the document to delete. (Required)
            *   **Example:** `C:\\Users\\YourUser\\projects\\neuralstark\\neuralstark\\knowledge_base\\internal\\document.pdf`
*   **Response:**
    *   `200 OK`: Successful deletion.
        ```json
        {
          "message": "File deletion initiated. It will be removed from the knowledge base."
        }
        ```
    *   `404 Not Found`: If the `file_path` does not exist.
    *   `500 Internal Server Error`: For other server-side errors.

---


For any questions or updates to the API, please refer to the backend development team.
