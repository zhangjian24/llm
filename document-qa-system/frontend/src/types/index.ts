export interface Document {
  document_id: string;
  filename: string;
  upload_time: string;
  status: string;
  size: number;
}

export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  status: string;
  message: string;
}

export interface QueryRequest {
  query: string;
  document_ids?: string[];
  top_k?: number;
}

export interface Source {
  document_id: string;
  filename: string;
  score: number;
  chunk_count: number;
}

export interface QueryResponse {
  query: string;
  answer: string;
  sources: Source[];
  confidence: number;
}

export interface DocumentListResponse {
  documents: Document[];
  total: number;
}

export interface HealthCheckResponse {
  status: string;
  timestamp: string;
  services: Record<string, string>;
}