import React from 'react';

interface DocumentFiltersProps {
  statusFilter: string;
  onStatusChange: (status: string) => void;
  onRefresh: () => void;
}

export const DocumentFilters: React.FC<DocumentFiltersProps> = ({
  statusFilter,
  onStatusChange,
  onRefresh,
}) => {
  return (
    <div className="flex justify-between items-center mb-4" data-testid="document-filters">
      <div className="flex items-center space-x-2">
        <label htmlFor="status-filter" className="text-sm text-gray-600">
          状态筛选：
        </label>
        <select
          id="status-filter"
          data-testid="status-filter"
          value={statusFilter}
          onChange={(e) => onStatusChange(e.target.value)}
          className="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:border-blue-500"
        >
          <option value="">全部</option>
          <option value="processing">处理中</option>
          <option value="ready">就绪</option>
          <option value="failed">失败</option>
        </select>
      </div>
      
      <button
        data-testid="refresh-button"
        onClick={onRefresh}
        className="flex items-center px-3 py-1 text-sm text-gray-600 hover:text-blue-600 transition-colors"
        title="刷新列表"
      >
        <svg
          className="w-4 h-4 mr-1"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          />
        </svg>
        刷新
      </button>
    </div>
  );
};
