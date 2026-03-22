import axios from 'axios';
import type { 
  Document, 
  DocumentUploadResponse, 
  DocumentListResponse,
  ChatQuery,
  ChatResponse,
  Conversation
} from '../types';

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 60000,
});

// 文档管理 API
export const documentAPI = {
  upload: async (file: File): Promise<DocumentUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post<DocumentUploadResponse>(
      '/documents/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        params: {
          mime_type: file.type,
          filename: file.name,
        },
      }
    );
    
    return response.data;
  },

  getList: async (page = 1, limit = 20, status?: string): Promise<DocumentListResponse> => {
    const response = await api.get<DocumentListResponse>('/documents', {
      params: { page, limit, status },
    });
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/documents/${id}`);
  },

  reprocess: async (id: string): Promise<void> => {
    await api.post(`/documents/${id}/reprocess`);
  },
};

// 对话聊天 API
export const chatAPI = {
  chat: async (query: ChatQuery): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/chat', query);
    return response.data;
  },

  chatStream: async (
    query: ChatQuery,
    onToken: (token: string) => void,
    onComplete: (conversationId: string) => void,
    onError: (error: string) => void
  ): Promise<void> => {
    const response = await fetch('/api/v1/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ ...query, stream: true }),
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const reader = response.body?.getReader();
    if (!reader) return;

    const decoder = new TextDecoder();

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            
            if (data.token) {
              onToken(data.token);
            }
            
            if (data.done) {
              onComplete(data.conversation_id);
            }
            
            if (data.error) {
              onError(data.error);
            }
          }
        }
      }
    } catch (error) {
      if (error instanceof Error) {
        onError(error.message);
      }
    }
  },

  getConversations: async (limit = 10): Promise<Conversation[]> => {
    const response = await api.get<{ code: number; data: Conversation[] }>('/chat/conversations', {
      params: { limit },
    });
    return response.data.data;
  },

  deleteConversation: async (id: string): Promise<void> => {
    await api.delete(`/chat/conversations/${id}`);
  },
};
