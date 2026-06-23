import { renderHook, act } from '@testing-library/react';
import { useTypewriter } from '../../hooks/useTypewriter';
import { vi } from 'vitest';

// Mock performance.now and requestAnimationFrame for tests
let now = 10000;
vi.stubGlobal('performance', {
    now: () => now,
});
vi.stubGlobal('requestAnimationFrame', (callback: FrameRequestCallback) => {
    return setTimeout(() => {
        now += 16;
        callback(now);
    }, 16);
});
vi.stubGlobal('cancelAnimationFrame', (id: number) => {
    clearTimeout(id);
});

test('should incrementally return text', () => {
    vi.useFakeTimers();
    // Advance timers to simulate rAF calls
    const { result } = renderHook(() => useTypewriter('hello', { speed: 50 }));
    
    // We need to advance time. 50ms per character, 100ms total = 2 characters.
    act(() => { vi.advanceTimersByTime(200); });
    expect(result.current.length).toBeGreaterThan(0);
});

test('should stop when finished', () => {
    vi.useFakeTimers();
    const { result } = renderHook(() => useTypewriter('a', { speed: 50 }));
    act(() => { vi.advanceTimersByTime(500); });
    expect(result.current).toBe('a');
});
