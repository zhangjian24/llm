import React from 'react';

interface ThinkingIndicatorProps {
  className?: string;
}

const ThinkingIndicator: React.FC<ThinkingIndicatorProps> = ({ className = '' }) => {
  return (
    <div className={`flex items-center space-x-1 ${className}`}>
      <span className="text-sm text-gray-500">AI 思考中</span>
      <div className="flex space-x-1">
        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
      </div>
    </div>
  );
};

export default ThinkingIndicator;