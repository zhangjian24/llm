import React, { useState, useRef } from 'react';
import { useChatStore } from '../../stores/chatStore';
import { chatAPI } from '../../services/api';
import type { Message } from '../../types';

export const ChatInput: React.FC = () => {
  const [input, setInput] = useState('');
  const { 
    addMessage, 
    updateLastAssistantMessage, 
    setCurrentConversation, 
    setLoading, 
    setError,
    currentConversationId,
    fetchConversations
  } = useChatStore();
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
      // 添加初始的助手消息
      addMessage({
        role: 'assistant',
        content: '',
        created_at: new Date().toISOString()
      });

      // 使用流式 API，传入当前对话 ID
      await chatAPI.chatStream(
        { 
          query: input.trim(), 
          top_k: 5, 
          stream: true,
          conversation_id: currentConversationId || undefined
        },
        (token) => {
          // 实时更新助手消息内容
          updateLastAssistantMessage(token);
        },
        (conversationId) => {
          setCurrentConversation(conversationId);
          setLoading(false);
          // 刷新对话列表以显示新对话或更新时间
          fetchConversations();
          // 保存消息到本地存储
          const currentMessages = useChatStore.getState().messages;
          localStorage.setItem(`conversation_${conversationId}`, JSON.stringify(currentMessages));
        },
        (error) => {
          setError(error);
          setLoading(false);
          // 在错误消息后添加错误提示
          addMessage({
            role: 'assistant',
            content: `❌ 抱歉，处理您的问题时出现错误: ${error}`,
            created_at: new Date().toISOString()
          });
        }
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : '发送失败');
      setLoading(false);
      // 添加错误提示消息
      addMessage({
        role: 'assistant',
        content: `❌ ${err instanceof Error ? err.message : '发送失败'}`,
        created_at: new Date().toISOString()
      });
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
