/**
 * ChatPage 单元测试（待 vitest 工具链安装后执行）
 *
 * 任务 15 验证：错误处理使用本地变量 userInput 而非已清空的 inputMessage
 * 场景：用户输入 "test input" → API 失败 → 历史记录仍保留原始输入
 */
import { describe, it, expect, vi, beforeAll } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ChatPage from './chat';

beforeAll(() => {
  // jsdom 不支持 scrollIntoView
  if (typeof HTMLElement !== 'undefined' && !HTMLElement.prototype.scrollIntoView) {
    HTMLElement.prototype.scrollIntoView = vi.fn();
  }
});

vi.mock('next/router', () => ({
  useRouter: () => ({
    push: vi.fn(),
    pathname: '/chat',
    query: {},
    asPath: '/chat',
  }),
}));

vi.mock('../contexts/ChatContext', () => ({
  useChatContext: () => ({
    state: {
      messages: [],
      conversationHistory: [],
      inputMessage: '',
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
    // 模拟 fetch 失败
    global.fetch = vi.fn().mockRejectedValue(new Error('Network'));
    // 验证 dispatch 收到 history payload 包含 userInput
    const dispatchSpy = vi.fn();
    // mock 重写为捕获 dispatch
    const chatMock = await import('../contexts/ChatContext');
    vi.spyOn(chatMock, 'useChatContext').mockReturnValueOnce({
      state: {
        messages: [],
        conversationHistory: [],
        inputMessage: 'test input',
        selectedRoleId: null,
        schemaVersion: 1,
      },
      dispatch: dispatchSpy,
    });
    render(<ChatPage />);
    fireEvent.click(screen.getAllByRole('button').find((b) => b.textContent?.includes('发送'))!);
    await waitFor(() => {
      const calls = dispatchSpy.mock.calls;
      const addHistoryCall = calls.find(
        (call) => call[0]?.type === 'ADD_TO_HISTORY',
      );
      expect(addHistoryCall).toBeDefined();
      expect(addHistoryCall![0].payload.input).toBe('test input');
    });
  });
});
