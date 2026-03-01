import axios from 'axios';
import { 
  DocumentUploadResponse, 
  QueryRequest, 
  QueryResponse, 
  DocumentListResponse,
  HealthCheckResponse 
} from '../types';

const API_BASE_URL = '/api';

// 获取API密钥（可以从环境变量或用户设置中获取）
const getApiKey = (): string => {
  // 在实际应用中，这里应该从安全的地方获取API密钥
  // 例如：localStorage、环境变量或用户登录后的token
  return localStorage.getItem('api_key') || 'YOUR_DEFAULT_API_KEY';
};

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,  // 60秒超时，适应文档处理和嵌入生成
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 添加Bearer Token认证
    const apiKey = getApiKey();
    if (apiKey && apiKey !== 'YOUR_DEFAULT_API_KEY') {
      config.headers.Authorization = `Bearer ${apiKey}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API请求错误:', error);
    throw error;
  }
);

// 文档相关API
export const documentApi = {
  // 上传文档
  uploadDocument: async (file: File): Promise<DocumentUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response;
  },

  // 获取文档列表
  getDocuments: async (): Promise<DocumentListResponse> => {
    const response = await apiClient.get('/documents/list');
    return response;
  },

  // 删除文档
  deleteDocument: async (documentId: string): Promise<void> => {
    await apiClient.delete(`/documents/${documentId}`);
  },

  // 获取文档详情
  getDocumentInfo: async (documentId: string): Promise<any> => {
    const response = await apiClient.get(`/documents/${documentId}/info`);
    return response;
  }
};

// 聊天相关API
export const chatApi = {
  // 查询文档
  queryDocuments: async (request: QueryRequest): Promise<QueryResponse> => {
    const response = await apiClient.post('/chat/query', request);
    return response;
  },

  // 对话聊天
  chatConversation: async (request: QueryRequest): Promise<any> => {
    const response = await apiClient.post('/chat/chat', request);
    return response;
  },

  // 获取查询建议
  getQuerySuggestions: async (documentIds?: string[]): Promise<{suggestions: string[]}> => {
    const params = documentIds ? { document_ids: documentIds.join(',') } : {};
    const response = await apiClient.get('/chat/suggestions', { params });
    return response;
  }
};

// 健康检查API
export const healthApi = {
  // 健康检查
  checkHealth: async (): Promise<HealthCheckResponse> => {
    const response = await apiClient.get('/health');
    return response;
  },

  // 获取版本信息
  getVersion: async (): Promise<any> => {
    const response = await apiClient.get('/version');
    return response;
  },

  // 获取系统统计
  getStats: async (): Promise<any> => {
    const response = await apiClient.get('/stats');
    return response;
  }
};

// 嵌入相关API
export const embeddingApi = {
  // 创建文本嵌入
  createEmbeddings: async (texts: string[]): Promise<any> => {
    const response = await apiClient.post('/embeddings', {
      input: texts,
      model: 'text-embedding-v4'
    });
    return response;
  },

  // 为查询创建嵌入
  createQueryEmbedding: async (query: string): Promise<any> => {
    const response = await apiClient.post('/embeddings/query', {
      query
    });
    return response;
  },

  // 获取可用模型列表
  getModels: async (): Promise<any> => {
    const response = await apiClient.get('/embeddings/models');
    return response;
  }
};

// 重排序相关API
export const rerankApi = {
  // 文档重排序
  rerankDocuments: async (query: string, documents: any[], topN: number = 10): Promise<any> => {
    const response = await apiClient.post('/rerank', {
      model: 'rerank-v3',
      query,
      documents,
      top_n: topN
    });
    return response;
  },

  // 批量重排序
  batchRerank: async (requests: any[]): Promise<any> => {
    const response = await apiClient.post('/rerank/batch', requests);
    return response;
  },

  // 获取重排序模型列表
  getModels: async (): Promise<any> => {
    const response = await apiClient.get('/rerank/models');
    return response;
  }
};

export default apiClient;