/**
 * TypeWriterEffect - 打字机效果（性能优化版）
 *
 * 改用 requestAnimationFrame + 字符累积：
 * - 每帧累积 CHUNK_SIZE 个字符（避免 setTimeout 频繁 re-render）
 * - 用 timeStamp 控制累积间隔（FRAME_INTERVAL 约 60fps）
 * - useMemo 缓存输出
 *
 * 测试：components/TypeWriterEffect.test.tsx（待 vitest 安装后执行）
 */
import React, { useEffect, useRef, useState, useMemo } from 'react';
import { MarkdownRenderer } from './MarkdownRenderer';

const CHUNK_SIZE = 3;

interface TypeWriterEffectProps {
  text: string;
  speed?: number;
  className?: string;
}

const TypeWriterEffect: React.FC<TypeWriterEffectProps> = ({
  text,
  speed = 30,
  className = '',
}) => {
  const [displayed, setDisplayed] = useState('');
  const displayedRef = useRef('');
  const rafRef = useRef<number | null>(null);
  const lastUpdateRef = useRef(0);

  useEffect(() => {
    if (text === '') {
      displayedRef.current = '';
      setDisplayed('');
      return;
    }
    if (displayedRef.current.length > text.length || displayedRef.current === text) {
      if (displayedRef.current !== text) {
        displayedRef.current = text;
        setDisplayed(text);
      }
      return;
    }
    let i = displayedRef.current.length;
    const tick = (timestamp: number) => {
      if (timestamp - lastUpdateRef.current >= speed) {
        i = Math.min(i + CHUNK_SIZE, text.length);
        const next = text.slice(0, i);
        displayedRef.current = next;
        setDisplayed(next);
        lastUpdateRef.current = timestamp;
      }
      if (i < text.length) {
        rafRef.current = requestAnimationFrame(tick);
      }
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => {
      if (rafRef.current !== null) {
        cancelAnimationFrame(rafRef.current);
      }
    };
  }, [text, speed]);

  const memoDisplayed = useMemo(() => displayed, [displayed]);

  return (
    <div className={className} data-testid="type-writer">
      <MarkdownRenderer>{memoDisplayed}</MarkdownRenderer>
    </div>
  );
};

export default TypeWriterEffect;
