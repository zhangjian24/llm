import React from 'react';
import { useChatStore } from '../../stores/chatStore';
import type { Message } from '../../types';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-blue-500 text-white'
            : 'bg-gray-100 text-gray-900'
        }`}
      >
        <div className="text-sm font-medium mb-1">
          {isUser ? '我' : '助手'}
        </div>
        <div className="whitespace-pre-wrap">{message.content}</div>
        
        {message.sources && message.sources.length > 0 && (
          <div className="mt-2 text-xs opacity-75">
            引用来源：{message.sources.length} 个文档片段
          </div>
        )}
      </div>
    </div>
  );
};
