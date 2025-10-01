const API_BASE_URL = '/api';

export interface ChatRequest {
  query: string;
  template_id?: string | null;
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

export interface SttResponse {
  text: string;
}

export interface Personality {
  name: string;
  description: string;
}

export interface GetPersonalitiesResponse {
  available_personalities: { [key: string]: Personality };
  current_personality: string;
}

export interface SetPersonalityRequest {
  personality_key: string;
}

export interface SetPersonalityResponse {
  message: string;
  current_personality: string;
}

export interface CanvasTemplate {
  [key: string]: any;
}

export interface GetCanvasTemplatesResponse {
  default_templates: { [key: string]: CanvasTemplate };
  user_templates: { [key: string]: CanvasTemplate };
}

export interface SaveCanvasTemplateRequest {
  template_id: string;
  template_data: CanvasTemplate;
}

export interface SaveCanvasTemplateResponse {
  message: string;
}

export interface ScheduledReport {
  name: string;
  tool_name: string;
  tool_input: any;
  interval_minutes: number;
  last_run: string | null;
}

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async chat(query: string, templateId: string | null = null, advancedFilters: any = {}): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query, template_id: templateId, ...advancedFilters }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || errorData.error || `Chat API error: ${response.statusText}`);
    }

    return response.json();
  }

  async stt(formData: FormData): Promise<SttResponse> {
    const response = await fetch(`${this.baseUrl}/stt`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || errorData.error || `STT API error: ${response.statusText}`);
    }

    return response.json();
  }

  async getPersonalities(): Promise<GetPersonalitiesResponse> {
    const response = await fetch(`${this.baseUrl}/personalities`);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || errorData.error || `Get Personalities API error: ${response.statusText}`);
    }

    return response.json();
  }

  async setPersonality(personalityKey: string): Promise<SetPersonalityResponse> {
    const response = await fetch(`${this.baseUrl}/personalities`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ personality_key: personalityKey }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || errorData.error || `Set Personality API error: ${response.statusText}`);
    }

    return response.json();
  }

  async getCanvasTemplates(): Promise<GetCanvasTemplatesResponse> {
    const response = await fetch(`${this.baseUrl}/canvas_templates`);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || errorData.error || `Get Canvas Templates API error: ${response.statusText}`);
    }

    return response.json();
  }

  async saveCanvasTemplate(templateId: string, templateData: CanvasTemplate): Promise<SaveCanvasTemplateResponse> {
    const response = await fetch(`${this.baseUrl}/canvas_templates`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ template_id: templateId, template_data: templateData }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || errorData.error || `Save Canvas Template API error: ${response.statusText}`);
    }

    return response.json();
  }

  async getDocuments(): Promise<DocumentsResponse> {
    const response = await fetch(`${this.baseUrl}/documents`);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || errorData.error || `Documents API error: ${response.statusText}`);
    }

    return response.json();
  }

  async healthCheck(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/health`);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || errorData.error || `Health check error: ${response.statusText}`);
    }

    return response.json();
  }

  async uploadDocument(file: File, sourceType: 'internal' | 'external', tags: string | null = null): Promise<UploadDocumentResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('source_type', sourceType);
    if (tags) {
        formData.append('tags', tags);
    }

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

  async getScheduledReports(): Promise<ScheduledReport[]> {
    const response = await fetch(`${this.baseUrl}/scheduled_reports`);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || errorData.error || `Get Scheduled Reports API error: ${response.statusText}`);
    }

    return response.json();
  }

  async createScheduledReport(report: Omit<ScheduledReport, 'last_run'>): Promise<any> {
    const response = await fetch(`${this.baseUrl}/scheduled_reports`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(report),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || errorData.error || `Create Scheduled Report API error: ${response.statusText}`);
    }

    return response.json();
  }
}

export const apiClient = new ApiClient();