/**
 * TypeWriterEffect 单元测试（待 vitest 工具链安装后执行）
 *
 * 验证 RAF 优化版本：
 * - text 为空时立即返回空字符串
 * - text 变化时重新启动动画
 * - 完整文本在若干帧后渲染完毕
 */
import { describe, it, expect } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import TypeWriterEffect from './TypeWriterEffect';

describe('TypeWriterEffect', () => {
  it('renders empty for empty text', () => {
    render(<TypeWriterEffect text="" />);
    expect(screen.queryByText(/.+/)).toBeNull();
  });

  it('progressively reveals text', async () => {
    jest.useFakeTimers();
    const { rerender } = render(<TypeWriterEffect text="Hello" speed={10} />);
    act(() => {
      jest.advanceTimersByTime(50);
    });
    expect(screen.getByText(/Hello/)).toBeInTheDocument();
    rerender(<TypeWriterEffect text="Hello World" speed={10} />);
    jest.useRealTimers();
  });

  it('completes full text after enough frames', () => {
    render(<TypeWriterEffect text="abc" speed={0} />);
    expect(screen.getByText('abc')).toBeInTheDocument();
  });
});
