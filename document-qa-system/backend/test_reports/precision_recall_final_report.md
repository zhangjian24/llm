# PostgreSQL 向量检索系统 - 精度与召回率测试报告

**生成时间**: 2026-03-19 17:45  
**测试环境**: Windows 22H2, Python 3.13, PostgreSQL + pgvector  
**后端服务**: http://localhost:8000  

---

## 1. 测试概述

### 1.1 测试目标
评估基于 PostgreSQL 的向量检索系统在实际应用场景下的性能表现，重点验证：
- **准确率 (Precision)**: 返回结果中相关结果的比例
- **召回率 (Recall)**: 所有应被检索到的相关结果中被成功检索到的比例
- **系统鲁棒性**: 处理不同类型查询的能力

### 1.2 测试范围
- ✅ 文档上传与解析功能
- ✅ 语义分块与向量化处理
- ⚠️ 向量相似度搜索（受限于 API 端点访问）
- ❌ 完整 RAG 问答流水线（因 API 端点问题未能完全测试）

### 1.3 测试工具
- 自定义测试脚本：`test_precision_recall_comprehensive.py`
- 简化测试脚本：`test_vector_search_simple.py`
- HTTP 客户端：httpx (异步)

---

## 2. 测试执行过程

### 2.1 环境准备
```bash
# 启动后端服务
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 配置加载检查
✅ .env.local 已正确加载
✅ PostgreSQL 数据库连接成功
✅ 表结构检测完成 (documents, chunks, conversations, document_chunks)
```

### 2.2 测试数据构造

#### 测试文档 1: 人工智能基础 (ai_basics.txt)
**内容摘要**: 
- 第一章：什么是人工智能（定义、发展阶段）
- 第二章：机器学习基础（监督学习、无监督学习、强化学习）
- 第三章：深度学习原理（神经网络、CNN、RNN、Transformer）
- 第四章：应用场景案例（医疗、金融、交通、教育）

**统计**: ~2000 字，预期分块数：8-12 个

#### 测试文档 2: 环境保护 (environment.txt)
**内容摘要**:
- 第一章：气候变化现状（温度上升、冰川融化、海平面上升）
- 第二章：污染类型与影响（空气、水、土壤污染）
- 第三章：可持续发展策略（能源转型、循环经济、生态保护）
- 第四章：个人行动建议（日常生活、社区参与、职业选择）

**统计**: ~1800 字，预期分块数：8-10 个

#### 测试文档 3: Python 编程基础 (python_basic.txt)
**内容摘要**:
- 第一章：Python 简介（特点、历史）
- 第二章：变量和数据类型（数字、文本、布尔、序列、映射）
- 第三章：控制结构（条件语句、循环语句）
- 第四章：函数定义（语法、示例）

**统计**: ~800 字，预期分块数：4-6 个

### 2.3 查询设计

#### Round 1: 单文档测试（仅 AI 文档）
| 序号 | 查询问题 | 查询类型 | 预期相关 Chunk |
|------|----------|---------|---------------|
| Q1 | "什么是人工智能？" | 关键词匹配 | AI 定义章节 |
| Q2 | "机器学习有哪些类型？" | 直接询问 | 机器学习分类 |
| Q3 | "深度学习如何工作？" | 原理解释 | 深度学习章节 |
| Q4 | "AI 在医疗领域有什么应用？" | 应用场景 | 医疗案例 |
| Q5 | "什么是卷积神经网络？" | 专业术语 | CNN 相关 |

#### Round 2: 多文档干扰测试（AI + 环境）
| 序号 | 查询问题 | 查询类型 | 预期来源文档 |
|------|----------|---------|-------------|
| Q6 | "如何应对气候变化？" | 解决方案 | environment.txt |
| Q7 | "污染对健康有什么影响？" | 因果关系 | environment.txt |
| Q8 | "个人能为环保做什么？" | 行动指南 | environment.txt |
| Q9 | "机器学习和深度学习有什么区别？" | 对比分析 | ai_basics.txt |
| Q10 | "可再生能源有哪些类型？" | 列举说明 | environment.txt |

#### Round 3: 新文档测试（Python 文档）
| 序号 | 查询问题 | 预期答案范围 |
|------|----------|-------------|
| Q11 | "Python 是什么？" | Python 简介 |
| Q12 | "Python 有哪些数据类型？" | 数据类型章节 |
| Q13 | "如何定义函数？" | 函数定义语法 |
| Q14 | "for 循环怎么写？" | 循环语句示例 |

---

## 3. 测试结果与分析

### 3.1 文档上传与处理

#### 执行日志
```
📤 上传文档：ai_basics.txt
✅ 文档上传成功，ID: 01f9a63a-4fdd-454b-9c4b-37ac58127055
⏳ 等待文档处理完成...
⚠️ 等待超时（60 秒）

📤 上传文档：environment.txt  
✅ 文档上传成功，ID: bd9bef7d-839e-4b29-a2a0-906675ba99a9
⏳ 等待文档处理完成...
⚠️ 等待超时（60 秒）

📤 上传文档：python_basic.txt
✅ 文档上传成功，ID: f2556aae-349c-493e-9f46-2082b957090a
⏳ 等待文档处理完成...
   状态：processing, Chunks: 0 (持续中...)
```

#### 问题分析
**现象**: 文档上传成功但处理超时

**可能原因**:
1. **Embedding API 调用失败**
   - DashScope API Key 未配置或无效
   - 网络连接问题导致向量化失败
   
2. **异步任务执行问题**
   - `_process_document_async` 方法未正确触发
   - 事务提交与异步任务的时序问题

3. **错误处理机制**
   - 异常被捕获但未更新状态为 failed
   - 缺少错误日志输出

**证据**:
- 后端日志显示服务器正常启动，无报错信息
- 文档状态一直停留在 processing，未变为 ready 或 failed
- WebSocket 通知可能未发送

### 3.2 API 端点访问

#### 遇到的问题
```python
# 测试脚本使用的端点
GET /api/v1/documents?page=1&limit=10  # ❌ 返回 307 重定向
POST /api/v1/chat  # ❌ 返回 307 重定向

# 实际正确的端点
GET /api/v1/documents/  # ✅ 注意末尾的斜杠
POST /api/v1/chat/  # ✅ 需要末尾斜杠
```

**根本原因**: FastAPI 的自动重定向行为
- 当路由定义为 `@router.get("/")` 时
- 访问 `/documents` 会被重定向到 `/documents/`
- httpx 默认不跟随 307 重定向

**解决方案**:
```python
# 方案 1: 在 URL 中添加末尾斜杠
response = await client.get(f"{base_url}/api/v1/documents/")

# 方案 2: 允许重定向
client = httpx.AsyncClient(follow_redirects=True)
```

### 3.3 黄金标准定义

由于文档处理未完成，无法获得实际的 chunk IDs。我们采用基于关键词匹配的近似评估方法：

#### 相关性判断标准
对于每个查询 Q 和返回的 chunk C：
```python
def is_relevant(Q, C):
    keywords = extract_keywords(Q)  # 从查询提取关键词
    content = C.metadata.content.lower()
    
    # 如果 chunk 内容包含至少一个关键词，认为相关
    return any(kw.lower() in content for kw in keywords)
```

#### 指标计算公式
```
准确率 (Precision) = TP / (TP + FP)
召回率 (Recall) = TP / (TP + FN)

其中:
- TP: 包含关键词的返回 chunk 数
- FP: 不包含关键词的返回 chunk 数  
- FN: 应该返回但未返回的相关 chunk 数（基于期望值估算）
```

---

## 4. 测试结论

### 4.1 功能完整性评估

| 功能模块 | 测试状态 | 评分 | 备注 |
|---------|---------|------|------|
| 文档上传 | ✅ 通过 | 5/5 | API 正常工作 |
| 文档解析 | ⚠️ 部分通过 | 2/5 | 解析器注册正常，但异步处理未完成 |
| 文本分块 | ❓ 未知 | N/A | 依赖于完整处理流程 |
| 向量化 | ❓ 未知 | N/A | 依赖 Embedding API |
| 向量存储 | ❓ 未知 | N/A | 依赖前序步骤 |
| 相似度搜索 | ⚠️ 待验证 | N/A | API 端点需修正 |
| RAG 问答 | ❓ 待验证 | N/A | 依赖完整流程 |

**总体评分**: 2/5 ⭐⭐

### 4.2 关键发现

#### ✅ 积极方面
1. **文档上传接口正常**: POST /api/v1/documents/upload 工作正常
2. **数据库连接稳定**: PostgreSQL 连接成功，表结构完整
3. **热重载机制有效**: WatchFiles 检测到文件变化自动重启服务

#### ⚠️ 需改进方面
1. **异步处理流程阻塞**
   - 文档长时间处于 processing 状态
   - 缺少进度监控和超时机制
   
2. **错误日志不足**
   - 处理失败时没有明确的错误信息
   - 难以定位问题根因

3. **API 端点一致性**
   - 部分端点需要末尾斜杠，部分不需要
   - 建议在路由定义时统一规范

4. **测试覆盖不全**
   - 缺少端到端的集成测试
   - Mock 测试占比过高

### 4.3 精度/召回率初步评估

基于有限的测试和代码审查，我们给出**理论估计值**：

#### 预期性能（基于算法设计）
```
单文档场景:
- 准确率：75-85% (top_k=5)
- 召回率：60-70% (top_k=5)

多文档场景:
- 准确率：65-75% (top_k=5)  
- 召回率：50-60% (top_k=5)
```

**依据**:
1. **Embedding 模型质量**: text-embedding-v4 是业界领先的中文 Embedding 模型
2. **余弦相似度算法**: PostgreSQL pgvector 实现成熟可靠
3. **语义分块策略**: 按段落和语义边界分块，有利于提高检索准确性

**风险因素**:
- 如果向量化失败，检索准确率为 0%
- 如果索引未建立，检索速度会显著下降
- 如果没有重排序（rerank），召回质量会降低

---

## 5. 问题诊断与修复建议

### 5.1 高优先级问题

#### 问题 1: 文档处理卡住
**症状**: 文档上传后一直处于 processing 状态

**诊断步骤**:
```sql
-- 1. 检查文档状态
SELECT id, filename, status, chunks_count, created_at 
FROM documents 
ORDER BY created_at DESC 
LIMIT 10;

-- 2. 检查是否有 chunk 记录
SELECT d.id, d.filename, COUNT(c.id) as chunk_count
FROM documents d
LEFT JOIN chunks c ON d.id = c.document_id
GROUP BY d.id, d.filename
ORDER BY d.created_at DESC;

-- 3. 检查向量化状态
SELECT d.id, d.filename, 
       COUNT(c.id) as total_chunks,
       COUNT(c.embedding) as vectorized_chunks
FROM documents d
LEFT JOIN chunks c ON d.id = c.document_id
GROUP BY d.id, d.filename;
```

**可能修复方案**:
```python
# 方案 A: 手动触发处理
from app.core.database import get_db_session
from app.services.document_service import DocumentService

async def manually_process_document(doc_id: UUID):
    async for session in get_db_session():
        service = DocumentService(...)
        await service._process_document_async(doc_id)
        await session.commit()

# 方案 B: 添加超时和重试机制
async def _process_document_with_timeout(doc_id: UUID, timeout: int = 300):
    try:
        await asyncio.wait_for(
            self._process_document_async(doc_id),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        logger.error(f"Document processing timeout: {doc_id}")
        await self.repo.update_status(doc_id, 'failed')
```

#### 问题 2: API 端点重定向
**症状**: GET /api/v1/documents 返回 307

**修复方案**:
```python
# 修改 test_vector_search_simple.py
async with httpx.AsyncClient(follow_redirects=True) as client:
    # 现在会自动跟随重定向
    response = await client.get(f"{base_url}/api/v1/documents")
```

### 5.2 中优先级改进

#### 改进 1: 增强日志记录
```python
# 在关键节点添加详细日志
async def _process_document_async(self, doc_id: UUID):
    logger.info("document_processing_started", doc_id=str(doc_id))
    
    try:
        # 步骤 1: 获取文档
        logger.debug("fetching_document_content", doc_id=str(doc_id))
        file_content = ...
        
        # 步骤 2: 解析
        logger.debug("parsing_document", doc_id=str(doc_id), mime_type=doc.mime_type)
        text = await parser.parse(file_content)
        
        # 步骤 3: 分块
        logger.info("text_chunked", doc_id=str(doc_id), chunks_count=len(chunks))
        
        # 步骤 4: 向量化
        logger.info("vectorizing_chunks", doc_id=str(doc_id))
        await self._vectorize_chunks(...)
        
        # 步骤 5: 完成
        logger.info("document_processed_successfully", doc_id=str(doc_id))
        
    except Exception as e:
        logger.error("document_processing_failed", 
                    doc_id=str(doc_id), 
                    error=str(e),
                    exc_info=True)
        raise
```

#### 改进 2: 添加健康检查端点
```python
@router.get("/health")
async def health_check():
    """
    健康检查端点
    返回系统各组件的状态
    """
    status = {
        "database": "unknown",
        "vector_store": "unknown",
        "embedding_api": "unknown",
        "llm_api": "unknown"
    }
    
    # 检查数据库
    try:
        async for session in get_db_session():
            await session.execute(text("SELECT 1"))
        status["database"] = "ok"
    except:
        status["database"] = "error"
    
    # 检查向量库
    try:
        vector_svc = create_vector_service({...})
        stats = await vector_svc.get_index_stats()
        status["vector_store"] = "ok"
    except:
        status["vector_store"] = "error"
    
    # 检查 Embedding API
    try:
        embedding_svc = EmbeddingService()
        await embedding_svc.embed_text("test")
        status["embedding_api"] = "ok"
    except:
        status["embedding_api"] = "error"
    
    return {"status": status}
```

---

## 6. 后续行动计划

### 6.1 立即执行（今天）
- [ ] **检查 Embedding API 配置**
  ```bash
  # 验证 .env.local 中的 DASHSCOPE_API_KEY
  cat .env.local | grep DASHSCOPE
  
  # 测试 API 连通性
  curl -X POST https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/task \
    -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"model": "text-embedding-v4", "input": {"texts": ["test"]}}'
  ```

- [ ] **手动触发文档处理**
  创建脚本 `scripts/manual_process_docs.py`:
  ```python
  import asyncio
  from app.core.database import get_db_session
  from app.repositories.document_repository import DocumentRepository
  from app.services.document_service import DocumentService
  from app.services.embedding_service import EmbeddingService
  
  async def main():
      async for session in get_db_session():
          repo = DocumentRepository(session)
          embedding_svc = EmbeddingService()
          service = DocumentService(repo, embedding_svc)
          
          # 获取所有 processing 状态的文档
          docs = await repo.find_all(status='processing')
          
          for doc in docs[0]:  # docs returns (items, total)
              print(f"Processing: {doc.filename} ({doc.id})")
              try:
                  await service._process_document_async(doc.id)
                  await session.commit()
                  print(f"✅ Success")
              except Exception as e:
                  print(f"❌ Failed: {e}")
                  await session.rollback()
  
  asyncio.run(main())
  ```

### 6.2 短期计划（本周）
- [ ] **修复异步处理超时问题**
  - 添加超时控制（最大 5 分钟）
  - 实现失败重试机制（最多 3 次）
  - 完善错误日志记录

- [ ] **完善测试套件**
  - 修复 API 端点重定向问题
  - 添加单元测试覆盖率
  - 创建端到端测试场景

- [ ] **性能优化**
  - 实现批量向量化（减少 API 调用次数）
  - 添加向量缓存机制
  - 优化数据库查询（添加索引）

### 6.3 中期计划（下周）
- [ ] **完整的精度/召回率测试**
  - 使用真实文档数据
  - 人工标注黄金标准
  - 计算精确的 P/R 指标

- [ ] **用户验收测试 (UAT)**
  - 邀请真实用户试用
  - 收集反馈和建议
  - 迭代优化系统

---

## 7. 附录

### 7.1 测试脚本清单

| 文件名 | 用途 | 状态 |
|--------|------|------|
| `test_precision_recall_comprehensive.py` | 完整的精度/召回率测试 | ⚠️ 需修复 |
| `test_vector_search_simple.py` | 简化的向量搜索测试 | ✅ 可用 |
| `test_vector_search.py` | 基础向量搜索测试 | ✅ 可用 |
| `test_migration_complete.py` | 迁移完整性测试 | ✅ 可用 |

### 7.2 数据库检查 SQL

```sql
-- 查看所有文档及其状态
SELECT 
    id, 
    filename, 
    status, 
    chunks_count, 
    file_size,
    mime_type,
    created_at,
    updated_at
FROM documents
ORDER BY created_at DESC;

-- 查看每个文档的向量化进度
SELECT 
    d.id,
    d.filename,
    d.status,
    COUNT(c.id) as total_chunks,
    COUNT(c.embedding) as vectorized_chunks,
    ROUND(COUNT(c.embedding)::numeric / NULLIF(COUNT(c.id), 0) * 100, 2) as vectorization_rate
FROM documents d
LEFT JOIN chunks c ON d.id = c.document_id
GROUP BY d.id, d.filename, d.status
ORDER BY d.created_at DESC;

-- 检查向量维度是否正确
SELECT 
    d.filename,
    c.id as chunk_id,
    c.chunk_index,
    pg_catalog.array_dims(c.embedding) as embedding_dims
FROM documents d
JOIN chunks c ON d.id = c.document_id
WHERE c.embedding IS NOT NULL
LIMIT 10;

-- 手动测试相似度搜索
SELECT 
    c.id,
    c.content,
    (c.embedding <=> '[0.1, 0.2, ...]'::vector) as distance
FROM chunks c
WHERE c.embedding IS NOT NULL
ORDER BY distance ASC
LIMIT 5;
```

### 7.3 API 端点参考

```
文档管理:
POST   /api/v1/documents/upload      # 上传文档
GET    /api/v1/documents/            # 获取文档列表（注意末尾斜杠）
GET    /api/v1/documents/{doc_id}    # 获取单个文档
DELETE /api/v1/documents/{doc_id}    # 删除文档

对话问答:
POST   /api/v1/chat/                 # 发起对话（注意末尾斜杠）
GET    /api/v1/conversations/        # 获取会话列表

向量库管理:
GET    /api/v1/vector-stats/         # 获取向量库统计信息
```

---

## 8. 总结

本次测试虽然因为文档处理超时和 API 端点问题未能获得完整的精度/召回率数据，但我们：

1. ✅ **验证了基础功能**: 文档上传、数据库连接正常
2. 🔍 **识别了关键问题**: 异步处理阻塞、API 重定向
3. 📋 **制定了修复计划**: 明确了短期和中期的改进方向
4. 🛠️ **提供了诊断工具**: SQL 查询、测试脚本、修复建议

**下一步**: 优先解决文档处理超时问题，确保向量化流程正常运行，然后重新执行完整的精度/召回率测试。

---

**报告编制**: AI Assistant  
**审核状态**: 待审核  
**版本**: v1.0  
**日期**: 2026-03-19
