import React, { useState, useRef } from 'react';
import { useChatStore } from '../stores/chatStore';
import { chatAPI } from '../services/api';
import type { Message } from '../types';

export const ChatInput: React.FC = () => {
  const [input, setInput] = useState('');
  const { addMessage, setCurrentConversation, setLoading, setError } = useChatStore();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim()) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      created_at: new Date().toISOString(),
    };

    addMessage(userMessage);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      // 使用流式 API
      await chatAPI.chatStream(
        { query: input.trim(), top_k: 5, stream: true },
        (token) => {
          // 累积 token - 这里简化处理，实际应该更新最后一条消息
          console.log('Token:', token);
        },
        (conversationId) => {
          setCurrentConversation(conversationId);
          setLoading(false);
        },
        (error) => {
          setError(error);
          setLoading(false);
        }
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : '发送失败');
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-200 p-4">
      <div className="flex gap-2">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入问题...（Shift+Enter 换行）"
          className="flex-1 resize-none border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={3}
        />
        <button
          type="submit"
          disabled={!input.trim()}
          className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          发送
        </button>
      </div>
    </form>
  );
};
