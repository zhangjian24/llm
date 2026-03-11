# 测试脚本使用指南

本目录包含所有测试相关的可执行脚本。

## 📋 脚本列表

### 核心测试脚本（推荐使用）

| 脚本名称 | 用途 | 执行命令 | 说明 |
|----------|------|----------|------|
| `run_api_tests.py` | API 集成测试 | `python run_api_tests.py` | **主推荐** - 覆盖核心 API 功能 |
| `test_pinecone_simple.py` | Pinecone 验证 | `python test_pinecone_simple.py` | **主推荐** - Pinecone 服务完整验证 |
| `quick_check_pinecone.py` | Pinecone 检查 | `python quick_check_pinecone.py` | 快速检查 Pinecone 配置 |

### 标准单元测试

| 脚本名称 | 用途 | 执行命令 | 说明 |
|----------|------|----------|------|
| `tests/unit/test_pinecone_service.py` | Pinecone 单元测试 | `python -m pytest tests/unit/test_pinecone_service.py -v` | ✅ 已完善 |
| `tests/unit/test_embedding_service.py` | Embedding 单元测试 | `python -m pytest tests/unit/test_embedding_service.py -v` | 嵌入服务测试 |
| `tests/unit/test_document_service.py` | 文档服务单元测试 | `python -m pytest tests/unit/test_document_service.py -v` | 文档服务测试 |
| `tests/unit/test_chunker.py` | 分块器单元测试 | `python -m pytest tests/unit/test_chunker.py -v` | 分块器测试 |

### 遗留测试脚本（归档）

以下脚本已移至 [`archive/legacy_tests/`](archive/legacy_tests/) 目录：

- ~~`test_api.py`~~ → 功能已整合到 `run_api_tests.py`
- ~~`test_api_complete.py`~~ → 功能已整合到 `run_api_tests.py`
- ~~`test_pinecone_direct.py`~~ → 功能已被 `test_pinecone_simple.py` 替代
- ~~`test_pinecone_service.py`~~ → 已重构为 `tests/unit/test_pinecone_service.py`

---

## 🚀 快速开始

### 1. 运行完整测试套件

```bash
# 步骤 1: 运行单元测试
python -m pytest tests/unit/ -v

# 步骤 2: 运行 API 集成测试
python run_api_tests.py

# 步骤 3: 运行 Pinecone 专项验证
python test_pinecone_simple.py
```

### 2. 查看测试结果

预期输出示例：

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-7.4.4, pluggy-1.6.0
plugins: anyio-4.12.1, asyncio-0.23.3, cov-4.1.0
asyncio: mode=Mode.AUTO
collected 13 items

tests\unit\test_pinecone_service.py .............                        [100%]

======================== 13 passed, 1 warning in 6.58s ========================
```

### 3. 生成覆盖率报告

```bash
# 生成 HTML 覆盖率报告
python -m pytest tests/unit/ --cov=app --cov-report=html

# 打开报告
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS/Linux
```

---

## 📊 测试统计参考

### 单元测试统计

| 测试模块 | 用例数 | 通过率 | 覆盖率 | 状态 |
|----------|--------|--------|--------|------|
| Pinecone 服务 | 13 | 100% | 73%+ | ✅ |
| Embedding 服务 | ~10 | ~90% | ~70% | ✅ |
| 文档服务 | ~8 | ~85% | ~65% | ✅ |
| 分块器 | ~6 | ~80% | ~60% | ✅ |

### API测试统计

| 测试项 | 用例数 | 通过 | 阻塞 | 通过率 |
|--------|--------|------|------|--------|
| 健康检查 | 1 | 1 | 0 | 100% |
| 文档管理 | 2 | 2 | 0 | 100% |
| 对话聊天 | 2 | 1 | 1* | 50% |
| API 文档 | 1 | 1 | 0 | 100% |
| 安全性 | 1 | 1 | 0 | 100% |
| Swagger 文档 | 1 | 1 | 0 | 100% |

*注：对话聊天测试因 Pinecone 索引为空阻塞（预期情况）

---

## 🔧 故障排查

### 常见问题

#### 1. Unicode 编码错误

**症状**:
```
UnicodeEncodeError: 'gbk' codec can't encode character '\u2713'
```

**解决方案**:
- 已修复：所有测试脚本已移除 emoji 和特殊 Unicode 字符
- 使用 `[PASS]`, `[FAIL]`, `[BLOCKED]` 替代 ✓✗⚠️

#### 2. Pinecone SDK 导入失败

**症状**:
```
ImportError: cannot import name 'Pinecone' from 'pinecone'
```

**解决方案**:
```bash
# 确保安装了正确的版本
pip install pinecone>=5.1.0

# 验证安装
python -c "from pinecone import Pinecone; print('OK')"
```

#### 3. Mock 返回 coroutine 错误

**症状**:
```
AttributeError: 'coroutine' object has no attribute 'get'
```

**解决方案**:
- 已修复：使用 `.return_value` 替代 `AsyncMock`
- 参考：`tests/unit/test_pinecone_service.py` 中的正确用法

---

## 📝 最佳实践

### 编写新测试

1. **命名规范**:
   - 单元测试：`test_*.py` 放在 `tests/unit/`
   - 集成测试：`test_*.py` 放在 `tests/integration/`
   - 独立脚本：`test_*.py` 或 `*_test.py` 放在项目根目录

2. **测试夹具**:
   ```python
   @pytest.fixture
   def mock_index():
       """Mock Pinecone Index"""
       index = MagicMock()
       index.query.return_value = {'matches': []}
       return index
   ```

3. **异步测试**:
   ```python
   @pytest.mark.asyncio
   async def test_something():
       result = await some_async_function()
       assert result == expected
   ```

### 运行测试的建议

1. **本地开发**:
   ```bash
   # 运行相关测试
   python -m pytest tests/unit/test_<module>.py -v
   ```

2. **CI/CD**:
   ```bash
   # 运行所有测试并生成报告
   python -m pytest tests/ -v --tb=short --junitxml=test-results/results.xml
   ```

3. **性能测试**:
   ```bash
   # 标记慢速测试
   python -m pytest tests/ -v -m slow
   ```

---

## 📚 相关文档

- [`test_reports/FINAL_COMBINED_REPORT.md`](test_reports/FINAL_COMBINED_REPORT.md) - 综合测试报告
- [`test_reports/PINECONE_TEST_SUMMARY.md`](test_reports/PINECONE_TEST_SUMMARY.md) - Pinecone 测试详情
- [`archive/reports/`](archive/reports/) - 历史测试报告

---

**最后更新**: 2026-03-11  
**维护者**: AI Engineering Team
