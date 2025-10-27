/**
 * API Client для работы с бэкендом
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export interface SessionResponse {
  session_id: string;
  created_at: string;
}

export interface FileMetadata {
  file_id: string;
  original_filename: string;
  file_size: number;
  upload_timestamp: string;
  rows?: number;
  columns?: number;
  column_names?: string[];
}

export interface AgentResponse {
  success: boolean;
  message: string;
  intent?: string;
  data?: any;
  preview?: Array<Record<string, any>>;
  visualization_ids?: string[];
  file_id?: string;
  error?: string;
}

export interface DataPreviewResponse {
  data: Array<Record<string, any>>;
  total_rows: number;
  total_columns: number;
  columns: string[];
}

class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  /**
   * Создать новую сессию
   */
  async createSession(): Promise<SessionResponse> {
    const response = await fetch(`${this.baseURL}/sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    });

    if (!response.ok) {
      throw new Error(`Failed to create session: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Загрузить файл
   */
  async uploadFile(
    sessionId: string,
    file: File
  ): Promise<{ success: boolean; file_id: string; metadata: FileMetadata }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseURL}/upload?session_id=${sessionId}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to upload file');
    }

    return response.json();
  }

  /**
   * Отправить сообщение в чат
   */
  async sendMessage(sessionId: string, message: string): Promise<AgentResponse> {
    const response = await fetch(`${this.baseURL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        message: message,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to send message');
    }

    return response.json();
  }

  /**
   * Получить preview данных
   */
  async getPreview(sessionId: string, rows: number = 10): Promise<DataPreviewResponse> {
    const response = await fetch(`${this.baseURL}/preview/${sessionId}?rows=${rows}`);

    if (!response.ok) {
      throw new Error('Failed to get preview');
    }

    return response.json();
  }

  /**
   * Получить URL для скачивания файла
   */
  getDownloadURL(filename: string): string {
    return `${this.baseURL}/download/${filename}`;
  }

  /**
   * Получить URL визуализации
   */
  getVisualizationURL(sessionId: string, vizId: string): string {
    return `${this.baseURL}/visualizations/${sessionId}/${vizId}`;
  }

  /**
   * Удалить сессию
   */
  async deleteSession(sessionId: string): Promise<void> {
    const response = await fetch(`${this.baseURL}/sessions/${sessionId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Failed to delete session');
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseURL}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}

export const apiClient = new APIClient();
