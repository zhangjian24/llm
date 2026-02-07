import React from 'react';
import { ConversationHistory } from '../types';

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
  onEvaluationChange
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-2 sm:p-4 z-50" onClick={onClose}>
      <div className="bg-white rounded-lg w-full max-w-6xl max-h-[95vh] sm:max-h-[90vh] overflow-hidden flex flex-col" onClick={(e) => e.stopPropagation()}>
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
          {history.length === 0 ? (
            <p className="text-gray-500 text-center py-8 sm:py-12">暂无对话历史记录</p>
          ) : (
            <div className="overflow-x-auto -mx-2 sm:-mx-4">
              <div className="inline-block min-w-full align-middle">
                <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
                  <table className="min-w-full divide-y divide-gray-300">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sm:px-4">时间</th>
                        <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sm:px-4">输入</th>
                        <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sm:px-4">输出</th>
                        <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sm:px-4 hidden sm:table-cell">模型</th>
                        <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sm:px-4 hidden md:table-cell">参数</th>
                        <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sm:px-4 hidden lg:table-cell">Token明细</th>
                        <th className="px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sm:px-4">效果评估</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {history.map((item) => (
                        <tr key={item.id} className="hover:bg-gray-50">
                          <td className="px-2 py-3 text-xs sm:text-sm text-gray-500 whitespace-nowrap sm:px-4">
                            {new Date(item.timestamp).toLocaleString()}
                          </td>
                          <td className="px-2 py-3 text-xs sm:text-sm text-gray-900 max-w-[80px] sm:max-w-xs truncate sm:px-4">
                            <div>
                              {item.input.substring(0, 30)}{item.input.length > 30 ? '...' : ''}
                            </div>
                          </td>
                          <td className="px-2 py-3 text-xs sm:text-sm text-gray-900 max-w-[100px] sm:max-w-md truncate sm:px-4">
                            <div>
                              {item.output.substring(0, 60)}{item.output.length > 60 ? '...' : ''}
                            </div>
                          </td>
                          <td className="px-2 py-3 text-xs sm:text-sm text-gray-900 whitespace-nowrap sm:px-4 hidden sm:table-cell">{item.model}</td>
                          <td className="px-2 py-3 text-xs sm:text-sm text-gray-500 sm:px-4 hidden md:table-cell">
                            <div className="space-y-1">
                              <div>temperature: {item.params.temperature.toFixed(2)}</div>
                              <div>top_p: {item.params.top_p.toFixed(2)}</div>
                              <div className="hidden lg:block">max_tokens: {item.params.max_tokens}</div>
                            </div>
                          </td>
                          <td className="px-2 py-3 text-xs sm:text-sm text-gray-500 sm:px-4 hidden lg:table-cell">
                            {item.tokenUsage && (
                              <div className="space-y-1">
                                <div>Prompt: {item.tokenUsage.prompt_tokens}</div>
                                <div>Completion: {item.tokenUsage.completion_tokens}</div>
                                <div>Total: {item.tokenUsage.total_tokens}</div>
                              </div>
                            )}
                          </td>
                          <td className="px-2 py-3 text-xs sm:text-sm sm:px-4">
                            <input
                              type="text"
                              value={item.evaluation}
                              onChange={(e) => onEvaluationChange(item.id, e.target.value)}
                              placeholder="请输入评价"
                              className="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-transparent text-xs sm:text-sm"
                            />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HistoryModal;