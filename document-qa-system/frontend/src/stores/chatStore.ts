import { create } from 'zustand';
import { ChatMessage, QueryRequest, QueryResponse } from '../types';

interface ChatState {
  messages: ChatMessage[];
  conversationId: string | null;
  isStreaming: boolean;
  addMessage: (message: ChatMessage) => void;
  setMessages: (messages: ChatMessage[]) => void;
  clearMessages: () => void;
  setConversationId: (id: string) => void;
  setIsStreaming: (streaming: boolean) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  conversationId: null,
  isStreaming: false,
  
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message]
  })),
  
  setMessages: (messages) => set({ messages }),
  
  clearMessages: () => set({ 
    messages: [], 
    conversationId: null,
    isStreaming: false 
  }),
  
  setConversationId: (id) => set({ conversationId: id }),
  
  setIsStreaming: (streaming) => set({ isStreaming: streaming })
}));