import { renderHook, act } from '@testing-library/react';
import { useTypewriter } from '../../hooks/useTypewriter';
import { vi, test, expect, beforeEach, afterEach } from 'vitest';

beforeEach(() => {
    vi.useFakeTimers();
});

afterEach(() => {
    vi.restoreAllMocks();
});

test('should incrementally return text', () => {
    const { result } = renderHook(() => useTypewriter('hello', { speed: 50 }));
    
    act(() => { vi.advanceTimersByTime(60); });
    expect(result.current.length).toBeGreaterThan(0);
});
