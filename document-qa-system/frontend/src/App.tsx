import React, { useState, useEffect } from 'react';
import { ChatMessages } from './components/chat/ChatMessages';
import { ChatInput } from './components/chat/ChatInput';
import { DocumentUpload } from './components/documents/DocumentUpload';
import { useDocumentStore } from './stores/documentStore';
import { useChatStore } from './stores/chatStore';
import { documentAPI } from './services/api';
import { useWebSocket } from './hooks/useWebSocket';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'chat' | 'documents'>('chat');
  const { documents, setDocuments, setError } = useDocumentStore();
  
  // 📡 初始化 WebSocket 连接
  const { isConnected } = useWebSocket('ws://localhost:8000/ws');
  
  // 添加连接状态文本
  const getConnectionStatusText = () => {
    if (isConnected) return '🟢 实时连接';
    return '🔴 连接断开';
  };
  
  const getConnectionStatusClass = () => {
    return isConnected ? 'text-green-600' : 'text-red-600';
  };
  
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

  // 当切换到文档标签页时重新加载（保持数据新鲜度）
  useEffect(() => {
    if (activeTab === 'documents') {
      loadDocuments();
    }
  }, [activeTab]);

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 侧边栏 */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">RAG 文档问答</h1>
        </div>

        <nav className="flex-1 p-4">
          <button
            onClick={() => setActiveTab('chat')}
            className={`w-full text-left px-4 py-2 rounded-lg mb-2 transition-colors ${
              activeTab === 'chat'
                ? 'bg-blue-50 text-blue-600'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            💬 对话
          </button>
          <button
            onClick={() => setActiveTab('documents')}
            className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'documents'
                ? 'bg-blue-50 text-blue-600'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            📄 文档 ({documents.length})
          </button>
        </nav>

        <div className="p-4 border-t border-gray-200 text-xs text-gray-500">
          v1.0.0
        </div>
      </aside>

      {/* 主内容区 */}
      <main className="flex-1 flex flex-col">
        {activeTab === 'chat' ? (
          <>
            <header className="bg-white border-b border-gray-200 px-6 py-4">
              <h2 className="text-lg font-semibold text-gray-900">智能问答</h2>
            </header>
            <div className="flex-1 flex flex-col relative">
              <ChatMessages />
              {/* 加载状态覆盖层 */}
              {useChatStore.getState().isLoading && (
                <div className="absolute inset-0 bg-black bg-opacity-10 flex items-center justify-center z-10">
                  <div className="bg-white rounded-lg p-4 shadow-lg flex items-center space-x-3">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500"></div>
                    <span className="text-gray-700">正在思考中...</span>
                  </div>
                </div>
              )}
              <ChatInput />
            </div>
          </>
        ) : (
          <>
            <header className="bg-white border-b border-gray-200 px-6 py-4">
              <h2 className="text-lg font-semibold text-gray-900">文档管理</h2>
            </header>
            <div className="flex-1 overflow-y-auto p-6">
              <DocumentUpload />
              
              {documents.length > 0 && (
                <div className="mt-6">
                  <div className="flex justify-between items-center mb-3">
                    <h3 className="text-sm font-medium text-gray-700">
                      已上传文档
                    </h3>
                    <div className="flex items-center space-x-2">
                      {/* WebSocket 连接状态指示器 */}
                      <div className={`flex items-center ${getConnectionStatusClass()}`}>
                        <div className={`w-2 h-2 rounded-full mr-1 ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
                        <span className="text-xs font-medium">
                          {getConnectionStatusText()}
                        </span>
                      </div>
                      <span className="text-xs text-gray-500">
                        共 {documents.length} 个
                      </span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    {documents.map((doc) => (
                      <div
                        key={doc.id}
                        className="bg-white rounded-lg border border-gray-200 p-4 flex items-center justify-between"
                      >
                        <div>
                          <div className="font-medium text-gray-900">
                            {doc.filename}
                          </div>
                          <div className="text-sm text-gray-500">
                            {(doc.file_size / 1024).toFixed(2)} KB •{' '}
                            {doc.status === 'ready' ? '✅ 就绪' : '⏳ 处理中'}
                          </div>
                        </div>
                        <div className="text-xs text-gray-400">
                          {new Date(doc.created_at).toLocaleString('zh-CN')}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  );
};

export default App;
