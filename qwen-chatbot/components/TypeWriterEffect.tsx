import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface TypeWriterEffectProps {
  text: string;
  speed?: number;
  className?: string;
}

const TypeWriterEffect: React.FC<TypeWriterEffectProps> = ({ 
  text, 
  speed = 100,
  className = ''
}) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(true);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // 每次text变化时重置
    setDisplayedText('');
    setIsTyping(true);
    
    // 清除之前的定时器
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // 如果文本为空，直接返回
    if (!text) {
      setIsTyping(false);
      return;
    }

    // 开始打字
    let index = 0;
    const typeNextChar = () => {
      if (index < text.length) {
        const char = text[index];
        // 确保字符不是undefined
        if (char !== undefined && char !== null) {
          // 强制更新，避免React优化
          setDisplayedText(prev => prev + char);
        }
        index++;
        timeoutRef.current = setTimeout(typeNextChar, speed);
      } else {
        setIsTyping(false);
      }
    };

    timeoutRef.current = setTimeout(typeNextChar, speed);

    // 清理
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [text, speed]);

  return (
    <div className={`${className}`}>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {displayedText}
      </ReactMarkdown>
      {isTyping && <span className="animate-pulse ml-1">|</span>}
    </div>
  );
};

export default TypeWriterEffect;