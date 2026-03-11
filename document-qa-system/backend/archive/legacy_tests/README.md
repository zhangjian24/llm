# 遗留测试脚本说明

本目录包含已归档的历史测试脚本，仅供参考和学习使用。

---

## 📁 文件清单

### 1. test_api.py（基础 API测试）

**原始位置**: `backend/test_api.py`  
**功能**: 基础 API 集成测试（6 个用例）  
**状态**: ⚠️ 已归档 - 功能已整合到 [`run_api_tests.py`](../test_scripts/run_api_tests.py)

**测试内容**:
- ✅ 健康检查接口
- ✅ 根路径接口
- ✅ 获取文档列表
- ✅ 上传 TXT 文档
- ⚠️ 非流式对话（阻塞）
- ✅ Swagger API 文档

**替代方案**:
```bash
python ../test_scripts/run_api_tests.py
```

**历史价值**:
- 展示了最基础的 API测试实现
- 包含完整的测试结果统计逻辑
- 适合学习 pytest + httpx 的基本用法

---

### 2. test_api_complete.py（完整 API测试）

**原始位置**: `backend/test_api_complete.py`  
**功能**: 基于 SRS 的完整 API 集成测试（8 个用例）  
**状态**: ⚠️ 已归档 - 功能已整合到 [`run_api_tests.py`](../test_scripts/run_api_tests.py)

**测试内容**:
- ✅ NFR-004: 健康检查
- ✅ FR-001: 上传 TXT 文档
- ✅ FR-007: 获取文档列表
- ⚠️ FR-004: 非流式问答（阻塞）
- ✅ FR-006: 流式问答
- ✅ FR-005: 对话历史查询
- ✅ NFR-004: Swagger API 文档
- ✅ NFR-002: 文件类型验证

**替代方案**:
```bash
python ../test_scripts/run_api_tests.py
```

**历史价值**:
- 展示了如何基于 SRS 编写测试用例
- 包含了更全面的测试场景
- 适合作为测试覆盖率提升的参考

---

### 3. test_pinecone_direct.py（Pinecone 直接测试）

**原始位置**: `backend/test_pinecone_direct.py`  
**功能**: Pinecone 服务直接测试  
**状态**: ⚠️ 已归档 - 功能已被 [`test_pinecone_simple.py`](../test_scripts/test_pinecone_simple.py) 替代

**测试内容**:
- Pinecone 客户端初始化
- Index 创建和管理
- 向量 upsert 和查询
- 错误处理验证

**替代方案**:
```bash
python ../test_scripts/test_pinecone_simple.py
```

**历史价值**:
- 展示了 Pinecone SDK v8 的早期使用方式
- 包含了详细的错误处理逻辑
- 适合学习 Pinecone 基本操作

---

## 🔍 代码对比

### run_api_tests.py vs test_api.py

**改进点**:
1. ✅ 移除了 emoji 字符，避免 Windows GBK 编码问题
2. ✅ 简化了测试逻辑，提高可维护性
3. ✅ 统一了输出格式，使用 `[PASS]`, `[FAIL]`, `[BLOCKED]`
4. ✅ 优化了错误处理，提供更清晰的错误信息

**示例对比**:

**test_api.py (旧)**:
```python
if response.status_code == 200 and data.get("status") == "healthy":
    print(f"  ✓ 通过 (HTTP {response.status_code}, 耗时：{duration:.3f}s)")
```

**run_api_tests.py (新)**:
```python
if response.status_code == 200 and data.get("status") == "healthy":
    print(f"  [PASS] 通过 (HTTP {response.status_code}, 耗时：{duration:.3f}s)")
```

---

### test_pinecone_simple.py vs test_pinecone_direct.py

**改进点**:
1. ✅ 简化了测试流程，从 10 步减少到 7 步
2. ✅ 优化了日志输出，更清晰易懂
3. ✅ 改进了错误处理，提供更友好的提示
4. ✅ 增加了等待时间，确保 Index 就绪

**示例对比**:

**test_pinecone_direct.py (旧)**:
```python
# 复杂的初始化和多个独立测试函数
def test_initialization():
    ...

def test_list_indexes():
    ...
```

**test_pinecone_simple.py (新)**:
```python
# 线性的测试流程，一个函数完成所有测试
async def test_pinecone_service():
    # Test 1: Initialization
    # Test 2: List All Indexes
    # Test 3: Create Index
    # ...
```

---

## 📖 学习建议

### 初学者路线

1. **从新脚本开始**:
   ```bash
   # 先运行现代版本的测试
   python ../test_scripts/run_api_tests.py
   python ../test_scripts/test_pinecone_simple.py
   ```

2. **理解测试原理**:
   - 阅读 `tests/unit/test_pinecone_service.py` 学习单元测试
   - 阅读 `test_scripts/README.md` 了解测试框架

3. **对比学习**:
   - 对比新旧脚本的实现差异
   - 理解为什么新版本更好

### 进阶学习

1. **研究测试演进**:
   - 查看 git history 了解测试文件的变更
   - 理解测试策略的变化

2. **学习测试设计**:
   - 分析 test_api_complete.py 中的 SRS 映射
   - 学习如何设计全面的测试用例

3. **改进测试框架**:
   - 基于现有测试提出改进建议
   - 添加新的测试场景

---

## ⚠️ 使用注意事项

### 不推荐直接使用的原因

1. **编码问题**:
   - 包含 emoji 字符，在 Windows 中文环境可能报错
   - 需要手动修改才能运行

2. **依赖问题**:
   - 部分测试依赖已过时的配置
   - Mock 对象配置不符合最新实践

3. **维护问题**:
   - 不再更新和维护
   - 可能与当前 API 不兼容

### 正确的使用方式

1. **作为参考资料**:
   ```bash
   # 查看历史实现
   cat test_api.py
   
   # 对比新旧版本
   diff test_api.py ../test_scripts/run_api_tests.py
   ```

2. **学习测试演进**:
   - 理解为什么某些实现被弃用
   - 学习最佳实践的演变过程

3. **解决疑难问题**:
   - 当新脚本遇到问题时，参考旧脚本的实现
   - 可能会找到解决问题的灵感

---

## 📚 相关文档

- [`../test_scripts/README.md`](../test_scripts/README.md) - 当前测试脚本说明
- [`../test_reports/FINAL_COMBINED_REPORT.md`](../test_reports/FINAL_COMBINED_REPORT.md) - 综合测试报告
- [`../../archive/README.md`](../../archive/README.md) - 归档说明

---

**归档日期**: 2026-03-11  
**维护者**: AI Engineering Team  
**审查周期**: 每季度审查一次

**状态**: ⚠️ 仅供参考学习，不建议直接使用
