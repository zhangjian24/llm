import React, { useState, useRef, useEffect } from 'react';
import { useChatStore } from '../../stores/chatStore';
import { ChatMessage } from '../../types';
import MessageBubble from './MessageBubble';
import UploadZone from '../upload/UploadZone';

interface ChatBoxProps {
  className?: string;
}

const ChatBox: React.FC<ChatBoxProps> = ({ className = '' }) => {
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { messages, addMessage, clearMessages } = useChatStore();

  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 发送消息
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString()
    };

    addMessage(userMessage);
    setInputValue('');
    setIsLoading(true);

    try {
      // 这里会调用实际的API
      // 暂时使用模拟响应
      setTimeout(() => {
        const botMessage: ChatMessage = {
          role: 'assistant',
          content: `这是对"${userMessage.content}"的模拟回答。在实际应用中，这里会调用RAG系统的API来获取基于文档的智能回答。`,
          timestamp: new Date().toISOString()
        };
        addMessage(botMessage);
        setIsLoading(false);
      }, 1500);
      
    } catch (error) {
      console.error('发送消息失败:', error);
      setIsLoading(false);
    }
  };

  // 清除对话
  const handleClear = () => {
    clearMessages();
  };

  return (
    <div className={`flex flex-col h-[calc(100vh-200px)] bg-white rounded-lg shadow-lg ${className}`}>
      {/* 头部 */}
      <div className="flex items-center justify-between p-4 border-b">
        <h2 className="text-lg font-semibold text-gray-800">💬 智能问答</h2>
        <div className="flex space-x-2">
          <button
            onClick={() => {/* 打开文档上传 */}}
            className="px-3 py-1 text-sm text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 rounded-md transition-colors"
          >
            上传文档
          </button>
          <button
            onClick={handleClear}
            disabled={messages.length === 0}
            className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed rounded-md transition-colors"
          >
            清除对话
          </button>
        </div>
      </div>

      {/* 消息区域 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <div className="text-6xl mb-4">🤖</div>
            <h3 className="text-xl font-medium mb-2">您好！我是您的文档助手</h3>
            <p className="text-center max-w-md">
              请上传文档或直接提问，我将基于文档内容为您提供准确的回答。
            </p>
            <div className="mt-6 w-full max-w-md">
              <UploadZone />
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <MessageBubble
                key={index}
                message={message}
                isStreaming={isLoading && index === messages.length - 1 && message.role === 'assistant'}
              />
            ))}
            {isLoading && messages[messages.length - 1]?.role !== 'assistant' && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-2xl rounded-bl-none px-4 py-3 max-w-xs">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* 输入区域 */}
      <div className="p-4 border-t">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="请输入您的问题..."
            disabled={isLoading}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            className="px-6 py-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <span className="loading-dots">思考中</span>
            ) : (
              '发送'
            )}
          </button>
        </form>
        <p className="text-xs text-gray-500 mt-2 text-center">
          支持基于上传文档的智能问答
        </p>
      </div>
    </div>
  );
};

export default ChatBox;