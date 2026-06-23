import React, { useEffect, useRef, useState, useMemo } from 'react';
import { MarkdownRenderer } from './MarkdownRenderer';

interface TypeWriterEffectProps {
  text: string;
  speed?: number;
  instant?: boolean;
  onComplete?: () => void;
  className?: string;
}

function getChunkSize(remaining: number): number {
  if (remaining <= 50) return 1;
  if (remaining <= 200) return 5;
  return 20;
}

const TypeWriterEffect: React.FC<TypeWriterEffectProps> = ({
  text,
  speed = 50,
  instant = false,
  onComplete,
  className = '',
}) => {
  const [displayed, setDisplayed] = useState(instant ? text : '');
  const displayedRef = useRef(instant ? text : '');
  const textRef = useRef(text);
  const speedRef = useRef(speed);
  const instantRef = useRef(instant);
  const rafRef = useRef<number | null>(null);
  const lastUpdateRef = useRef(0);
  const completedRef = useRef(false);
  const onCompleteRef = useRef(onComplete);

  textRef.current = text;
  speedRef.current = speed;
  instantRef.current = instant;
  onCompleteRef.current = onComplete;

  useEffect(() => {
    completedRef.current = false;

    if (instant) {
      displayedRef.current = text;
      setDisplayed(text);
      completedRef.current = true;
      onCompleteRef.current?.();
      return;
    }

    if (text === '') {
      displayedRef.current = '';
      setDisplayed('');
      completedRef.current = true;
      return;
    }

    if (
      displayedRef.current.length > text.length ||
      !text.startsWith(displayedRef.current)
    ) {
      displayedRef.current = text;
      setDisplayed(text);
    }
  }, [text, instant]);

  useEffect(() => {
    if (instantRef.current) return;

    const tick = () => {
      if (instantRef.current) {
        rafRef.current = requestAnimationFrame(tick);
        return;
      }

      const currentText = textRef.current;

      if (displayedRef.current.length < currentText.length) {
        const now = performance.now();
        if (now - lastUpdateRef.current >= speedRef.current) {
          const remaining = currentText.length - displayedRef.current.length;
          const chunk = getChunkSize(remaining);
          const nextLen = Math.min(
            displayedRef.current.length + chunk,
            currentText.length
          );
          displayedRef.current = currentText.slice(0, nextLen);
          setDisplayed(displayedRef.current);
          lastUpdateRef.current = now;
        }
      }

      if (
        displayedRef.current.length >= currentText.length &&
        !completedRef.current
      ) {
        completedRef.current = true;
        onCompleteRef.current?.();
      }

      rafRef.current = requestAnimationFrame(tick);
    };

    lastUpdateRef.current = performance.now();
    rafRef.current = requestAnimationFrame(tick);

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