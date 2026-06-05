/**
 * UIContext - 临时 UI 状态（不入存储）
 *
 * 拆分自原 AppContext。包含：
 * - isThinking：是否在思考阶段
 * - isGenerating：是否在生成流式响应
 * - currentResponse：当前流式响应的内容（实况显示）
 * - showHistoryModal：历史记录模态框开关
 *
 * 与 ChatContext 的区别：UIContext 状态不持久化，刷新即重置。
 */
import { createContext, useContext, useState, type ReactNode } from 'react';

interface UIState {
  isThinking: boolean;
  isGenerating: boolean;
  currentResponse: string;
  showHistoryModal: boolean;
}

type UIDispatch = {
  setIsThinking: (b: boolean) => void;
  setIsGenerating: (b: boolean) => void;
  setCurrentResponse: (s: string) => void;
  setShowHistoryModal: (b: boolean) => void;
};

const UIContext = createContext<(UIState & UIDispatch) | null>(null);

export function UIProvider({ children }: { children: ReactNode }) {
  const [isThinking, setIsThinking] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentResponse, setCurrentResponse] = useState('');
  const [showHistoryModal, setShowHistoryModal] = useState(false);

  return (
    <UIContext.Provider
      value={{
        isThinking,
        setIsThinking,
        isGenerating,
        setIsGenerating,
        currentResponse,
        setCurrentResponse,
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
