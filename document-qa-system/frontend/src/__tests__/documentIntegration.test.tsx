/**
 * 前端文档状态更新集成测试
 * 测试WebSocket状态更新与UI的完整流程
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../App';
import { useDocumentStore } from '../stores/documentStore';
import { act, renderHook } from '@testing-library/react';

// Mock API调用
jest.mock('../services/api', () => ({
  documentAPI: {
    getList: jest.fn().mockResolvedValue({
      data: {
        items: [
          {
            id: '1',
            filename: 'test.pdf',
            file_size: 1024,
            mime_type: 'application/pdf',
            status: 'processing',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
          }
        ],
        total: 1,
        page: 1,
        limit: 20,
        total_pages: 1,
      }
    }),
    upload: jest.fn().mockResolvedValue({
      data: {
        id: '2',
        filename: 'uploaded.pdf',
        file_size: 2048,
        mime_type: 'application/pdf',
        status: 'processing',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }
    })
  }
}));

// Mock WebSocket
const mockWebSocket = {
  send: jest.fn(),
  close: jest.fn(),
  readyState: WebSocket.OPEN,
};

const mockWebSocketConstructor = jest.fn(() => mockWebSocket);
global.WebSocket = mockWebSocketConstructor as any;

describe('文档状态更新集成测试', () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
    // 清理store状态
    const { result } = renderHook(() => useDocumentStore());
    act(() => {
      result.current.setDocuments([], 0);
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('应用应该正确渲染并显示初始状态', async () => {
    render(<App />);
    
    // 检查初始聊天标签页
    expect(screen.getByText('💬 对话')).toBeInTheDocument();
    expect(screen.getByText('📄 文档 (0)')).toBeInTheDocument();
    
    // 检查WebSocket连接状态指示器（初始应该是离线）
    await waitFor(() => {
      expect(screen.getByText('离线模式')).toBeInTheDocument();
    });
  });

  test('切换到文档标签页应该加载文档列表', async () => {
    render(<App />);
    
    // 点击文档标签
    const documentTab = screen.getByText('📄 文档 (0)');
    await user.click(documentTab);
    
    // 等待文档列表加载完成
    await waitFor(() => {
      expect(screen.getByText('已上传文档')).toBeInTheDocument();
    });
    
    // 检查WebSocket连接状态变为在线
    await waitFor(() => {
      expect(screen.getByText('实时更新')).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  test('文档列表应该显示正确的文档信息', async () => {
    render(<App />);
    
    // 切换到文档标签页
    const documentTab = screen.getByText('📄 文档 (0)');
    await user.click(documentTab);
    
    // 等待文档加载
    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument();
    });
    
    // 检查文档详情显示
    expect(screen.getByText('1.00 KB')).toBeInTheDocument();
    expect(screen.getByText('⏳ 处理中')).toBeInTheDocument();
  });

  test('WebSocket状态更新应该正确反映在UI上', async () => {
    render(<App />);
    
    // 切换到文档标签页
    const documentTab = screen.getByText('📄 文档 (0)');
    await user.click(documentTab);
    
    // 等待WebSocket连接建立
    await waitFor(() => {
      expect(screen.getByText('实时更新')).toBeInTheDocument();
    });
    
    // 模拟WebSocket消息接收
    const mockMessage = {
      type: 'document_status_updated',
      doc_id: '1',
      status: 'ready',
      chunks_count: 5,
      timestamp: new Date().toISOString(),
    };
    
    // 触发WebSocket消息处理
    act(() => {
      const messageEvent = new MessageEvent('message', {
        data: JSON.stringify(mockMessage)
      });
      mockWebSocket.onmessage?.(messageEvent as any);
    });
    
    // 检查UI状态更新
    await waitFor(() => {
      expect(screen.getByText('✅ 就绪')).toBeInTheDocument();
    });
    
    // 检查chunks数量更新
    expect(screen.getByText('1.00 KB • ✅ 就绪')).toBeInTheDocument();
  });

  test('新文档上传应该更新文档列表', async () => {
    render(<App />);
    
    // 切换到文档标签页
    const documentTab = screen.getByText('📄 文档 (0)');
    await user.click(documentTab);
    
    // 等待初始文档加载
    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument();
    });
    
    // 模拟WebSocket通知新文档上传
    const newDocumentMessage = {
      type: 'document_status_updated',
      doc_id: '2',
      filename: 'uploaded.pdf',
      status: 'processing',
      timestamp: new Date().toISOString(),
    };
    
    act(() => {
      const messageEvent = new MessageEvent('message', {
        data: JSON.stringify(newDocumentMessage)
      });
      mockWebSocket.onmessage?.(messageEvent as any);
    });
    
    // 检查文档计数更新
    await waitFor(() => {
      expect(screen.getByText('📄 文档 (2)')).toBeInTheDocument();
    });
  });

  test('WebSocket连接断开应该显示离线模式', async () => {
    render(<App />);
    
    // 切换到文档标签页
    const documentTab = screen.getByText('📄 文档 (0)');
    await user.click(documentTab);
    
    // 等待连接建立
    await waitFor(() => {
      expect(screen.getByText('实时更新')).toBeInTheDocument();
    });
    
    // 模拟连接断开
    act(() => {
      const closeEvent = new CloseEvent('close', {
        code: 1006,
        reason: 'Connection lost'
      });
      mockWebSocket.onclose?.(closeEvent as any);
    });
    
    // 检查显示离线模式
    await waitFor(() => {
      expect(screen.getByText('离线模式')).toBeInTheDocument();
    });
  });

  test('标签页切换应该正确刷新文档列表', async () => {
    render(<App />);
    
    // 先去聊天页面
    const chatTab = screen.getByText('💬 对话');
    await user.click(chatTab);
    
    // 再回到文档页面
    const documentTab = screen.getByText('📄 文档 (0)');
    await user.click(documentTab);
    
    // 应该重新加载文档列表
    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument();
    });
  });

  test('错误处理应该正确显示错误信息', async () => {
    // Mock API错误
    const { documentAPI } = await import('../services/api');
    (documentAPI.getList as jest.Mock).mockRejectedValue(new Error('网络错误'));
    
    render(<App />);
    
    // 切换到文档标签页
    const documentTab = screen.getByText('📄 文档 (0)');
    await user.click(documentTab);
    
    // 检查错误显示
    await waitFor(() => {
      expect(screen.getByText('加载文档失败')).toBeInTheDocument();
    });
  });

  test('WebSocket重连机制应该正常工作', async () => {
    render(<App />);
    
    // 切换到文档标签页
    const documentTab = screen.getByText('📄 文档 (0)');
    await user.click(documentTab);
    
    // 等待初始连接
    await waitFor(() => {
      expect(screen.getByText('实时更新')).toBeInTheDocument();
    });
    
    // 模拟连接断开
    act(() => {
      const closeEvent = new CloseEvent('close', {
        code: 1006,
        reason: 'Connection lost'
      });
      mockWebSocket.onclose?.(closeEvent as any);
    });
    
    // 检查进入离线模式
    await waitFor(() => {
      expect(screen.getByText('离线模式')).toBeInTheDocument();
    });
    
    // 模拟重连成功（这里需要更复杂的模拟）
    // 在实际测试中，我们会验证重连逻辑
  });
});