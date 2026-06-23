import { useState, useEffect, useRef } from 'react';

export function useTypewriter(fullText: string, options: { speed: number; chunkSize?: number }) {
  const [displayedText, setDisplayedText] = useState('');
  const fullTextRef = useRef(fullText);
  fullTextRef.current = fullText;
  const isFinished = useRef(false);
  const chunkSize = options.chunkSize || 1;

  const prevFullTextRef = useRef(fullText);
  if (fullText !== prevFullTextRef.current) {
    prevFullTextRef.current = fullText;
    if (displayedText.length > fullText.length || !fullText.startsWith(displayedText)) {
      setDisplayedText(fullText);
      isFinished.current = true;
    } else if (displayedText.length < fullText.length) {
      isFinished.current = false;
    }
  }

  useEffect(() => {
    let animationFrame: number;
    let lastUpdate = performance.now();

    if (fullText.length === 0) {
      setDisplayedText('');
      return;
    }

    if (isFinished.current) return;

    const tick = (now: number) => {
      if (isFinished.current) return;

      if (now - lastUpdate >= options.speed) {
        setDisplayedText(prev => {
          const currentText = fullTextRef.current;
          if (prev.length < currentText.length) {
            const nextLen = Math.min(prev.length + chunkSize, currentText.length);
            const next = currentText.slice(0, nextLen);
            if (next.length === currentText.length) {
              isFinished.current = true;
            }
            return next;
          }
          isFinished.current = true;
          return prev;
        });
        lastUpdate = now;
      }

      if (!isFinished.current) {
        animationFrame = requestAnimationFrame(tick);
      }
    };

    animationFrame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animationFrame);
  }, [options.speed, chunkSize, fullText]);

  return displayedText;
}
