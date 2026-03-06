# 测试技能提示词 (Test Skill Prompt)

## 📋 使用说明

本提示词用于指导 AI 或开发人员系统性地完成全栈项目的测试工作，适用于瀑布模型的测试阶段。

**适用范围**:
- 全栈项目（FastAPI + React + TypeScript）
- 单元测试、集成测试、端到端测试
- MVP 阶段到生产环境的各测试需求

**输入参数**:
- `project_root`: 项目根目录路径
- `test_phase`: 测试阶段（unit/integration/e2e/uat）
- `coverage_target`: 目标覆盖率（默认 80%）
- `mvp_mode`: 是否 MVP 模式（默认 false，可简化部分测试）

---

## 🎯 第一步：明确测试目标

### 1.1 分析项目架构

请首先扫描项目结构，识别以下关键信息：

```bash
# 查看项目整体结构
tree -L 3 -I 'node_modules|__pycache__|*.pyc'

# 识别技术栈
cat backend/requirements.txt  # Python 后端依赖
cat frontend/package.json     # 前端依赖
```

**期望的项目结构**:
```
project/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── services/    # 业务逻辑层
│   │   ├── repositories/# 数据访问层
│   │   ├── models/      # 数据模型
│   │   ├── api/         # API 路由
│   │   └── utils/       # 工具函数
│   └── tests/           # 后端测试
│       ├── unit/        # 单元测试
│       └── integration/ # 集成测试
├── frontend/            # React 前端
│   └── src/
│       ├── components/  # UI 组件
│       ├── services/    # API 服务
│       └── stores/      # 状态管理
└── docs/               # 项目文档
```

### 1.2 定义测试范围

根据项目架构，确定以下测试层次：

#### Level 1: 单元测试（必做）
- **后端**: 
  - ✅ Services 层核心业务逻辑
  - ✅ Utils 工具函数
  - ✅ Parsers/Chunkers 算法类
  - ⚠️ Repositories 层（可选，使用 Mock）
  
- **前端**:
  - ✅ Utility 函数（格式化、验证等）
  - ✅ Store 状态管理逻辑
  - ⚠️ 纯 UI 组件（MVP 阶段可选）

#### Level 2: 集成测试（推荐）
- **API 端点测试**: 
  - POST/GET/DELETE 接口功能
  - 参数验证和错误处理
  - 数据库交互
  
- **服务间集成**:
  - Service → Repository → Database
  - Service → External API (Mock)

#### Level 3: 端到端测试（可选）
- **关键用户流程**:
  - 文档上传 → 处理 → 问答
  - 完整对话流程
  
- **性能测试**:
  - API 响应时间
  - 并发承载能力

### 1.3 制定测试策略

根据 `mvp_mode` 调整测试优先级：

**MVP 模式** (`mvp_mode=true`):
```yaml
优先级:
  P0: 核心业务逻辑单元测试 (DocumentService, TextChunker)
  P1: API 端点集成测试 (Upload, Chat)
  P2: 关键路径 E2E 测试
  可忽略：权限测试、性能压力测试、UI 组件测试
```

**生产模式** (`mvp_mode=false`):
```yaml
优先级:
  P0: 所有单元测试（覆盖率 > 80%）
  P1: 所有集成测试
  P2: E2E 测试 + 性能测试
  P3: 安全测试 + 兼容性测试
```

---

## 🔧 第二步：环境准备与依赖安装

### 2.1 后端测试环境

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装测试依赖
pip install -r requirements.txt
pip install pytest==7.4.4 \
            pytest-asyncio==0.23.3 \
            pytest-cov==4.1.0 \
            httpx==0.26.0 \
            respx==0.20.2  # HTTP Mock
```

### 2.2 前端测试环境

```bash
# 进入前端目录
cd frontend

# 安装测试依赖（如未安装）
pnpm add -D vitest@1.3.1 \
          @testing-library/react@14.2.0 \
          @testing-library/jest-dom@6.4.2 \
          jsdom@24.0.0 \
          @vitest/coverage-v8@1.3.1
```

### 2.3 配置测试环境变量

创建 `.env.test` 文件：

```bash
# 后端测试配置
cp .env.example .env.test

# 编辑 .env.test，使用测试数据库
DATABASE_URL=postgresql+asyncpg://localhost/rag_qa_test
PINECONE_API_KEY=test-key-only
DASHSCOPE_API_KEY=test-key-only

# 关闭日志输出（加速测试）
LOG_LEVEL=CRITICAL
```

---

## 📝 第三步：编写测试用例

### 3.1 后端单元测试模板

#### 示例 1: Service 层测试

```python
# tests/unit/test_document_service.py
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.document_service import DocumentService
from app.exceptions import FileTooLargeError, UnsupportedFileTypeError

class TestDocumentService:
    """DocumentService 单元测试"""
    
    @pytest.fixture
    def mock_repo(self):
        """Mock Repository"""
        repo = Mock()
        repo.save = AsyncMock(return_value=uuid4())
        repo.find_by_id = AsyncMock(return_value=None)
        repo.update_status = AsyncMock(return_value=True)
        return repo
    
    @pytest.fixture
    def mock_embedding_svc(self):
        """Mock Embedding Service"""
        embedding_svc = Mock()
        embedding_svc.embed_text = AsyncMock(return_value=[0.1] * 1536)
        return embedding_svc
    
    @pytest.fixture
    def service(self, mock_repo, mock_embedding_svc):
        """创建 DocumentService 实例"""
        return DocumentService(mock_repo, mock_embedding_svc)
    
    @pytest.mark.asyncio
    async def test_upload_document_success(self, service, mock_repo):
        """测试文档上传成功场景"""
        # Arrange
        file_content = b"test content"
        filename = "test.pdf"
        mime_type = "application/pdf"
        file_size = 1024 * 100  # 100KB
        
        with patch('app.services.document_service.ParserRegistry') as mock_registry:
            mock_registry.is_supported.return_value = True
            
            # Act
            doc_id = await service.upload_document(
                file_content, filename, mime_type, file_size
            )
            
            # Assert
            assert doc_id is not None
            mock_repo.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_upload_document_file_too_large(self, service):
        """测试文件过大异常"""
        # Arrange
        file_content = b"x" * (60 * 1024 * 1024)  # 60MB
        
        # Act & Assert
        with pytest.raises(FileTooLargeError):
            await service.upload_document(
                file_content, "large.pdf", "application/pdf", len(file_content)
            )
    
    @pytest.mark.asyncio
    async def test_upload_document_unsupported_type(self, service):
        """测试不支持的文件类型"""
        # Arrange
        file_content = b"test"
        
        # Act & Assert
        with pytest.raises(UnsupportedFileTypeError):
            await service.upload_document(
                file_content, "image.png", "image/png", 5
            )
```

#### 示例 2: 算法类测试

```python
# tests/unit/test_chunker.py
import pytest
from app.chunkers.semantic_chunker import TextChunker, TextChunk

class TestTextChunker:
    """TextChunker 单元测试"""
    
    @pytest.fixture
    def chunker(self):
        return TextChunker(chunk_size=100, overlap=20)
    
    def test_chunk_by_semantic_empty_text(self, chunker):
        """测试空文本分块"""
        text = ""
        chunks = chunker.chunk_by_semantic(text)
        assert len(chunks) == 0
    
    def test_chunk_by_semantic_single_paragraph(self, chunker):
        """测试单段落分块"""
        text = "这是一个测试段落。内容不是很长，应该可以作为一个完整的块。"
        chunks = chunker.chunk_by_semantic(text)
        assert len(chunks) >= 1
        assert chunks[0].content == text
    
    def test_chunk_by_semantic_multiple_paragraphs(self, chunker):
        """测试多段落分块"""
        text = "第一段内容。\n\n第二段内容。\n\n第三段内容。"
        chunks = chunker.chunk_by_semantic(text)
        assert len(chunks) >= 3
        assert all('\n\n' not in chunk.content for chunk in chunks)
    
    def test_chunk_token_count_estimation(self, chunker):
        """测试 Token 数量估算"""
        text = "测试内容" * 100
        chunks = chunker.chunk_by_semantic(text)
        for chunk in chunks:
            assert chunk.token_count > 0
            assert isinstance(chunk.token_count, int)
```

#### 示例 3: 使用夹具的复杂测试

```python
# tests/conftest.py
"""
pytest 全局夹具
"""
import pytest
from unittest.mock import AsyncMock, Mock
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest.fixture
def mock_db_session():
    """Mock 数据库会话"""
    session = Mock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.add = Mock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session

@pytest.fixture
def mock_embedding_service():
    """Mock 嵌入向量化服务"""
    service = Mock()
    service.embed_text = AsyncMock(return_value=[0.1] * 1536)
    service.embed_batch = AsyncMock(return_value=[[0.1] * 1536])
    return service

@pytest.fixture
def mock_parser_registry():
    """Mock 解析器注册表"""
    registry = Mock()
    parser_instance = Mock()
    parser_instance.parse = AsyncMock(return_value="测试文本内容")
    registry.get_parser = Mock(return_value=parser_instance)
    registry.is_supported = Mock(return_value=True)
    return registry

@pytest.fixture
def test_file_pdf():
    """测试用 PDF 文件内容"""
    return b"%PDF-1.4 test pdf content"

@pytest.fixture
def test_file_docx():
    """测试用 Word 文件内容"""
    return b"PK\x03\x04 test docx content"
```

### 3.2 前端单元测试模板

#### 示例 4: React 组件测试（Vitest + Testing Library）

```typescript
// src/components/chat/__tests__/ChatInput.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ChatInput } from '../ChatInput';
import { useChatStore } from '../../../stores/chatStore';

// Mock Zustand store
vi.mock('../../../stores/chatStore', () => ({
  useChatStore: vi.fn(() => ({
    addMessage: vi.fn(),
    setCurrentConversation: vi.fn(),
    setLoading: vi.fn(),
    setError: vi.fn(),
  })),
}));

describe('ChatInput', () => {
  it('渲染输入框和发送按钮', () => {
    render(<ChatInput />);
    
    expect(screen.getByPlaceholderText(/输入问题/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /发送/i })).toBeInTheDocument();
  });

  it('允许输入文本', () => {
    render(<ChatInput />);
    const input = screen.getByPlaceholderText(/输入问题/i);
    
    fireEvent.change(input, { target: { value: '测试问题' } });
    
    expect(input).toHaveValue('测试问题');
  });

  it('点击发送按钮时调用 handleSubmit', () => {
    const mockAddMessage = vi.fn();
    vi.mocked(useChatStore).mockReturnValue({
      addMessage: mockAddMessage,
      setCurrentConversation: vi.fn(),
      setLoading: vi.fn(),
      setError: vi.fn(),
    });

    render(<ChatInput />);
    const input = screen.getByPlaceholderText(/输入问题/i);
    const button = screen.getByRole('button', { name: /发送/i });

    fireEvent.change(input, { target: { value: '测试问题' } });
    fireEvent.click(button);

    expect(mockAddMessage).toHaveBeenCalledWith(
      expect.objectContaining({
        role: 'user',
        content: '测试问题',
      })
    );
  });

  it('禁用空内容的发送按钮', () => {
    render(<ChatInput />);
    const button = screen.getByRole('button', { name: /发送/i });
    
    expect(button).toBeDisabled();
  });
});
```

#### 示例 5: Utility 函数测试

```typescript
// src/utils/__tests__/format.test.ts
import { describe, it, expect } from 'vitest';
import { formatFileSize, formatDate } from '../format';

describe('formatFileSize', () => {
  it('格式化字节为 KB', () => {
    expect(formatFileSize(1024)).toBe('1.00 KB');
    expect(formatFileSize(2048)).toBe('2.00 KB');
  });

  it('格式化字节为 MB', () => {
    expect(formatFileSize(1024 * 1024)).toBe('1.00 MB');
    expect(formatFileSize(2.5 * 1024 * 1024)).toBe('2.50 MB');
  });

  it('处理零值', () => {
    expect(formatFileSize(0)).toBe('0 B');
  });
});

describe('formatDate', () => {
  it('格式化日期字符串', () => {
    const date = new Date('2026-03-05T10:00:00Z');
    expect(formatDate(date)).toMatch(/2026 年 3 月 5 日/);
  });

  it('处理无效日期', () => {
    expect(formatDate(null)).toBe('');
    expect(formatDate(undefined)).toBe('');
  });
});
```

---

## 🚀 第四步：执行测试与收集结果

### 4.1 后端测试执行

```bash
cd backend

# 运行所有单元测试并生成覆盖率报告
pytest tests/unit/ \
  --cov=app \
  --cov-report=html \
  --cov-report=term-missing \
  --cov-report=json \
  --junitxml=test-results/unit.xml \
  -v

# 运行集成测试
pytest tests/integration/ \
  --cov=app \
  --cov-append \
  --junitxml=test-results/integration.xml \
  -v

# 查看覆盖率报告
# HTML: htmlcov/index.html
# JSON: coverage.json
```

### 4.2 前端测试执行

```bash
cd frontend

# 运行所有测试并生成覆盖率报告
pnpm vitest run \
  --coverage \
  --coverage.reporter=html \
  --coverage.reporter=json \
  --reporter=junit \
  --outputFile=test-results/results.xml

# 查看覆盖率报告
# HTML: coverage/index.html
# JSON: coverage/coverage-final.json
```

### 4.3 持续集成模式

```bash
# 监听模式（开发时使用）
pytest tests/ --cov=app --watch

# 失败重跑模式
pytest tests/ --cov=app --last-failed --exitfirst

# 并行测试（加速执行）
pytest tests/ --cov=app --numprocesses=auto
```

---

## 📊 第五步：生成结构化测试报告

### 5.1 测试报告模板

测试完成后，必须生成《测试分析报告》，包含以下内容：

```markdown
# [项目名称] 测试分析报告

## 1. 执行概况
- **执行时间**: YYYY-MM-DD HH:MM
- **测试阶段**: [单元测试/集成测试/E2E 测试]
- **总用例数**: XX
- **通过数**: XX
- **失败数**: XX
- **跳过数**: XX
- **执行时长**: XX 秒
- **覆盖率**: XX%

## 2. 测试结果详情

### 2.1 按模块统计
| 模块 | 用例数 | 通过 | 失败 | 覆盖率 |
|------|--------|------|------|--------|
| services/ | XX | XX | XX | XX% |
| utils/ | XX | XX | XX | XX% |
| ... | ... | ... | ... | ... |

### 2.2 失败用例分析
| 用例 ID | 测试方法 | 失败原因 | 严重性 | 修复建议 |
|---------|----------|----------|--------|----------|
| UT-01 | test_xxx | AssertionError: expected... | 高 | 检查边界条件 |

## 3. 覆盖率分析

### 3.1 总体覆盖率
- **语句覆盖率**: XX%
- **分支覆盖率**: XX%
- **函数覆盖率**: XX%

### 3.2 未覆盖的关键代码
| 文件 | 行号 | 代码片段 | 原因 |
|------|------|----------|------|
| service.py | 120-130 | if error: ... | 异常路径未测试 |

## 4. 质量评估

### 4.1 测试充分性
- ✅ 核心功能已覆盖
- ⚠️ 边界条件覆盖不足
- ❌ 性能测试缺失

### 4.2 风险评估
- **高风险**: [描述]
- **中风险**: [描述]
- **低风险**: [描述]

## 5. 改进建议

### 5.1 短期（立即执行）
1. [ ] 修复失败的测试用例
2. [ ] 补充边界条件测试
3. [ ] 增加异常路径测试

### 5.2 中期（下个迭代）
1. [ ] 实现性能基准测试
2. [ ] 添加 E2E 测试
3. [ ] 提升覆盖率至 90%

## 6. 结论
- [ ] 通过测试，准予发布
- [ ] 有条件通过（需修复 X 个 Bug）
- [ ] 不通过，需重新测试
```

### 5.2 自动化报告生成脚本

创建 `scripts/generate_test_report.py`:

```python
#!/usr/bin/env python3
"""
从 pytest 结果自动生成《测试分析报告》
"""
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

def parse_pytest_results(xml_path: str) -> dict:
    """解析 pytest JUnit XML 结果"""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    total = int(root.attrib['tests'])
    failures = int(root.attrib['failures'])
    errors = int(root.attrib['errors'])
    skipped = int(root.attrib['skipped'])
    time = float(root.attrib['time'])
    
    return {
        'total': total,
        'passed': total - failures - errors - skipped,
        'failed': failures,
        'errors': errors,
        'skipped': skipped,
        'time': time
    }

def parse_coverage_json(json_path: str) -> dict:
    """解析 coverage.py JSON 报告"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return {
        'statement_coverage': data['totals']['percent_covered'],
        'branch_coverage': data['totals'].get('branches_percent_covered', 0),
        'missing_lines': data['totals']['missing']
    }

def generate_report(project_name: str, output_path: str):
    """生成 Markdown 测试报告"""
    # 解析结果
    pytest_results = parse_pytest_results('test-results/unit.xml')
    coverage_data = parse_coverage_json('coverage.json')
    
    # 生成报告
    report = f"""# {project_name} 测试分析报告

## 1. 执行概况
- **执行时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
- **测试阶段**: 单元测试
- **总用例数**: {pytest_results['total']}
- **通过数**: {pytest_results['passed']}
- **失败数**: {pytest_results['failed'] + pytest_results['errors']}
- **跳过数**: {pytest_results['skipped']}
- **执行时长**: {pytest_results['time']:.2f}秒
- **覆盖率**: {coverage_data['statement_coverage']:.1f}%

## 2. 测试结果详情

### 2.1 测试质量
- **通过率**: {pytest_results['passed']/pytest_results['total']*100:.1f}%
- **错误率**: {(pytest_results['failed']+pytest_results['errors'])/pytest_results['total']*100:.1f}%

## 3. 覆盖率分析

### 3.1 总体覆盖率
- **语句覆盖率**: {coverage_data['statement_coverage']:.1f}%
- **分支覆盖率**: {coverage_data['branch_coverage']:.1f}%

## 4. 结论

✅ **通过测试，准予进入下一阶段**

---
*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    # 保存报告
    Path(output_path).write_text(report, encoding='utf-8')
    print(f"✅ 测试报告已生成：{output_path}")

if __name__ == '__main__':
    generate_report('RAG 文档问答系统', 'docs/test_report.md')
```

---

## ✅ 第六步：质量保证清单

测试完成后，请确认以下项目：

### 6.1 测试完整性
- [ ] 所有核心功能都有单元测试
- [ ] 关键路径有集成测试
- [ ] 至少有一个 E2E 测试场景
- [ ] 异常处理有对应测试

### 6.2 测试质量
- [ ] 测试用例独立，无相互依赖
- [ ] 使用了 Mock 隔离外部依赖
- [ ] 测试数据与生产数据分离
- [ ] 测试用例命名清晰（test_场景_预期）

### 6.3 覆盖率要求
- [ ] 总体覆盖率 ≥ 80%
- [ ] 核心模块覆盖率 ≥ 90%
- [ ] 无未测试的关键路径
- [ ] 边界条件有测试覆盖

### 6.4 文档要求
- [ ] 生成《测试分析报告》
- [ ] 记录所有失败用例及原因
- [ ] 提供改进建议和优先级
- [ ] 明确是否通过验收

---

## 🔄 持续改进

### 测试左移（Shift Left）
- 在编码阶段就编写测试
- TDD/BDD 实践
- 代码审查包含测试审查

### 测试右移（Shift Right）
- 生产环境监控
- A/B 测试
- 用户反馈收集

### 自动化程度提升
```bash
# Git Hook: 提交前自动运行测试
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
cd backend && pytest tests/unit -q
if [ $? -ne 0 ]; then
    echo "❌ 测试失败，禁止提交"
    exit 1
fi
echo "✅ 测试通过"
EOF
chmod +x .git/hooks/pre-commit
```

---

## 📚 附录

### A. 常用断言参考

```python
# 值断言
assert result == expected
assert result > 0
assert abs(a - b) < 0.01

# 异常断言
with pytest.raises(ValueError):
    risky_function()

# Mock 断言
mock_method.assert_called_once()
mock_method.assert_called_with(arg1='value')

# 异步断言
result = await async_function()
assert result is not None
```

### B. 测试最佳实践

1. **FIRST 原则**:
   - **F**ast: 测试要快
   - **I**ndependent: 相互独立
   - **R**epeatable: 可重复
   - **S**elf-validating: 自验证
   - **T**imely: 及时编写

2. **AAA 模式**:
   ```python
   def test_xxx(self):
       # Arrange
       setup_data()
       
       # Act
       result = function_under_test()
       
       # Assert
       assert result == expected
   ```

3. **测试命名规范**:
   ```python
   test_<method>_<scenario>_<expected_result>()
   # 示例：
   test_upload_document_file_too_large_should_raise_error()
   ```

---

**版本**: v1.0  
**更新日期**: 2026-03-05  
**适用项目**: 全栈 Web 应用（FastAPI + React）  
**维护者**: [待填写]
