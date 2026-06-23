import React, { useEffect, useMemo, useRef } from 'react';
import { MarkdownRenderer } from './MarkdownRenderer';
import { useTypewriter } from '../hooks/useTypewriter';

interface TypeWriterEffectProps {
  text: string;
  speed?: number;
  instant?: boolean;
  onComplete?: () => void;
  className?: string;
}

function getChunkSize(total: number): number {
  if (total <= 50) return 1;
  if (total <= 200) return 5;
  return 20;
}

const TypeWriterEffect: React.FC<TypeWriterEffectProps> = ({
  text,
  speed = 50,
  instant = false,
  onComplete,
  className = '',
}) => {
  const onCompleteRef = useRef(onComplete);
  onCompleteRef.current = onComplete;

  const chunkSize = instant ? text.length : getChunkSize(text.length);
  const displayed = useTypewriter(instant ? '' : text, { speed, chunkSize });
  const displayText = instant ? text : displayed;

  useEffect(() => {
    if (instant) {
      onCompleteRef.current?.();
    } else if (displayed.length === text.length && text.length > 0) {
      onCompleteRef.current?.();
    }
  }, [displayed, text, instant]);

  const memoDisplayed = useMemo(() => displayText, [displayText]);

  return (
    <div className={className} data-testid="type-writer">
      <MarkdownRenderer>{memoDisplayed}</MarkdownRenderer>
    </div>
  );
};

export default TypeWriterEffect;