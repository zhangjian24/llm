import { useState, useEffect, useRef } from 'react';

export function useTypewriter(fullText: string, options: { speed: number }) {
  const [displayedText, setDisplayedText] = useState('');
  const fullTextRef = useRef(fullText);
  fullTextRef.current = fullText;

  useEffect(() => {
    let timeout: NodeJS.Timeout;
    const updateText = () => {
      setDisplayedText(prev => {
        if (prev.length < fullTextRef.current.length) {
          return fullTextRef.current.slice(0, prev.length + 1);
        }
        return prev;
      });
      timeout = setTimeout(updateText, options.speed);
    };

    timeout = setTimeout(updateText, options.speed);
    return () => clearTimeout(timeout);
  }, [options.speed]);

  return displayedText;
}
