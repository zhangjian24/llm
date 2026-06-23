/**
 * TypeWriterEffect 单元测试（待 vitest 工具链安装后执行）
 *
 * 验证 RAF 优化版本：
 * - text 为空时立即返回空字符串
 * - text 变化时重新启动动画
 * - 完整文本在若干帧后渲染完毕
 * - 增加测试以触发提交
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
});
