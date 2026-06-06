import React from 'react';
import TypeWriterEffect from './TypeWriterEffect';
import { MarkdownRenderer } from './MarkdownRenderer';
import { AiOutlineRobot, AiOutlineUser } from 'react-icons/ai';
import ThinkingIndicator from './ThinkingIndicator';
import { log } from '../lib/logger';
import type { Message } from '../types';

interface ChatWindowProps {
  messages: Message[];
  isThinking?: boolean;
  isStreaming?: boolean;
}

const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  isThinking = false,
  isStreaming = false,
}) => {
  log.debug(
    'ChatWindow received messages:',
    messages,
    'isThinking:',
    isThinking,
    'isStreaming:',
    isStreaming,
  );
  const lastIndex = messages.length - 1;
  return (
    <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
      {messages.length === 0 ? (
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-700 mb-2">Welcome to Qwen Chatbot!</h2>
          <p className="text-gray-500">Ask me anything, and I&apos;ll do my best to assist you.</p>
        </div>
      ) : (
        <div className="space-y-4 w-full">
          {messages.map((message, index) => {
            const isLastAssistant =
              isStreaming && index === lastIndex && message.role === 'assistant';
            return (
              <div
                key={message.id || `msg-${index}-${message.role}`}
                data-testid={message.role === 'assistant' ? 'assistant-message' : 'user-message'}
                className={`flex gap-3 ${message.role.toLowerCase() === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {message.role.toLowerCase() === 'assistant' ? (
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm">
                    <AiOutlineRobot className="w-4 h-4" />
                  </div>
                ) : (
                  <div className="flex-shrink-0 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-white text-sm">
                    <AiOutlineUser className="w-4 h-4" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] ${message.role.toLowerCase() === 'user' ? 'bg-blue-500 text-white' : 'bg-white text-gray-800'} rounded-2xl px-4 py-3 shadow-sm`}
                >
                  {message.role.toLowerCase() === 'assistant' ? (
                    isLastAssistant ? (
                      <TypeWriterEffect text={message.content} />
                    ) : (
                      <MarkdownRenderer>{message.content || 'AI 正在思考...'}</MarkdownRenderer>
                    )
                  ) : (
                    message.content || '请发送消息'
                  )}
                </div>
              </div>
            );
          })}
          {/* 思考阶段（仅在助手消息尚未出现时显示） */}
          {isThinking && messages[messages.length - 1]?.role !== 'assistant' && (
            <div className="flex gap-3 justify-start">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm">
                <AiOutlineRobot className="w-4 h-4" />
              </div>
              <div className="max-w-[80%] bg-white text-gray-800 rounded-2xl px-4 py-3 shadow-sm">
                <ThinkingIndicator />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default React.memo(ChatWindow);
