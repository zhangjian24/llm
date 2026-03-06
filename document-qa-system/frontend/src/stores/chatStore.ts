import { create } from 'zustand';
import type { Message } from '../types';

interface ChatState {
  messages: Message[];
  currentConversationId: string | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  addMessage: (message: Message) => void;
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
