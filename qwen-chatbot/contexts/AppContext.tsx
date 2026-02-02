import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { Message, ConversationHistory } from '../types';

// 定义应用状态类型
interface AppState {
  messages: Message[];
  conversationHistory: ConversationHistory[];
  inputMessage: string;
  selectedRoleId: string | null;
}

// 定义动作类型
type AppAction =
  | { type: 'SET_MESSAGES'; payload: Message[] }
  | { type: 'ADD_MESSAGE'; payload: Message }
  | { type: 'CLEAR_MESSAGES' }
  | { type: 'SET_CONVERSATION_HISTORY'; payload: ConversationHistory[] }
  | { type: 'ADD_TO_HISTORY'; payload: ConversationHistory }
  | { type: 'UPDATE_HISTORY_EVALUATION'; payload: { id: number; evaluation: string } }
  | { type: 'SET_INPUT_MESSAGE'; payload: string }
  | { type: 'SET_SELECTED_ROLE'; payload: string | null };

// 定义Context类型
interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
}

// 创建Context
const AppContext = createContext<AppContextType | undefined>(undefined);

// 初始状态
const getInitialState = (): AppState => {
  const defaultState: AppState = {
    messages: [],
    conversationHistory: [],
    inputMessage: '',
    selectedRoleId: null,
  };

  // 从localStorage加载初始状态
  if (typeof window !== 'undefined') {
    try {
      const serializedState = localStorage.getItem('appState');
      if (serializedState !== null) {
        const loadedState = JSON.parse(serializedState);
        // 确保加载的状态包含所有必需的字段
        return {
          ...defaultState,
          ...loadedState,
          // 确保消息数组中的对象格式正确
          messages: Array.isArray(loadedState.messages) ? loadedState.messages : defaultState.messages,
          conversationHistory: Array.isArray(loadedState.conversationHistory) ? loadedState.conversationHistory : defaultState.conversationHistory,
        };
      }
    } catch (err) {
      console.error('Could not load state from localStorage:', err);
    }
  }

  return defaultState;
};

// Reducer函数
const appReducer = (state: AppState, action: AppAction): AppState => {
  let newState: AppState;

  switch (action.type) {
    case 'SET_MESSAGES':
      newState = { ...state, messages: action.payload };
      break;
    case 'ADD_MESSAGE':
      newState = { ...state, messages: [...state.messages, action.payload] };
      break;
    case 'CLEAR_MESSAGES':
      newState = { ...state, messages: [] };
      break;
    case 'SET_CONVERSATION_HISTORY':
      newState = { ...state, conversationHistory: action.payload };
      break;
    case 'ADD_TO_HISTORY':
      newState = { ...state, conversationHistory: [action.payload, ...state.conversationHistory] };
      break;
    case 'UPDATE_HISTORY_EVALUATION':
      newState = {
        ...state,
        conversationHistory: state.conversationHistory.map(item =>
          item.id === action.payload.id ? { ...item, evaluation: action.payload.evaluation } : item
        ),
      };
      break;
    case 'SET_INPUT_MESSAGE':
      newState = { ...state, inputMessage: action.payload };
      break;
    case 'SET_SELECTED_ROLE':
      newState = { ...state, selectedRoleId: action.payload };
      break;
    default:
      newState = state;
      break;
  }

  // 保存状态到localStorage
  try {
    if (typeof window !== 'undefined') {
      const serializedState = JSON.stringify(newState);
      localStorage.setItem('appState', serializedState);
    }
  } catch (err) {
    console.error('Could not save state to localStorage:', err);
  }

  return newState;
};

// Provider组件
interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, undefined, getInitialState);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
};

// 自定义Hook
export const useAppContext = (): AppContextType => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};

export default AppContext;