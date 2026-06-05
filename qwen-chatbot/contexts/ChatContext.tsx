/**
 * ChatContext - 持久化的聊天状态
 *
 * 拆分自原 AppContext。包含：
 * - messages：当前对话消息流
 * - conversationHistory：历史对话记录
 * - selectedRoleId：当前选中的角色 ID
 * - inputMessage：当前输入框内容（保留原持久化行为，避免刷新丢失）
 * - schemaVersion：持久化 schema 版本号（未来迁移用）
 *
 * 持久化：
 * - localStorage key: 'appState'
 * - 写入节流 500ms（use-debounce）
 * - beforeunload 事件强制 flush，避免丢失
 */
import { createContext, useContext, useReducer, useEffect, useRef, type ReactNode } from 'react';
import { useDebouncedCallback } from 'use-debounce';
import type { Message, ConversationHistory } from '../types';

const STORAGE_KEY = 'appState';
const SCHEMA_VERSION = 1;
const PERSIST_DEBOUNCE_MS = 500;

interface ChatState {
  messages: Message[];
  conversationHistory: ConversationHistory[];
  inputMessage: string;
  selectedRoleId: string | null;
  schemaVersion: number;
}

type ChatAction =
  | { type: 'SET_MESSAGES'; payload: Message[] }
  | { type: 'ADD_MESSAGE'; payload: Message }
  | { type: 'CLEAR_MESSAGES' }
  | { type: 'SET_CONVERSATION_HISTORY'; payload: ConversationHistory[] }
  | { type: 'ADD_TO_HISTORY'; payload: ConversationHistory }
  | { type: 'UPDATE_HISTORY_EVALUATION'; payload: { id: number; evaluation: string } }
  | { type: 'SET_INPUT_MESSAGE'; payload: string }
  | { type: 'SET_SELECTED_ROLE'; payload: string | null };

function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case 'SET_MESSAGES':
      return { ...state, messages: action.payload };
    case 'ADD_MESSAGE':
      return { ...state, messages: [...state.messages, action.payload] };
    case 'CLEAR_MESSAGES':
      return { ...state, messages: [] };
    case 'SET_CONVERSATION_HISTORY':
      return { ...state, conversationHistory: action.payload };
    case 'ADD_TO_HISTORY':
      return {
        ...state,
        conversationHistory: [action.payload, ...state.conversationHistory],
      };
    case 'UPDATE_HISTORY_EVALUATION':
      return {
        ...state,
        conversationHistory: state.conversationHistory.map((item) =>
          item.id === action.payload.id ? { ...item, evaluation: action.payload.evaluation } : item,
        ),
      };
    case 'SET_INPUT_MESSAGE':
      return { ...state, inputMessage: action.payload };
    case 'SET_SELECTED_ROLE':
      return { ...state, selectedRoleId: action.payload };
    default:
      return state;
  }
}

const defaultState: ChatState = {
  messages: [],
  conversationHistory: [],
  inputMessage: '',
  selectedRoleId: null,
  schemaVersion: SCHEMA_VERSION,
};

/**
 * 严格校验从 localStorage 加载的状态
 * - 字段缺失或类型错误时降级为默认值
 * - 这是容错读取（spec/chat-state-management §REQ-CS-003）
 */
function loadInitialState(): ChatState {
  if (typeof window === 'undefined') return defaultState;
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return defaultState;
    const parsed = JSON.parse(stored);
    if (!parsed || typeof parsed !== 'object') return defaultState;
    return {
      messages: Array.isArray(parsed.messages) ? parsed.messages : defaultState.messages,
      conversationHistory: Array.isArray(parsed.conversationHistory)
        ? parsed.conversationHistory
        : defaultState.conversationHistory,
      inputMessage:
        typeof parsed.inputMessage === 'string' ? parsed.inputMessage : defaultState.inputMessage,
      selectedRoleId:
        typeof parsed.selectedRoleId === 'string' || parsed.selectedRoleId === null
          ? parsed.selectedRoleId
          : defaultState.selectedRoleId,
      schemaVersion: SCHEMA_VERSION,
    };
  } catch (err) {
    console.error('Could not load chat state from localStorage:', err);
    return defaultState;
  }
}

const ChatContext = createContext<{
  state: ChatState;
  dispatch: React.Dispatch<ChatAction>;
} | null>(null);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(chatReducer, undefined, loadInitialState);
  const stateRef = useRef(state);

  // 节流持久化：500ms 内的多次状态变更合并为一次写入
  const debouncedPersist = useDebouncedCallback((s: ChatState) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
    } catch (err) {
      console.error('Could not save chat state to localStorage:', err);
    }
  }, PERSIST_DEBOUNCE_MS);

  useEffect(() => {
    // 同步 ref 与 state（仅在 commit 阶段）
    stateRef.current = state;
    debouncedPersist(state);
  }, [state, debouncedPersist]);

  // beforeunload 强制 flush，避免刷新/关闭时丢失未节流的最新状态
  useEffect(() => {
    const handler = () => {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(stateRef.current));
      } catch {
        /* ignore */
      }
    };
    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
  }, []);

  return <ChatContext.Provider value={{ state, dispatch }}>{children}</ChatContext.Provider>;
}

export function useChatContext() {
  const ctx = useContext(ChatContext);
  if (!ctx) {
    throw new Error('useChatContext must be used within ChatProvider');
  }
  return ctx;
}
