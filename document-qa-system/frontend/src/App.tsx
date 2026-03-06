import React, { useState } from 'react';
import { ChatMessages } from './components/chat/ChatMessages';
import { ChatInput } from './components/chat/ChatInput';
import { DocumentUpload } from './components/documents/DocumentUpload';
import { useDocumentStore } from './stores/documentStore';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'chat' | 'documents'>('chat');
  const { documents } = useDocumentStore();

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
            <div className="flex-1 flex flex-col">
              <ChatMessages />
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
                  <h3 className="text-sm font-medium text-gray-700 mb-3">
                    已上传文档
                  </h3>
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
