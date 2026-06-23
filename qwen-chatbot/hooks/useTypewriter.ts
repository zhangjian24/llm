import { useState, useEffect, useRef } from 'react';

export function useTypewriter(fullText: string, options: { speed: number; chunkSize?: number }) {
  const [displayedText, setDisplayedText] = useState('');
  const fullTextRef = useRef(fullText);
  fullTextRef.current = fullText;
  const isFinished = useRef(false);
  const chunkSize = options.chunkSize || 1;

  useEffect(() => {
    let animationFrame: number;
    let lastUpdate = performance.now();

    const tick = (now: number) => {
      if (isFinished.current) return;

      if (now - lastUpdate >= options.speed) {
        setDisplayedText(prev => {
          if (prev.length < fullTextRef.current.length) {
            const nextLen = Math.min(prev.length + chunkSize, fullTextRef.current.length);
            const next = fullTextRef.current.slice(0, nextLen);
            if (next.length === fullTextRef.current.length) {
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

    if (fullText.length > 0) {
      isFinished.current = false;
      animationFrame = requestAnimationFrame(tick);
    } else {
      setDisplayedText('');
      isFinished.current = true;
    }
    
    return () => cancelAnimationFrame(animationFrame);
  }, [options.speed, chunkSize, fullText]);

  return displayedText;
}
