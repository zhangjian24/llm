/**
 * 前端类型定义
 */

export interface DocumentMetadata {
  doc_id: string;
  filename: string;
  file_size: number;
  content_type: string;
  upload_time: string;
  chunk_count: number;
}

export interface SearchResult {
  content: string;
  metadata: Record<string, any>;
  score: number;
  doc_id: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: SearchResult[];
}

export interface QueryRequest {
  query: string;
  conversation_id?: string;
  stream?: boolean;
}

export interface QueryResponse {
  answer: string;
  sources: SearchResult[];
  conversation_id: string;
  processing_time: number;
}

export interface StreamChunk {
  type: 'answer' | 'sources' | 'status' | 'error' | 'end';
  content?: string;
  sources?: SearchResult[];
  done: boolean;
}

export interface DocumentUploadResponse {
  doc_id: string;
  filename: string;
  status: string;
  message: string;
}

export interface DocumentListResponse {
  documents: DocumentMetadata[];
  total_count: number;
}

export interface HealthCheckResponse {
  status: string;
  timestamp: string;
  version: string;
  services: Record<string, string>;
}

// 组件Props类型
export interface ChatBoxProps {
  className?: string;
}

export interface MessageBubbleProps {
  message: ChatMessage;
  isStreaming?: boolean;
}

export interface UploadZoneProps {
  onUploadComplete?: (response: DocumentUploadResponse) => void;
}

export interface SourcesDisplayProps {
  sources: SearchResult[];
  isOpen: boolean;
  onClose: () => void;
}