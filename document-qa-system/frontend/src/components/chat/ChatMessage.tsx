import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github.css';
import type { Message } from '../../types';

interface ChatMessageProps {
  message: Message;
}

// 提取 markdown 代码块中的内容
const extractMarkdownFromCodeBlock = (content: string): string => {
  // 匹配 ```markdown 代码块，支持多行内容
  const markdownCodeBlockRegex = /```markdown\s*\n([\s\S]*?)```/;
  const match = content.match(markdownCodeBlockRegex);
  if (match) {
    return match[1].trim();
  }
  return content;
};

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  
  // 如果是助手消息，尝试提取 markdown 代码块内容
  const displayContent = isUser ? message.content : extractMarkdownFromCodeBlock(message.content);

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-blue-500 text-white'
            : 'bg-gray-100 text-gray-900'
        }`}
      >
        <div className="text-sm font-medium mb-1">
          {isUser ? '我' : '助手'}
        </div>
        {isUser ? (
          <div className="whitespace-pre-wrap">{message.content}</div>
        ) : (
          <div className="markdown-content text-sm leading-relaxed">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeHighlight]}
            >
              {displayContent}
            </ReactMarkdown>
          </div>
        )}
        
        {message.sources && message.sources.length > 0 && (
          <div className="mt-2 text-xs opacity-75">
            引用来源：{message.sources.length} 个文档片段
          </div>
        )}
      </div>
    </div>
  );
};
