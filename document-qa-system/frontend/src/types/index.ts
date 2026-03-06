// 文档相关类型
export interface Document {
  id: string;
  filename: string;
  file_size: number;
  mime_type: string;
  status: 'processing' | 'ready' | 'failed';
  chunks_count?: number;
  created_at: string;
  updated_at: string;
}

export interface DocumentUploadResponse {
  code: number;
  message: string;
  data: Document;
}

export interface DocumentListResponse {
  code: number;
  message: string;
  data: {
    total: number;
    items: Document[];
    page: number;
    limit: number;
    total_pages: number;
  };
}

// 对话相关类型
export interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{
    chunk_id: string;
    relevance_score: number;
  }>;
  created_at?: string;
}

export interface Conversation {
  id: string;
  title: string;
  last_message?: string;
  turns: number;
  updated_at: string;
}

export interface ChatQuery {
  query: string;
  top_k?: number;
  stream?: boolean;
  conversation_id?: string;
}

export interface ChatTokenResponse {
  token?: string;
  done?: boolean;
  conversation_id?: string;
  error?: string;
}

export interface ChatResponse {
  code: number;
  message: string;
  data: {
    answer: string;
    conversation_id: string;
  };
}

// 通用类型
export interface APIResponse<T> {
  code: number;
  message: string;
  data: T;
}
