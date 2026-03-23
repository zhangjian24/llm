import React, { useEffect } from 'react';
import { useDocumentStore } from './stores/documentStore';
import { documentAPI } from './services/api';
import { useWebSocket } from './hooks/useWebSocket';

// App 组件 - 负责全局数据加载和 WebSocket 连接
const App: React.FC = () => {
  const { setDocuments, setError } = useDocumentStore();
  
  // 📡 初始化 WebSocket 连接
  useWebSocket('ws://localhost:8000/ws');
  
  // 提取文档加载逻辑为独立函数
  const loadDocuments = async () => {
    try {
      const response = await documentAPI.getList(1, 100);
      setDocuments(response.data.items, response.data.total);
    } catch (error) {
      console.error('Failed to load documents:', error);
      setError(error instanceof Error ? error.message : '加载文档失败');
    }
  };

  // 应用启动时加载文档数据
  useEffect(() => {
    loadDocuments();
  }, []);

  // 这个组件不渲染任何 UI，只负责后台数据加载
  return null;
};

export default App;
