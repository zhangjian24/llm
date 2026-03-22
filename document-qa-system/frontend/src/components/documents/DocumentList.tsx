import React from 'react';
import type { Document } from '../../types';

interface DocumentListProps {
  documents: Document[];
  isLoading: boolean;
  onDelete: (id: string) => Promise<void>;
  onReprocess: (id: string) => Promise<void>;
}

export const DocumentList: React.FC<DocumentListProps> = ({
  documents,
  isLoading,
  onDelete,
  onReprocess,
}) => {
  // 辅助函数：格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  // 辅助函数：获取 MIME 类型的友好标签
  const getMimeTypeLabel = (mimeType: string): string => {
    const mimeMap: Record<string, string> = {
      'application/pdf': 'PDF',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word',
      'text/plain': 'TXT',
      'text/markdown': 'Markdown',
    };
    return mimeMap[mimeType] || mimeType.split('/')[1]?.toUpperCase() || 'FILE';
  };

  // 辅助函数：格式化日期
  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // 辅助函数：获取状态标签样式和文本
  const getStatusBadge = (status: Document['status']) => {
    const statusConfig = {
      processing: { color: 'bg-yellow-100 text-yellow-800', label: '⏳ 处理中' },
      ready: { color: 'bg-green-100 text-green-800', label: '✅ 就绪' },
      failed: { color: 'bg-red-100 text-red-800', label: '❌ 失败' },
    };
    const config = statusConfig[status];
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`} data-testid="status-badge">
        {config.label}
      </span>
    );
  };

  // 删除处理函数
  const handleDelete = async (id: string) => {
    if (window.confirm('确定要删除此文档吗？此操作不可恢复。')) {
      await onDelete(id);
    }
  };

  // 加载状态
  if (isLoading) {
    return (
      <div className="overflow-x-auto min-w-[900px] bg-white rounded-lg" data-testid="loading-spinner">
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  // 表格渲染（始终显示表头，即使没有数据）
  return (
    <div className="overflow-x-auto min-w-[900px] bg-white rounded-lg" data-testid="document-list-table">
      <table className="min-w-full divide-y divide-gray-200 table-fixed">
        <thead className="bg-gray-50">
          <tr>
            <th className="w-[25%] px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">文件名</th>
            <th className="w-[10%] px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">大小</th>
            <th className="w-[10%] px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">类型</th>
            <th className="w-[12%] px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
            <th className="w-[8%] px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">块数</th>
            <th className="w-[20%] px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">上传时间</th>
            <th className="w-[15%] px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {documents.length === 0 ? (
            <tr>
              <td colSpan={7} className="px-6 py-12 text-center h-[220px]" data-testid="empty-state">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p className="mt-2 text-sm text-gray-600">暂无文档</p>
              </td>
            </tr>
          ) : (
            documents.map((doc) => (
              <tr key={doc.id} data-testid={`document-row-${doc.id}`} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{doc.filename}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-500">{formatFileSize(doc.file_size)}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                    {getMimeTypeLabel(doc.mime_type)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(doc.status)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {doc.chunks_count !== null && doc.chunks_count !== undefined ? doc.chunks_count : '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {formatDate(doc.created_at)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => onReprocess(doc.id)}
                    disabled={doc.status === 'processing'}
                    className={`text-blue-600 hover:text-blue-900 mr-3 ${
                      doc.status === 'processing' ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                    data-testid="reprocess-button"
                    title={doc.status === 'processing' ? '处理中无法重新处理' : '重新处理'}
                  >
                    {doc.status === 'processing' ? '处理中...' : '重新处理'}
                  </button>
                  <button
                    onClick={() => handleDelete(doc.id)}
                    disabled={doc.status === 'processing'}
                    className={`text-red-600 hover:text-red-900 ${
                      doc.status === 'processing' ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                    data-testid="delete-button"
                    title={doc.status === 'processing' ? '处理中无法删除' : '删除'}
                  >
                    {doc.status === 'processing' ? '删除中...' : '删除'}
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};
