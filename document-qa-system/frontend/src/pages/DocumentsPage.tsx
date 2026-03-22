import React, { useState, useEffect } from 'react';
import { useDocumentStore } from '../stores/documentStore';
import { DocumentUpload } from '../components/documents/DocumentUpload';
import { DocumentFilters } from '../components/documents/DocumentFilters';
import { DocumentList } from '../components/documents/DocumentList';

export const DocumentsPage: React.FC = () => {
  const {
    documents,
    total,
    page,
    limit,
    isLoading,
    error,
    fetchDocuments,
    deleteDocument,
    reprocessDocument,
    setStatusFilter,
    setError,
  } = useDocumentStore();

  const [localStatusFilter, setLocalStatusFilter] = useState('');

  // 初始加载
  useEffect(() => {
    loadDocuments();
  }, [page, limit, localStatusFilter]);

  const loadDocuments = async () => {
    try {
      await fetchDocuments(page, limit, localStatusFilter);
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载文档失败');
    }
  };

  const handleStatusChange = (status: string) => {
    setLocalStatusFilter(status);
    setStatusFilter(status);
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteDocument(id);
      // 删除成功后重新加载列表
      await loadDocuments();
    } catch (err) {
      alert(err instanceof Error ? err.message : '删除失败');
    }
  };

  const handleReprocess = async (id: string) => {
    try {
      await reprocessDocument(id);
      // 重新处理后重新加载列表
      await loadDocuments();
    } catch (err) {
      alert(err instanceof Error ? err.message : '重新处理失败');
    }
  };

  const handleRefresh = async () => {
    await loadDocuments();
  };

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= Math.ceil(total / limit)) {
      // 更新页码（会通过 useEffect 触发加载）
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto min-w-[900px]" data-testid="documents-page">
      {/* 页面标题 */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">文档管理</h2>
        <p className="text-sm text-gray-600 mt-1">
          共 {total} 个文档
        </p>
      </div>

      {/* 上传区域 */}
      <div className="mb-6">
        <DocumentUpload />
      </div>

      {/* 筛选器 */}
      <div className="mb-4">
        <DocumentFilters
          statusFilter={localStatusFilter}
          onStatusChange={handleStatusChange}
          onRefresh={handleRefresh}
        />
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg" data-testid="error-message">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* 文档列表 */}
      <div className="bg-white rounded-lg shadow min-w-full">
        <DocumentList
          documents={documents}
          isLoading={isLoading}
          onDelete={handleDelete}
          onReprocess={handleReprocess}
        />
      </div>

      {/* 分页控件 */}
      {total > limit && (
        <div className="mt-4 flex justify-between items-center" data-testid="pagination-controls">
          <button
            onClick={() => handlePageChange(page - 1)}
            disabled={page === 1}
            className="px-4 py-2 border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
            data-testid="prev-page-button"
          >
            上一页
          </button>
          <span className="text-sm text-gray-600">
            第 {page} 页，共 {Math.ceil(total / limit)} 页
          </span>
          <button
            onClick={() => handlePageChange(page + 1)}
            disabled={page >= Math.ceil(total / limit)}
            className="px-4 py-2 border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
            data-testid="next-page-button"
          >
            下一页
          </button>
        </div>
      )}
    </div>
  );
};
