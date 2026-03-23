import { create } from 'zustand';
import { chatAPI } from '../services/api';
import type { Message, Conversation } from '../types';

interface ChatState {
  // 消息相关状态
  messages: Message[];
  currentConversationId: string | null;
  isLoading: boolean;
  error: string | null;
  
  // 对话侧边栏相关状态
  conversations: Conversation[];
  isSidebarOpen: boolean;
  isLoadingConversations: boolean;
  
  // 消息相关 Actions
  addMessage: (message: Message) => void;
  updateLastAssistantMessage: (content: string) => void;
  setCurrentConversation: (id: string | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearMessages: () => void;
  
  // 对话侧边栏相关 Actions
  fetchConversations: () => Promise<void>;
  selectConversation: (id: string) => void;
  createNewConversation: () => void;
  deleteConversation: (id: string) => Promise<void>;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  loadConversationMessages: (messages: Message[], conversationId: string) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  // 初始状态
  messages: [],
  currentConversationId: null,
  isLoading: false,
  error: null,
  conversations: [],
  isSidebarOpen: true,
  isLoadingConversations: false,

  // ========== 消息相关 Actions ==========
  
  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),

  updateLastAssistantMessage: (content) =>
    set((state) => {
      const messages = [...state.messages];
      const lastMessage = messages[messages.length - 1];
      
      if (lastMessage && lastMessage.role === 'assistant') {
        messages[messages.length - 1] = {
          ...lastMessage,
          content: lastMessage.content + content
        };
      } else {
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

  // ========== 对话侧边栏相关 Actions ==========
  
  fetchConversations: async () => {
    set({ isLoadingConversations: true });
    try {
      const conversations = await chatAPI.getConversations(50);
      set({ 
        conversations: conversations.sort((a, b) => 
          new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
        ),
        isLoadingConversations: false 
      });
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
      set({ isLoadingConversations: false });
    }
  },

  selectConversation: (id) => {
    set({ currentConversationId: id });
    const savedMessages = localStorage.getItem(`conversation_${id}`);
    if (savedMessages) {
      try {
        const messages = JSON.parse(savedMessages);
        set({ messages });
      } catch (e) {
        console.error('Failed to parse saved messages:', e);
      }
    } else {
      set({ messages: [] });
    }
  },

  createNewConversation: () => {
    set({ 
      messages: [],
      currentConversationId: null,
      error: null,
      isLoading: false 
    });
  },

  deleteConversation: async (id) => {
    try {
      await chatAPI.deleteConversation(id);
      set((state) => ({
        conversations: state.conversations.filter(c => c.id !== id)
      }));
      if (get().currentConversationId === id) {
        get().createNewConversation();
      }
      localStorage.removeItem(`conversation_${id}`);
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
  },

  toggleSidebar: () => {
    set((state) => ({ isSidebarOpen: !state.isSidebarOpen }));
  },

  setSidebarOpen: (open) => {
    set({ isSidebarOpen: open });
  },

  loadConversationMessages: (messages, conversationId) => {
    set({ 
      messages,
      currentConversationId: conversationId 
    });
    localStorage.setItem(`conversation_${conversationId}`, JSON.stringify(messages));
  },
}));
