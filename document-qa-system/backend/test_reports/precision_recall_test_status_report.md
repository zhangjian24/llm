# PostgreSQL 向量检索系统 - 精度/召回率测试报告

**生成时间**: 2026-03-19  
**测试人员**: AI Assistant  
**测试阶段**: 集成测试  

---

## 1. 执行概况

### 测试环境
- **后端框架**: FastAPI + SQLAlchemy Async
- **向量数据库**: PostgreSQL 14 + pgvector
- **Embedding 模型**: text-embedding-v4 (阿里云百炼)
- **向量维度**: 1024
- **相似度算法**: 余弦相似度

### 测试范围
- ✅ 文档上传接口测试
- ✅ 文档处理流程验证  
- ⚠️ 向量检索功能调试
- ❌ 精度/召回率量化测试（未完成）

### 测试执行结果
| 测试项 | 状态 | 说明 |
|--------|------|------|
| 文档上传 | ✅ 通过 | 支持 PDF/DOCX/TXT格式 |
| 文档解析 | ✅ 通过 | 文本解析正常 |
| 文本分块 | ✅ 通过 | 语义分块算法工作正常 |
| 向量化 | ⚠️ 部分失败 | Embedding API 调用偶发失败 |
| 向量存储 | ❌ 失败 | Chunks 表 embedding 字段为 NULL |
| 相似度检索 | ❌ 无法测试 | 数据库中无有效 embeddings |
| RAG 问答 | ❌ 无法测试 | 检索不到相关文档 |

---

## 2. 问题分析

### 2.1 核心问题：向量存储失败

**现象**:
- 文档状态显示为 `ready`
- `chunks_count` 字段有值（如 3、2 等）
- 但查询 `chunks` 表时发现 `embedding` 字段全部为 `NULL`

**根本原因**:
在 `DocumentService._vectorize_chunks()` 方法中：

```python
# app/services/document_service.py:605-616
try:
    vector_values = await embedding_svc.embed_text(chunk.content)
    vectors.append({"id": vector_id, "values": vector_values, ...})
except Exception as embed_error:
    failed_embeddings += 1
    logger.error("embedding_failed_for_chunk", ...)
    continue  # 继续处理其他 chunks，不中断整个流程
```

**问题影响**:
1. 向量化失败时不抛出异常
2. Chunks 实体已保存到数据库（embedding=None）
3. 事务提交后，chunks 记录存在但无 embedding
4. 相似度搜索时 `WHERE embedding IS NOT NULL` 过滤导致返回空结果

### 2.2 次要问题：事务隔离

**现象**:
在测试脚本中：
1. 插入 Document 记录（未 commit）
2. 调用 `_process_document_async()` 
3. 该方法内查询不到未提交的 Document

**原因**:
- 测试脚本使用单个 session
- `_process_document_async` 内部创建新 session
- PostgreSQL 事务隔离级别导致

---

## 3. 技术债务与修复建议

### 3.1 紧急修复（阻塞测试）

#### 问题 1: 向量化错误处理过于宽松
**文件**: `app/services/document_service.py:666-676`

**当前代码**:
```python
except Exception as e:
    logger.error("pinecone_upsert_failed", ...)
    # 注意：这里不抛出异常，因为数据库已经保存成功
```

**建议修复**:
```python
# 选项 A: 抛出异常，回滚事务
raise VectorizationException(f"向量化失败：{str(e)}") from e

# 选项 B: 部分失败处理
if failed_embeddings > 0:
    logger.warning("partial_vectorization_failure", ...)
    # 可以选择删除失败的 chunks 或标记为待处理
```

#### 问题 2: Embedding API 稳定性
**观察**: API 调用偶发超时或失败

**建议**:
- 添加重试机制（指数退避）
- 添加电路断路器模式
- 考虑本地缓存已计算的 embeddings

### 3.2 架构改进

#### 建议 1: 分离写入和检索路径
**当前问题**: 文档处理和查询使用同一数据库连接池

**建议**: 
- 使用消息队列（Redis/RabbitMQ）异步处理文档
- 文档处理完成后发送事件通知
- 查询服务监听事件更新索引

#### 建议 2: 添加健康检查端点
```python
@app.get("/health/vector_db")
async def check_vector_db():
    """检查向量数据库状态"""
    async with session() as db:
        result = await db.execute(
            select(func.count(Chunk.id)).where(Chunk.embedding.isnot(None))
        )
        count = result.scalar()
        return {"status": "healthy" if count > 0 else "degraded", "chunks": count}
```

---

## 4. 测试阻塞点

### 当前阻塞测试的问题链

```
1. 上传文档 → processing 状态
   ↓
2. 解析文档 → 成功
   ↓  
3. 文本分块 → 成功
   ↓
4. 向量化 → ⚠️ 失败（Embedding API 或存储问题）
   ↓
5. 保存 chunks → ⚠️ 部分成功（embedding=NULL）
   ↓
6. 更新状态 → ready（错误）
   ↓
7. 相似度搜索 → ❌ 返回空结果
   ↓
8. RAG 问答 → ❌ 无相关文档
```

### 需要优先解决的问题

1. **诊断 Embedding API 调用**
   - 检查 API Key 是否有效
   - 检查网络连接
   - 检查请求频率限制

2. **验证向量存储逻辑**
   - 检查 `PostgreSQLVectorService.upsert_vectors()` 实现
   - 确认 SQL UPDATE 语句正确执行
   - 验证 pgvector 扩展正常工作

3. **修复事务管理**
   - 确保向量化成功后再提交
   - 考虑使用两阶段提交

---

## 5. 下一步行动计划

### Phase 1: 修复向量化存储（预计 2-4 小时）

- [ ] 调试 `EmbeddingService.embed_text()` 方法
  - 验证 API 调用参数
  - 检查返回向量维度
  - 确认无异常抛出

- [ ] 调试 `PostgreSQLVectorService.upsert_vectors()`
  - 验证 SQL UPDATE 语句
  - 检查 embedding 字段类型是否为 `VECTOR(1024)`
  - 确认事务提交

- [ ] 添加详细日志
  - 在向量化前后记录 chunk 状态
  - 记录 SQL 执行结果

### Phase 2: 重新运行测试（预计 1-2 小时）

- [ ] 清理测试数据
  ```sql
  DELETE FROM chunks;
  DELETE FROM documents;
  ```

- [ ] 重新上传测试文档
  - 使用小文件（< 1MB）
  - 纯文本内容
  - 等待处理完成

- [ ] 验证数据存储
  ```sql
  SELECT d.filename, d.status, COUNT(c.id) as total_chunks, 
         SUM(CASE WHEN c.embedding IS NOT NULL THEN 1 ELSE 0 END) as embedded_chunks
  FROM documents d
  LEFT JOIN chunks c ON d.id = c.document_id
  GROUP BY d.id, d.filename, d.status;
  ```

### Phase 3: 执行精度/召回率测试（预计 2-3 小时）

- [ ] 准备测试数据集
  - 10+ 个文档，覆盖不同主题
  - 为每个文档编写摘要和关键词

- [ ] 设计测试查询
  - 5-10 个问题，覆盖：
    - 关键词匹配
    - 语义相似
    - 多跳推理

- [ ] 定义黄金标准
  - 为每个问题标注预期返回的文档
  - 设定相关性阈值

- [ ] 执行测试并计算指标
  - Precision = TP / (TP + FP)
  - Recall = TP / (TP + FN)

---

## 6. 结论

### 当前状态
- **系统架构**: ✅ 完整实现（FastAPI + PostgreSQL + pgvector）
- **文档处理**: ⚠️ 部分工作（解析→分块正常，向量化失败）
- **向量检索**: ❌ 无法使用（无有效 embeddings）
- **RAG 问答**: ❌ 无法使用（检索失败）

### 风险评估
- **技术风险**: 中等 - 核心功能实现但存在 Bug
- **进度风险**: 高 - 关键路径阻塞
- **质量风险**: 未知 - 无法量化评估精度/召回率

### 建议
1. **立即暂停精度/召回率测试**
2. **优先修复向量化存储问题**
3. **添加端到端调试工具**
4. **考虑降级方案**：先用 Pinecone 等托管服务验证业务逻辑

---

## 附录 A: 已创建的测试脚本

| 文件名 | 用途 | 状态 |
|--------|------|------|
| `test_debug_api.py` | 调试 API 响应格式 | ✅ 发现 SSE 流问题 |
| `debug_vector_search.py` | 调试向量搜索 | ✅ 发现 chunks 表为空 |
| `reprocess_documents.py` | 重新处理文档 | ⚠️ 因类型错误失败 |
| `test_full_pipeline.py` | 完整流程测试 | ⚠️ 因事务隔离失败 |
| `test_precision_recall_final.py` | 精度/召回率测试 | ✅ 能运行但无数据 |

## 附录 B: 相关 SQL 查询

### 检查文档和 Chunks 状态
```sql
SELECT 
    d.id,
    d.filename,
    d.status,
    d.chunks_count,
    COUNT(c.id) as actual_chunks,
    SUM(CASE WHEN c.embedding IS NOT NULL THEN 1 ELSE 0 END) as chunks_with_embedding
FROM documents d
LEFT JOIN chunks c ON d.id = c.document_id
GROUP BY d.id, d.filename, d.chunks_count, d.status
ORDER BY d.created_at DESC;
```

### 检查 pgvector 扩展
```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
SELECT column_name, data_type, udt_name 
FROM information_schema.columns 
WHERE table_name = 'chunks' AND column_name = 'embedding';
```

---

**报告生成时间**: 2026-03-19 19:50  
**下次更新**: 待向量化问题修复后
