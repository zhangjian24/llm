"""
PostgreSQL 向量数据库服务
使用 pgvector 扩展实现向量存储和检索功能
"""

from typing import List, Dict, Any, Optional, Tuple
import asyncio
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func
from app.models.chunk import Chunk
from app.models.types import cosine_similarity, euclidean_distance
from app.core.config import get_settings
from app.exceptions import RetrievalException
import structlog

logger = structlog.get_logger()
settings = get_settings()


class PostgreSQLVectorService:
    """
    PostgreSQL 向量数据库服务
    
    功能:
    - 向量存储和检索
    - 余弦相似度搜索
    - 元数据过滤
    - 批量操作支持
    
    使用 pgvector 扩展实现高效的向量操作
    """

    def __init__(self):
        """初始化 PostgreSQL 向量服务"""
        self.dimension = settings.VECTOR_DIMENSION
        self.index_type = settings.VECTOR_INDEX_TYPE
        
    async def similarity_search(
        self,
        session: AsyncSession,
        query_vector: List[float],
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        向量相似度搜索（余弦相似度）
        
        Args:
            session: 数据库会话
            query_vector: 查询向量
            top_k: 返回最相似的 K 个结果
            filter_dict: 过滤条件（如 document_id）
            include_metadata: 是否返回元数据
            
        Returns:
            List[Dict[str, Any]]: 搜索结果，按相似度降序排列
                示例：[{
                    "id": "chunk_id",
                    "score": 0.95,
                    "metadata": {...}
                }]
        """
        try:
            # 验证向量维度
            if len(query_vector) != self.dimension:
                raise ValueError(f"查询向量维度不匹配：期望 {self.dimension}，得到 {len(query_vector)}")
            
            # 构建基础查询
            stmt = select(Chunk).where(Chunk.embedding.isnot(None))
            
            # 添加过滤条件
            if filter_dict:
                if 'document_id' in filter_dict:
                    stmt = stmt.where(Chunk.document_id == filter_dict['document_id'])
                # 可以添加更多过滤条件
            
            # 执行相似度搜索
            # 使用原生 SQL 查询，正确处理 pgvector 类型
            from sqlalchemy import text
            
            # 将向量转换为 PostgreSQL 可接受的格式
            # pgvector 接受数组格式的向量
            query_vector_str = '[' + ','.join([f'{x:.6f}' for x in query_vector]) + ']'
            
            sql = text(f"""
                SELECT id, document_id, chunk_index, content, token_count, embedding, metadata,
                       (embedding <=> CAST(:query_vector AS VECTOR({self.dimension}))) as cosine_distance
                FROM chunks 
                WHERE embedding IS NOT NULL
                ORDER BY cosine_distance ASC 
                LIMIT :limit
            """)
            
            # 执行查询
            params = {"query_vector": query_vector_str, "limit": top_k}
            if filter_dict and 'document_id' in filter_dict:
                sql = text(str(sql).replace("WHERE embedding IS NOT NULL", 
                                          "WHERE embedding IS NOT NULL AND document_id = :document_id"))
                params["document_id"] = filter_dict['document_id']
                
            result = await session.execute(sql, params)
            rows = result.fetchall()
            
            # 转换为 Pinecone 兼适格式
            matches = []
                        
            for row in rows:
                if row.embedding is not None:
                    # 从 cosine_distance 转换为相似度分数 (cosine_distance 越小越相似)
                    # 余弦相似度 = 1 - cosine_distance
                    similarity_score = 1.0 - float(row.cosine_distance)
                                
                    match = {
                        "id": str(row.id),
                        "score": float(similarity_score),
                        "metadata": {
                            "document_id": str(row.document_id),
                            "chunk_index": row.chunk_index,
                            "content": row.content,
                            "token_count": row.token_count
                        }
                    }
                    matches.append(match)
            
            logger.info(
                "postgres_vector_search_completed",
                top_k=top_k,
                results_count=len(matches),
                filter=filter_dict
            )
            
            return matches
            
        except Exception as e:
            logger.error(
                "postgres_vector_search_failed",
                error=str(e),
                exc_info=True
            )
            raise RetrievalException(f"PostgreSQL 向量检索失败：{str(e)}")

    async def batch_similarity_search(
        self,
        session: AsyncSession,
        query_vectors: List[List[float]],
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[List[Dict[str, Any]]]:
        """
        批量向量相似度搜索
        
        Args:
            session: 数据库会话
            query_vectors: 查询向量列表
            top_k: 每个查询返回的结果数
            filter_dict: 过滤条件
            
        Returns:
            List[List[Dict[str, Any]]]: 批量搜索结果
        """
        results = []
        for query_vector in query_vectors:
            result = await self.similarity_search(
                session, query_vector, top_k, filter_dict
            )
            results.append(result)
        return results

    async def upsert_vectors(
        self,
        session: AsyncSession,
        vectors: List[Dict[str, Any]],
        namespace: Optional[str] = None  # ✅ 添加 namespace 参数以统一接口（PostgreSQL 不使用）
    ):
        """
        插入或更新向量
        
        Args:
            session: 数据库会话
            vectors: 向量列表，每个向量包含:
                {
                    "id": "chunk_id",
                    "values": [0.1, 0.2, ...],
                    "metadata": {
                        "document_id": "doc_id",
                        "chunk_index": 1,
                        "content": "content"
                    }
                }
            namespace: 命名空间（可选，Pinecone 专用，PostgreSQL 忽略此参数）
        """
        try:
            logger.info(
                "postgres_vector_upsert_started",
                vectors_count=len(vectors),
                dimension=self.dimension
            )
            
            success_count = 0
            failed_count = 0
            not_found_count = 0
            
            for i, vector_data in enumerate(vectors):
                chunk_id = vector_data["id"]
                embedding = vector_data["values"]
                metadata = vector_data.get("metadata", {})
                
                logger.debug(
                    "processing_vector_upsert",
                    index=i,
                    chunk_id=chunk_id,
                    has_values="values" in vector_data,
                    values_dimension=len(embedding) if "values" in vector_data else 0,
                    has_metadata="metadata" in vector_data,
                    metadata_keys=list(metadata.keys()) if metadata else None
                )
                
                # 📝 关键日志：验证输入数据
                logger.debug(
                    "vector_data_validation",
                    chunk_id=chunk_id,
                    embedding_type=type(embedding).__name__,
                    embedding_len=len(embedding),
                    embedding_sample=embedding[:3] if len(embedding) > 0 else None,
                    metadata_type=type(metadata).__name__,
                    metadata_content_preview=metadata.get("content", "")[:50] if metadata else None
                )
                
                # 验证向量维度
                if len(embedding) != self.dimension:
                    logger.error(
                        "vector_dimension_mismatch",
                        chunk_id=chunk_id,
                        expected_dimension=self.dimension,
                        actual_dimension=len(embedding)
                    )
                    raise ValueError(f"向量维度不匹配：期望 {self.dimension}，得到 {len(embedding)}")
                
                # 📝 关键：直接执行 UPDATE，避免 SELECT 加载 embedding 字段
                # 使用 update().values() 方式
                from sqlalchemy import update
                
                # 📝 注意：metadata 是 SQLAlchemy 保留字，需要使用 chunk_metadata
                update_data = {
                    "embedding": np.array(embedding, dtype=np.float32),
                    "content": metadata.get("content"),
                    "chunk_index": metadata.get("chunk_index"),
                    "chunk_metadata": metadata if metadata else None  # ✅ 使用 chunk_metadata 而非 metadata
                }
                
                update_stmt = (
                    update(Chunk)
                    .where(Chunk.id == chunk_id)
                    .values(**update_data)
                )
                
                await session.execute(update_stmt)
                success_count += 1
                
                logger.info(
                    "chunk_updated_successfully",
                    chunk_id=chunk_id,
                    embedding_dimension=len(embedding)
                )
            
            logger.info(
                "postgres_vector_upsert_phase_completed",
                total_vectors=len(vectors),
                successful_updates=success_count,
                chunks_not_found=not_found_count,
                failed_updates=failed_count
            )
            
            # ✅ 不再在这里 commit，由外部 session 统一管理事务
            logger.info(
                "postgres_vector_upsert_completed_without_commit",
                committed_count=success_count
            )
            
        except Exception as e:
            logger.error(
                "postgres_vector_upsert_failed",
                error=str(e),
                error_type=type(e).__name__,
                vectors_count=len(vectors),
                exc_info=True
            )
            await session.rollback()
            raise RetrievalException(f"PostgreSQL 向量插入失败：{str(e)}")

    async def delete_vectors(
        self,
        session: AsyncSession,
        ids: Optional[List[str]] = None,
        delete_all: bool = False,
        filter_dict: Optional[Dict[str, Any]] = None
    ):
        """
        删除向量
        
        Args:
            session: 数据库会话
            ids: 要删除的向量 ID 列表
            delete_all: 是否删除所有向量
            filter_dict: 过滤条件
        """
        try:
            if delete_all:
                # 删除所有向量（将 embedding 设为 NULL）
                stmt = text("UPDATE chunks SET embedding = NULL")
                await session.execute(stmt)
                logger.info("postgres_delete_all_vectors")
                
            elif ids:
                # 删除指定 ID 的向量
                for chunk_id in ids:
                    stmt = select(Chunk).where(Chunk.id == chunk_id)
                    result = await session.execute(stmt)
                    chunk = result.scalar_one_or_none()
                    if chunk:
                        chunk.embedding = None
                
                logger.info(
                    "postgres_delete_vectors_by_ids",
                    count=len(ids)
                )
                
            elif filter_dict:
                # 根据过滤条件删除向量
                stmt = select(Chunk)
                if 'document_id' in filter_dict:
                    stmt = stmt.where(Chunk.document_id == filter_dict['document_id'])
                
                result = await session.execute(stmt)
                chunks = result.scalars().all()
                
                for chunk in chunks:
                    chunk.embedding = None
                
                logger.info(
                    "postgres_delete_vectors_by_filter",
                    filter=filter_dict,
                    count=len(chunks)
                )
            
            await session.commit()
            
        except Exception as e:
            logger.error(
                "postgres_vector_delete_failed",
                error=str(e),
                exc_info=True
            )
            raise RetrievalException(f"PostgreSQL 向量删除失败：{str(e)}")

    async def get_index_stats(self, session: AsyncSession) -> Dict[str, Any]:
        """
        获取索引统计信息
        
        Args:
            session: 数据库会话
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            # 统计总向量数
            stmt = select(func.count(Chunk.id)).where(Chunk.embedding.isnot(None))
            result = await session.execute(stmt)
            total_vectors = result.scalar()
            
            # 统计按文档分组的向量数
            stmt = select(
                Chunk.document_id,
                func.count(Chunk.id)
            ).where(
                Chunk.embedding.isnot(None)
            ).group_by(Chunk.document_id)
            
            result = await session.execute(stmt)
            doc_stats = result.all()
            
            stats = {
                "total_vector_count": total_vectors or 0,
                "dimension": self.dimension,
                "index_type": self.index_type,
                "documents": [
                    {
                        "document_id": str(doc_id),
                        "vector_count": count
                    }
                    for doc_id, count in doc_stats
                ]
            }
            
            logger.debug(
                "postgres_vector_stats_retrieved",
                total_count=stats["total_vector_count"]
            )
            
            return stats
            
        except Exception as e:
            logger.error(
                "postgres_vector_stats_failed",
                error=str(e)
            )
            return {"total_vector_count": 0, "error": str(e)}

    def calculate_similarity(
        self,
        query_vector: List[float],
        candidate_vectors: List[List[float]]
    ) -> List[Tuple[int, float]]:
        """
        计算查询向量与候选向量的相似度（纯 Python 实现）
        
        Args:
            query_vector: 查询向量
            candidate_vectors: 候选向量列表
            
        Returns:
            List[Tuple[int, float]]: (索引, 相似度) 元组列表，按相似度降序排列
        """
        query_vec_np = np.array(query_vector, dtype=np.float32)
        similarities = []
        
        for i, candidate in enumerate(candidate_vectors):
            if len(candidate) != self.dimension:
                continue
                
            candidate_vec_np = np.array(candidate, dtype=np.float32)
            similarity = cosine_similarity(query_vec_np, candidate_vec_np)
            similarities.append((i, float(similarity)))
        
        # 按相似度降序排列
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities