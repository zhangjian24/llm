import React, { useState, useEffect, useRef, useCallback } from 'react';
import styles from '../styles/TypeWriterEffect.module.css';

interface TypeWriterEffectProps {
  text: string;
  speed?: number; // 打字速度，毫秒
  onComplete?: () => void; // 完成时的回调函数
  className?: string; // 自定义类名
}

const TypeWriterEffect: React.FC<TypeWriterEffectProps> = ({
  text,
  speed = 20, // 打字速度，毫秒/字符
  onComplete,
  className = ''
}) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(true);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // 当文本变化时，开始打字效果
  useEffect(() => {
    if (text && text.length > displayedText.length) {
      setIsTyping(true);
      
      // 清除之前的定时器
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      
      // 逐字符添加
      let currentIndex = displayedText.length;
      const addChar = () => {
        if (currentIndex < text.length) {
          setDisplayedText(prev => prev + text[currentIndex]);
          currentIndex++;
          timeoutRef.current = setTimeout(addChar, speed);
        } else {
          // 打字完成
          setIsTyping(false);
          if (onComplete) {
            onComplete();
          }
        }
      };
      
      timeoutRef.current = setTimeout(addChar, speed);
    }
  }, [text, displayedText, speed, onComplete]);
  
  // 清理定时器
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return (
    <span className={`${styles.typeWriterText} ${className}`}>
      {displayedText}
      {isTyping && <span className={styles.cursor}>|</span>}
    </span>
  );
};

export default TypeWriterEffect;