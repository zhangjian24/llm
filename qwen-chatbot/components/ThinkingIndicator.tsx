import React from 'react';

interface ThinkingIndicatorProps {
  className?: string;
}

const ThinkingIndicator: React.FC<ThinkingIndicatorProps> = ({ className = '' }) => {
  return (
    <div className={`flex items-center space-x-3 py-1 ${className}`}>
      <div className="flex space-x-1">
        <div className="w-3 h-3 bg-gradient-to-r from-blue-400 to-purple-500 rounded-full animate-pulse"></div>
        <div className="w-3 h-3 bg-gradient-to-r from-blue-400 to-purple-500 rounded-full animate-pulse" style={{ animationDelay: '0.3s' }}></div>
        <div className="w-3 h-3 bg-gradient-to-r from-blue-400 to-purple-500 rounded-full animate-pulse" style={{ animationDelay: '0.6s' }}></div>
      </div>
      <span className="text-gray-700 font-medium">AI 正在思考...</span>
    </div>
  );
};

export default ThinkingIndicator;