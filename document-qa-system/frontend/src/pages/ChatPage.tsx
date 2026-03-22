import React from 'react';
import { ChatMessages } from '../components/chat/ChatMessages';
import { ChatInput } from '../components/chat/ChatInput';
import { useChatStore } from '../stores/chatStore';

export const ChatPage: React.FC = () => {
  return (
    <div className="flex-1 flex flex-col h-full">
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
    </div>
  );
};
