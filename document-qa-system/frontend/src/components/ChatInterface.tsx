import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { FaPaperPlane, FaRobot, FaUser, FaSpinner, FaLightbulb, FaBook } from 'react-icons/fa';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Source[];
}

interface Source {
  document_id: string;
  filename: string;
  content: string;
  score: number;
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInputValue(value);
    
    // 获取查询建议
    if (value.trim().length > 2) {
      getSuggestions(value.trim());
    } else {
      setSuggestions([]);
    }
  };

  const getSuggestions = async (query: string) => {
    try {
      const response = await axios.get(`/api/v1/chat/suggestions?prefix=${encodeURIComponent(query)}`);
      setSuggestions(response.data.suggestions || []);
    } catch (error) {
      console.error('获取建议失败:', error);
      setSuggestions([]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setSuggestions([]);
    setIsLoading(true);

    try {
      const response = await axios.post('/api/v1/chat/query', {
        query: userMessage.content,
        history: messages.slice(-5).map(msg => ({
          role: msg.role,
          content: msg.content,
          timestamp: msg.timestamp.toISOString()
        }))
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.answer,
        timestamp: new Date(),
        sources: response.data.sources
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('发送消息失败:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '抱歉，我遇到了一些问题。请稍后重试。',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion);
    setSuggestions([]);
  };

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-200px)] flex flex-col">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">智能问答</h1>
        <p className="text-gray-600">基于已上传文档的智能问答系统</p>
      </div>

      {/* 聊天历史 */}
      <div className="flex-1 overflow-y-auto mb-4 bg-white rounded-lg shadow-md border border-gray-200">
        <div className="p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <FaRobot className="mx-auto text-5xl text-gray-300 mb-4" />
              <h3 className="text-xl font-medium text-gray-500 mb-2">您好！我是文档问答助手</h3>
              <p className="text-gray-400">请上传文档后向我提问</p>
              
              <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <FaLightbulb className="text-blue-500 text-xl mb-2" />
                  <h4 className="font-medium text-blue-800 mb-1">使用技巧</h4>
                  <ul className="text-sm text-blue-600 space-y-1">
                    <li>• 上传相关文档</li>
                    <li>• 提出具体问题</li>
                    <li>• 查看引用来源</li>
                  </ul>
                </div>
                
                <div className="bg-green-50 p-4 rounded-lg">
                  <FaBook className="text-green-500 text-xl mb-2" />
                  <h4 className="font-medium text-green-800 mb-1">支持功能</h4>
                  <ul className="text-sm text-green-600 space-y-1">
                    <li>• 智能文档理解</li>
                    <li>• 语义相似度搜索</li>
                    <li>• 上下文对话</li>
                  </ul>
                </div>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`flex max-w-3xl ${message.role === 'user' ? 'flex-row-reverse' : ''}`}>
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                    message.role === 'user' ? 'bg-blue-500 ml-3' : 'bg-gray-300 mr-3'
                  }`}>
                    {message.role === 'user' ? (
                      <FaUser className="text-white text-sm" />
                    ) : (
                      <FaRobot className="text-gray-600 text-sm" />
                    )}
                  </div>
                  
                  <div className={`rounded-lg p-4 ${
                    message.role === 'user' 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    <div className="prose prose-sm max-w-none">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {message.content}
                      </ReactMarkdown>
                    </div>
                    
                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-opacity-20 border-white">
                        <p className="text-xs opacity-80 mb-2">参考文档：</p>
                        <div className="space-y-2">
                          {message.sources.slice(0, 2).map((source, index) => (
                            <div key={index} className="text-xs bg-black bg-opacity-10 p-2 rounded">
                              <p className="font-medium">{source.filename}</p>
                              <p className="opacity-80 mt-1 line-clamp-2">{source.content}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    <div className={`text-xs mt-2 ${
                      message.role === 'user' ? 'text-blue-200' : 'text-gray-500'
                    }`}>
                      {formatTimestamp(message.timestamp)}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex">
                <div className="w-8 h-8 rounded-full bg-gray-300 mr-3 flex items-center justify-center">
                  <FaRobot className="text-gray-600 text-sm" />
                </div>
                <div className="bg-gray-100 rounded-lg p-4">
                  <div className="flex items-center space-x-2">
                    <FaSpinner className="animate-spin text-gray-500" />
                    <span className="text-gray-500">正在思考...</span>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* 输入区域 */}
      <div className="relative">
        {/* 查询建议 */}
        {suggestions.length > 0 && (
          <div className="absolute bottom-full left-0 right-0 mb-2 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
            <div className="py-2">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full text-left px-4 py-2 hover:bg-gray-50 text-gray-700 text-sm transition-colors duration-150"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="flex space-x-3">
          <div className="flex-1 relative">
            <input
              type="text"
              value={inputValue}
              onChange={handleInputChange}
              placeholder="请输入您的问题..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-12"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isLoading}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 text-gray-400 hover:text-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <FaSpinner className="animate-spin" />
              ) : (
                <FaPaperPlane />
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;