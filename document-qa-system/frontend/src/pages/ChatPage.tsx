import React from 'react';
import { ChatMessages } from '../components/chat/ChatMessages';
import { ChatInput } from '../components/chat/ChatInput';
import { ConversationSidebar } from '../components/chat/ConversationSidebar';
import { useChatStore } from '../stores/chatStore';

export const ChatPage: React.FC = () => {
  return (
    <div className="flex flex-1 h-full overflow-hidden bg-gray-50 dark:bg-gray-900">
      {/* 对话侧边栏 */}
      <ConversationSidebar />
      
      {/* 主内容区 */}
      <main className="flex-1 flex flex-col min-w-0 min-h-0">
        <header className="bg-white dark:bg-slate-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center gap-4 shrink-0">
          {/* 展开侧边栏按钮（在侧边栏收起时显示） */}
          <SidebarToggle />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">智能问答</h2>
        </header>
        <div className="flex-1 flex flex-col relative min-h-0">
          <ChatMessages />
          {/* 加载状态覆盖层 */}
          {useChatStore.getState().isLoading && (
            <div className="absolute inset-0 bg-black bg-opacity-10 flex items-center justify-center z-10">
              <div className="bg-white dark:bg-slate-800 rounded-lg p-4 shadow-lg flex items-center space-x-3">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500"></div>
                <span className="text-gray-700 dark:text-gray-300">正在思考中...</span>
              </div>
            </div>
          )}
          <ChatInput />
        </div>
      </main>
    </div>
  );
};

// 侧边栏切换按钮组件
const SidebarToggle: React.FC = () => {
  const { isSidebarOpen, toggleSidebar } = useChatStore();
  
  if (isSidebarOpen) return null;
  
  return (
    <button
      onClick={toggleSidebar}
      className="
        p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700
        text-gray-600 dark:text-gray-400
        transition-colors
      "
      title="展开侧边栏"
    >
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    </button>
  );
};
