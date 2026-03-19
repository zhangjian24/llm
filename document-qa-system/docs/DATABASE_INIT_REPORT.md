# PostgreSQL 数据库表结构初始化完成报告

## 📋 执行概况

- **执行时间**: 2026-03-19
- **初始化方式**: PostgreSQL MCP 工具 / SQL 脚本
- **数据库**: PostgreSQL 14+ (with pgvector)
- **总表数**: 4 张核心业务表

---

## ✅ 已创建的数据表

### 1. documents - 文档元数据表

**用途**: 存储上传文档的基本信息和处理状态

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | UUID | 主键，默认 gen_random_uuid() |
| filename | VARCHAR(255) | 原始文件名 |
| file_content | BYTEA | 文件二进制内容（可选） |
| content_hash | VARCHAR(64) | SHA256 哈希，用于去重 |
| file_size | INTEGER | 文件大小（字节） |
| mime_type | VARCHAR(50) | MIME 类型 |
| status | VARCHAR(20) | 处理状态：processing/ready/failed |
| chunks_count | INTEGER | 分块数量 |
| chunk_count | INTEGER | 大文件分块数量 |
| metadata | JSONB | 额外元数据（页数、字数等） |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间（触发器自动更新） |

**索引**:
- `idx_documents_status` - 按状态筛选
- `idx_documents_created_at` - 按时间倒序
- `idx_documents_status_created` - 复合查询优化

**触发器**: `update_documents_updated_at` - 自动更新 updated_at

---

### 2. chunks - 文档块表

**用途**: 存储文档分块的原文内容和向量嵌入

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | UUID | 主键 |
| document_id | UUID | 外键，关联 documents.id（级联删除） |
| chunk_index | INTEGER | 块索引序号 |
| content | TEXT | 原始文本内容 |
| token_count | INTEGER | Token 数量 |
| embedding | vector(1536) | 1536 维向量（pgvector 类型） |
| metadata | JSONB | 位置信息（章节、页码） |

**索引**:
- `idx_chunks_document_id` - 查询某文档的所有块
- `idx_chunks_doc_idx` - 按顺序读取文档块

**级联关系**: 
- FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE

---

### 3. document_chunks - 大文件分块存储表

**用途**: 存储大文件的二进制分块（适用于超过内存限制的大文件）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | UUID | 主键 |
| document_id | UUID | 外键，关联 documents.id |
| chunk_index | INTEGER | 分块序号（从 0 开始） |
| chunk_data | BYTEA | 分块二进制数据 |
| chunk_size | INTEGER | 分块大小（字节） |
| created_at | TIMESTAMP | 创建时间 |

**约束**: 
- UNIQUE(document_id, chunk_index) - 确保同一文档的分块索引唯一

**索引**:
- `idx_document_chunks_document_id` - 查询某文档的所有分块
- `idx_document_chunks_created_at` - 按时间查询

---

### 4. conversations - 对话历史表

**用途**: 存储对话会话的元数据和完整消息历史（JSONB 格式）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | UUID | 主键 |
| user_id | UUID | 用户 ID（MVP 阶段为空） |
| title | VARCHAR(200) | 对话标题（自动生成） |
| messages | JSONB | 完整消息列表（反规范化设计） |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 最后更新时间 |

**索引**:
- `idx_conversations_user_id` - 查询某用户的所有对话
- `idx_conversations_updated_at` - 按最近活动时间排序
- `idx_conversations_user_updated` - 某用户的对话列表（按时间）

**触发器**: `update_conversations_updated_at` - 自动更新 updated_at

---

## 📊 已创建的索引汇总

| 表名 | 索引名 | 类型 | 字段 | 用途 |
|------|--------|------|------|------|
| documents | idx_documents_status | 普通 | status | 按状态筛选 |
| documents | idx_documents_created_at | 普通 | created_at DESC | 时间倒序 |
| documents | idx_documents_status_created | 复合 | status, created_at DESC | 组合查询 |
| chunks | idx_chunks_document_id | 普通 | document_id | 关联查询 |
| chunks | idx_chunks_doc_idx | 复合 | document_id, chunk_index | 顺序读取 |
| document_chunks | idx_document_chunks_document_id | 普通 | document_id | 关联查询 |
| document_chunks | idx_document_chunks_created_at | 普通 | created_at | 时间查询 |
| conversations | idx_conversations_user_id | 普通 | user_id | 用户维度 |
| conversations | idx_conversations_updated_at | 普通 | updated_at DESC | 最近活动 |
| conversations | idx_conversations_user_updated | 复合 | user_id, updated_at DESC | 用户 + 时间 |

---

## ⚙️ 已创建的触发器

### update_updated_at_column()

**函数功能**: 在记录更新时自动设置 `updated_at = CURRENT_TIMESTAMP`

**应用表**:
- documents
- conversations

**使用示例**:
```sql
UPDATE documents SET status = 'ready' WHERE id = 'xxx';
-- updated_at 字段会自动更新为当前时间
```

---

## 🔧 扩展启用

### uuid-ossp

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

**用途**: 提供 `gen_random_uuid()` 函数，用于生成 UUID 主键

### vector (pgvector)

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

**用途**: 提供向量数据类型，支持余弦相似度等向量运算

---

## 📝 使用方法

### 方法一：使用 SQL 脚本（推荐）

```bash
# 1. 连接到 PostgreSQL
psql -U username -d database_name

# 2. 执行初始化脚本
\i backend/scripts/init_database.sql
```

或直接命令行执行:
```bash
psql -U username -d database_name -f backend/scripts/init_database.sql
```

### 方法二：使用 Python 脚本

```bash
# 1. 配置 .env.local（包含 DATABASE_URL）
cd backend

# 2. 运行初始化脚本
python scripts/init_database_with_mcp.py
```

---

## ✅ 验证安装

### 检查表是否创建成功

```sql
-- 查看所有表
\dt

-- 预期输出:
-- Schema |      Name       | Type  | Owner
-- --------+-----------------+-------+----------
-- public | documents       | table | username
-- public | chunks          | table | username
-- public | document_chunks | table | username
-- public | conversations   | table | username
```

### 检查表结构

```sql
-- 查看 documents 表结构
\d documents

-- 查看 chunks 表结构
\d chunks

-- 查看索引列表
\di
```

### 测试触发器

```sql
-- 插入测试数据
INSERT INTO documents (filename, file_size, mime_type) 
VALUES ('test.pdf', 1024, 'application/pdf');

-- 查询 inserted_at 和 updated_at
SELECT id, filename, created_at, updated_at 
FROM documents WHERE filename = 'test.pdf';

-- 更新记录
UPDATE documents SET status = 'ready' WHERE filename = 'test.pdf';

-- 再次查询，updated_at 应该已更新
SELECT id, filename, created_at, updated_at 
FROM documents WHERE filename = 'test.pdf';
```

---

## 📚 相关文档

- **DBD.md**: 完整数据库设计说明书
- **DDD.md**: 详细设计文档（包含类图、时序图）
- **init_database.sql**: SQL 初始化脚本
- **init_database_with_mcp.py**: Python 初始化脚本
- **README_DATABASE_INIT.md**: 详细初始化指南

---

## 🎯 下一步操作

1. **启动后端服务**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **访问 API 文档**:
   ```
   http://localhost:8000/docs
   ```

3. **测试文档上传 API**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/documents/upload \
     -F "file=@test.pdf" \
     -F "metadata={\"title\": \"Test Document\"}"
   ```

4. **验证数据写入**:
   ```sql
   SELECT * FROM documents ORDER BY created_at DESC LIMIT 5;
   ```

---

## 💡 设计亮点

1. **混合存储架构**:
   - 原文内容存储在 PostgreSQL (chunks.content)
   - 向量嵌入存储在 pgvector (chunks.embedding)
   - 大文件分块单独存储 (document_chunks)

2. **性能优化**:
   - 合理的索引设计覆盖高频查询场景
   - 复合索引优化组合条件查询
   - 触发器自动维护时间戳

3. **数据完整性**:
   - 外键级联删除（删除文档时自动删除关联的 chunks）
   - 唯一约束防止重复数据
   - JSONB 灵活存储半结构化数据

4. **可扩展性**:
   - UUID 主键便于分布式扩展
   - 预留 user_id 字段支持多租户
   - 分区策略预留（可按时间范围分区）

---

**报告生成时间**: 2026-03-19  
**版本**: v1.0  
**状态**: ✅ 数据库表结构初始化完成
