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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" onClick={onClose}>
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col" onClick={(e) => e.stopPropagation()}>
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-800">对话历史记录</h2>
          <button 
            className="text-gray-500 hover:text-gray-700 text-2xl w-8 h-8 flex items-center justify-center"
            onClick={onClose}
          >
            ×
          </button>
        </div>
        
        <div className="flex-1 overflow-auto p-6">
          {history.length === 0 ? (
            <p className="text-gray-500 text-center py-12">暂无对话历史记录</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50 sticky top-0">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">时间</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">输入</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">输出</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">模型</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">参数</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Token明细</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">效果评估</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {history.map((item) => (
                    <tr key={item.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm text-gray-500 whitespace-nowrap">
                        {new Date(item.timestamp).toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 max-w-xs truncate">
                        <div>
                          {item.input.substring(0, 50)}{item.input.length > 50 ? '...' : ''}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 max-w-md truncate">
                        <div>
                          {item.output.substring(0, 80)}{item.output.length > 80 ? '...' : ''}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 whitespace-nowrap">{item.model}</td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        <div>
                          <div>temperature: {item.params.temperature}</div>
                          <div>top_p: {item.params.top_p}</div>
                          <div>max_tokens: {item.params.max_tokens}</div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {item.tokenUsage && (
                          <div>
                            <div>Prompt: {item.tokenUsage.prompt_tokens}</div>
                            <div>Completion: {item.tokenUsage.completion_tokens}</div>
                            <div>Total: {item.tokenUsage.total_tokens}</div>
                          </div>
                        )}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <input
                          type="text"
                          value={item.evaluation}
                          onChange={(e) => onEvaluationChange(item.id, e.target.value)}
                          placeholder="请输入评价"
                          className="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-transparent text-sm"
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HistoryModal;