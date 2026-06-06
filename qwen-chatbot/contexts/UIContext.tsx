/**
 * UIContext - 临时 UI 状态（不被持久化）
 *
 * - isThinking: AI 正在思考（首 token 未到）
 * - isGenerating: AI 正在生成内容
 * - showHistoryModal: 历史记录模态框是否打开
 *
 * 注：流式响应内容直接从 messages 最后一条派生，不在此处维护
 */
import { createContext, useContext, useState, type ReactNode } from 'react';

interface UIState {
  isThinking: boolean;
  isGenerating: boolean;
  showHistoryModal: boolean;
}

type UIDispatch = {
  setIsThinking: (b: boolean) => void;
  setIsGenerating: (b: boolean) => void;
  setShowHistoryModal: (b: boolean) => void;
};

const UIContext = createContext<(UIState & UIDispatch) | null>(null);

export function UIProvider({ children }: { children: ReactNode }) {
  const [isThinking, setIsThinking] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);

  return (
    <UIContext.Provider
      value={{
        isThinking,
        setIsThinking,
        isGenerating,
        setIsGenerating,
        showHistoryModal,
        setShowHistoryModal,
      }}
    >
      {children}
    </UIContext.Provider>
  );
}

export function useUIContext() {
  const ctx = useContext(UIContext);
  if (!ctx) {
    throw new Error('useUIContext must be used within UIProvider');
  }
  return ctx;
}
