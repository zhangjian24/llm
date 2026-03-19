import { create } from 'zustand';
import type { Message } from '../types';

interface ChatState {
  messages: Message[];
  currentConversationId: string | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  addMessage: (message: Message) => void;
  updateLastAssistantMessage: (content: string) => void;
  setCurrentConversation: (id: string | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  currentConversationId: null,
  isLoading: false,
  error: null,

  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),

  updateLastAssistantMessage: (content) =>
    set((state) => {
      const messages = [...state.messages];
      const lastMessage = messages[messages.length - 1];
      
      if (lastMessage && lastMessage.role === 'assistant') {
        // 更新最后一条助手消息
        messages[messages.length - 1] = {
          ...lastMessage,
          content: lastMessage.content + content
        };
      } else {
        // 添加新的助手消息
        messages.push({
          role: 'assistant',
          content: content,
          created_at: new Date().toISOString()
        });
      }
      
      return { messages };
    }),

  setCurrentConversation: (id) =>
    set({ currentConversationId: id }),

  setLoading: (loading) =>
    set({ isLoading: loading }),

  setError: (error) =>
    set({ error }),

  clearMessages: () =>
    set({ 
      messages: [], 
      currentConversationId: null, 
      error: null,
      isLoading: false 
    }),
}));
