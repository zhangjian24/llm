# Phase 3: 高级优化详细方案

## 3.1 目标

提升复杂查询的检索准确性，优化成本，实现高级检索功能。

---

## 3.2 pgvector HNSW调优

### 3.2.1 当前配置分析

```python
# config.py 当前值
HNSW_M: int = 16                    # 较低
HNSW_EF_CONSTRUCTION: int = 64       # 较低
```

### 3.2.2 参数说明

| 参数 | 说明 | 当前值 | 推荐值 | 影响 |
|------|------|--------|--------|------|
| m | 每个节点的边数 | 16 | 32 | 提高recall，更多内存 |
| ef_construction | 建索引时搜索深度 | 64 | 128 | 更好的图质量，更长建索引时间 |
| ef (runtime) | 查询时搜索深度 | - | 64 | 查询时动态调整 |

### 3.2.3 索引重建SQL

```sql
-- 方案1: 删除重建
DROP INDEX IF EXISTS chunks_embedding_idx;

CREATE INDEX chunks_embedding_idx 
ON chunks 
USING hnsw (embedding vector_cosine_ops)
WITH (
    m = 32,
    ef_construction = 128
);

-- 方案2: CONCURRENTLY 在线重建（推荐）
-- 注意: 需要PostgreSQL 11+

CREATE INDEX CONCURRENTLY chunks_embedding_idx_new
ON chunks 
USING hnsw (embedding vector_cosine_ops)
WITH (
    m = 32,
    ef_construction = 128
);

-- 验证新索引
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'chunks';

-- 切换索引名
ALTER INDEX chunks_embedding_idx RENAME TO chunks_embedding_idx_old;
ALTER INDEX chunks_embedding_idx_new RENAME TO chunks_embedding_idx;

-- 删除旧索引
DROP INDEX chunks_embedding_idx_old;
```

### 3.2.4 Python重建脚本

```python
# backend/scripts/rebuild_hnsw_index.py
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import text
from app.core.database import get_async_session

async def rebuild_hnsw_index(m: int = 32, ef_construction: int = 128):
    """重建HNSW索引"""
    
    async with get_async_session() as session:
        # 1. 检查索引是否存在
        result = await session.execute(text("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'chunks' 
            AND indexname LIKE '%embedding%'
        """))
        existing_indexes = [row[0] for row in result.fetchall()]
        
        print(f"现有索引: {existing_indexes}")
        
        # 2. 创建新索引
        new_index_name = "chunks_embedding_idx_new"
        
        print(f"创建新索引: {new_index_name} (m={m}, ef_construction={ef_construction})")
        
        await session.execute(text(f"""
            CREATE INDEX CONCURRENTLY {new_index_name}
            ON chunks 
            USING hnsw (embedding vector_cosine_ops)
            WITH (
                m = {m},
                ef_construction = {ef_construction}
            )
        """))
        
        await session.commit()
        
        # 3. 验证
        result = await session.execute(text("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'chunks' 
            AND indexname = :index_name
        """), {"index_name": new_index_name})
        
        row = result.fetchone()
        if row:
            print(f"✓ 新索引创建成功: {row[0]}")
            print(f"  定义: {row[1]}")
        
        print("\n索引重建完成!")
        print("如需切换索引名，执行:")
        print(f"  ALTER INDEX {new_index_name} RENAME TO chunks_embedding_idx;")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="重建HNSW索引")
    parser.add_argument("--m", type=int, default=32, help="m参数")
    parser.add_argument("--ef", type=int, default=128, help="ef_construction参数")
    
    args = parser.parse_args()
    
    asyncio.run(rebuild_hnsw_index(args.m, args.ef))
```

### 3.2.5 配置更新

```python
# backend/app/core/config.py

class Settings(BaseSettings):
    # ... 现有配置 ...
    
    # HNSW 索引参数
    HNSW_M: int = 32                    # 从16提升到32
    HNSW_EF_CONSTRUCTION: int = 128      # 从64提升到128
    HNSW_EF_RUNTIME: int = 64            # 新增：查询时搜索深度
```

### 3.2.6 效果预估

| 指标 | 提升 |
|------|------|
| 召回率 | 10-15% |
| 内存 | 增加约50% |
| 索引构建时间 | 增加约2-3倍 |

---

## 3.3 混合搜索（pgvector + BM25）

### 3.3.1 技术方案

利用PostgreSQL的全文搜索功能(TSVECTOR)结合pgvector：

```sql
-- 1. 为chunks表添加全文搜索列
ALTER TABLE chunks ADD COLUMN IF NOT EXISTS textsearch tsvector
GENERATED ALWAYS AS (to_tsvector('chinese', content)) STORED;

-- 2. 创建GIN索引
CREATE INDEX chunks_textsearch_idx ON chunks USING GIN (textsearch);

-- 3. 可选：添加英文支持
-- to_tsvector('english', content) 或 to_tsvector('simple', content)
```

### 3.3.2 混合搜索服务实现

```python
# backend/app/services/hybrid_retrieval.py
from typing import List, Dict, Any, Tuple
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

class HybridRetrievalService:
    """
    混合检索服务
    
    结合:
    - pgvector 向量相似度
    - PostgreSQL 全文搜索(BM25)
    - Reciprocal Rank Fusion (RRF) 融合
    """
    
    def __init__(self, vector_service, alpha: float = 0.5):
        """
        初始化
        
        Args:
            alpha: 向量搜索权重 (1-alpha为BM25权重)
        """
        self.alpha = alpha
        self.vector_service = vector_service
    
    async def search(
        self,
        session: AsyncSession,
        query_vector: List[float],
        query_text: str,
        top_k: int = 10,
        vector_weight: float = None
    ) -> List[Dict[str, Any]]:
        """执行混合搜索"""
        
        alpha = vector_weight or self.alpha
        
        # 1. 向量搜索
        vector_results = await self._vector_search(
            session, query_vector, top_k * 3
        )
        
        # 2. 全文搜索
        bm25_results = await self._bm25_search(
            session, query_text, top_k * 3
        )
        
        # 3. RRF融合
        fused = self._rrf_fusion(vector_results, bm25_results, k=60)
        
        # 4. 获取完整chunks信息
        result_chunks = await self._get_chunks_by_ids(
            session, 
            [item["id"] for item in fused[:top_k]]
        )
        
        # 5. 合并分数
        for chunk in result_chunks:
            for item in fused:
                if item["id"] == chunk["id"]:
                    chunk["fusion_score"] = item["fusion_score"]
                    break
        
        return result_chunks
    
    async def _vector_search(
        self, 
        session: AsyncSession, 
        query_vector: List[float],
        top_k: int
    ) -> List[Tuple[str, float]]:
        """pgvector相似度搜索"""
        
        query_str = '[' + ','.join([f'{x:.6f}' for x in query_vector]) + ']'
        
        sql = text("""
            SELECT id, (embedding <=> CAST(:query_vec AS vector)) as distance
            FROM chunks
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> CAST(:query_vec AS vector)
            LIMIT :limit
        """)
        
        result = await session.execute(sql, {
            "query_vec": query_str,
            "limit": top_k
        })
        
        return [
            (str(row.id), 1.0 - float(row.distance))  # 转换为相似度
            for row in result.fetchall()
        ]
    
    async def _bm25_search(
        self, 
        session: AsyncSession, 
        query_text: str, 
        top_k: int
    ) -> List[Tuple[str, float]]:
        """PostgreSQL全文搜索"""
        
        sql = text("""
            SELECT id, ts_rank_cd(textsearch, plainto_tsquery('chinese', :query)) as rank
            FROM chunks
            WHERE textsearch @@ plainto_tsquery('chinese', :query)
            ORDER BY ts_rank_cd(textsearch, plainto_tsquery('chinese', :query)) DESC
            LIMIT :limit
        """)
        
        result = await session.execute(sql, {
            "query": query_text,
            "limit": top_k
        })
        
        # 归一化分数
        max_rank = 0.1  # 避免除零
        return [
            (str(row.id), float(row.rank) / max_rank)
            for row in result.fetchall()
        ]
    
    async def _get_chunks_by_ids(
        self, 
        session: AsyncSession, 
        ids: List[str]
    ) -> List[Dict]:
        """根据ID列表获取chunks"""
        
        if not ids:
            return []
        
        sql = text("""
            SELECT id, document_id, chunk_index, content, token_count, metadata
            FROM chunks
            WHERE id = ANY(:ids)
        """)
        
        result = await session.execute(sql, {"ids": ids})
        
        id_to_data = {str(row.id): {
            "id": str(row.id),
            "score": 0,
            "metadata": {
                "document_id": str(row.document_id),
                "chunk_index": row.chunk_index,
                "content": row.content,
                "token_count": row.token_count
            }
        } for row in result.fetchall()}
        
        return [id_to_data.get(id) for id in ids if id in id_to_data]
    
    def _rrf_fusion(
        self, 
        vector_results: List[Tuple[str, float]],
        bm25_results: List[Tuple[str, float]],
        k: int = 60
    ) -> List[Dict[str, Any]]:
        """Reciprocal Rank Fusion融合"""
        
        scores = {}
        
        # 向量结果评分
        for rank, (doc_id, score) in enumerate(vector_results):
            scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank + 1)
        
        # BM25结果评分
        for rank, (doc_id, score) in enumerate(bm25_results):
            scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank + 1)
        
        # 排序
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"id": doc_id, "fusion_score": score}
            for doc_id, score in sorted_docs
        ]
```

### 3.3.3 RAG服务集成

```python
# backend/app/services/rag_service.py 修改

class RAGService:
    def __init__(self, ...):
        # ... 现有初始化
        self.use_hybrid = settings.USE_HYBRID_SEARCH  # 新增配置
        if self.use_hybrid:
            self.hybrid_service = HybridRetrievalService(self.vector_svc)
    
    async def _retrieve_similar_chunks(
        self,
        query_vector: List[float],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """检索相似文档块"""
        
        if self.use_hybrid:
            # 使用混合搜索
            return await self.hybrid_service.search(
                session=None,  # 需要传递session
                query_vector=query_vector,
                query_text=self.current_question,  # 需要保存当前问题
                top_k=top_k
            )
        else:
            # 使用原有向量搜索
            matches = await self.vector_svc.similarity_search(
                query_vector=query_vector,
                top_k=top_k,
                include_metadata=True
            )
            return matches
```

### 3.3.4 配置

```python
# backend/app/core/config.py

class Settings(BaseSettings):
    # ... 现有配置 ...
    
    # 混合搜索配置
    USE_HYBRID_SEARCH: bool = False  # 是否启用混合搜索
    HYBRID_ALPHA: float = 0.5         # 向量权重 (1-alpha为BM25权重)
```

---

## 3.4 模型路由

### 3.4.1 架构设计

```
                    ┌─────────────────┐
                    │   Query Router  │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │   简单查询   │   │   中等查询   │   │   复杂查询   │
   │   (<30字)   │   │  (30-80字)  │   │   (>80字)   │
   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
          │                  │                  │
          ▼                  ▼                  ▼
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │ qwen-turbo  │   │  qwen-max   │   │  qwen-max   │
   │  (低成本)   │   │   (均衡)    │   │  (高质量)   │
   └─────────────┘   └─────────────┘   └─────────────┘
```

### 3.4.2 实现

```python
# backend/app/services/query_router.py
from enum import Enum
from typing import Literal
import re

class QueryComplexity(Enum):
    SIMPLE = "simple"      # <30字符，简单事实
    MEDIUM = "medium"     # 30-80字符，需要推理
    COMPLEX = "complex"   # >80字符，复杂分析

class QueryRouter:
    """查询复杂度路由器"""
    
    def __init__(self, llm_service=None):
        self.llm_service = llm_service
    
    def classify(self, query: str) -> QueryComplexity:
        """分类查询复杂度"""
        
        # 1. 长度快速判断
        if len(query) < 30:
            if self._has_complex_indicators(query):
                return QueryComplexity.MEDIUM
            return QueryComplexity.SIMPLE
        
        if len(query) > 80:
            return QueryComplexity.COMPLEX
        
        # 2. 关键词判断
        if self._has_comparison(query):
            return QueryComplexity.COMPLEX
        if self._has_reasoning(query):
            return QueryComplexity.MEDIUM
        
        return QueryComplexity.SIMPLE
    
    def _has_complex_indicators(self, query: str) -> bool:
        """是否有复杂特征"""
        complex_words = ["比较", "分析", "为什么", "原因", "如何实现"]
        return any(word in query for word in complex_words)
    
    def _has_comparison(self, query: str) -> bool:
        """是否是比较查询"""
        comparison_words = ["比较", "区别", "差异", "哪个更好", "对比"]
        return any(word in query for word in comparison_words)
    
    def _has_reasoning(self, query: str) -> bool:
        """是否需要推理"""
        reasoning_words = ["为什么", "原因", "结果", "影响", "关系"]
        return any(word in query for word in reasoning_words)
    
    def route_model(self, complexity: QueryComplexity) -> str:
        """根据复杂度选择模型"""
        model_map = {
            QueryComplexity.SIMPLE: "qwen-turbo",
            QueryComplexity.MEDIUM: "qwen-max",
            QueryComplexity.COMPLEX: "qwen-max"
        }
        return model_map[complexity]
    
    def route_top_k(self, complexity: QueryComplexity) -> int:
        """根据复杂度选择检索数量"""
        top_k_map = {
            QueryComplexity.SIMPLE: 5,
            QueryComplexity.MEDIUM: 10,
            QueryComplexity.COMPLEX: 15
        }
        return top_k_map[complexity]
```

### 3.4.3 RAG服务集成

```python
# backend/app/services/rag_service.py 修改

class RAGService:
    def __init__(self, ...):
        # ... 现有初始化
        self.query_router = QueryRouter()
        self.use_routing = settings.USE_QUERY_ROUTING  # 新增配置
    
    async def query(self, question: str, ...):
        
        # 查询路由
        if self.use_routing:
            complexity = self.query_router.classify(question)
            model = self.query_router.route_model(complexity)
            top_k = self.query_router.route_top_k(complexity)
            
            logger.info(
                "query_routed",
                complexity=complexity.value,
                model=model,
                top_k=top_k
            )
            
            # 使用路由的top_k
            if top_k != (top_k or settings.RAG_TOP_K):
                rerank_top_k = top_k
        else:
            top_k = top_k or settings.RAG_TOP_K
        
        # ... 后续流程使用选定的model和top_k
```

### 3.4.4 配置

```python
# backend/app/core/config.py

class Settings(BaseSettings):
    # ... 现有配置 ...
    
    # 模型路由配置
    USE_QUERY_ROUTING: bool = False  # 是否启用查询路由
```

---

## 3.5 交付物清单

| 交付物 | 验收标准 | 文件位置 |
|--------|----------|----------|
| HNSW索引调优 | 召回率提升10% | backend/scripts/rebuild_hnsw_index.py |
| 混合搜索服务 | 向量+BM25融合 | backend/app/services/hybrid_retrieval.py |
| 查询路由器 | 复杂度分类 | backend/app/services/query_router.py |
| 效果对比报告 | 各优化项效果数据 | - |

---

## 3.6 效果预估

| 优化项 | 预期效果 |
|--------|---------|
| HNSW调优 | 召回率提升10-15% |
| 混合搜索 | 复杂查询准确率提升20% |
| 模型路由 | LLM成本降低30-50% |

---

## 3.7 下一步行动

1. 执行HNSW索引重建
2. 实现混合搜索服务
3. 实现查询路由器
4. 配置功能开关
5. 运行评估对比效果

---

**文档版本**: v1.0  
**创建日期**: 2026-03-31
