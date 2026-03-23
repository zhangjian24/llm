import React from 'react';
import type { Conversation } from '../../types';

interface ConversationItemProps {
  conversation: Conversation;
  isActive: boolean;
  onClick: () => void;
  onDelete: () => void;
}

export const ConversationItem: React.FC<ConversationItemProps> = ({
  conversation,
  isActive,
  onClick,
  onDelete,
}) => {
  // 格式化时间显示
  const formatTime = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diffInDays === 0) {
      return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    } else if (diffInDays === 1) {
      return '昨天';
    } else if (diffInDays < 7) {
      return `${diffInDays}天前`;
    } else {
      return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
    }
  };

  // 截断标题
  const truncateTitle = (title: string, maxLength: number = 20): string => {
    if (title.length <= maxLength) return title;
    return title.slice(0, maxLength) + '...';
  };

  // 截断最后消息预览
  const truncateMessage = (message: string | undefined, maxLength: number = 30): string => {
    if (!message) return '';
    if (message.length <= maxLength) return message;
    return message.slice(0, maxLength) + '...';
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('确定要删除这个对话吗？')) {
      onDelete();
    }
  };

  return (
    <div
      onClick={onClick}
      className={`
        group relative p-3 rounded-lg cursor-pointer transition-all duration-200
        ${isActive 
          ? 'bg-blue-100 dark:bg-blue-900/30 border-l-4 border-blue-500' 
          : 'hover:bg-gray-100 dark:hover:bg-gray-800 border-l-4 border-transparent'
        }
      `}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <h3 className={`
            text-sm font-medium truncate
            ${isActive ? 'text-blue-700 dark:text-blue-300' : 'text-gray-800 dark:text-gray-200'}
          `}>
            {truncateTitle(conversation.title)}
          </h3>
          {conversation.last_message && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 truncate">
              {truncateMessage(conversation.last_message)}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2 ml-2">
          <span className="text-xs text-gray-400 dark:text-gray-500">
            {formatTime(conversation.updated_at)}
          </span>
          {/* 删除按钮 - 悬停时显示 */}
          <button
            onClick={handleDelete}
            className="
              opacity-0 group-hover:opacity-100
              p-1 rounded hover:bg-red-100 dark:hover:bg-red-900/30
              text-gray-400 hover:text-red-500
              transition-all duration-200
            "
            title="删除对话"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
      
      {/* 对话轮数指示器 */}
      {conversation.turns > 0 && (
        <div className="mt-2 flex items-center">
          <span className="
            text-xs px-2 py-0.5 rounded-full
            bg-gray-100 dark:bg-gray-700
            text-gray-500 dark:text-gray-400
          ">
            {conversation.turns} 轮对话
          </span>
        </div>
      )}
    </div>
  );
};
