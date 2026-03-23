import React, { useEffect, useState } from 'react';
import { useChatStore } from '../../stores/chatStore';
import { ConversationItem } from './ConversationItem';

export const ConversationSidebar: React.FC = () => {
  const {
    conversations,
    isSidebarOpen,
    isLoadingConversations,
    currentConversationId,
    fetchConversations,
    selectConversation,
    createNewConversation,
    deleteConversation,
    toggleSidebar,
  } = useChatStore();

  const [showConfirmClear, setShowConfirmClear] = useState(false);

  // 组件挂载时加载对话列表
  useEffect(() => {
    fetchConversations();
    // 每 30 秒刷新一次列表
    const interval = setInterval(fetchConversations, 30000);
    return () => clearInterval(interval);
  }, [fetchConversations]);

  const handleNewConversation = () => {
    createNewConversation();
    // 在移动端自动关闭侧边栏
    if (window.innerWidth < 768) {
      toggleSidebar();
    }
  };

  const handleClearAll = () => {
    if (showConfirmClear) {
      // 执行清空操作
      conversations.forEach((conv) => {
        deleteConversation(conv.id);
      });
      setShowConfirmClear(false);
    } else {
      setShowConfirmClear(true);
      // 3 秒后自动取消确认状态
      setTimeout(() => setShowConfirmClear(false), 3000);
    }
  };

  return (
    <>
      {/* 移动端遮罩层 */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={toggleSidebar}
        />
      )}

      {/* 侧边栏 */}
      <aside
        className={`
          fixed md:static inset-y-0 left-0 z-50
          bg-slate-50 dark:bg-slate-900
          border-r border-gray-200 dark:border-gray-700
          transition-all duration-300 ease-in-out
          flex flex-col
          ${isSidebarOpen ? 'w-72 translate-x-0' : 'w-0 -translate-x-full md:w-0 md:translate-x-0 overflow-hidden'}
        `}
      >
        {/* Header */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
            对话历史
          </h2>
          <button
            onClick={toggleSidebar}
            className="md:hidden p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
          >
            <svg className="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* 新建对话按钮 */}
        <div className="p-3">
          <button
            onClick={handleNewConversation}
            className="
              w-full flex items-center justify-center gap-2
              px-4 py-2 rounded-lg
              bg-blue-600 hover:bg-blue-700
              text-white font-medium
              transition-colors duration-200
              shadow-sm hover:shadow
            "
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            新建对话
          </button>
        </div>

        {/* 对话列表 */}
        <div className="flex-1 overflow-y-auto px-2 py-2 space-y-1">
          {isLoadingConversations ? (
            // 加载状态
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            </div>
          ) : conversations.length === 0 ? (
            // 空状态
            <div className="text-center py-8 px-4">
              <svg className="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                还没有对话记录
              </p>
              <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                点击上方按钮开始新对话
              </p>
            </div>
          ) : (
            // 对话列表
            conversations.map((conversation) => (
              <ConversationItem
                key={conversation.id}
                conversation={conversation}
                isActive={conversation.id === currentConversationId}
                onClick={() => {
                  selectConversation(conversation.id);
                  // 在移动端自动关闭侧边栏
                  if (window.innerWidth < 768) {
                    toggleSidebar();
                  }
                }}
                onDelete={() => deleteConversation(conversation.id)}
              />
            ))
          )}
        </div>

        {/* Footer - 清空全部按钮 */}
        {conversations.length > 0 && (
          <div className="p-3 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={handleClearAll}
              className={`
                w-full flex items-center justify-center gap-2
                px-4 py-2 rounded-lg text-sm font-medium
                transition-colors duration-200
                ${showConfirmClear 
                  ? 'bg-red-100 text-red-600 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-400' 
                  : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
                }
              `}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              {showConfirmClear ? '再次点击确认清空' : '清空全部对话'}
            </button>
          </div>
        )}
      </aside>

      {/* 展开侧边栏按钮（当侧边栏收起时显示） */}
      {!isSidebarOpen && (
        <button
          onClick={toggleSidebar}
          className="
            fixed left-4 top-4 z-30
            p-2 rounded-lg
            bg-white dark:bg-slate-800
            shadow-md hover:shadow-lg
            border border-gray-200 dark:border-gray-700
            text-gray-600 dark:text-gray-300
            transition-all duration-200
            md:static md:mr-4
          "
          title="展开侧边栏"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      )}
    </>
  );
};
