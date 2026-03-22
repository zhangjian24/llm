import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DocumentFilters } from '../components/documents/DocumentFilters';

describe('DocumentFilters', () => {
  const mockOnStatusChange = jest.fn();
  const mockOnRefresh = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  const renderComponent = (statusFilter = '') => {
    return render(
      <DocumentFilters
        statusFilter={statusFilter}
        onStatusChange={mockOnStatusChange}
        onRefresh={mockOnRefresh}
      />
    );
  };

  describe('渲染测试', () => {
    test('应该正确渲染筛选器容器', () => {
      renderComponent();
      
      expect(screen.getByTestId('document-filters')).toBeInTheDocument();
    });

    test('应该显示状态筛选标签', () => {
      renderComponent();
      
      expect(screen.getByText('状态筛选：')).toBeInTheDocument();
    });

    test('应该渲染状态下拉选择框', () => {
      renderComponent();
      
      const select = screen.getByTestId('status-filter');
      expect(select).toBeInTheDocument();
    });

    test('应该渲染刷新按钮', () => {
      renderComponent();
      
      expect(screen.getByTestId('refresh-button')).toBeInTheDocument();
    });

    test('刷新按钮应该包含刷新图标和文字', () => {
      renderComponent();
      
      const button = screen.getByTestId('refresh-button');
      expect(button).toHaveTextContent('刷新');
    });
  });

  describe('状态下拉选项测试', () => {
    test('应该包含"全部"选项', () => {
      renderComponent();
      
      const allOption = screen.getByRole('option', { name: '全部' });
      
      expect(allOption).toBeInTheDocument();
      expect(allOption).toHaveValue('');
    });

    test('应该包含"处理中"选项', () => {
      renderComponent();
      
      const processingOption = screen.getByRole('option', { name: '处理中' });
      
      expect(processingOption).toBeInTheDocument();
      expect(processingOption).toHaveValue('processing');
    });

    test('应该包含"就绪"选项', () => {
      renderComponent();
      
      const readyOption = screen.getByRole('option', { name: '就绪' });
      
      expect(readyOption).toBeInTheDocument();
      expect(readyOption).toHaveValue('ready');
    });

    test('应该包含"失败"选项', () => {
      renderComponent();
      
      const failedOption = screen.getByRole('option', { name: '失败' });
      
      expect(failedOption).toBeInTheDocument();
      expect(failedOption).toHaveValue('failed');
    });

    test('应该正确显示当前选中的状态', () => {
      renderComponent('ready');
      
      const select = screen.getByTestId('status-filter') as HTMLSelectElement;
      expect(select.value).toBe('ready');
    });

    test('初始值为空时应该选中"全部"选项', () => {
      renderComponent('');
      
      const select = screen.getByTestId('status-filter') as HTMLSelectElement;
      expect(select.value).toBe('');
    });
  });

  describe('交互测试', () => {
    test('切换状态应该调用 onStatusChange 回调', async () => {
      const user = userEvent.setup();
      renderComponent();
      
      const select = screen.getByTestId('status-filter');
      await user.selectOptions(select, 'processing');
      
      expect(mockOnStatusChange).toHaveBeenCalledWith('processing');
      expect(mockOnStatusChange).toHaveBeenCalledTimes(1);
    });

    test('切换到"就绪"状态应该触发正确的回调', async () => {
      const user = userEvent.setup();
      renderComponent();
      
      const select = screen.getByTestId('status-filter');
      await user.selectOptions(select, 'ready');
      
      expect(mockOnStatusChange).toHaveBeenCalledWith('ready');
    });

    test('切换到"失败"状态应该触发正确的回调', async () => {
      const user = userEvent.setup();
      renderComponent();
      
      const select = screen.getByTestId('status-filter');
      await user.selectOptions(select, 'failed');
      
      expect(mockOnStatusChange).toHaveBeenCalledWith('failed');
    });

    test('切换到"全部"状态应该触发空字符串回调', async () => {
      const user = userEvent.setup();
      renderComponent('processing');
      
      const select = screen.getByTestId('status-filter');
      await user.selectOptions(select, '');
      
      expect(mockOnStatusChange).toHaveBeenCalledWith('');
    });

    test('点击刷新按钮应该调用 onRefresh 回调', async () => {
      const user = userEvent.setup();
      renderComponent();
      
      const refreshButton = screen.getByTestId('refresh-button');
      await user.click(refreshButton);
      
      expect(mockOnRefresh).toHaveBeenCalledTimes(1);
    });

    test('多次点击刷新按钮应该每次都触发回调', async () => {
      const user = userEvent.setup();
      renderComponent();
      
      const refreshButton = screen.getByTestId('refresh-button');
      await user.click(refreshButton);
      await user.click(refreshButton);
      await user.click(refreshButton);
      
      expect(mockOnRefresh).toHaveBeenCalledTimes(3);
    });
  });

  describe('可访问性测试', () => {
    test('标签应该正确关联到下拉框', () => {
      renderComponent();
      
      const label = screen.getByLabelText('状态筛选：');
      expect(label).toBeInTheDocument();
      expect(label.tagName).toBe('SELECT');
    });

    test('刷新按钮应该有 title 属性', () => {
      renderComponent();
      
      const refreshButton = screen.getByTestId('refresh-button');
      expect(refreshButton).toHaveAttribute('title', '刷新列表');
    });

    test('下拉框应该有 id 属性', () => {
      renderComponent();
      
      const select = screen.getByTestId('status-filter');
      expect(select).toHaveAttribute('id', 'status-filter');
    });
  });

  describe('样式测试', () => {
    test('筛选器容器应该有正确的 Tailwind 类', () => {
      renderComponent();
      
      const container = screen.getByTestId('document-filters');
      expect(container).toHaveClass('flex');
      expect(container).toHaveClass('justify-between');
      expect(container).toHaveClass('items-center');
      expect(container).toHaveClass('mb-4');
    });

    test('状态下拉框应该有焦点样式', () => {
      renderComponent();
      
      const select = screen.getByTestId('status-filter');
      expect(select).toHaveClass('focus:outline-none');
      expect(select).toHaveClass('focus:border-blue-500');
    });

    test('刷新按钮应该有悬停效果', () => {
      renderComponent();
      
      const button = screen.getByTestId('refresh-button');
      expect(button).toHaveClass('hover:text-blue-600');
      expect(button).toHaveClass('transition-colors');
    });
  });
});
