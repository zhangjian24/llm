/**
 * API服务层
 * 封装所有后端API调用
 */

import {
  QueryRequest,
  QueryResponse,
  DocumentUploadResponse,
  DocumentListResponse,
  HealthCheckResponse,
  StreamChunk
} from '../types';

const API_BASE_URL = '/api';

// API错误处理
class ApiError extends Error {
  constructor(
    public status: number,
    public message: string,
    public details?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// 基础请求配置
const request = async <T>(
  url: string,
  options: RequestInit = {}
): Promise<T> => {
  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(`${API_BASE_URL}${url}`, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        response.status,
        errorData.message || `请求失败: ${response.status}`,
        errorData
      );
    }
    
    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, '网络请求失败', error);
  }
};

// 文件上传请求
const uploadRequest = async <T>(
  url: string,
  formData: FormData
): Promise<T> => {
  try {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        response.status,
        errorData.message || `上传失败: ${response.status}`,
        errorData
      );
    }
    
    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, '文件上传失败', error);
  }
};

// 聊天相关API
export const chatApi = {
  // 同步查询
  query: async (data: QueryRequest): Promise<QueryResponse> => {
    return request('/chat/query', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // 流式查询
  streamQuery: async (
    data: QueryRequest,
    onChunk: (chunk: StreamChunk) => void,
    onError?: (error: Error) => void
  ): Promise<void> => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ...data, stream: true }),
      });

      if (!response.ok) {
        throw new ApiError(response.status, '流式请求失败');
      }

      if (!response.body) {
        throw new Error('响应体为空');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      try {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) break;
          
          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') {
                return;
              }
              
              try {
                const parsedData = JSON.parse(data);
                onChunk(parsedData);
              } catch (parseError) {
                console.warn('解析流数据失败:', parseError);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }
    } catch (error) {
      if (error instanceof ApiError) {
        onError?.(error);
      } else {
        onError?.(new Error(`流式请求失败: ${error}`));
      }
    }
  },

  // 获取对话历史
  getHistory: async (conversationId: string) => {
    return request(`/chat/history/${conversationId}`);
  },

  // 清除对话历史
  clearHistory: async (conversationId: string) => {
    return request(`/chat/history/${conversationId}`, {
      method: 'DELETE',
    });
  },

  // 测试连接
  testConnection: async () => {
    return request('/chat/test');
  }
};

// 文档相关API
export const documentApi = {
  // 上传文档
  upload: async (file: File): Promise<DocumentUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    return uploadRequest('/documents/upload', formData);
  },

  // 获取文档列表
  list: async (): Promise<DocumentListResponse> => {
    return request('/documents');
  },

  // 删除文档
  delete: async (docId: string) => {
    return request(`/documents/${docId}`, {
      method: 'DELETE',
    });
  },

  // 获取文档信息
  getInfo: async (docId: string) => {
    return request(`/documents/${docId}/info`);
  }
};

// 健康检查API
export const healthApi = {
  check: async (): Promise<HealthCheckResponse> => {
    return request('/health');
  },

  ready: async () => {
    return request('/health/ready');
  },

  live: async () => {
    return request('/health/live');
  }
};

// 默认导出所有API
export default {
  chat: chatApi,
  documents: documentApi,
  health: healthApi
};