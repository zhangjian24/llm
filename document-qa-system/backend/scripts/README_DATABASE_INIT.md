# 数据库表结构初始化指南

## 方法一：使用 Python 脚本（推荐）

### 步骤

1. **配置数据库连接**

   在 `backend/` 目录下创建 `.env.local` 文件:

   ```bash
   # PostgreSQL 数据库连接
   DATABASE_URL=postgresql+asyncpg://username:password@host:port/database_name
   
   # 示例 (本地开发):
   # DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/rag_qa_system
   ```

   **注意**: 
   - 将 `username` 和 `password` 替换为你的 PostgreSQL 凭据
   - 确保数据库已存在（如果不存在，需先手动创建）

2. **运行初始化脚本**

   ```bash
   cd backend
   python scripts/init_database_with_mcp.py
   ```

3. **验证结果**

   脚本执行成功后会显示:
   ```
   ✓ 数据库表结构初始化完成！
   
   已创建的表:
     1. documents - 文档元数据表
     2. chunks - 文档块表（含向量字段）
     3. document_chunks - 大文件分块存储表
     4. conversations - 对话历史表
   ```

## 方法二：使用 SQL 脚本直接执行

### 步骤

1. **连接到 PostgreSQL**

   ```bash
   psql -U username -d database_name
   ```

2. **执行建表 SQL**

   按顺序执行以下 SQL 语句:

   ```sql
   -- 启用扩展
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   
   -- 创建 documents 表
   CREATE TABLE IF NOT EXISTS documents (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       filename VARCHAR(255) NOT NULL,
       file_content BYTEA,
       content_hash VARCHAR(64) UNIQUE,
       file_size INTEGER NOT NULL,
       mime_type VARCHAR(50) NOT NULL,
       status VARCHAR(20) NOT NULL DEFAULT 'processing',
       chunks_count INTEGER,
       chunk_count INTEGER,
       metadata JSONB,
       created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
   );
   
   -- 创建 chunks 表
   CREATE TABLE IF NOT EXISTS chunks (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
       chunk_index INTEGER NOT NULL,
       content TEXT NOT NULL,
       token_count INTEGER NOT NULL,
       embedding vector(1536),
       metadata JSONB
   );
   
   -- 创建 document_chunks 表
   CREATE TABLE IF NOT EXISTS document_chunks (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
       chunk_index INTEGER NOT NULL,
       chunk_data BYTEA NOT NULL,
       chunk_size INTEGER NOT NULL,
       created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
       UNIQUE(document_id, chunk_index)
   );
   
   -- 创建 conversations 表
   CREATE TABLE IF NOT EXISTS conversations (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       user_id UUID,
       title VARCHAR(200),
       messages JSONB,
       created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
   );
   
   -- 创建索引
   CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
   CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at DESC);
   CREATE INDEX IF NOT EXISTS idx_documents_status_created ON documents(status, created_at DESC);
   
   CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
   CREATE INDEX IF NOT EXISTS idx_chunks_doc_idx ON chunks(document_id, chunk_index);
   
   CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);
   CREATE INDEX IF NOT EXISTS idx_document_chunks_created_at ON document_chunks(created_at);
   
   CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
   CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at DESC);
   CREATE INDEX IF NOT EXISTS idx_conversations_user_updated ON conversations(user_id, updated_at DESC);
   
   -- 创建触发器函数
   CREATE OR REPLACE FUNCTION update_updated_at_column()
   RETURNS TRIGGER AS $$
   BEGIN
       NEW.updated_at = CURRENT_TIMESTAMP;
       RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;
   
   -- 创建触发器
   DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;
   CREATE TRIGGER update_documents_updated_at
       BEFORE UPDATE ON documents
       FOR EACH ROW
       EXECUTE FUNCTION update_updated_at_column();
   
   DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;
   CREATE TRIGGER update_conversations_updated_at
       BEFORE UPDATE ON conversations
       FOR EACH ROW
       EXECUTE FUNCTION update_updated_at_column();
   ```

## 前置要求

### 1. PostgreSQL 安装

- **版本要求**: PostgreSQL 14+ (支持 pgvector 扩展)
- **扩展要求**: 
  - `uuid-ossp` - UUID 生成
  - `pgvector` - 向量数据存储 (用于 chunks 表的 embedding 字段)

### 2. 创建数据库

```bash
# 使用 psql 创建数据库
createdb -U postgres rag_qa_system
```

或使用 SQL:
```sql
CREATE DATABASE rag_qa_system;
```

### 3. 安装 pgvector 扩展

如果在执行脚本报 `vector` 类型错误，需要先安装 pgvector:

**Windows (使用 StackBuilder)**:
1. 打开 PostgreSQL 安装目录
2. 运行 StackBuilder
3. 选择 PostgreSQL 版本
4. 在 Extensions 中找到并安装 pgvector

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install postgresql-14-pgvector
```

**macOS (Homebrew)**:
```bash
brew install pgvector
```

然后在数据库中启用:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## 常见问题

### Q1: password authentication failed

**原因**: 数据库用户名或密码错误

**解决方法**:
1. 检查 `.env.local` 中的 `DATABASE_URL` 配置
2. 确认 PostgreSQL 用户存在且密码正确
3. 检查 `pg_hba.conf` 认证配置

### Q2: relation "vector" does not exist

**原因**: pgvector 扩展未安装或未启用

**解决方法**:
```sql
-- 在目标数据库中执行
CREATE EXTENSION IF NOT EXISTS vector;
```

### Q3: permission denied for schema public

**原因**: 数据库用户权限不足

**解决方法**:
```sql
-- 使用超级用户执行
GRANT ALL ON SCHEMA public TO your_username;
GRANT ALL PRIVILEGES ON DATABASE rag_qa_system TO your_username;
```

### Q4: asyncpg.exceptions.InvalidPasswordError

**原因**: asyncpg 驱动认证失败

**解决方法**:
1. 确认 PostgreSQL 服务正在运行
2. 检查用户名密码是否正确
3. 尝试使用 psql 命令行测试连接:
   ```bash
   psql -U username -h localhost -d database_name
   ```

## 验证安装

执行以下 SQL 验证表是否创建成功:

```sql
-- 查看所有表
\dt

-- 应该看到:
-- Schema |      Name       | Type  | Owner
-- --------+-----------------+-------+----------
-- public | documents       | table | username
-- public | chunks          | table | username
-- public | document_chunks | table | username
-- public | conversations   | table | username

-- 查看 documents 表结构
\d documents

-- 查看 chunks 表结构
\d chunks

-- 查看索引
\di
```

## 数据库设计文档

详细的数据库设计请参考项目文档:
- `docs/DBD.md` - 完整数据库设计说明书
- `docs/DDD.md` - 详细设计文档

## 下一步

数据库表创建完成后，可以:

1. **启动后端服务**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **访问 API 文档**:
   ```
   http://localhost:8000/docs
   ```

3. **上传测试文档**:
   使用 API 或 Postman 测试文档上传功能

---

**最后更新**: 2026-03-19  
**作者**: AI Assistant
