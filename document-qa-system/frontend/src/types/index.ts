export interface Document {
  id: string;
  filename: string;
  content_type: string;
  size: number;
  status: 'uploaded' | 'processing' | 'processed' | 'failed';
  created_at: string;
  processed_at?: string;
  chunk_count?: number;
  total_tokens?: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Source[];
}

export interface Source {
  document_id: string;
  filename: string;
  content: string;
  score: number;
}

export interface ChatRequest {
  query: string;
  document_ids?: string[];
  history?: Array<{
    role: string;
    content: string;
    timestamp: string;
  }>;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
  confidence: number;
}

export interface SearchResult {
  document_id: string;
  content: string;
  score: number;
  metadata: Record<string, any>;
}

export interface QuerySuggestion {
  suggestions: string[];
}

export interface DocumentStats {
  document: Document;
  vector_stats: Record<string, any>;
}

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}