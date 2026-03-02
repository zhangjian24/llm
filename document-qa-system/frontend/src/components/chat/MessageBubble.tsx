import React from 'react';
import { ChatMessage } from '../../types';

interface MessageBubbleProps {
  message: ChatMessage;
  isStreaming?: boolean;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ 
  message, 
  isStreaming = false 
}) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-xs md:max-w-md lg:max-w-lg xl:max-w-xl ${
        isUser 
          ? 'bg-blue-600 text-white rounded-2xl rounded-br-none' 
          : 'bg-gray-100 text-gray-800 rounded-2xl rounded-bl-none'
      } px-4 py-3`}>
        {isStreaming ? (
          <div className="flex items-center">
            <span className="mr-2">{message.content}</span>
            <span className="loading-dots"></span>
          </div>
        ) : (
          <div>
            <p className="whitespace-pre-wrap break-words">{message.content}</p>
            {message.sources && message.sources.length > 0 && (
              <div className="mt-2 pt-2 border-t border-opacity-20 border-white">
                <p className="text-xs opacity-80">
                  🔍 基于 {message.sources.length} 个文档片段
                </p>
              </div>
            )}
          </div>
        )}
        <div className={`text-xs mt-1 ${
          isUser ? 'text-blue-100' : 'text-gray-500'
        }`}>
          {new Date(message.timestamp).toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;