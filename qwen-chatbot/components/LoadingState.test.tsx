/**
 * LoadingState 组件单元测试
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { LoadingState } from './LoadingState';

describe('LoadingState', () => {
  it('渲染默认 loading 文案', () => {
    render(<LoadingState />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('渲染自定义文案', () => {
    render(<LoadingState message="加载角色中..." />);
    expect(screen.getByText('加载角色中...')).toBeInTheDocument();
  });
});
