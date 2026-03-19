/**
 * 前端文档状态更新逻辑测试
 * 测试文档列表状态更新的核心功能
 */

import { useDocumentStore } from '../stores/documentStore';
import { act, renderHook } from '@testing-library/react';

// Mock WebSocket
global.WebSocket = jest.fn(() => ({
  send: jest.fn(),
  close: jest.fn(),
  readyState: WebSocket.OPEN,
})) as any;

describe('文档状态更新逻辑测试', () => {
  beforeEach(() => {
    // 重置store状态
    const { result } = renderHook(() => useDocumentStore());
    act(() => {
      result.current.setDocuments([], 0);
    });
  });

  test('应该能够初始化文档存储', () => {
    const { result } = renderHook(() => useDocumentStore());
    
    expect(result.current.documents).toEqual([]);
    expect(result.current.total).toBe(0);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  test('应该能够设置文档列表', () => {
    const { result } = renderHook(() => useDocumentStore());
    const mockDocuments = [
      {
        id: '1',
        filename: 'test.pdf',
        file_size: 1024,
        mime_type: 'application/pdf',
        status: 'processing' as const,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }
    ];

    act(() => {
      result.current.setDocuments(mockDocuments, 1);
    });

    expect(result.current.documents).toEqual(mockDocuments);
    expect(result.current.total).toBe(1);
    expect(result.current.isLoading).toBe(false);
  });

  test('应该能够添加新文档', () => {
    const { result } = renderHook(() => useDocumentStore());
    const newDocument = {
      id: '2',
      filename: 'new.docx',
      file_size: 2048,
      mime_type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      status: 'processing' as const,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };

    act(() => {
      result.current.addDocument(newDocument);
    });

    expect(result.current.documents).toHaveLength(1);
    expect(result.current.documents[0]).toEqual(newDocument);
    expect(result.current.total).toBe(1);
  });

  test('应该能够删除文档', () => {
    const { result } = renderHook(() => useDocumentStore());
    const documents = [
      {
        id: '1',
        filename: 'test1.pdf',
        file_size: 1024,
        mime_type: 'application/pdf',
        status: 'ready' as const,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: '2',
        filename: 'test2.pdf',
        file_size: 2048,
        mime_type: 'application/pdf',
        status: 'processing' as const,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }
    ];

    // 设置初始文档
    act(() => {
      result.current.setDocuments(documents, 2);
    });

    // 删除文档
    act(() => {
      result.current.removeDocument('1');
    });

    expect(result.current.documents).toHaveLength(1);
    expect(result.current.documents[0].id).toBe('2');
    expect(result.current.total).toBe(1);
  });

  test('应该能够更新文档状态', () => {
    const { result } = renderHook(() => useDocumentStore());
    const initialDocument = {
      id: '1',
      filename: 'test.pdf',
      file_size: 1024,
      mime_type: 'application/pdf',
      status: 'processing' as const,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };

    // 设置初始文档
    act(() => {
      result.current.setDocuments([initialDocument], 1);
    });

    // 更新状态
    act(() => {
      result.current.updateDocumentStatus('1', 'ready', 5);
    });

    const updatedDocument = result.current.documents[0];
    expect(updatedDocument.status).toBe('ready');
    expect(updatedDocument.chunks_count).toBe(5);
    expect(updatedDocument.updated_at).not.toBe(initialDocument.updated_at);
  });

  test('更新不存在的文档ID应该不改变状态', () => {
    const { result } = renderHook(() => useDocumentStore());
    const document = {
      id: '1',
      filename: 'test.pdf',
      file_size: 1024,
      mime_type: 'application/pdf',
      status: 'processing' as const,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };

    act(() => {
      result.current.setDocuments([document], 1);
    });

    const originalUpdatedAt = document.updated_at;
    
    act(() => {
      result.current.updateDocumentStatus('999', 'ready', 5);
    });

    expect(result.current.documents[0].status).toBe('processing');
    expect(result.current.documents[0].updated_at).toBe(originalUpdatedAt);
  });

  test('应该能够设置加载状态', () => {
    const { result } = renderHook(() => useDocumentStore());

    act(() => {
      result.current.setLoading(true);
    });

    expect(result.current.isLoading).toBe(true);

    act(() => {
      result.current.setLoading(false);
    });

    expect(result.current.isLoading).toBe(false);
  });

  test('应该能够设置错误状态', () => {
    const { result } = renderHook(() => useDocumentStore());
    const errorMessage = '测试错误信息';

    act(() => {
      result.current.setError(errorMessage);
    });

    expect(result.current.error).toBe(errorMessage);
    expect(result.current.isLoading).toBe(false);
  });

  test('多个操作应该正确组合', () => {
    const { result } = renderHook(() => useDocumentStore());
    
    // 添加文档
    act(() => {
      result.current.addDocument({
        id: '1',
        filename: 'test1.pdf',
        file_size: 1024,
        mime_type: 'application/pdf',
        status: 'processing' as const,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      });
    });

    // 更新状态
    act(() => {
      result.current.updateDocumentStatus('1', 'ready', 3);
    });

    // 添加更多文档
    act(() => {
      result.current.addDocument({
        id: '2',
        filename: 'test2.pdf',
        file_size: 2048,
        mime_type: 'application/pdf',
        status: 'processing' as const,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      });
    });

    expect(result.current.documents).toHaveLength(2);
    expect(result.current.documents[0].status).toBe('ready');
    expect(result.current.documents[1].status).toBe('processing');
    expect(result.current.total).toBe(2);
  });
});