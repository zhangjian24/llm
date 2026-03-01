import React, { useState, useRef, useEffect } from 'react';
import { FiSend, FiLoader, FiBook, FiRefreshCw, FiSettings, FiCpu, FiBarChart2 } from 'react-icons/fi';
import { chatApi } from '../services/api';
import { QueryRequest, QueryResponse } from '../types';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: any[];
  confidence?: number;
}

interface ModelStatus {
  name: string;
  status: 'online' | 'offline' | 'loading';
  latency?: number;
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [modelStatus, setModelStatus] = useState<ModelStatus>({
    name: 'qwen-max',
    status: 'loading',
    latency: undefined
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const startTime = Date.now();
    
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);
    
    // 更新模型状态为处理中
    setModelStatus(prev => ({
      ...prev,
      status: 'loading'
    }));

    try {
      const request: QueryRequest = {
        query: userMessage.content,
        top_k: 5
      };

      const response: QueryResponse = await chatApi.queryDocuments(request);
      
      const endTime = Date.now();
      const latency = endTime - startTime;

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        sources: response.sources,
        confidence: response.confidence
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // 更新模型状态为在线并记录延迟
      setModelStatus(prev => ({
        ...prev,
        status: 'online',
        latency
      }));
      
    } catch (err: any) {
      setError(err.response?.data?.detail || '发送消息失败，请重试');
      // 更新模型状态为离线
      setModelStatus(prev => ({
        ...prev,
        status: 'offline'
      }));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString('zh-CN', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto">
      {/* 聊天头部 */}
      <div className="bg-white border-b border-gray-200 p-4 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">智能问答</h2>
          <p className="text-gray-600 text-sm">基于已上传文档进行智能问答</p>
        </div>
        <div className="flex items-center space-x-3">
          {/* 模型状态指示器 */}
          <div className="flex items-center space-x-2 px-3 py-1 bg-gray-100 rounded-lg">
            <div className={`w-2 h-2 rounded-full $ {
              modelStatus.status === 'online' ? 'bg-green-500' :
              modelStatus.status === 'loading' ? 'bg-yellow-500' :
              'bg-red-500'
            }`}></div>
            <span className="text-xs text-gray-600">
              {modelStatus.name}
            </span>
            {modelStatus.latency && (
              <span className="text-xs text-gray-500">
                {modelStatus.latency}ms
              </span>
            )}
          </div>
          
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="btn-secondary flex items-center space-x-2"
          >
            <FiSettings className="w-4 h-4" />
          </button>
          
          <button
            onClick={clearChat}
            className="btn-secondary flex items-center space-x-2"
          >
            <FiRefreshCw className="w-4 h-4" />
            <span>清空</span>
          </button>
        </div>
      </div>
      
      {/* 设置面板 */}
      {showSettings && (
        <div className="bg-white border-b border-gray-200 p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="flex items-center mb-2">
                <FiCpu className="w-5 h-5 text-blue-600 mr-2" />
                <h3 className="font-medium text-gray-900">模型配置</h3>
              </div>
              <div className="space-y-2 text-sm text-gray-600">
                <p>当前模型: {modelStatus.name}</p>
                <p>状态: {modelStatus.status === 'online' ? '在线' : modelStatus.status === 'loading' ? '处理中' : '离线'}</p>
                {modelStatus.latency && <p>平均延迟: {modelStatus.latency}ms</p>}
              </div>
            </div>
            
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="flex items-center mb-2">
                <FiBarChart2 className="w-5 h-5 text-green-600 mr-2" />
                <h3 className="font-medium text-gray-900">系统统计</h3>
              </div>
              <div className="space-y-2 text-sm text-gray-600">
                <p>对话轮次: {messages.length / 2}</p>
                <p>总字符数: {messages.reduce((acc, msg) => acc + msg.content.length, 0)}</p>
                <p>引用文档: {Array.from(new Set(messages.flatMap(msg => msg.sources?.map(s => s.document_id) || [])).values()).length}</p>
              </div>
            </div>
            
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="flex items-center mb-2">
                <FiSettings className="w-5 h-5 text-purple-600 mr-2" />
                <h3 className="font-medium text-gray-900">高级设置</h3>
              </div>
              <div className="space-y-2 text-sm text-gray-600">
                <p>Top-K: 5</p>
                <p>置信度阈值: 0.7</p>
                <p>最大上下文: 2048 tokens</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 消息区域 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <div className="bg-white rounded-lg p-8 max-w-md mx-auto shadow-sm">
              <FiBook className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">开始提问吧！</h3>
              <p className="text-gray-600">
                请输入您的问题，系统将基于已上传的文档为您提供准确的答案。
              </p>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-800 shadow-sm'
              }`}
            >
              <div className="whitespace-pre-wrap">{message.content}</div>
              
              {message.type === 'assistant' && message.confidence && (
                <div className="mt-2 pt-2 border-t border-gray-200 text-xs">
                  <span className="text-gray-500">
                    置信度: {(message.confidence * 100).toFixed(1)}%
                  </span>
                </div>
              )}
              
              {message.type === 'assistant' && message.sources && message.sources.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-200">
                  <p className="text-xs text-gray-500 mb-1">参考文档:</p>
                  <div className="space-y-1">
                    {message.sources.slice(0, 2).map((source, index) => (
                      <div key={index} className="text-xs text-gray-600 flex items-center">
                        <FiBook className="w-3 h-3 mr-1" />
                        <span className="truncate">{source.filename}</span>
                        <span className="ml-1 text-gray-400">
                          ({(source.score * 100).toFixed(0)}%)
                        </span>
                      </div>
                    ))}
                    {message.sources.length > 2 && (
                      <p className="text-xs text-gray-500">
                        +{message.sources.length - 2} 更多文档...
                      </p>
                    )}
                  </div>
                </div>
              )}
              
              <div className={`text-xs mt-1 ${
                message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
              }`}>
                {formatTime(message.timestamp)}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white px-4 py-2 rounded-lg shadow-sm">
              <div className="flex items-center space-x-2">
                <FiLoader className="animate-spin h-4 w-4 text-gray-500" />
                <span className="text-gray-600">正在思考...</span>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div className="bg-white border-t border-gray-200 p-4">
        <div className="flex space-x-2">
          <div className="flex-1 relative">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="输入您的问题..."
              className="input-field resize-none pr-12"
              rows={2}
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
              className="absolute right-2 bottom-2 bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <FiSend className="w-4 h-4" />
            </button>
          </div>
        </div>
        
        <div className="mt-2 text-xs text-gray-500">
          支持多轮对话，按 Enter 发送，Shift + Enter 换行
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;