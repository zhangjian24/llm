import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { DocumentUploadResponse } from '../../types';

interface UploadZoneProps {
  onUploadComplete?: (response: DocumentUploadResponse) => void;
  className?: string;
}

const UploadZone: React.FC<UploadZoneProps> = ({ 
  onUploadComplete,
  className = ''
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [progress, setProgress] = useState(0);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    
    const file = acceptedFiles[0];
    handleFileUpload(file);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/*': ['.txt', '.md', '.csv'],
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024 // 10MB
  });

  const handleFileUpload = async (file: File) => {
    setUploadStatus('uploading');
    setProgress(0);
    
    try {
      // 模拟上传进度
      const interval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(interval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // 这里会调用实际的上传API
      // 暂时使用模拟响应
      setTimeout(() => {
        clearInterval(interval);
        setProgress(100);
        
        const mockResponse: DocumentUploadResponse = {
          doc_id: 'mock-doc-' + Date.now(),
          filename: file.name,
          status: 'success',
          message: `文档 "${file.name}" 上传成功并已完成处理`
        };
        
        setUploadStatus('success');
        onUploadComplete?.(mockResponse);
        
        // 2秒后重置状态
        setTimeout(() => {
          setUploadStatus('idle');
          setProgress(0);
        }, 2000);
        
      }, 2000);
      
    } catch (error) {
      console.error('上传失败:', error);
      setUploadStatus('error');
      setProgress(0);
    }
  };

  const getStatusColor = () => {
    switch (uploadStatus) {
      case 'uploading': return 'blue';
      case 'success': return 'green';
      case 'error': return 'red';
      default: return 'gray';
    }
  };

  const getStatusIcon = () => {
    switch (uploadStatus) {
      case 'uploading': return '📤';
      case 'success': return '✅';
      case 'error': return '❌';
      default: return '📁';
    }
  };

  return (
    <div className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 ${
      isDragActive 
        ? 'border-blue-500 bg-blue-50' 
        : uploadStatus === 'idle' 
          ? 'border-gray-300 hover:border-gray-400' 
          : `border-${getStatusColor()}-500 bg-${getStatusColor()}-50`
    } ${className}`}>
      <div {...getRootProps()} className="cursor-pointer">
        <input {...getInputProps()} />
        
        <div className="text-4xl mb-4">
          {getStatusIcon()}
        </div>
        
        {uploadStatus === 'idle' && (
          <div>
            <p className="text-lg font-medium text-gray-700 mb-2">
              拖拽文件到这里或点击选择
            </p>
            <p className="text-sm text-gray-500">
              支持 PDF, DOC, DOCX, TXT, MD 等格式
            </p>
            <p className="text-xs text-gray-400 mt-1">
              最大文件大小: 10MB
            </p>
          </div>
        )}
        
        {uploadStatus === 'uploading' && (
          <div>
            <p className="text-lg font-medium text-blue-700 mb-4">
              正在上传文件...
            </p>
            <div className="w-full bg-blue-200 rounded-full h-2.5">
              <div 
                className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <p className="text-sm text-blue-600 mt-2">
              {progress}% 完成
            </p>
          </div>
        )}
        
        {uploadStatus === 'success' && (
          <div>
            <p className="text-lg font-medium text-green-700 mb-2">
              上传成功！
            </p>
            <p className="text-sm text-green-600">
              文档已准备就绪，可以开始提问了
            </p>
          </div>
        )}
        
        {uploadStatus === 'error' && (
          <div>
            <p className="text-lg font-medium text-red-700 mb-2">
              上传失败
            </p>
            <p className="text-sm text-red-600">
              请稍后重试或联系管理员
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadZone;