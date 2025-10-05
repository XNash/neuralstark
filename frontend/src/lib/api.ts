const API_BASE_URL = '/api';

export interface ChatRequest {
  query: string;
}

export interface ChatResponse {
  response: string | { canvas: any };
}

export interface DocumentsResponse {
  indexed_documents: string[];
}

export interface HealthResponse {
  status: string;
}

export interface UploadDocumentResponse {
  message: string;
  file_path: string;
  source_type: string;
}

export interface DocumentContentResponse {
  file_path: string;
  content: string;
}

export interface DeleteDocumentResponse {
  message: string;
}

export interface ResetKnowledgeBaseResponse {
  message: string;
}

export interface DeleteRequest {
  file_path: string;
}

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async chat(query: string): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || errorData.error || `Chat API error: ${response.statusText}`);
    }

    return response.json();
  }

  async getDocuments(): Promise<DocumentsResponse> {
    const response = await fetch(`${this.baseUrl}/documents`);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || errorData.error || `Documents API error: ${response.statusText}`);
    }

    const data = await response.json();
    
    // Ensure the response has the expected structure
    if (typeof data !== 'object' || !Array.isArray(data.indexed_documents)) {
      console.warn('Unexpected API response structure:', data);
      return { indexed_documents: [] };
    }

    return data;
  }

  async healthCheck(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/health`);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || errorData.error || `Health check error: ${response.statusText}`);
    }

    return response.json();
  }

  async uploadDocument(file: File, sourceType: 'internal' | 'external'): Promise<UploadDocumentResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('source_type', sourceType);

    const response = await fetch(`${this.baseUrl}/documents/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || errorData.error || `Upload API error: ${response.statusText}`);
    }

    return response.json();
  }

  async getDocumentContent(filePath: string): Promise<DocumentContentResponse> {
    const params = new URLSearchParams({ file_path: filePath });
    const response = await fetch(`${this.baseUrl}/documents/content?${params.toString()}`);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || errorData.error || `Get Document Content API error: ${response.statusText}`);
    }

    return response.json();
  }

  async deleteDocument(filePath: string): Promise<DeleteDocumentResponse> {
    const response = await fetch(`${this.baseUrl}/documents/delete`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ file_path: filePath }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || errorData.error || `Delete Document API error: ${response.statusText}`);
    }

    return response.json();
  }

  async resetKnowledgeBase(resetType: 'hard' | 'soft'): Promise<ResetKnowledgeBaseResponse> {
    const response = await fetch(`${this.baseUrl}/knowledge_base/reset?reset_type=${resetType}`, {
      method: 'POST',
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || errorData.error || `Reset Knowledge Base API error: ${response.statusText}`);
    }

    return response.json();
  }
}

export const apiClient = new ApiClient();