import React from 'react';

interface ConversationHistory {
  id: number;
  timestamp: string;
  input: string;
  output: string;
  model: string;
  params: {
    temperature: number;
    top_p: number;
    max_tokens: number;
  };
  tokenUsage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  evaluation: string;
}

interface ConversationHistoryTableProps {
  history: ConversationHistory[];
  onEvaluationChange: (id: number, evaluation: string) => void;
}

const ConversationHistoryTable: React.FC<ConversationHistoryTableProps> = ({ history, onEvaluationChange }) => {
  const formatDate = (timestamp: string) => {
    return new Intl.DateTimeFormat('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(new Date(timestamp));
  };

  const autoEvaluate = (output: string): string => {
    if (output.includes('Error:') || output.includes('error') || output.includes('失败')) {
      return '响应错误';
    }
    
    const wordCount = output.trim().split(/\s+/).length;
    
    if (wordCount < 5) return '响应过短';
    if (wordCount > 100) return '响应详细';
    return '响应适中';
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 sm:p-6">
      <h3 className="text-lg sm:text-xl font-bold text-gray-800 mb-4">对话历史记录</h3>
      {history.length === 0 ? (
        <p className="text-gray-500 text-center py-8">暂无对话历史</p>
      ) : (
        <div className="overflow-x-auto -mx-4 sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full align-middle">
            <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
              <table className="min-w-full divide-y divide-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sm:px-4">时间</th>
                    <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sm:px-4">输入</th>
                    <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sm:px-4">输出</th>
                    <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sm:px-4 hidden sm:table-cell">模型</th>
                    <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sm:px-4 hidden md:table-cell">参数</th>
                    <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sm:px-4 hidden lg:table-cell">Token明细</th>
                    <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sm:px-4">效果评估</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {history.map((item) => (
                    <tr key={`history-${item.id}`} className="hover:bg-gray-50">
                      <td className="px-3 py-3 text-xs sm:text-sm text-gray-500 whitespace-nowrap sm:px-4">{formatDate(item.timestamp)}</td>
                      <td className="px-3 py-3 text-xs sm:text-sm text-gray-900 max-w-[100px] sm:max-w-xs truncate sm:px-4">{item.input}</td>
                      <td className="px-3 py-3 text-xs sm:text-sm text-gray-900 max-w-[100px] sm:max-w-xs truncate sm:px-4">{item.output.substring(0, 120)}{item.output.length > 120 ? '...' : ''}</td>
                      <td className="px-3 py-3 text-xs sm:text-sm text-gray-900 whitespace-nowrap sm:px-4 hidden sm:table-cell">{item.model}</td>
                      <td className="px-3 py-3 text-xs sm:text-sm text-gray-500 sm:px-4 hidden md:table-cell">
                        <div className="space-y-1">
                          <div><span className="font-medium">温度:</span> {item.params.temperature.toFixed(2)}</div>
                          <div><span className="font-medium">Top-P:</span> {item.params.top_p.toFixed(2)}</div>
                          <div className="hidden lg:block"><span className="font-medium">最大Tokens:</span> {item.params.max_tokens}</div>
                        </div>
                      </td>
                      <td className="px-3 py-3 text-xs sm:text-sm text-gray-500 sm:px-4 hidden lg:table-cell">
                        {item.tokenUsage ? (
                          <div className="space-y-1">
                            <div><span className="font-medium">输入:</span> {item.tokenUsage.prompt_tokens}</div>
                            <div><span className="font-medium">输出:</span> {item.tokenUsage.completion_tokens}</div>
                            <div><span className="font-medium">总计:</span> {item.tokenUsage.total_tokens}</div>
                          </div>
                        ) : (
                          <div><span className="text-gray-400">未记录</span></div>
                        )}
                      </td>
                      <td className="px-3 py-3 text-xs sm:text-sm sm:px-4">
                        <input
                          type="text"
                          value={item.evaluation}
                          onChange={(e) => onEvaluationChange(item.id, e.target.value)}
                          placeholder={item.evaluation || autoEvaluate(item.output)}
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
  );
};

export default ConversationHistoryTable;