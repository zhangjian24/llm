/**
 * TypeWriterEffect - 打字机效果（持续 RAF 循环版，修复 SSE 竞态）
 *
 * 关键设计（解决流式闪烁/全蹦 bug）：
 * - 使用 textRef/speedRef 存储最新 props，每次 render 同步更新（无重渲染）
 * - useEffect 依赖 []，仅挂载时启动一次 RAF 循环，**永不因 text 变化重启**
 * - RAF tick 内读取 textRef.current 获取最新文本，累积到 displayedRef
 * - lastUpdateRef 控制打字速度，与 text 变化完全解耦
 * - text 变空：同步重置 displayedRef
 * - text 变短：直接同步（不做动画回退）
 * - 组件卸载时才取消 RAF
 * - CHUNK_SIZE=1，speed=50ms（20 字符/秒，肉眼可见）
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
  const textRef = useRef(text);
  const speedRef = useRef(speed);
  const rafRef = useRef<number | null>(null);
  const lastUpdateRef = useRef(0);

  // 每次 render 同步更新 refs（同步操作，不触发重渲染）
  textRef.current = text;
  speedRef.current = speed;

  // 处理 text 变空或变短：同步重置/同步
  useEffect(() => {
    if (text === '') {
      displayedRef.current = '';
      setDisplayed('');
    } else if (displayedRef.current.length > text.length) {
      // text 变短：直接同步到新文本（不做动画回退）
      displayedRef.current = text;
      setDisplayed(text);
    }
  }, [text]);

  // 挂载时启动一次持续 RAF 循环，卸载时清理
  useEffect(() => {
    const tick = () => {
      const currentText = textRef.current;
      const currentSpeed = speedRef.current;

      // 文本为空：保持空状态，继续检查
      if (currentText === '') {
        rafRef.current = requestAnimationFrame(tick);
        return;
      }

      // 还有字符未显示：按速度累积
      if (displayedRef.current.length < currentText.length) {
        const now = performance.now();
        if (now - lastUpdateRef.current >= currentSpeed) {
          const nextLen = Math.min(
            displayedRef.current.length + CHUNK_SIZE,
            currentText.length
          );
          const next = currentText.slice(0, nextLen);
          displayedRef.current = next;
          setDisplayed(next);
          lastUpdateRef.current = now;
        }
      }

      // 无论是否已完成，持续调度下一帧（等待文本增长）
      rafRef.current = requestAnimationFrame(tick);
    };

    // 启动循环
    if (rafRef.current === null) {
      lastUpdateRef.current = performance.now();
      rafRef.current = requestAnimationFrame(tick);
    }

    // 仅组件卸载时清理
    return () => {
      if (rafRef.current !== null) {
        cancelAnimationFrame(rafRef.current);
        rafRef.current = null;
      }
    };
  }, []);

  const memoDisplayed = useMemo(() => displayed, [displayed]);

  return (
    <div className={className} data-testid="type-writer">
      <MarkdownRenderer>{memoDisplayed}</MarkdownRenderer>
    </div>
  );
};

export default TypeWriterEffect;