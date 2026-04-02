import React, { useState } from 'react';
import { useDocumentStore } from '../../stores/documentStore';
import { documentAPI } from '../../services/api';

export const DocumentUpload: React.FC = () => {
  const [isUploading, setIsUploading] = useState(false);
  const { addDocument, setError } = useDocumentStore();

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setError(null);

    try {
      const response = await documentAPI.upload(file);
      addDocument(response.data);
      
      // 清空 input
      e.target.value = '';
    } catch (err) {
      setError(err instanceof Error ? err.message : '上传失败');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition-colors">
      <input
        type="file"
        id="file-upload"
        className="hidden"
        accept=".pdf,.docx,.txt,.md"
        onChange={handleFileChange}
        disabled={isUploading}
      />
      <label
        htmlFor="file-upload"
        className="cursor-pointer flex flex-col items-center"
      >
        <svg
          className="w-12 h-12 text-gray-400 mb-2"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>
        <span className="text-sm text-gray-600">
          {isUploading ? '上传中...' : '点击或拖拽文件到此处'}
        </span>
        <span className="text-xs text-gray-500 mt-1">
          支持 PDF、DOCX、TXT、Markdown 格式，最大 50MB
        </span>
      </label>
    </div>
  );
};
