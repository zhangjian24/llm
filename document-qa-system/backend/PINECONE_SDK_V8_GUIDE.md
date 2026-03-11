# Pinecone Python SDK v8+ 使用指南

**版本**: SDK v8+ (pinecone>=5.1.0)  
**更新时间**: 2026-03-11  
**适用项目**: RAG 文档问答系统

---

## 📋 目录

1. [SDK 安装与配置](#1-sdk-安装与配置)
2. [初始化客户端](#2-初始化客户端)
3. [Index 管理](#3-index-管理)
4. [向量操作](#4-向量操作)
5. [查询与搜索](#5-查询与搜索)
6. [高级功能](#6-高级功能)
7. [最佳实践](#7-最佳实践)
8. [常见问题](#8-常见问题)

---

## 1. SDK 安装与配置

### 1.1 安装

```bash
pip install pinecone>=5.1.0
```

### 1.2 环境配置

在 `.env.local` 文件中配置：

```bash
# Pinecone 向量数据库配置
PINECONE_API_KEY=pcsk_xxx_your_api_key_here
PINECONE_INDEX_NAME=document-qa-index

# 注意：SDK v8+ 不再需要配置 PINECONE_HOST
# SDK 会自动根据 index_name 解析 endpoint
```

### 1.3 获取 API Key

1. 登录 [Pinecone Console](https://app.pinecone.io)
2. 进入 **Organizations → API Keys**
3. 创建新的 API Key 并保存

---

## 2. 初始化客户端

### 2.1 基础初始化

```python
from pinecone import Pinecone

# 方式 1: 直接传入 API Key
pc = Pinecone(api_key="pcsk_xxx_your_api_key")

# 方式 2: 从环境变量读取（推荐）
import os
from pinecone import Pinecone

pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
```

### 2.2 完整初始化示例

```python
from pinecone import Pinecone, ServerlessSpec, CloudProvider, AwsRegion, VectorType

class PineconeService:
    def __init__(self):
        self.api_key = "pcsk_xxx"
        self.index_name = "document-qa-index"
        self.dimension = 1024  # text-embedding-v4 输出维度
        
        # 导入 SDK v8+ 模块
        self.Pinecone = Pinecone
        self.ServerlessSpec = ServerlessSpec
        self.CloudProvider = CloudProvider
        self.AwsRegion = AwsRegion
        self.VectorType = VectorType
        
        # 初始化客户端
        self.pc = Pinecone(api_key=self.api_key)
        self._index = None
    
    @property
    def index(self):
        """懒加载 Index"""
        if self._index is None:
            self._index = self.pc.Index(self.index_name)
        return self._index
```

---

## 3. Index 管理

### 3.1 列出所有 Index

```python
# 获取所有 Index 列表
indexes = pc.list_indexes()

# 打印所有 Index 名称
for idx in indexes:
    print(f"Index: {idx.name}")
    print(f"  - Dimension: {idx.dimension()}")
    print(f"  - Metric: {idx.metric()}")
    print(f"  - Host: {idx.host()}")
```

### 3.2 检查 Index 是否存在

```python
# 方式 1: 使用 has_index() 方法
if pc.has_index("my-index"):
    print("Index exists!")

# 方式 2: 遍历 list_indexes()
index_names = [idx.name for idx in pc.list_indexes()]
exists = "my-index" in index_names
```

### 3.3 创建新 Index

#### 方式 A: 自带向量（传统方式）

```python
# 创建不带嵌入模型的 Index（需要自己生成向量）
pc.create_index(
    name="my-index",
    dimension=1024,
    metric="cosine",  # cosine | euclidean | dotproduct
    spec=ServerlessSpec(
        cloud=CloudProvider.AWS,
        region=AwsRegion.US_EAST_1,
        vector_type=VectorType.DENSE  # DENSE | SPARSE
    )
)
```

#### 方式 B: 集成嵌入模型（推荐）

```python
# 创建带嵌入模型的 Index（自动向量化）
pc.create_index_for_model(
    name="quickstart-py",
    cloud="aws",
    region="us-east-1",
    embed={
        "model": "llama-text-embed-v2",
        "field_map": {"text": "chunk_text"}
    }
)
```

**支持的嵌入模型**:
- `llama-text-embed-v2` - Llama 文本嵌入
- `cohere-embed-v3` - Cohere 多语言嵌入
- 更多模型请参考官方文档

### 3.4 删除 Index

```python
# 删除指定 Index
pc.delete_index("my-index")

# 安全删除（先检查是否存在）
if pc.has_index("my-index"):
    pc.delete_index("my-index")
    print("Index deleted!")
```

### 3.5 获取 Index 信息

```python
# 获取 Index 对象
index = pc.Index("my-index")

# 获取统计信息
stats = index.describe_index_stats()
print(f"Total vectors: {stats['total_vector_count']}")
print(f"Namespaces: {stats['namespaces'].keys()}")
```

---

## 4. 向量操作

### 4.1 Upsert（插入/更新）

Upsert 是 insert + update 的组合操作，如果向量 ID 已存在则更新，否则插入。

#### 方式 A: 自带向量（传统方式）

```python
import numpy as np

# 准备数据
vectors = [
    {
        "id": "doc-001-chunk-1",
        "values": np.random.rand(1024).tolist(),  # 1024 维向量
        "metadata": {
            "document_id": "doc-001",
            "chunk_index": 1,
            "content": "这是文档内容",
            "category": "technical"
        }
    },
    {
        "id": "doc-001-chunk-2",
        "values": np.random.rand(1024).tolist(),
        "metadata": {
            "document_id": "doc-001",
            "chunk_index": 2,
            "content": "这是第二段内容",
            "category": "technical"
        }
    }
]

# Upsert 到默认 namespace
index.upsert(vectors=vectors)

# Upsert 到指定 namespace
index.upsert(vectors=vectors, namespace="production")
```

#### 方式 B: 使用文本（集成嵌入模型）

```python
# 如果 Index 集成了嵌入模型，可以直接 upsert 文本
records = [
    {
        "_id": "rec1",
        "chunk_text": "The Eiffel Tower was completed in 1889.",
        "category": "history"
    },
    {
        "_id": "rec2",
        "chunk_text": "Photosynthesis allows plants to convert sunlight.",
        "category": "science"
    }
]

# 自动嵌入并存储
index.upsert_text(records=records)
```

### 4.2 批量 Upsert

```python
# 分批处理大量向量
def batch_upsert(vectors, batch_size=100):
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch)
        print(f"Upserted batch {i//batch_size + 1}")

# 使用示例
large_dataset = [...]  # 10000 个向量
batch_upsert(large_dataset, batch_size=100)
```

### 4.3 Fetch（获取向量）

```python
# 根据 ID 获取向量
response = index.fetch(ids=["doc-001-chunk-1"])

# 访问结果
for vector_id, vector_data in response["vectors"].items():
    print(f"ID: {vector_id}")
    print(f"  Values: {vector_data['values'][:5]}...")  # 只显示前 5 个
    print(f"  Metadata: {vector_data['metadata']}")

# 从指定 namespace 获取
response = index.fetch(ids=["doc-001"], namespace="production")
```

### 4.4 Delete（删除向量）

```python
# 删除单个向量
index.delete(ids=["doc-001"])

# 删除多个向量
index.delete(ids=["doc-001", "doc-002", "doc-003"])

# 删除整个 namespace
index.delete(delete_all=True, namespace="production")

# 条件删除（使用 filter）
index.delete(filter={"category": {"$eq": "outdated"}})
```

### 4.5 使用 Namespace

Namespace 用于在同一个 Index 内逻辑隔离数据。

```python
# Upsert 到不同 namespace
index.upsert(vectors=vectors_a, namespace="dev")
index.upsert(vectors=vectors_b, namespace="staging")
index.upsert(vectors=vectors_c, namespace="production")

# 查询指定 namespace
results = index.query(
    vector=query_vector,
    top_k=10,
    namespace="production"
)

# 获取 namespace 统计
stats = index.describe_index_stats()
for ns_name, ns_stats in stats["namespaces"].items():
    print(f"Namespace '{ns_name}': {ns_stats['vector_count']} vectors")
```

---

## 5. 查询与搜索

### 5.1 向量相似度搜索

```python
# 准备查询向量
query_vector = np.random.rand(1024).tolist()

# 基础查询
results = index.query(
    vector=query_vector,
    top_k=5,  # 返回最相关的 5 个结果
    include_metadata=True,  # 包含元数据
    include_values=False  # 不包含向量值（节省带宽）
)

# 处理结果
for match in results["matches"]:
    print(f"ID: {match['id']}")
    print(f"  Score: {match['score']}")  # 相似度分数（越高越相关）
    print(f"  Metadata: {match['metadata']}")
```

### 5.2 带过滤条件的查询

```python
# 元数据过滤器
query_filter = {
    "category": {"$eq": "technical"},  # 精确匹配
    "created_at": {"$gte": 1700000000}  # 大于等于
}

results = index.query(
    vector=query_vector,
    top_k=10,
    filter=query_filter,
    include_metadata=True
)
```

**支持的过滤操作符**:
- `$eq` - 等于
- `$ne` - 不等于
- `$lt`, `$lte` - 小于/小于等于
- `$gt`, `$gte` - 大于/大于等于
- `$in` - 在列表中
- `$nin` - 不在列表中
- `$and`, `$or` - 逻辑组合

### 5.3 复杂过滤示例

```python
# 组合过滤
complex_filter = {
    "$and": [
        {"category": {"$eq": "technical"}},
        {"$or": [
            {"priority": {"$gte": 5}},
            {"tags": {"$in": ["important", "urgent"]}}
        ]}
    ]
}

results = index.query(
    vector=query_vector,
    top_k=10,
    filter=complex_filter
)
```

### 5.4 使用文本查询（集成嵌入模型）

```python
# 如果 Index 集成了嵌入模型，可以直接用文本查询
results = index.search(
    query_text="What is photosynthesis?",
    top_k=5,
    filter={"category": {"$eq": "science"}}
)

for match in results["matches"]:
    print(f"Text: {match['metadata']['chunk_text']}")
    print(f"Score: {match['score']}")
```

---

## 6. 高级功能

### 6.1 异步操作

```python
import asyncio
from pinecone import PineconeAsyncio

async def async_operations():
    pc_async = PineconeAsyncio(api_key="xxx")
    index = pc_async.Index("my-index")
    
    # 异步 upsert
    await index.upsert(vectors=vectors)
    
    # 异步查询
    results = await index.query(vector=query_vector, top_k=10)
    
    # 关闭连接
    await pc_async.close()

asyncio.run(async_operations())
```

### 6.2 分页查询

```python
def paginate_query(index, query_vector, page_size=100):
    """分页查询大量结果"""
    all_results = []
    pagination_token = None
    
    while True:
        params = {
            "vector": query_vector,
            "top_k": page_size,
            "include_metadata": True
        }
        
        if pagination_token:
            params["pagination"] = {"token": pagination_token}
        
        response = index.query(**params)
        all_results.extend(response["matches"])
        
        # 检查是否有更多结果
        if not response.get("pagination", {}).get("next"):
            break
        pagination_token = response["pagination"]["next"]
    
    return all_results
```

### 6.3 混合搜索（Dense + Sparse）

```python
# 创建支持混合搜索的 Index
pc.create_index(
    name="hybrid-index",
    dimension=1024,
    metric="dotproduct",
    spec=ServerlessSpec(
        cloud=CloudProvider.AWS,
        region=AwsRegion.US_EAST_1,
        vector_type=VectorType.HYBRID  # HYBRID = Dense + Sparse
    )
)

# 混合搜索查询
results = index.query(
    vector=dense_vector,
    sparse_vector=sparse_vector,  # 稀疏向量（关键词搜索）
    top_k=10,
    alpha=0.5  # dense 和 sparse 的权重（0.5 = 各占 50%）
)
```

### 6.4 元数据建模最佳实践

```python
# ✅ 好的元数据设计
good_metadata = {
    "document_id": "doc-001",      # 用于过滤
    "chunk_index": 1,              # 用于排序
    "category": "technical",       # 用于过滤
    "created_at": 1709280000,      # 用于时间范围过滤
    "author": "John Doe",          # 用于作者过滤
    "word_count": 1500             # 用于数值过滤
}

# ❌ 避免过大的元数据
bad_metadata = {
    "full_content": "长篇大论的完整内容...",  # 应该放在外部存储
    "large_array": [1,2,3,...1000],  # 避免大数组
    "nested_object": {...}  # 保持扁平结构
}
```

---

## 7. 最佳实践

### 7.1 性能优化

```python
# ✅ 批量操作
def efficient_upsert(index, large_dataset):
    BATCH_SIZE = 100
    for i in range(0, len(large_dataset), BATCH_SIZE):
        batch = large_dataset[i:i+BATCH_SIZE]
        index.upsert(vectors=batch)

# ✅ 使用合适的 top_k
results = index.query(vector=q, top_k=10)  # 不要请求过多结果

# ✅ 避免返回向量值
results = index.query(
    vector=q,
    include_values=False  # 除非必要，否则设为 False
)
```

### 7.2 错误处理

```python
from pinecone import exceptions as pinecone_exceptions

try:
    index.upsert(vectors=vectors)
except pinecone_exceptions.PineconeApiException as e:
    if e.status == 429:
        print("Rate limit exceeded, retry later")
    elif e.status == 503:
        print("Service unavailable")
    else:
        raise
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 7.3 成本控制

```python
# 监控使用量
stats = index.describe_index_stats()
print(f"Total vectors: {stats['total_vector_count']}")

# 定期清理无用数据
old_vectors = index.query(
    vector=[0]*1024,  # 随机向量，仅用于获取数据
    filter={"created_at": {"$lt": 1672531200}},  # 2023 年之前的数据
    top_k=10000
)

if old_vectors["matches"]:
    ids_to_delete = [m["id"] for m in old_vectors["matches"]]
    index.delete(ids=ids_to_delete)
```

### 7.4 安全实践

```python
# ✅ 使用环境变量存储 API Key
import os
api_key = os.environ.get("PINECONE_API_KEY")

# ✅ 分离开发和生产环境
if os.environ.get("ENV") == "production":
    index_name = "prod-index"
else:
    index_name = "dev-index"

# ✅ 限制 API Key 权限
# 在 Pinecone Console 创建只读/只写 Key
read_only_pc = Pinecone(api_key="pcsk_read_xxx")
write_only_pc = Pinecone(api_key="pcsk_write_xxx")
```

---

## 8. 常见问题

### Q1: 索引创建后多久可以使用？

**A**: 通常立即生效，但大规模数据导入可能需要几分钟才能完全可用。

### Q2: 如何选择相似度度量（metric）？

- **cosine**（余弦相似度）: 最常用，适用于归一化向量
- **euclidean**（欧氏距离）: 适用于向量长度有意义的场景
- **dotproduct**（点积）: 适用于推荐系统

### Q3: 为什么查询返回的结果不相关？

可能原因：
1. Embedding 模型不适合你的领域
2. 查询向量维度与 Index 不匹配
3. 需要调整 top_k 或添加过滤条件
4. 数据质量问题

### Q4: 如何迁移数据到新 Index？

```python
# 1. 创建新 Index
pc.create_index(name="new-index", dimension=1024)
new_index = pc.Index("new-index")

# 2. 从旧 Index 导出数据
old_index = pc.Index("old-index")
all_vectors = export_all_vectors(old_index)

# 3. 导入到新 Index
batch_upsert(new_index, all_vectors)

# 4. 验证数据完整性
old_stats = old_index.describe_index_stats()
new_stats = new_index.describe_index_stats()
assert old_stats["total_vector_count"] == new_stats["total_vector_count"]

# 5. 切换应用配置
# 更新 .env.local 中的 PINECONE_INDEX_NAME
```

### Q5: SDK v7 和 v8 有什么区别？

**主要变更**:
1. ✅ 移除 `PINECONE_HOST` 配置，自动解析 endpoint
2. ✅ 新增枚举类型（`CloudProvider`, `VectorType` 等）
3. ✅ 更简洁的 API：`pc.has_index()`, `pc.create_index_for_model()`
4. ✅ 更好的类型提示和错误处理

**迁移指南**:
```python
# v7 旧代码
from pinecone import pinecone
pinecone.init(api_key="xxx", environment="gcp-us-west1")

# v8 新代码
from pinecone import Pinecone
pc = Pinecone(api_key="xxx")  # 不再需要 environment
```

---

## 📚 参考资源

- [Pinecone 官方文档](https://docs.pinecone.io)
- [Python SDK API Reference](https://docs.pinecone.io/reference/sdks/python)
- [Pinecone CLI](https://docs.pinecone.io/reference/cli)
- [示例代码库](https://github.com/pinecone-io/examples)
- [Pricing Calculator](https://www.pinecone.io/pricing/)

---

**最后更新**: 2026-03-11  
**维护者**: AI Engineering Team
