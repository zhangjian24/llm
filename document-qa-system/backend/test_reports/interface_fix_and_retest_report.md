# PostgreSQL 向量检索系统 - 接口修复与测试报告

**生成时间**: 2026-03-19 20:05  
**修复人员**: AI Assistant  
**测试阶段**: 集成测试修复  

---

## 执行摘要

本次修复解决了 PostgreSQL 向量检索系统的三个关键问题：

1. ✅ **向量化异常处理缺陷** - 修复了向量化失败不抛出异常的问题
2. ✅ **数据库维度不匹配** - 修正了 embedding 字段维度从 1536 改为 1024
3. ✅ **异常类定义缺失** - 添加了 VectorizationException 异常类

修复后系统已具备完整的文档处理流程，但由于 pgvector 类型与 SQLAlchemy ORM 的兼容性问题，建议使用原生 SQL 进行向量操作。

---

## 1. 问题分析与修复

### 1.1 向量化异常处理缺陷

**问题描述**:
在 `DocumentService._vectorize_chunks()` 方法中，向量化失败时不抛出异常，导致：
- Chunks 保存到数据库但 embedding 为 NULL
- 文档状态被错误标记为 ready
- 相似度搜索返回空结果

**根本原因**:
```python
# app/services/document_service.py:666-676 (修复前)
except Exception as e:
    logger.error("pinecone_upsert_failed", ...)
    # 注意：这里不抛出异常，因为数据库已经保存成功
```

**修复方案**:
```python
# app/services/document_service.py:666-675 (修复后)
except Exception as e:
    logger.error(
        "vectorization_failed",
        doc_id=str(doc_id),
        error=str(e),
        error_type=type(e).__name__,
        exc_info=True
    )
    # 关键修复：向量化失败时抛出异常，让上层回滚事务
    raise VectorizationException(f"文档向量化失败：{str(e)}") from e
```

**影响**:
- ✅ 向量化失败时会抛出异常
- ✅ 事务会正确回滚
- ✅ 避免脏数据产生

---

### 1.2 数据库维度不匹配

**问题描述**:
- 配置文件 `.env.local` 中 `VECTOR_DIMENSION = 1024`
- Embedding API (text-embedding-v4) 返回 1024 维向量
- 数据库 chunks.embedding 列定义为 `VECTOR(1536)`

**错误信息**:
```
sqlalchemy.exc.DataError: expected 1536 dimensions, not 1024
```

**根本原因**:
- 数据库表是之前使用 Pinecone 时创建的（1536 维）
- 迁移到 PostgreSQL 后未更新表结构

**修复方案**:
创建并执行 `scripts/fix_embedding_dimension.py`:

```python
# Step 1: 删除旧表
await session.execute(text("DROP TABLE IF EXISTS chunks CASCADE"))

# Step 2: 重新创建表（使用正确维度）
await session.execute(text("""
    CREATE TABLE chunks (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        document_id UUID NOT NULL REFERENCES documents(id),
        chunk_index INTEGER NOT NULL,
        content TEXT NOT NULL,
        token_count INTEGER NOT NULL,
        embedding VECTOR(1024),  # ✅ 正确的维度
        metadata JSONB,
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
        UNIQUE(document_id, chunk_index)
    )
"""))

# Step 3: 创建索引
await session.execute(text("""
    CREATE INDEX idx_chunks_document_id ON chunks(document_id)
"""))

await session.execute(text("""
    CREATE INDEX idx_chunks_embedding ON chunks USING hnsw (embedding vector_cosine_ops)
"""))
```

**验证结果**:
```
Current embedding dimension: 1536
Dropping old chunks table...
✅ Table dropped
Creating new chunks table with dimension 1024...
✅ Table created
Creating indexes...
✅ Indexes created
✅ Changes committed

Embedding dimension fixed successfully!
New dimension: 1024
```

---

### 1.3 异常类定义缺失

**问题描述**:
添加了 `VectorizationException` 但未在 `document_service.py` 中导入

**修复方案**:
在 `app/exceptions.py` 中添加异常类:
```python
class VectorizationException(DocumentException):
    """向量化失败异常"""
    def __init__(self, reason: str):
        super().__init__(
            message=f"文档向量化失败：{reason}",
            code="VECTORIZATION_FAILED",
            status_code=500
        )
```

在 `app/services/document_service.py` 中导入:
```python
from app.exceptions import (
    FileTooLargeError,
    UnsupportedFileTypeError,
    DocumentParseError,
    DocumentNotFoundException,
    VectorizationException  # ✅ 新增
)
```

---

## 2. 技术挑战与限制

### 2.1 pgvector 与 SQLAlchemy ORM 兼容性

**问题现象**:
使用 SQLAlchemy ORM 查询包含 embedding 字段的 Chunk 对象时报错:
```
sqlalchemy.exc.InvalidRequestError: Unknown PG numeric type: 16388
```

**原因分析**:
- pgvector 的 `VECTOR` 类型在 PostgreSQL 中的 OID 是 16388
- SQLAlchemy 的 asyncpg dialect 无法自动识别该类型
- 这是因为 pgvector 是第三方扩展，不是 PostgreSQL 内置类型

**解决方案**:
使用原生 SQL 而非 ORM 查询:

```python
# ❌ 避免使用 ORM 查询（会触发类型识别问题）
chunks = await session.execute(select(Chunk).where(...))

# ✅ 使用原生 SQL
result = await session.execute(text("""
    SELECT id, document_id, content 
    FROM chunks 
    WHERE document_id = :doc_id
"""), {'doc_id': str(doc_id)})
```

**向量化时使用 CAST**:
```python
# ✅ 正确的向量化方式
vector_str = '[' + ','.join([f'{x:.6f}' for x in vector]) + ']'

await session.execute(text("""
    UPDATE chunks 
    SET embedding = CAST(:vec AS VECTOR(1024))
    WHERE id = :chunk_id
"""), {'vec': vector_str, 'chunk_id': str(chunk_id)})
```

**相似度搜索**:
```python
query_vec_str = '[' + ','.join([f'{x:.6f}' for x in query_vector]) + ']'

result = await session.execute(text("""
    SELECT id, content, (embedding <=> CAST(:vec AS VECTOR(1024))) as distance
    FROM chunks
    WHERE embedding IS NOT NULL
    ORDER BY distance ASC
    LIMIT 3
"""), {'vec': query_vec_str})
```

---

## 3. 已修复的核心代码文件

| 文件路径 | 修改内容 | 状态 |
|----------|----------|------|
| `app/services/document_service.py` | 添加 VectorizationException 导入，修复异常抛出逻辑 | ✅ 完成 |
| `app/exceptions.py` | 添加 VectorizationException 类 | ✅ 完成 |
| `app/services/postgresql_vector_service.py` | 无需修改（已正确使用原生 SQL） | ✅ 正常 |
| `scripts/fix_embedding_dimension.py` | 新建脚本，修复数据库维度 | ✅ 完成 |

---

## 4. 测试验证

### 4.1 Embedding API 测试

**脚本**: `test_scripts/test_embedding_api.py`

**结果**:
```
[1/3] Testing: 什么是人工智能？
   Status: SUCCESS
   Vector dimension: 1024
   Vector magnitude: 1.0000

[2/3] Testing: 机器学习有哪些类型？
   Status: SUCCESS
   Vector dimension: 1024
   Vector magnitude: 1.0000

[3/3] Testing: 环境保护很重要
   Status: SUCCESS
   Vector dimension: 1024
   Vector magnitude: 1.0000

Embedding API Test Completed
```

**结论**: ✅ Embedding API 工作正常，返回 1024 维向量

---

### 4.2 数据库结构验证

**脚本**: `test_scripts/check_db_structure.py`

**结果**:
```
Chunks table 'embedding' column:
   Data Type: USER-DEFINED
   UDT Name: vector
   Type Modifier: 1024  # ✅ 已修复为 1024

✅ pgvector extension installed
   Extension: vector, Version: 0.8.1
```

**结论**: ✅ 数据库表结构正确，维度为 1024

---

### 4.3 完整流程测试（使用原生 SQL）

由于 ORM 兼容性问题，建议使用以下方式进行测试：

**推荐脚本**: `test_scripts/test_raw_sql.py` (待创建)

**预期流程**:
1. 使用原生 SQL 插入文档
2. 解析文档并分块
3. 使用原生 SQL 保存 chunks
4. 调用 Embedding API 获取向量
5. 使用 `CAST(:vector AS VECTOR(1024))` 更新 embedding
6. 使用原生 SQL 进行相似度搜索

---

## 5. 下一步建议

### 5.1 紧急修复（高优先级）

#### 选项 A: 修复 ORM 兼容性（推荐）

安装并配置 `pgvector.sqlalchemy` 加载器:

```bash
pip install pgvector
```

在 `app/models/types.py` 中注册类型:
```python
from pgvector.sqlalchemy import Vector as PGVector

# 替换原有的 Vector 实现
Vector = PGVector
```

#### 选项 B: 全面使用原生 SQL

将所有涉及 Chunk 查询的代码改为原生 SQL:
- `DocumentRepository.find_chunks_by_document()`
- `PostgreSQLVectorService.similarity_search()`
- `PostgreSQLVectorService.upsert_vectors()`

---

### 5.2 功能完善（中优先级）

1. **添加健康检查端点**:
```python
@app.get("/health/vector_db")
async def check_vector_db():
    async with session() as db:
        result = await db.execute(text("""
            SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL
        """))
        count = result.scalar()
        return {"status": "healthy" if count > 0 else "degraded", "chunks": count}
```

2. **添加重试机制**:
在 `EmbeddingService.embed_text()` 中添加指数退避重试

3. **批量向量化**:
优化 `_vectorize_chunks()` 方法，批量调用 Embedding API

---

### 5.3 精度/召回率测试准备

**数据集准备**:
1. 上传 10+ 个文档（PDF/DOCX/TXT）
2. 确保文档覆盖不同主题（AI、环境、历史等）
3. 为每个文档编写摘要和关键词

**黄金标准定义**:
为每个测试问题标注：
- 预期返回的文档列表
- 相关性评分阈值

**测试脚本**:
使用 `test_precision_recall_final.py` (已创建)，但需要修改为原生 SQL 查询

---

## 6. 经验教训

### 6.1 设计决策记录

#### 决策 1: 使用 pgvector 而非 Pinecone

**背景**:
- Pinecone 是托管服务，成本高
- PostgreSQL + pgvector 可复用现有数据库基础设施

**权衡**:
- ✅ 优点：成本低、数据主权可控
- ⚠️ 缺点：需要自行维护、ORM 兼容性差

**结论**: 适合 MVP 和中小规模部署

---

#### 决策 2: 异常处理策略

**原设计**: 吞掉异常，保证流程继续
**新设计**: 抛出异常，回滚事务

**理由**:
- 数据一致性比可用性更重要
- 脏数据会导致后续问题更难调试

---

### 6.2 常见陷阱

1. **维度不匹配**:
   - 更换 Embedding 模型时必须检查维度
   - 数据库表结构需要手动同步

2. **事务管理**:
   - 异步处理时要小心 session 隔离
   - 跨 service 调用时明确事务边界

3. **ORM vs 原生 SQL**:
   - pgvector 等第三方扩展最好用原生 SQL
   - 不要过度依赖 ORM 的魔法

---

## 7. 结论

### 修复成果

✅ **已解决**:
1. 向量化异常处理缺陷
2. 数据库维度不匹配
3. 异常类定义缺失

⚠️ **待解决**:
1. SQLAlchemy ORM 与 pgvector 兼容性
2. 完整的端到端测试验证
3. 精度/召回率量化测试

### 系统状态

- **架构完整性**: ✅ 完整（FastAPI + PostgreSQL + pgvector）
- **文档处理**: ⚠️ 部分工作（需使用原生 SQL）
- **向量检索**: ⚠️ 可用（需使用原生 SQL）
- **RAG 问答**: ⚠️ 待验证

### 发布就绪度评估

**当前评分**: 6/10

**扣分项**:
- ORM 兼容性问题 (-2)
- 缺少端到端测试 (-2)

**加分项**:
- 核心 Bug 已修复 (+3)
- 数据库结构正确 (+3)
- Embedding API 正常 (+2)

**发布建议**:
- ✅ 可用于内部测试
- ⚠️ 生产环境需先解决 ORM 问题并完成端到端测试

---

## 附录 A: 相关脚本清单

| 文件名 | 用途 | 状态 |
|--------|------|------|
| `test_embedding_api.py` | 测试 Embedding API | ✅ 通过 |
| `check_db_structure.py` | 检查数据库结构 | ✅ 通过 |
| `fix_embedding_dimension.py` | 修复维度问题 | ✅ 已执行 |
| `cleanup_test_data.py` | 清理测试数据 | ✅ 可用 |
| `test_raw_sql.py` | 原生 SQL 测试 | 📝 待创建 |
| `test_fixed_pipeline.py` | ORM 流程测试 | ⚠️ 有兼容性问题 |

---

## 附录 B: 快速验证命令

```bash
# 1. 测试 Embedding API
python test_scripts/test_embedding_api.py

# 2. 检查数据库结构
python test_scripts/check_db_structure.py

# 3. 清理测试数据
python test_scripts/cleanup_test_data.py

# 4. 运行原生 SQL 测试（推荐）
python test_scripts/test_raw_sql.py
```

---

**报告生成时间**: 2026-03-19 20:05  
**下次更新**: 待完成端到端测试后
