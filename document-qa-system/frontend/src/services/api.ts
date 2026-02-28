import axios from 'axios';
import { 
  DocumentUploadResponse, 
  QueryRequest, 
  QueryResponse, 
  DocumentListResponse,
  HealthCheckResponse 
} from '../types';

const API_BASE_URL = '/api';

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
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

export default apiClient;