import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Outlet, useLocation, Link } from 'react-router-dom'
import App from './App'
import { DocumentsPage } from './pages/DocumentsPage'
import { ChatPage } from './pages/ChatPage'
import { useDocumentStore } from './stores/documentStore'
import './index.css'

// 导航组件
const Navigation: React.FC = () => {
  const location = useLocation();
  const { total } = useDocumentStore();
  const activeTab = location.pathname === '/documents' ? 'documents' : 'chat';
  
  return (
    <nav className="flex-1 p-4">
      <Link
        to="/chat"
        className={`block px-4 py-2 rounded-lg mb-2 transition-colors ${
          activeTab === 'chat'
            ? 'bg-blue-50 text-blue-600'
            : 'text-gray-700 hover:bg-gray-100'
        }`}
      >
        💬 对话
      </Link>
      <Link
        to="/documents"
        className={`block px-4 py-2 rounded-lg transition-colors ${
          activeTab === 'documents'
            ? 'bg-blue-50 text-blue-600'
            : 'text-gray-700 hover:bg-gray-100'
        }`}
      >
        📄 文档 ({total})
      </Link>
    </nav>
  );
};

// 创建一个包含侧边栏的布局组件
const Layout: React.FC = () => {
  return (
    <div className="flex h-screen bg-gray-50">
      {/* 侧边栏 */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">RAG 文档问答</h1>
        </div>

        <Navigation />

        <div className="p-4 border-t border-gray-200 text-xs text-gray-500">
          v1.0.0
        </div>
      </aside>

      {/* 主内容区 - 路由将渲染到这里 */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <Outlet />
      </main>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {/* App 组件负责全局数据加载和 WebSocket 连接 */}
    <App />
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<ChatPage />} />
          <Route path="documents" element={<DocumentsPage />} />
          <Route path="chat" element={<ChatPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
)
