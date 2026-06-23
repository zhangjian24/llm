import React, { useMemo } from 'react';
import { MarkdownRenderer } from './MarkdownRenderer';
import { useTypewriter } from '../hooks/useTypewriter';

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
  const displayed = useTypewriter(text, { speed });

  const memoDisplayed = useMemo(() => displayed, [displayed]);

  return (
    <div className={className} data-testid="type-writer">
      <MarkdownRenderer>{memoDisplayed}</MarkdownRenderer>
    </div>
  );
};

export default TypeWriterEffect;
