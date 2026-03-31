# Phase 2: 基础优化详细方案

## 2.1 目标

基于基线评估结果，实施快速低成本优化，优先实施高收益、低复杂度项。

---

## 2.2 Prompt优化

### 2.2.1 当前Prompt分析

```python
# 当前 (backend/app/services/rag_service.py)
SYSTEM_PROMPT = """你是一个专业的文档问答助手。请根据以下文档片段回答问题。

【相关文档】
{context_text}

【对话历史】
{history_text}

【用户问题】
{question}

请用中文回答，并确保：
1. 基于文档内容回答，不要编造信息
2. 如果文档中没有相关信息，请说明
3. 回答要准确、简洁、有条理
4. 必要时可以引用文档来源

回答："""
```

### 2.2.2 问题

| 问题 | 影响 |
|------|------|
| 指令冗长 | 增加30%+ prompt tokens |
| 格式不明确 | 响应长度不可控 |
| 缺少引用格式 | 可追溯性差 |

### 2.2.3 优化方案

```python
# 优化后
SYSTEM_PROMPT = """你是一个专业的文档问答助手。

要求：
1. 只基于【文档内容】回答，不要编造
2. 如需引用，格式：[来源X]
3. 回答简洁，不超过3句话
4. 不知道的问题明确说明

【文档】{context_text}
【历史】{history_text}
【问题】{question}

回答："""
```

### 2.2.4 效果预估

| 优化项 | 效果 |
|--------|------|
| tokens减少 | 约30% |
| 响应长度 | 减少约40% |
| 质量 | 不下降 |

---

## 2.3 缓存机制

### 2.3.1 缓存架构

```
┌─────────────────────────────────────────────────────────┐
│                      请求入口                           │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              缓存层 (Redis)                             │
├─────────────────┬─────────────────┬───────────────────┤
│ Query Embedding │ Retrieval Result│ Response Cache    │
│ TTL: 24h        │ TTL: 1h         │ TTL: 30min       │
│ 命中率: 30-50%  │ 命中率: 20-30%  │ 命中率: 10-20%   │
└─────────────────┴─────────────────┴───────────────────┘
```

### 2.3.2 Redis依赖

```bash
pip install redis[hiredis]
```

### 2.3.3 缓存服务实现

```python
# backend/app/services/cache_service.py
import redis.asyncio as redis
import json
import hashlib
from typing import Optional, List, Dict, Any
import structlog

logger = structlog.get_logger()

class CacheService:
    """RAG缓存服务"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis = redis.from_url(redis_url, decode_responses=False)
        self.default_ttl = 3600
    
    # ============ Query Embedding 缓存 ============
    
    async def get_query_embedding(self, query: str) -> Optional[List[float]]:
        """获取缓存的query embedding"""
        key = f"qe:{self._hash(query)}"
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    async def set_query_embedding(self, query: str, embedding: List[float], ttl: int = 86400):
        """缓存query embedding (24小时)"""
        key = f"qe:{self._hash(query)}"
        await self.redis.setex(key, ttl, json.dumps(embedding))
        logger.debug("cached_query_embedding", query=query[:30], ttl=ttl)
    
    # ============ 检索结果缓存 ============
    
    async def get_retrieval_result(self, query: str, top_k: int) -> Optional[List[Dict]]:
        """获取缓存的检索结果"""
        key = f"rr:{self._hash(query)}:{top_k}"
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    async def set_retrieval_result(
        self, 
        query: str, 
        top_k: int, 
        results: List[Dict],
        ttl: int = 3600
    ):
        """缓存检索结果 (1小时)"""
        key = f"rr:{self._hash(query)}:{top_k}"
        await self.redis.setex(key, ttl, json.dumps(results))
        logger.debug("cached_retrieval_result", query=query[:30], top_k=top_k, ttl=ttl)
    
    # ============ 响应缓存 ============
    
    async def get_response(self, query: str, context_hash: str) -> Optional[str]:
        """获取缓存的响应"""
        key = f"resp:{self._hash(query)}:{context_hash}"
        return await self.redis.get(key)
    
    async def set_response(
        self, 
        query: str, 
        context_hash: str, 
        response: str, 
        ttl: int = 1800
    ):
        """缓存响应 (30分钟)"""
        key = f"resp:{self._hash(query)}:{context_hash}"
        await self.redis.setex(key, ttl, response)
        logger.debug("cached_response", query=query[:30], ttl=ttl)
    
    # ============ 工具方法 ============
    
    def _hash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()[:16]
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        info = await self.redis.info("stats")
        return {
            "hits": info.get("keyspace_hits", 0),
            "misses": info.get("keyspace_misses", 0),
            "hit_rate": self._calc_hit_rate(info)
        }
    
    def _calc_hit_rate(self, info: dict) -> float:
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        return hits / total if total > 0 else 0.0
    
    async def close(self):
        """关闭连接"""
        await self.redis.close()
```

### 2.3.4 RAG服务集成

```python
# backend/app/services/rag_service.py 修改

class RAGService:
    def __init__(self, ...):
        # ... 现有初始化
        self.cache = CacheService()
    
    async def query(
        self,
        question: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        top_k: int = None,
        rerank_top_k: int = None
    ) -> AsyncGenerator[str, None]:
        
        # ... 现有代码 ...
        
        # ============ Step 0: 检查缓存 ============
        
        # 计算context hash用于响应缓存
        # 这里简化处理，实际应该基于检索到的chunk内容
        context_hash = f"{question[:50]}:{top_k}"
        
        # 检查响应缓存
        cached_response = await self.cache.get_response(question, context_hash)
        if cached_response:
            logger.info("cache_hit_response", question=question[:50])
            yield cached_response
            return
        
        # ... 后续流程 ...
        
        # 生成完成后缓存响应
        await self.cache.set_response(question, context_hash, full_response)
        
        return
    
    async def _embed_question(self, question: str) -> List[float]:
        """将问题转换为向量（含缓存）"""
        
        # 检查embedding缓存
        cached_embedding = await self.cache.get_query_embedding(question)
        if cached_embedding:
            logger.debug("cache_hit_embedding", question=question[:30])
            return cached_embedding
        
        # 调用embedding服务
        embedding = await self.embedding_svc.embed_text(question)
        
        # 缓存embedding
        await self.cache.set_query_embedding(question, embedding)
        
        return embedding
```

---

## 2.4 分块策略增强

### 2.4.1 当前配置

```python
# config.py
CHUNK_SIZE: int = 800
CHUNK_OVERLAP: int = 150
```

### 2.4.2 优化方案

| 参数 | 当前值 | 建议值 | 说明 |
|------|--------|--------|------|
| CHUNK_SIZE | 800 | 600 | 更小的chunk提高精度 |
| CHUNK_OVERLAP | 150 | 200 | 更多重叠减少边界丢失 |

### 2.4.3 新增多级分块器

```python
# backend/app/chunkers/multi_level_chunker.py
from typing import List, Dict, Optional
import re

class MultiLevelChunker:
    """
    多级分块器
    
    策略优先级:
    1. 按层级标题分割 (# ## ###)
    2. 按Markdown结构分割
    3. 按段落分割
    4. 按句子分割（兜底）
    """
    
    def __init__(
        self, 
        chunk_size: int = 600,
        overlap: int = 200,
        min_chunk_size: int = 100
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_size = min_chunk_size
    
    def chunk(self, text: str, metadata: Dict = None) -> List[Dict]:
        """执行多级分块"""
        
        # 1. 检测文本结构
        structure = self._detect_structure(text)
        
        if structure["has_headers"]:
            # 使用层级分块
            return self._chunk_by_headers(text, metadata)
        elif structure["has_list"]:
            # 使用列表项分块
            return self._chunk_by_lists(text, metadata)
        else:
            # 使用语义分块
            return self._chunk_by_paragraphs(text, metadata)
    
    def _detect_structure(self, text: str) -> Dict:
        """检测文本结构"""
        return {
            "has_headers": bool(re.search(r'^#{1,6}\s+', text, re.MULTILINE)),
            "has_list": bool(re.search(r'^[\d\-\*]\s+', text, re.MULTILINE)),
            "has_code": bool(re.search(r'```[\s\S]*?```', text)),
            "has_tables": bool(re.search(r'\|.*\|', text))
        }
    
    def _chunk_by_headers(self, text: str, metadata: Dict = None) -> List[Dict]:
        """按层级标题分割"""
        sections = []
        current_section = {"level": 0, "title": "", "content": ""}
        
        for line in text.split('\n'):
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            
            if header_match:
                if current_section["content"]:
                    sections.append(current_section)
                
                current_section = {
                    "level": len(header_match.group(1)),
                    "title": header_match.group(2),
                    "content": ""
                }
            else:
                current_section["content"] += line + "\n"
        
        if current_section["content"]:
            sections.append(current_section)
        
        # 转换为chunks
        chunks = []
        for i, section in enumerate(sections):
            content = section["content"].strip()
            if not content:
                continue
            
            if len(content) > self.chunk_size:
                sub_chunks = self._chunk_by_paragraphs(content, metadata)
                chunks.extend(sub_chunks)
            else:
                chunks.append({
                    "content": content,
                    "metadata": {
                        **(metadata or {}),
                        "section_title": section["title"],
                        "section_level": section["level"],
                        "chunk_type": "section"
                    }
                })
        
        return chunks
    
    def _chunk_by_lists(self, text: str, metadata: Dict = None) -> List[Dict]:
        """按列表项分割"""
        items = []
        current_item = ""
        
        for line in text.split('\n'):
            list_match = re.match(r'^([\d\-\*])\s+(.+)$', line)
            
            if list_match:
                if current_item:
                    items.append(current_item)
                current_item = list_match.group(2)
            elif current_item:
                current_item += " " + line.strip()
        
        if current_item:
            items.append(current_item)
        
        # 合并小项
        chunks = []
        current_chunk = ""
        
        for item in items:
            if len(current_chunk) + len(item) <= self.chunk_size:
                current_chunk += item + "\n"
            else:
                if current_chunk:
                    chunks.append({"content": current_chunk.strip(), "metadata": metadata})
                current_chunk = item + "\n"
        
        if current_chunk:
            chunks.append({"content": current_chunk.strip(), "metadata": metadata})
        
        return chunks
    
    def _chunk_by_paragraphs(self, text: str, metadata: Dict = None) -> List[Dict]:
        """按段落分割（复用现有逻辑）"""
        from app.chunkers.semantic_chunker import TextChunker
        
        chunker = TextChunker(
            chunk_size=self.chunk_size,
            overlap=self.overlap
        )
        
        text_chunks = chunker.chunk_by_semantic(text)
        
        return [
            {
                "content": chunk.content,
                "metadata": {
                    **(metadata or {}),
                    "chunk_type": "paragraph"
                }
            }
            for chunk in text_chunks
            if len(chunk.content) >= self.min_chunk_size
        ]
```

### 2.4.4 配置更新

```python
# backend/app/core/config.py

class Settings(BaseSettings):
    # ... 现有配置 ...
    
    # RAG 配置
    CHUNK_SIZE: int = 600              # 从800调整为600
    CHUNK_OVERLAP: int = 200           # 从150调整为200
    MIN_CHUNK_SIZE: int = 100          # 新增：最小chunk大小
    
    # 缓存配置
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_EMBEDDING_TTL: int = 86400   # 24小时
    CACHE_RETRIEVAL_TTL: int = 3600    # 1小时
    CACHE_RESPONSE_TTL: int = 1800     # 30分钟
```

---

## 2.5 交付物清单

| 交付物 | 验收标准 | 文件位置 |
|--------|----------|----------|
| Prompt优化 | tokens减少30%，质量不降 | backend/app/services/rag_service.py |
| Redis缓存服务 | 命中率>30% | backend/app/services/cache_service.py |
| 多级分块器 | 支持标题层级分割 | backend/app/chunkers/multi_level_chunker.py |
| 优化效果报告 | 对比Phase1基线 | - |

---

## 2.6 效果预估

| 优化项 | 预期效果 |
|--------|---------|
| Prompt优化 | 成本降低20-30% |
| Redis缓存 | API调用减少30-50% |
| 分块增强 | 检索质量提升10-15% |

---

## 2.7 下一步行动

1. 修改Prompt模板
2. 集成Redis缓存服务
3. 实现多级分块器
4. 更新配置
5. 运行评估对比效果

---

**文档版本**: v1.0  
**创建日期**: 2026-03-31
