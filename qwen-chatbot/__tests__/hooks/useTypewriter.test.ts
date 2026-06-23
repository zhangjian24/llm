import { renderHook, act } from '@testing-library/react';
import { useTypewriter } from '../../hooks/useTypewriter';

test('should incrementally return text', () => {
    const { result } = renderHook(() => useTypewriter('hello', { speed: 50 }));
    // Wait for internal timer to advance
    act(() => { jest.advanceTimersByTime(100); });
    expect(result.current.length).toBeGreaterThan(0);
});

test('should stop when finished', () => {
    const { result } = renderHook(() => useTypewriter('a', { speed: 50 }));
    act(() => { jest.advanceTimersByTime(500); });
    expect(result.current).toBe('a');
});
