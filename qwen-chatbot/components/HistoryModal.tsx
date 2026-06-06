/**
 * HistoryModal - 历史记录模态框容器
 * 表格内容委托给 HistoryTable 组件
 */
import React from 'react';
import { HistoryTable } from './HistoryTable';
import type { ConversationHistory } from '../types';

interface HistoryModalProps {
  history: ConversationHistory[];
  isOpen: boolean;
  onClose: () => void;
  onEvaluationChange: (id: number, evaluation: string) => void;
}

const HistoryModal: React.FC<HistoryModalProps> = ({
  history,
  isOpen,
  onClose,
  onEvaluationChange,
}) => {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-2 sm:p-4 z-50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg w-full max-w-6xl max-h-[95vh] sm:max-h-[90vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center p-4 sm:p-6 border-b border-gray-200">
          <h2 className="text-lg sm:text-xl font-bold text-gray-800">对话历史记录</h2>
          <button
            className="text-gray-500 hover:text-gray-700 text-xl sm:text-2xl w-6 h-6 sm:w-8 sm:h-8 flex items-center justify-center"
            onClick={onClose}
            aria-label="关闭对话历史"
          >
            ×
          </button>
        </div>

        <div className="flex-1 overflow-auto p-4 sm:p-6">
          <HistoryTable history={history} onEvaluationChange={onEvaluationChange} />
        </div>
      </div>
    </div>
  );
};

export default HistoryModal;
