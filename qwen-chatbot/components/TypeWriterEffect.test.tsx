/**
 * TypeWriterEffect 单元测试（待 vitest 工具链安装后执行）
 *
 * 验证 RAF 优化版本：
 * - text 为空时立即返回空字符串
 * - text 变化时重新启动动画
 * - 完整文本在若干帧后渲染完毕
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, act, waitFor } from '@testing-library/react';
import TypeWriterEffect from './TypeWriterEffect';

describe('TypeWriterEffect', () => {
  it('renders empty container for empty text', () => {
    const { container } = render(<TypeWriterEffect text="" />);
    expect(container.querySelector('div')).toBeInTheDocument();
  });

  it('progressively reveals text via RAF', async () => {
    const { rerender } = render(<TypeWriterEffect text="Hello" speed={10} />);
    // 等待 RAF tick 累积到完整文本
    await waitFor(
      () => {
        expect(screen.getByText(/Hello/)).toBeInTheDocument();
      },
      { timeout: 500 },
    );
    rerender(<TypeWriterEffect text="Hello World" speed={10} />);
  });

  it('reveals full text after RAF ticks', async () => {
    render(<TypeWriterEffect text="abc" speed={0} />);
    await waitFor(
      () => {
        // markdown 渲染可能包裹元素，用 container.textContent 验证
        const container = screen.getByTestId('type-writer');
        expect(container.textContent).toContain('abc');
      },
      { timeout: 500 },
    );
  });

  it('keeps displayed text growing without restart when text prop increases mid-stream', async () => {
    const { rerender, unmount } = render(<TypeWriterEffect text="Hello" speed={10} />);
    await waitFor(
      () => {
        expect(screen.getByTestId('type-writer').textContent).toContain('Hello');
      },
      { timeout: 500 },
    );
    // Buggy impl: rerender triggers useEffect -> setDisplayed('') -> displayed flashes empty
    // Fixed impl: displayedRef tracks progress, no clear, no restart
    rerender(<TypeWriterEffect text="Hello World" speed={10} />);
    // Flush effects synchronously
    await act(async () => {
      await Promise.resolve();
    });
    // With bug: displayed drops below 'Hello'.length (restarted from 0)
    // With fix: displayed >= 'Hello'.length (monotonic, never drops)
    const displayed = screen.getByTestId('type-writer').textContent ?? '';
    expect(displayed.length).toBeGreaterThanOrEqual('Hello'.length);
    // Wait for full accumulation
    await waitFor(
      () => {
        expect(screen.getByTestId('type-writer').textContent).toContain('Hello World');
      },
      { timeout: 2000 },
    );
    expect(screen.getByTestId('type-writer').textContent).toBe('Hello World');
    unmount();
  });

  it('synchronizes displayed text when text prop becomes shorter than already-shown', async () => {
    const { rerender, unmount } = render(<TypeWriterEffect text="Hello World" speed={10} />);
    await waitFor(
      () => {
        expect(screen.getByTestId('type-writer').textContent).toContain('Hello World');
      },
      { timeout: 500 },
    );
    // Use shorter text but still > CHUNK_SIZE (3) to catch intermediate animation frames
    rerender(<TypeWriterEffect text="Hi there" speed={10} />);
    await act(async () => {
      await Promise.resolve();
    });
    // With bug: animation restarts from '' and builds up (intermediate states)
    // With fix: immediately syncs to 'Hi there' (no animation, direct sync)
    const displayed = screen.getByTestId('type-writer').textContent ?? '';
    // Bug would show intermediate state (length < 8), fix shows full immediately
    expect(displayed).toBe('Hi there');
    unmount();
  });
});
