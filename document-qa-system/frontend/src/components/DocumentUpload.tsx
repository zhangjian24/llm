import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { FaUpload, FaFilePdf, FaFileWord, FaFileAlt, FaCheck, FaTimes, FaSpinner } from 'react-icons/fa';

interface Document {
  id: string;
  filename: string;
  content_type: string;
  size: number;
  status: 'uploaded' | 'processing' | 'processed' | 'failed';
  created_at: string;
  processed_at?: string;
}

const DocumentUpload: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setUploading(true);
    setUploadProgress(0);

    try {
      for (const file of acceptedFiles) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await axios.post('/api/v1/documents/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            const progress = progressEvent.total 
              ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
              : 0;
            setUploadProgress(progress);
          },
        });

        setDocuments(prev => [...prev, response.data]);
      }
    } catch (error) {
      console.error('上传失败:', error);
      alert('文件上传失败，请重试');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: true
  });

  const getFileIcon = (contentType: string) => {
    switch (contentType) {
      case 'application/pdf':
        return <FaFilePdf className="text-red-500" />;
      case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
      case 'application/msword':
        return <FaFileWord className="text-blue-500" />;
      case 'text/plain':
        return <FaFileAlt className="text-gray-500" />;
      default:
        return <FaFileAlt className="text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processed':
        return 'text-green-600 bg-green-100';
      case 'processing':
        return 'text-yellow-600 bg-yellow-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">文档上传</h1>
        <p className="text-gray-600">上传PDF、Word或TXT文档，系统将自动处理并建立索引</p>
      </div>

      {/* 上传区域 */}
      <div 
        {...getRootProps()} 
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200 mb-8 ${
          isDragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
        }`}
      >
        <input {...getInputProps()} />
        <FaUpload className="mx-auto text-4xl text-gray-400 mb-4" />
        {isDragActive ? (
          <p className="text-lg text-blue-600 font-medium">释放文件以上传</p>
        ) : (
          <>
            <p className="text-lg text-gray-600 mb-2">
              拖拽文件到此处或点击选择文件
            </p>
            <p className="text-sm text-gray-500">
              支持 PDF、DOCX、DOC、TXT 格式，最大10MB
            </p>
          </>
        )}
      </div>

      {/* 上传进度 */}
      {uploading && (
        <div className="mb-6">
          <div className="flex justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">上传进度</span>
            <span className="text-sm text-gray-500">{uploadProgress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div 
              className="bg-blue-600 h-2.5 rounded-full transition-all duration-300" 
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* 文档列表 */}
      {documents.length > 0 && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-800">已上传文档</h2>
          </div>
          <div className="divide-y divide-gray-200">
            {documents.map((doc) => (
              <div key={doc.id} className="px-6 py-4 hover:bg-gray-50 transition-colors duration-150">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    {getFileIcon(doc.content_type)}
                    <div>
                      <h3 className="font-medium text-gray-900">{doc.filename}</h3>
                      <p className="text-sm text-gray-500">
                        {formatFileSize(doc.size)} • {new Date(doc.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(doc.status)}`}>
                      {doc.status === 'uploaded' && '已上传'}
                      {doc.status === 'processing' && (
                        <span className="flex items-center">
                          <FaSpinner className="animate-spin mr-1" />
                          处理中
                        </span>
                      )}
                      {doc.status === 'processed' && (
                        <span className="flex items-center">
                          <FaCheck className="mr-1" />
                          已处理
                        </span>
                      )}
                      {doc.status === 'failed' && (
                        <span className="flex items-center">
                          <FaTimes className="mr-1" />
                          失败
                        </span>
                      )}
                    </span>
                    
                    {doc.status === 'processed' && (
                      <button className="btn-primary text-sm">
                        开始问答
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 提示信息 */}
      <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <h3 className="font-medium text-blue-800 mb-2">使用说明</h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• 文档上传后会自动进行文本提取和向量化处理</li>
          <li>• 处理完成后即可进行智能问答</li>
          <li>• 支持同时上传多个文档</li>
          <li>• 处理状态会实时更新</li>
        </ul>
      </div>
    </div>
  );
};

export default DocumentUpload;