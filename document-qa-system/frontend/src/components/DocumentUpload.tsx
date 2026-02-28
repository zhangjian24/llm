import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { FiUpload, FiFile, FiCheckCircle, FiAlertCircle, FiTrash2 } from 'react-icons/fi';
import { documentApi, DocumentUploadResponse } from '../services/api';

interface DocumentUploadProps {
  onUploadSuccess?: () => void;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<DocumentUploadResponse[]>([]);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setUploading(true);
    setError(null);
    
    try {
      const results = await Promise.all(
        acceptedFiles.map(async (file) => {
          const result = await documentApi.uploadDocument(file);
          return result;
        })
      );
      
      setUploadedFiles(prev => [...prev, ...results]);
      if (onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || '上传失败，请重试');
    } finally {
      setUploading(false);
    }
  }, [onUploadSuccess]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/html': ['.html', '.htm']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: true
  });

  const removeFile = (documentId: string) => {
    setUploadedFiles(prev => prev.filter(file => file.document_id !== documentId));
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">文档上传</h2>
        <p className="text-gray-600">
          上传PDF、TXT、DOCX等格式的文档，系统将自动处理并建立索引
        </p>
      </div>

      {/* 上传区域 */}
      <div 
        {...getRootProps()} 
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200 mb-8 ${
          isDragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
        } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} disabled={uploading} />
        <FiUpload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        {isDragActive ? (
          <p className="text-lg font-medium text-blue-600">释放文件开始上传</p>
        ) : (
          <>
            <p className="text-lg font-medium text-gray-900 mb-2">
              拖拽文件到这里，或点击选择文件
            </p>
            <p className="text-gray-500">
              支持 PDF, TXT, DOCX, DOC, HTML 格式，最大10MB
            </p>
          </>
        )}
        {uploading && (
          <div className="mt-4">
            <div className="loading-spinner mx-auto"></div>
            <p className="text-gray-600 mt-2">正在上传和处理文档...</p>
          </div>
        )}
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex items-center">
            <FiAlertCircle className="h-5 w-5 text-red-400 mr-2" />
            <p className="text-red-800">{error}</p>
          </div>
        </div>
      )}

      {/* 已上传文件列表 */}
      {uploadedFiles.length > 0 && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">已上传文档</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {uploadedFiles.map((file) => (
              <div key={file.document_id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <FiFile className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="font-medium text-gray-900">{file.filename}</p>
                      <p className="text-sm text-gray-500">{file.message}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <FiCheckCircle className="h-5 w-5 text-green-500" />
                    <button
                      onClick={() => removeFile(file.document_id)}
                      className="text-gray-400 hover:text-red-500 transition-colors"
                    >
                      <FiTrash2 className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 上传说明 */}
      <div className="mt-8 bg-blue-50 rounded-lg p-6">
        <h3 className="font-medium text-blue-900 mb-2">使用说明</h3>
        <ul className="text-blue-800 space-y-1 text-sm">
          <li>• 支持批量上传多个文档</li>
          <li>• 系统会自动提取文档内容并建立向量索引</li>
          <li>• 处理完成后即可进行智能问答</li>
          <li>• 建议上传结构清晰、内容完整的文档</li>
        </ul>
      </div>
    </div>
  );
};

export default DocumentUpload;