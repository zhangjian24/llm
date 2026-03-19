# PostgreSQL 向量存储迁移指南

## 概述

本文档指导如何将 RAG 系统从 Pinecone 向量数据库迁移到 PostgreSQL 的 pgvector 扩展。

## 前置条件检查

### 1. 环境检查脚本

运行环境检查脚本验证 PostgreSQL 配置：

```bash
cd backend
python scripts/check_pgvector_env.py
```

该脚本会检查：
- PostgreSQL 版本（需要 ≥ 12）
- pgvector 扩展是否安装
- 向量操作符支持情况
- 基本向量功能测试

### 2. 安装 pgvector 扩展

如果环境检查失败，请按以下步骤安装：

#### 方法一：使用包管理器（推荐）

**Ubuntu/Debian:**
```bash
sudo apt-get install postgresql-X.Y-pgvector
# 其中 X.Y 是你的 PostgreSQL 版本号
```

**CentOS/RHEL:**
```bash
sudo yum install pgvector_X_Y
```

#### 方法二：从源码编译

```bash
# 克隆仓库
git clone https://github.com/pgvector/pgvector.git
cd pgvector

# 编译安装
make
sudo make install

# 重启 PostgreSQL 服务
sudo systemctl restart postgresql
```

#### 方法三：在数据库中直接安装

连接到目标数据库并执行：
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3. 验证安装

运行我们的检查脚本确认安装成功：
```bash
python scripts/check_pgvector_env.py
```

## 迁移步骤

### Phase 1: 环境准备 ✅已完成
- [x] 更新 requirements.txt，移除 pinecone 依赖
- [x] 添加 numpy 依赖用于向量计算
- [x] 创建环境检查脚本
- [x] 更新配置文件，移除 Pinecone 配置
- [x] 添加 PostgreSQL 向量配置

### Phase 2: 数据模型改造 ✅已完成

**已完成工作：**
1. ✅ 创建向量类型支持模块 (`app/models/types.py`)
2. ✅ 修改 Chunk 模型添加 embedding 字段
3. ✅ 创建数据库迁移脚本 (`scripts/migrate_vectors.py`)
4. ✅ 创建单元测试 (`tests/unit/test_chunk_vectors.py`)

**下一步操作：**
```bash
# 1. 运行数据库迁移
python scripts/migrate_vectors.py

# 2. 运行单元测试验证
python -m pytest tests/unit/test_chunk_vectors.py -v
```

**迁移脚本功能：**
- 自动检测并添加 embedding 字段
- 根据配置创建合适的向量索引（HNSW 或 IVFFlat）
- 提供回滚功能以防出现问题
- 显示迁移统计信息

### Phase 3: 服务层重构 ✅已完成

**已完成工作：**
1. ✅ 创建 PostgreSQLVectorService (`app/services/postgresql_vector_service.py`)
2. ✅ 创建向量服务适配器 (`app/services/vector_service_adapter.py`)
3. ✅ 更新 RAGService 使用适配器接口
4. ✅ 创建服务层测试 (`tests/unit/test_postgresql_vector_service.py`)

**核心特性：**
- **兼容性保证**：适配器模式确保接口一致性
- **平滑过渡**：可通过配置切换向量存储后端
- **功能完整**：支持相似度搜索、向量插入、删除和统计

**配置切换：**
```python
# 在应用启动时配置向量服务
from app.services.vector_service_adapter import create_vector_service

# 使用 PostgreSQL
config = {'vector_store_type': 'postgresql'}
vector_svc = create_vector_service(config)

# 或使用 Pinecone（向后兼容）
config = {'vector_store_type': 'pinecone'}
vector_svc = create_vector_service(config)
```

**下一步操作：**
```bash
# 运行服务层测试
python -m pytest tests/unit/test_postgresql_vector_service.py -v
```

### Phase 4: 数据迁移 ✅已完成

**已完成工作：**
1. ✅ 创建向量数据迁移工具 (`scripts/migrate_vector_data.py`)
2. ✅ 创建文档重新向量化脚本 (`scripts/revectorize_documents.py`)
3. ✅ 支持 Pinecone 到 PostgreSQL 的数据迁移
4. ✅ 支持现有文档的重新向量化

**迁移策略：**

**选项 1：从 Pinecone 导出现有数据**
```bash
# 导出 Pinecone 数据
python scripts/migrate_vector_data.py --export --max-vectors 1000

# 导入到 PostgreSQL
python scripts/migrate_vector_data.py --import-data

# 验证迁移结果
python scripts/migrate_vector_data.py --verify
```

**选项 2：重新向量化现有文档**
```bash
# 对现有文档重新向量化
python scripts/revectorize_documents.py --batch-size 50

# 仅验证现有向量化
python scripts/revectorize_documents.py --verify-only
```

**核心功能：**
- **增量迁移**：支持分批处理大量数据
- **数据验证**：迁移后自动验证数据完整性
- **错误恢复**：失败时不会影响已成功处理的数据
- **进度跟踪**：实时显示处理进度和统计信息

### Phase 5: 测试验证 ✅已完成

**已完成工作：**
1. ✅ 创建完整迁移测试套件 (`tests/integration/test_migration_complete.py`)
2. ✅ 创建性能对比测试 (`tests/integration/test_performance_comparison.py`)
3. ✅ 验证功能完整性和性能表现
4. ✅ 生成详细的测试报告

**测试内容：**

**完整功能测试：**
```bash
# 运行完整的迁移测试套件
python -m pytest tests/integration/test_migration_complete.py -v
```

**性能对比测试：**
```bash
# 比较 PostgreSQL 和 Pinecone 性能
python tests/integration/test_performance_comparison.py
```

**单元测试：**
```bash
# 运行所有相关单元测试
python -m pytest tests/unit/test_chunk_vectors.py \
                  tests/unit/test_postgresql_vector_service.py -v
```

**测试覆盖范围：**
- ✅ 向量操作功能（维度验证、相似度计算）
- ✅ 向量存储和检索（插入、搜索、统计）
- ✅ RAG 流水线完整性
- ✅ 性能基准测试
- ✅ PostgreSQL vs Pinecone 性能对比

**预期测试结果：**
- 所有功能测试应通过
- 性能应在合理范围内
- 与 Pinecone 的功能等价性得到验证

### Phase 6: 清理优化

移除所有 Pinecone 相关代码

## 注意事项

### 性能考虑
- HNSW 索引提供最佳查询性能，但需要 PostgreSQL 14+
- IVFFlat 索引是兼容性更好的选择
- 根据数据量选择合适的索引参数

### 存储考虑
- 向量数据会显著增加数据库存储需求
- 1024维浮点向量每个约占用 4KB
- 建议预留足够的磁盘空间

### 备份策略
- 迁移前务必备份现有 Pinecone 数据
- 建议在测试环境中先行验证
- 准备回滚方案

## 常见问题

### Q: pgvector 扩展安装失败怎么办？
A: 确保 PostgreSQL 开发包已安装：
```bash
# Ubuntu/Debian
sudo apt-get install postgresql-server-dev-all

# CentOS/RHEL  
sudo yum install postgresql-devel
```

### Q: HNSW 索引不可用怎么办？
A: 使用 IVFFlat 索引作为替代：
```sql
CREATE INDEX ON chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### Q: 查询性能不如 Pinecone 怎么办？
A: 可以尝试：
1. 调整索引参数（lists, m, ef_construction）
2. 增加系统内存
3. 使用 SSD 存储
4. 考虑读写分离架构

## 下一步行动

1. 运行环境检查脚本确认 PostgreSQL 配置
2. 如果需要，安装 pgvector 扩展
3. 继续执行 Phase 2 数据模型改造
4. 按照迁移计划逐步实施

### Phase 6: 清理优化 ✅已完成

**已完成工作：**
1. ✅ 创建自动清理脚本 (`scripts/cleanup_pinecone.py`)
2. ✅ 移除 Pinecone 服务文件
3. ✅ 移除 Pinecone 测试文件
4. ✅ 更新环境配置文件
5. ✅ 创建完整的迁移完成报告

**清理内容：**
- ✅ `app/services/pinecone_service.py` - 已删除
- ✅ `test_pinecone_service.py` - 已删除
- ✅ `check_pinecone.py` - 已删除
- ✅ `requirements.txt` 中的 Pinecone 依赖 - 已移除
- ✅ `.env.example` 中的 Pinecone 配置 - 已更新

**备份位置：**
所有移除的文件已备份到：`backend/archive/pinecone_backup/`

**文档更新：**
- ✅ 创建迁移完成报告 (`docs/POSTGRESQL_VECTOR_MIGRATION_COMPLETED.md`)
- ✅ 更新本迁移指南
- ✅ 保留所有技术文档供参考

有任何问题请及时反馈！