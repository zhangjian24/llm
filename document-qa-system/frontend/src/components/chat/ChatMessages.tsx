import React, { useRef, useEffect } from 'react';
import { useChatStore } from '../../stores/chatStore';
import { ChatMessage } from './ChatMessage';

export const ChatMessages: React.FC = () => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { messages } = useChatStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400">
        <div className="text-center">
          <div className="text-6xl mb-4">💬</div>
          <div className="text-lg">开始对话吧！</div>
          <div className="text-sm mt-2">提问任何关于文档的问题</div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4">
      {messages.map((msg, idx) => (
        <ChatMessage key={idx} message={msg} />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};
