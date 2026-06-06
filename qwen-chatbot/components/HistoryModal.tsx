/**
 * HistoryModal - 历史记录模态框容器
 * 表格内容委托给 HistoryTable 组件
 *
 * 可访问性补齐 (T20):
 * - role="dialog" + aria-modal="true"
 * - aria-labelledby 指向标题
 * - ESC 键关闭
 * - focus trap (Tab 循环在模态框内)
 * - 打开时自动聚焦关闭按钮
 */
import React, { useEffect, useRef } from 'react';
import { HistoryTable } from './HistoryTable';
import type { ConversationHistory } from '../types';

interface HistoryModalProps {
  history: ConversationHistory[];
  isOpen: boolean;
  onClose: () => void;
  onEvaluationChange: (id: number, evaluation: string) => void;
}

const TITLE_ID = 'history-modal-title';
const FOCUSABLE_SELECTOR =
  'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';

const HistoryModal: React.FC<HistoryModalProps> = ({
  history,
  isOpen,
  onClose,
  onEvaluationChange,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const closeBtnRef = useRef<HTMLButtonElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!isOpen) return;

    // 保存打开前焦点
    previousFocusRef.current = document.activeElement as HTMLElement | null;
    // 聚焦关闭按钮
    closeBtnRef.current?.focus();

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
        return;
      }
      if (e.key === 'Tab' && containerRef.current) {
        const focusables = Array.from(
          containerRef.current.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR),
        ).filter((el) => !el.hasAttribute('disabled') && el.offsetParent !== null);
        if (focusables.length === 0) return;
        const first = focusables[0];
        const last = focusables[focusables.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      // 恢复打开前的焦点
      previousFocusRef.current?.focus?.();
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-2 sm:p-4 z-50"
      onClick={onClose}
    >
      <div
        ref={containerRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={TITLE_ID}
        className="bg-white rounded-lg w-full max-w-6xl max-h-[95vh] sm:max-h-[90vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center p-4 sm:p-6 border-b border-gray-200">
          <h2 id={TITLE_ID} className="text-lg sm:text-xl font-bold text-gray-800">
            对话历史记录
          </h2>
          <button
            ref={closeBtnRef}
            className="text-gray-500 hover:text-gray-700 text-xl sm:text-2xl w-6 h-6 sm:w-8 sm:h-8 flex items-center justify-center"
            onClick={onClose}
            aria-label="关闭"
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
