# 🚀 测试快速参考卡片

## 📋 常用命令速查

### 后端测试 (pytest)

```bash
# 基础测试
pytest tests/                              # 运行所有测试
pytest tests/unit/                         # 只运行单元测试
pytest tests/integration/                  # 只运行集成测试

# 带覆盖率
pytest tests/ --cov=app                    # 运行并统计覆盖率
pytest tests/ --cov=app --cov-report=html  # 生成 HTML 报告
pytest tests/ --cov=app --cov-report=term-missing  # 显示缺失行

# 调试模式
pytest tests/ -v                           # 详细输出
pytest tests/ -s                           # 显示 print 输出
pytest tests/ --tb=long                    # 详细错误追踪
pytest tests/ -x                           # 遇到失败立即停止
pytest tests/ --last-failed              # 只跑上次失败的

# 特定测试
pytest tests/test_file.py                  # 运行指定文件
pytest tests/test_file.py::test_function   # 运行指定函数
pytest -k "test_upload"                    # 运行名称包含 upload 的测试

# 性能优化
pytest tests/ -n auto                      # 并行执行
pytest tests/ --cache-clear               # 清除缓存
```

### 前端测试 (vitest)

```bash
# 基础测试
pnpm vitest run                            # 运行所有测试
pnpm vitest watch                          # 监听模式

# 带覆盖率
pnpm vitest run --coverage                 # 运行并统计覆盖率
pnpm vitest run --coverage --reporter=html # HTML 报告

# 特定测试
pnpm vitest run test_file.test.ts          # 指定文件
pnpm vitest run -t "按钮点击"               # 按名称过滤

# UI 组件测试
pnpm vitest run --ui                       # 图形界面（需安装）
```

---

## 🎯 测试模板速查

### 后端 Service 测试模板

```python
import pytest
from unittest.mock import Mock, AsyncMock

class TestYourService:
    @pytest.fixture
    def mock_repo(self):
        repo = Mock()
        repo.save = AsyncMock(return_value=uuid4())
        return repo
    
    @pytest.fixture
    def service(self, mock_repo):
        return YourService(mock_repo)
    
    @pytest.mark.asyncio
    async def test_success(self, service, mock_repo):
        # Arrange
        input_data = {...}
        
        # Act
        result = await service.method(input_data)
        
        # Assert
        assert result is not None
        mock_repo.method.assert_called_once()
```

### 前端 Component 测试模板

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

describe('YourComponent', () => {
  it('渲染正常', () => {
    render(<YourComponent />);
    expect(screen.getByText(/文本/i)).toBeInTheDocument();
  });

  it('处理点击事件', () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick} />);
    fireEvent.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
```

---

## 🔧 Mock 技巧

### Mock 数据库会话

```python
@pytest.fixture
def mock_db_session():
    session = Mock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.add = Mock()
    session.commit = AsyncMock()
    return session
```

### Mock HTTP 请求

```python
# 使用 respx
import respx
from httpx import Response

@respx.mock
async def test_http_call():
    respx.get("http://api.example.com").mock(
        return_value=Response(200, json={"data": "test"})
    )
    
    response = await client.get("http://api.example.com")
    assert response.json() == {"data": "test"}
```

### Mock 外部服务

```python
@pytest.fixture
def mock_embedding_service():
    service = Mock()
    service.embed_text = AsyncMock(return_value=[0.1] * 1536)
    return service
```

---

## 📊 断言速查

### 值断言

```python
assert result == expected          # 相等
assert result > 0                   # 大于
assert abs(a - b) < 0.01           # 约等于
assert result in [1, 2, 3]         # 包含
assert len(result) == 5            # 长度
assert result is not None          # 非空
```

### 异常断言

```python
with pytest.raises(ValueError):
    risky_function()

with pytest.raises(Exception) as exc_info:
    function()
assert str(exc_info.value) == "错误信息"
```

### Mock 断言

```python
mock_method.assert_called_once()
mock_method.assert_called_with(arg='value')
mock_method.assert_not_called()
```

### React Testing Library 断言

```typescript
expect(element).toBeInTheDocument()
expect(element).toBeVisible()
expect(element).toHaveTextContent('文本')
expect(element).toHaveAttribute('type', 'text')
expect(element).toBeDisabled()
```

---

## 🎯 测试覆盖率目标

| 项目类型 | 语句覆盖 | 分支覆盖 | 函数覆盖 |
|----------|----------|----------|----------|
| **核心模块** | ≥ 90% | ≥ 80% | ≥ 95% |
| **业务模块** | ≥ 80% | ≥ 70% | ≥ 90% |
| **工具函数** | ≥ 95% | ≥ 85% | 100% |
| **整体项目** | ≥ 80% | ≥ 70% | ≥ 90% |

---

## 📝 测试报告生成

```bash
# 自动生成测试报告
python scripts/generate_test_report.py \
  --project "项目名称" \
  --phase unit \
  --xml test-results/results.xml \
  --coverage coverage.json \
  --output docs/test_report.md
```

---

## 💡 常见问题排查

### Q: 测试运行太慢？
```bash
# 使用并行执行
pytest tests/ -n auto

# 只运行变化的测试
pytest tests/ --last-failed

# 清除缓存
pytest tests/ --cache-clear
```

### Q: 异步测试报错？
```python
# 确保使用 pytest.mark.asyncio
@pytest.mark.asyncio
async def test_async_function():
    result = await async_func()
    assert result is not None
```

### Q: Mock 不生效？
```python
# 检查 Mock 路径是否正确
# ❌ 错误：mock 实际导入的模块
with patch('real_module.func'):
    ...

# ✅ 正确：mock 被测试模块导入的版本
with patch('your_module.func'):
    ...
```

### Q: 数据库测试污染？
```python
# 使用事务回滚
@pytest.fixture
def db_session():
    engine = create_async_engine(TEST_DB_URL)
    session = AsyncSession(engine)
    
    yield session
    
    await session.rollback()
    await session.close()
```

---

## 🎯 FIRST 原则

- ✅ **F**ast: 测试要快（< 100ms/个）
- ✅ **I**ndependent: 相互独立
- ✅ **R**epeatable: 可重复执行
- ✅ **S**elf-validating: 自动验证结果
- ✅ **T**imely: 及时编写（最好在编码前）

---

## 🔄 AAA 模式

```python
def test_xxx(self):
    # Arrange (准备)
    setup_test_data()
    
    # Act (执行)
    result = function_under_test()
    
    # Assert (断言)
    assert result == expected_value
```

---

## 📚 更多资源

- 完整提示词：`test_skill_prompt.md`
- 使用说明：`README_TEST.md`
- 报告脚本：`scripts/generate_test_report.py`

---

**打印此卡片作为桌面参考！** 📌
