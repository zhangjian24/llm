/**
 * HistoryTable 组件单元测试
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { HistoryTable } from './HistoryTable';
import type { ConversationHistory } from '../types';

describe('HistoryTable', () => {
  const sampleItem: ConversationHistory = {
    id: 1,
    input: 'hello world',
    output: 'hi there',
    model: 'qwen-plus',
    params: { temperature: 0.7, top_p: 0.8, max_tokens: 1000 },
    tokenUsage: { prompt_tokens: 10, completion_tokens: 5, total_tokens: 15 },
    timestamp: '2026-01-01T00:00:00.000Z',
    evaluation: '',
  };

  it('空列表显示空提示', () => {
    render(<HistoryTable history={[]} onEvaluationChange={vi.fn()} />);
    expect(screen.getByText(/暂无对话历史/)).toBeInTheDocument();
  });

  it('渲染条目 input/output', () => {
    render(<HistoryTable history={[sampleItem]} onEvaluationChange={vi.fn()} />);
    expect(screen.getByText('hello world')).toBeInTheDocument();
    expect(screen.getByText('hi there')).toBeInTheDocument();
  });

  it('input 长于 30 字符时截断', () => {
    const long: ConversationHistory = {
      ...sampleItem,
      id: 2,
      input: 'a'.repeat(50),
    };
    render(<HistoryTable history={[long]} onEvaluationChange={vi.fn()} />);
    expect(screen.getByText(/^a+\.\.\.$/)).toBeInTheDocument();
  });
});
