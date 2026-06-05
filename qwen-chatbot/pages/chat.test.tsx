/**
 * ChatPage 单元测试（待 vitest 工具链安装后执行）
 *
 * 任务 15 验证：错误处理使用本地变量 userInput 而非已清空的 inputMessage
 * 场景：用户输入 "test input" → API 失败 → 历史记录仍保留原始输入
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ChatPage from './chat';

vi.mock('../contexts/ChatContext', () => ({
  useChatContext: () => ({
    state: {
      messages: [],
      conversationHistory: [],
      selectedRoleId: null,
      schemaVersion: 1,
    },
    dispatch: vi.fn(),
  }),
}));

vi.mock('../contexts/UIContext', () => ({
  useUIContext: () => ({
    isThinking: false,
    isGenerating: false,
    showHistoryModal: false,
    setIsThinking: vi.fn(),
    setIsGenerating: vi.fn(),
    setShowHistoryModal: vi.fn(),
  }),
}));

vi.mock('../contexts/RoleContext', () => ({
  useRoleContext: () => ({
    roles: [],
    loading: false,
    getDefaultRole: () => null,
    setDefaultRole: vi.fn(),
  }),
}));

vi.mock('../components/useAISettings', () => ({
  getStoredApiKey: () => 'mock-key',
}));

describe('ChatPage error path', () => {
  it('records user input in history when API errors', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('Network'));
    render(<ChatPage />);
    const textarea = screen.getByRole('textbox');
    fireEvent.change(textarea, { target: { value: 'test input' } });
    fireEvent.click(screen.getByRole('button', { name: /发送/ }));
    await waitFor(() => {
      expect(screen.getByText('test input')).toBeInTheDocument();
    });
  });
});
