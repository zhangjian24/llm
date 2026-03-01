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

// 嵌入相关类型
export interface EmbeddingRequest {
  input: string[];
  model: string;
}

export interface TextEmbedding {
  object: string;
  embedding: number[];
  index: number;
}

export interface EmbeddingResponse {
  object: string;
  data: TextEmbedding[];
  model: string;
  usage: Record<string, number>;
}

export interface QueryEmbeddingRequest {
  query: string;
}

// 重排序相关类型
export interface RerankRequest {
  model: string;
  query: string;
  documents: any[];
  top_n?: number;
}

export interface RerankResult {
  index: number;
  document: string;
  relevance_score: number;
  document_id: string;
}

export interface RerankResponse {
  id: string;
  results: RerankResult[];
  usage: Record<string, number>;
}

// API密钥配置类型
export interface ApiConfig {
  apiKey: string;
  apiUrl: string;
  modelName: string;
}