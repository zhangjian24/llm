import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DocumentList } from '../components/documents/DocumentList';

interface Document {
  id: string;
  filename: string;
  file_size: number;
  mime_type: string;
  status: 'processing' | 'ready' | 'failed';
  chunks_count?: number;
  created_at: string;
  updated_at: string;
}

// Mock document data
const mockDocuments: Document[] = [
  {
    id: 'doc-1',
    filename: 'test-document-1.pdf',
    file_size: 1024000,
    mime_type: 'application/pdf',
    status: 'ready',
    chunks_count: 15,
    created_at: '2024-01-15T10:30:00Z',
    updated_at: '2024-01-15T10:35:00Z',
  },
  {
    id: 'doc-2',
    filename: 'test-document-2.docx',
    file_size: 2048576,
    mime_type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    status: 'processing',
    chunks_count: undefined,
    created_at: '2024-01-15T11:00:00Z',
    updated_at: '2024-01-15T11:00:00Z',
  },
  {
    id: 'doc-3',
    filename: 'test-document-3.txt',
    file_size: 512,
    mime_type: 'text/plain',
    status: 'failed',
    chunks_count: 0,
    created_at: '2024-01-15T09:00:00Z',
    updated_at: '2024-01-15T09:05:00Z',
  },
];

describe('DocumentList Component', () => {
  describe('Rendering', () => {
    test('应该渲染加载状态', () => {
      render(
        <DocumentList
          documents={[]}
          isLoading={true}
          onDelete={async () => {}}
          onReprocess={async () => {}}
        />
      );

      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });

    test('应该渲染空列表状态', () => {
      render(
        <DocumentList
          documents={[]}
          isLoading={false}
          onDelete={async () => {}}
          onReprocess={async () => {}}
        />
      );

      expect(screen.getByText('暂无文档')).toBeInTheDocument();
    });

    test('应该渲染文档列表', () => {
      render(
        <DocumentList
          documents={mockDocuments}
          isLoading={false}
          onDelete={async () => {}}
          onReprocess={async () => {}}
        />
      );

      expect(screen.getByTestId('document-list-table')).toBeInTheDocument();
      // 验证所有文档行都存在
      expect(screen.getByTestId('document-row-doc-1')).toBeInTheDocument();
      expect(screen.getByTestId('document-row-doc-2')).toBeInTheDocument();
      expect(screen.getByTestId('document-row-doc-3')).toBeInTheDocument();
    });
  });

  describe('Document Display', () => {
    test('应该显示文档文件名', () => {
      render(
        <DocumentList
          documents={mockDocuments}
          isLoading={false}
          onDelete={async () => {}}
          onReprocess={async () => {}}
        />
      );

      expect(screen.getByText('test-document-1.pdf')).toBeInTheDocument();
      expect(screen.getByText('test-document-2.docx')).toBeInTheDocument();
      expect(screen.getByText('test-document-3.txt')).toBeInTheDocument();
    });

    test('应该显示文件大小（格式化后）', () => {
      render(
        <DocumentList
          documents={mockDocuments}
          isLoading={false}
          onDelete={async () => {}}
          onReprocess={async () => {}}
        />
      );

      // 1024000 bytes = 1000 KB (formatFileSize uses base-1024)
      expect(screen.getByText('1000 KB')).toBeInTheDocument();
      // 2048576 bytes = 1.95 MB
      expect(screen.getByText('1.95 MB')).toBeInTheDocument();
      // 512 bytes
      expect(screen.getByText('512 B')).toBeInTheDocument();
    });

    test('应该显示文件类型标签', () => {
      render(
        <DocumentList
          documents={mockDocuments}
          isLoading={false}
          onDelete={async () => {}}
          onReprocess={async () => {}}
        />
      );

      expect(screen.getByText('PDF')).toBeInTheDocument();
      expect(screen.getByText('Word')).toBeInTheDocument();
      expect(screen.getByText('TXT')).toBeInTheDocument();
    });

    test('应该显示状态标签', () => {
      render(
        <DocumentList
          documents={mockDocuments}
          isLoading={false}
          onDelete={async () => {}}
          onReprocess={async () => {}}
        />
      );

      expect(screen.getAllByTestId('status-badge')).toHaveLength(3);
      // 使用包含 emoji 的完整文本
      expect(screen.getByText('✅ 就绪')).toBeInTheDocument();
      expect(screen.getByText('⏳ 处理中')).toBeInTheDocument();
      expect(screen.getByText('❌ 失败')).toBeInTheDocument();
    });

    test('应该显示块数', () => {
      render(
        <DocumentList
          documents={mockDocuments}
          isLoading={false}
          onDelete={async () => {}}
          onReprocess={async () => {}}
        />
      );

      expect(screen.getByText('15')).toBeInTheDocument();
      expect(screen.getByText('0')).toBeInTheDocument();
      // null 值应该显示 '-'
      expect(screen.getByText('-')).toBeInTheDocument();
    });

    test('应该显示上传时间（格式化后）', () => {
      render(
        <DocumentList
          documents={mockDocuments}
          isLoading={false}
          onDelete={async () => {}}
          onReprocess={async () => {}}
        />
      );

      // 验证时间是否被渲染（具体格式取决于本地化设置）
      const timeElements = screen.getAllByText(/2024/);
      expect(timeElements.length).toBeGreaterThan(0);
    });
  });

  describe('Delete Functionality', () => {
    beforeEach(() => {
      // Mock window.confirm
      window.confirm = jest.fn(() => true);
    });

    afterEach(() => {
      jest.restoreAllMocks();
    });

    test('应该调用 onDelete 当点击删除按钮', async () => {
      const handleDelete = jest.fn().mockResolvedValue(undefined);
      
      render(
        <DocumentList
          documents={mockDocuments}
          isLoading={false}
          onDelete={handleDelete}
          onReprocess={async () => {}}
        />
      );

      const deleteButtons = screen.getAllByTestId('delete-button');
      await userEvent.click(deleteButtons[0]);

      await waitFor(() => {
        expect(handleDelete).toHaveBeenCalledWith('doc-1');
      });
    });

    test('删除按钮应该有正确的测试 ID', () => {
      render(
        <DocumentList
          documents={mockDocuments}
          isLoading={false}
          onDelete={async () => {}}
          onReprocess={async () => {}}
        />
      );

      const deleteButtons = screen.getAllByTestId('delete-button');
      expect(deleteButtons).toHaveLength(3);
    });
  });

  describe('Reprocess Functionality', () => {
    test('应该调用 onReprocess 当点击重新处理按钮', async () => {
      const handleReprocess = jest.fn().mockResolvedValue(undefined);
      
      render(
        <DocumentList
          documents={mockDocuments}
          isLoading={false}
          onDelete={async () => {}}
          onReprocess={handleReprocess}
        />
      );

      const reprocessButtons = screen.getAllByTestId('reprocess-button');
      await userEvent.click(reprocessButtons[0]);

      await waitFor(() => {
        expect(handleReprocess).toHaveBeenCalledWith('doc-1');
      });
    });

    test('处理中的文档应该禁用重新处理按钮', () => {
      render(
        <DocumentList
          documents={mockDocuments}
          isLoading={false}
          onDelete={async () => {}}
          onReprocess={async () => {}}
        />
      );

      const processingRow = screen.getByTestId('document-row-doc-2');
      const reprocessButton = processingRow.querySelector('[data-testid="reprocess-button"]');
      
      expect(reprocessButton).toBeDisabled();
    });

    test('非处理中的文档应该启用重新处理按钮', () => {
      render(
        <DocumentList
          documents={mockDocuments}
          isLoading={false}
          onDelete={async () => {}}
          onReprocess={async () => {}}
        />
      );

      const readyRow = screen.getByTestId('document-row-doc-1');
      const reprocessButton = readyRow.querySelector('[data-testid="reprocess-button"]');
      
      expect(reprocessButton).not.toBeDisabled();
    });
  });

  describe('Helper Functions', () => {
    describe('formatFileSize', () => {
      test('应该格式化字节大小为可读格式', () => {
        render(
          <DocumentList
            documents={[{
              ...mockDocuments[0],
              file_size: 0,
            }]}
            isLoading={false}
            onDelete={async () => {}}
            onReprocess={async () => {}}
          />
        );

        expect(screen.getByText('0 B')).toBeInTheDocument();
      });

      test('应该正确处理 KB 单位', () => {
        render(
          <DocumentList
            documents={[{
              ...mockDocuments[0],
              file_size: 1536, // 1.5 KB
            }]}
            isLoading={false}
            onDelete={async () => {}}
            onReprocess={async () => {}}
          />
        );

        expect(screen.getByText(/1.5 KB/i)).toBeInTheDocument();
      });

      test('应该正确处理 MB 单位', () => {
        render(
          <DocumentList
            documents={[{
              ...mockDocuments[0],
              file_size: 1572864, // 1.5 MB
            }]}
            isLoading={false}
            onDelete={async () => {}}
            onReprocess={async () => {}}
          />
        );

        expect(screen.getByText(/1.5 MB/i)).toBeInTheDocument();
      });
    });

    describe('getMimeTypeLabel', () => {
      test('应该显示 PDF 标签', () => {
        render(
          <DocumentList
            documents={[{
              ...mockDocuments[0],
              mime_type: 'application/pdf',
            }]}
            isLoading={false}
            onDelete={async () => {}}
            onReprocess={async () => {}}
          />
        );

        expect(screen.getByText('PDF')).toBeInTheDocument();
      });

      test('应该显示 Word 标签', () => {
        render(
          <DocumentList
            documents={[{
              ...mockDocuments[0],
              mime_type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            }]}
            isLoading={false}
            onDelete={async () => {}}
            onReprocess={async () => {}}
          />
        );

        expect(screen.getByText('Word')).toBeInTheDocument();
      });

      test('应该显示 TXT 标签', () => {
        render(
          <DocumentList
            documents={[{
              ...mockDocuments[0],
              mime_type: 'text/plain',
            }]}
            isLoading={false}
            onDelete={async () => {}}
            onReprocess={async () => {}}
          />
        );

        expect(screen.getByText('TXT')).toBeInTheDocument();
      });

      test('应该为未知 MIME 类型显示扩展名', () => {
        render(
          <DocumentList
            documents={[{
              ...mockDocuments[0],
              mime_type: 'image/png',
            }]}
            isLoading={false}
            onDelete={async () => {}}
            onReprocess={async () => {}}
          />
        );

        expect(screen.getByText('PNG')).toBeInTheDocument();
      });
    });

    describe('formatDate', () => {
      test('应该格式化日期字符串', () => {
        render(
          <DocumentList
            documents={mockDocuments}
            isLoading={false}
            onDelete={async () => {}}
            onReprocess={async () => {}}
          />
        );

        // 验证日期元素存在（具体格式取决于本地化）
        const dateElements = screen.getAllByText(/\d{4}/);
        expect(dateElements.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Table Structure', () => {
    test('应该包含所有必需的表头', () => {
      render(
        <DocumentList
          documents={mockDocuments}
          isLoading={false}
          onDelete={async () => {}}
          onReprocess={async () => {}}
        />
      );

      expect(screen.getByText('文件名')).toBeInTheDocument();
      expect(screen.getByText('大小')).toBeInTheDocument();
      expect(screen.getByText('类型')).toBeInTheDocument();
      expect(screen.getByText('状态')).toBeInTheDocument();
      expect(screen.getByText('块数')).toBeInTheDocument();
      expect(screen.getByText('上传时间')).toBeInTheDocument();
      expect(screen.getByText('操作')).toBeInTheDocument();
    });

    test('表格应该有正确的测试 ID', () => {
      render(
        <DocumentList
          documents={mockDocuments}
          isLoading={false}
          onDelete={async () => {}}
          onReprocess={async () => {}}
        />
      );

      expect(screen.getByTestId('document-list-table')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    test('每行文档应该有正确的测试 ID', () => {
      render(
        <DocumentList
          documents={mockDocuments}
          isLoading={false}
          onDelete={async () => {}}
          onReprocess={async () => {}}
        />
      );

      expect(screen.getByTestId('document-row-doc-1')).toBeInTheDocument();
      expect(screen.getByTestId('document-row-doc-2')).toBeInTheDocument();
      expect(screen.getByTestId('document-row-doc-3')).toBeInTheDocument();
    });

    test('操作按钮应该有无障碍标签', () => {
      render(
        <DocumentList
          documents={mockDocuments}
          isLoading={false}
          onDelete={async () => {}}
          onReprocess={async () => {}}
        />
      );

      const deleteButtons = screen.getAllByTestId('delete-button');
      const reprocessButtons = screen.getAllByTestId('reprocess-button');

      deleteButtons.forEach(button => {
        expect(button).toHaveTextContent('删除');
      });

      reprocessButtons.forEach((button, index) => {
        if (index !== 1) { // 跳过处理中的文档
          expect(button).toHaveTextContent('重新处理');
        }
      });
    });
  });
});
