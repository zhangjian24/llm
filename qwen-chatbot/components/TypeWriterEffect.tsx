/**
 * TypeWriterEffect - 打字机效果（SSE 流式累积版）
 *
 * 关键设计（修复流式闪烁 bug）：
 * - useEffect 依赖 [text, speed]，**不**包含 displayed
 * - 用 displayedRef 跟踪动画进度，RAF tick 内**同时**更新 ref + setDisplayed
 * - text 变长：从 displayedRef.current.length 持续累积到 text.length（不重启）
 * - text 变短：直接同步（不做动画回退）
 * - text === displayedRef.current：跳过 RAF 调度（幂等保护）
 * - 每帧累积 1 个字符（CHUNK_SIZE=1，打字机效果）
 * - 速度默认 50ms/字符（20 字符/秒，肉眼明显）
 * - useMemo 缓存输出
 *
 * 测试：components/TypeWriterEffect.test.tsx
 */
import React, { useEffect, useRef, useState, useMemo } from 'react';
import { MarkdownRenderer } from './MarkdownRenderer';

const CHUNK_SIZE = 1;

interface TypeWriterEffectProps {
  text: string;
  speed?: number;
  className?: string;
}

const TypeWriterEffect: React.FC<TypeWriterEffectProps> = ({
  text,
  speed = 50,
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
