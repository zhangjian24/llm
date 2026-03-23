import { render, screen, waitFor } from '@testing-library/react';
import { DocumentsPage } from '../pages/DocumentsPage';
import { useDocumentStore } from '../stores/documentStore';
import { documentAPI } from '../services/api';

// Mock API
jest.mock('../services/api', () => ({
  documentAPI: {
    getList: jest.fn(),
    delete: jest.fn(),
    reprocess: jest.fn(),
  },
}));

// 声明 global 类型
declare const global: typeof globalThis & {
  confirm: typeof confirm;
  WebSocket: typeof WebSocket;
};

describe('DocumentsPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // 重置 store 状态
    useDocumentStore.setState({
      documents: [],
      total: 0,
      page: 1,
      limit: 20,
      isLoading: false,
      error: null,
      statusFilter: '',
    });
  });

  test('应该加载并显示文档列表', async () => {
    // Arrange
    const mockDocs = [
      {
        id: 'doc-1',
        filename: 'test.pdf',
        file_size: 1024,
        mime_type: 'application/pdf',
        status: 'ready',
        chunks_count: 15,
        created_at: '2024-01-15T10:30:00Z',
        updated_at: '2024-01-15T10:35:00Z',
      },
    ];
    
    (documentAPI.getList as jest.Mock).mockResolvedValue({
      data: {
        total: 1,
        items: mockDocs,
        page: 1,
        limit: 20,
        total_pages: 1,
      },
    });

    // Act
    render(<DocumentsPage />);
    
    // Assert
    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument();
    });
    
    expect(screen.getByText('文档管理')).toBeInTheDocument();
    expect(screen.getByText('共 1 个文档')).toBeInTheDocument();
  });

  test('应该显示空状态提示', async () => {
    // Arrange
    (documentAPI.getList as jest.Mock).mockResolvedValue({
      data: {
        total: 0,
        items: [],
        page: 1,
        limit: 20,
        total_pages: 1,
      },
    });

    // Act
    render(<DocumentsPage />);
    
    // Assert
    await waitFor(() => {
      expect(screen.getByText('暂无文档')).toBeInTheDocument();
    });
  });

  test('应该显示加载状态', () => {
    // Arrange
    useDocumentStore.setState({ isLoading: true });
    
    // Act
    render(<DocumentsPage />);
    
    // Assert
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  test('应该处理删除操作', async () => {
    // Arrange
    const mockDocs = [
      {
        id: 'doc-1',
        filename: 'test.pdf',
        file_size: 1024,
        mime_type: 'application/pdf',
        status: 'ready',
        chunks_count: 15,
        created_at: '2024-01-15T10:30:00Z',
        updated_at: '2024-01-15T10:35:00Z',
      },
    ];
    
    (documentAPI.getList as jest.Mock).mockResolvedValue({
      data: {
        total: 1,
        items: mockDocs,
        page: 1,
        limit: 20,
        total_pages: 1,
      },
    });
    
    (documentAPI.delete as jest.Mock).mockResolvedValue(undefined);

    render(<DocumentsPage />);
    
    // Wait for document to load
    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument();
    });

    // Act
    const deleteButton = screen.getByTestId('delete-button');
    deleteButton.click();
    
    // Assert
    await waitFor(() => {
      expect(documentAPI.delete).toHaveBeenCalledWith('doc-1');
    });
  });

  test('应该处理状态筛选', async () => {
    // Arrange
    (documentAPI.getList as jest.Mock).mockResolvedValue({
      data: {
        total: 0,
        items: [],
        page: 1,
        limit: 20,
        total_pages: 1,
      },
    });

    render(<DocumentsPage />);
    
    // Act
    const statusFilter = screen.getByTestId('status-filter');
    const userEvent = (await import('@testing-library/user-event')).default;
    await userEvent.selectOptions(statusFilter, 'failed');
    
    // Assert
    expect(documentAPI.getList).toHaveBeenCalledWith(1, 20, 'failed');
  });

  test('应该显示分页控件', async () => {
    // Arrange
    const mockDocs = Array(25).fill(null).map((_, i) => ({
      id: `doc-${i}`,
      filename: `test-${i}.pdf`,
      file_size: 1024,
      mime_type: 'application/pdf',
      status: 'ready',
      chunks_count: 15,
      created_at: '2024-01-15T10:30:00Z',
      updated_at: '2024-01-15T10:35:00Z',
    }));
    
    (documentAPI.getList as jest.Mock).mockResolvedValue({
      data: {
        total: 25,
        items: mockDocs,
        page: 1,
        limit: 20,
        total_pages: 2,
      },
    });

    render(<DocumentsPage />);
    
    // Assert
    await waitFor(() => {
      expect(screen.getByTestId('pagination-controls')).toBeInTheDocument();
      expect(screen.getByText('第 1 页，共 2 页')).toBeInTheDocument();
    });
  });

  test('应该禁用上一页按钮（第一页）', async () => {
    // Arrange
    const mockDocs = Array(5).fill(null).map((_, i) => ({
      id: `doc-${i}`,
      filename: `test-${i}.pdf`,
      file_size: 1024,
      mime_type: 'application/pdf',
      status: 'ready',
      chunks_count: 15,
      created_at: '2024-01-15T10:30:00Z',
      updated_at: '2024-01-15T10:35:00Z',
    }));
    
    (documentAPI.getList as jest.Mock).mockResolvedValue({
      data: {
        total: 5,
        items: mockDocs,
        page: 1,
        limit: 20,
        total_pages: 1,
      },
    });

    render(<DocumentsPage />);
    
    // Assert
    await waitFor(() => {
      const prevButton = screen.getByTestId('prev-page-button');
      expect(prevButton).toBeDisabled();
    });
  });
});
