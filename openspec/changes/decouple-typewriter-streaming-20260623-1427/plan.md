# Typewriter Decoupling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decouple `TypeWriterEffect` component from streaming data source, enabling smooth rendering regardless of API response speed.

**Architecture:** Use `useTypewriter` Hook to manage animation state independently, rendering buffered content from `messages`.

**Tech Stack:** React 19, TypeScript, Framer Motion (if available) or `requestAnimationFrame`.

--

## Global Constraints

- Must maintain typewriter animation even when streaming chunks arrive quickly.
- Must ensure `ChatWindow` component remains performant.

---

## Task 1: Create `useTypewriter` Hook

**Files:**
- Create: `qwen-chatbot/hooks/useTypewriter.ts`
- Test: `qwen-chatbot/__tests__/hooks/useTypewriter.test.ts`

**Interfaces:**
- Consumes: `fullText: string`, `speed: number`
- Produces: `displayedText: string`

- [ ] **Step 1: Write failing test**
```typescript
import { renderHook, act } from '@testing-library/react';
import { useTypewriter } from '../../hooks/useTypewriter';

test('should incrementally return text', () => {
    const { result } = renderHook(() => useTypewriter('hello', { speed: 50 }));
    // Wait for internal timer to advance
    act(() => { jest.advanceTimersByTime(100); });
    expect(result.current.length).toBeGreaterThan(0);
});
```

- [ ] **Step 2: Run test (verify fail)**

- [ ] **Step 3: Minimal implementation**
```typescript
import { useState, useEffect, useRef } from 'react';

export function useTypewriter(fullText: string, options: { speed: number }) {
  const [displayedText, setDisplayedText] = useState('');
  const fullTextRef = useRef(fullText);
  fullTextRef.current = fullText;

  useEffect(() => {
    let animationFrame: number;
    let lastUpdate = performance.now();

    const tick = (now: number) => {
      if (now - lastUpdate >= options.speed) {
        setDisplayedText(prev => {
          if (prev.length < fullTextRef.current.length) {
            return fullTextRef.current.slice(0, prev.length + 1);
          }
          return prev;
        });
        lastUpdate = now;
      }
      animationFrame = requestAnimationFrame(tick);
    };

    animationFrame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animationFrame);
  }, [options.speed]);

  return displayedText;
}
```

- [ ] **Step 4: Run test (verify pass)**

- [ ] **Step 5: Commit**
```bash
git add qwen-chatbot/hooks/useTypewriter.ts qwen-chatbot/__tests__/hooks/useTypewriter.test.ts
git commit -m "feat: add useTypewriter hook"
```

## Task 2: Refactor `TypeWriterEffect`

**Files:**
- Modify: `qwen-chatbot/components/TypeWriterEffect.tsx`

**Interfaces:**
- Consumes: `text: string`
- Produces: `<div>{MarkdownRenderer(text)}</div>`

- [ ] **Step 1: Refactor to simple component**
```tsx
import React from 'react';
import { MarkdownRenderer } from './MarkdownRenderer';
import { useTypewriter } from '../hooks/useTypewriter';

interface TypeWriterEffectProps {
  text: string;
  speed?: number;
  className?: string;
}

export const TypeWriterEffect: React.FC<TypeWriterEffectProps> = ({
  text,
  speed = 50,
  className = '',
}) => {
  const displayed = useTypewriter(text, { speed });
  return (
    <div className={className}>
      <MarkdownRenderer>{displayed}</MarkdownRenderer>
    </div>
  );
};
```

- [ ] **Step 2: Commit**
```bash
git add qwen-chatbot/components/TypeWriterEffect.tsx
git commit -m "refactor: typewritereffect component"
```

## Task 3: Update `ChatWindow`

**Files:**
- Modify: `qwen-chatbot/components/ChatWindow.tsx`

- [ ] **Step 1: Simplify ChatWindow logic**
Replace existing `TypeWriterEffect` usage with new component (it just receives text now).

- [ ] **Step 2: Run E2E test**
```bash
npx playwright test e2e/09-typewriter-animation.spec.ts
```

- [ ] **Step 3: Commit**
```bash
git add qwen-chatbot/components/ChatWindow.tsx
git commit -m "fix: chatwindow typewriter integration"
```
