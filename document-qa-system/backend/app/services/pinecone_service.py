"""
Pinecone 向量数据库服务
负责向量的存储和检索

注意：已升级至 Pinecone SDK v8+
API 文档：https://docs.pinecone.io/reference/api
"""
from typing import List, Dict, Any, Optional
import asyncio
from app.core.config import get_settings
from app.exceptions import RetrievalException
import structlog

logger = structlog.get_logger()
settings = get_settings()


class PineconeService:
    """
    Pinecone 向量数据库服务 (SDK v8+)
    
    功能:
    - 创建和管理 Index
    - 向量 upsert（插入/更新）
    - 相似度搜索
    - 向量删除
    
    SDK v8 变更:
    - 延迟导入 pinecone 模块以避免版本冲突
    - 使用新 API: pc.has_index(), pc.create_index_for_model()
    """
    
    def __init__(self):
        """初始化 Pinecone 客户端（延迟导入）"""
        self.api_key = settings.PINECONE_API_KEY
        self.index_name = settings.PINECONE_INDEX_NAME
        self.dimension = 1024  # text-embedding-v4 实际输出维度为 1024
        
        # 延迟导入 Pinecone SDK v8
        try:
            from pinecone import Pinecone, ServerlessSpec, CloudProvider, AwsRegion, VectorType
            self.Pinecone = Pinecone
            self.ServerlessSpec = ServerlessSpec
            self.CloudProvider = CloudProvider
            self.AwsRegion = AwsRegion
            self.VectorType = VectorType
        except ImportError as e:
            logger.error(
                "pinecone_sdk_import_failed",
                error=str(e),
                suggestion="Please install pinecone>=5.1.0"
            )
            raise RetrievalException(f"Pinecone SDK v8 导入失败：{str(e)}")
        
        # 初始化客户端 (v8 API)
        # Option A: Pass API key directly
        self.pc = Pinecone(api_key=self.api_key)
        self._index = None
    
    @property
    def index(self):
        """懒加载 Index"""
        if self._index is None:
            try:
                self._index = self.pc.Index(self.index_name)
            except Exception as e:
                logger.error(
                    "pinecone_index_not_found",
                    index_name=self.index_name,
                    error=str(e)
                )
                raise RetrievalException(f"Pinecone Index '{self.index_name}' not found")
        return self._index
    
    async def create_index_if_not_exists(self):
        """
        如果 Index 不存在则创建
        
        SDK v8+ API:
        - pc.list_indexes(): 列出所有索引
        - pc.create_index(): 创建新索引
        - pc.delete_index(): 删除索引
        """
        try:
            # 检查索引是否存在 (v8+ API)
            existing_indexes = self.pc.list_indexes()
            index_names = [idx.name for idx in existing_indexes]
            
            if self.index_name not in index_names:
                logger.info(
                    "creating_pinecone_index",
                    index_name=self.index_name,
                    dimension=self.dimension,
                    sdk_version="v8+"
                )
                
                # 使用 v8+ API 创建索引
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=self.ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    ),
                    vector_type=self.VectorType.DENSE
                )
                
                # 等待索引准备就绪
                import time
                while True:
                    index_info = self.pc.describe_index(self.index_name)
                    if index_info.status.ready:
                        break
                    logger.info(
                        "waiting_for_index_ready",
                        index_name=self.index_name,
                        status=index_info.status.state
                    )
                    await asyncio.sleep(2)
                
                logger.info(
                    "pinecone_index_created",
                    index_name=self.index_name
                )
            else:
                logger.info(
                    "pinecone_index_exists",
                    index_name=self.index_name
                )
                
        except Exception as e:
            logger.error(
                "pinecone_index_creation_failed",
                index_name=self.index_name,
                error=str(e),
                sdk_version="v8+"
            )
            raise RetrievalException(f"创建 Pinecone Index 失败：{str(e)}")
    
    async def upsert_vectors(
        self, 
        vectors: List[Dict[str, Any]],
        namespace: Optional[str] = None
    ):
        """
        插入或更新向量
        
        Args:
            vectors: 向量列表，每个向量包含 id, values, metadata
                示例：[{
                    "id": "chunk_123",
                    "values": [0.1, 0.2, ...],
                    "metadata": {
                        "document_id": "doc_456",
                        "chunk_index": 1,
                        "content": "原文片段"
                    }
                }]
            namespace: 命名空间（用于隔离不同文档）
        """
        try:
            # 批量 upsert（Pinecone 限制每批 100 个向量）
            batch_size = 100
            
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                
                await asyncio.to_thread(
                    self.index.upsert,
                    vectors=batch,
                    namespace=namespace or "default"
                )
                
                logger.debug(
                    "pinecone_upsert_batch",
                    batch_num=i // batch_size + 1,
                    count=len(batch)
                )
            
            logger.info(
                "pinecone_upsert_completed",
                total_count=len(vectors),
                namespace=namespace
            )
            
        except Exception as e:
            logger.error(
                "pinecone_upsert_failed",
                error=str(e),
                exc_info=True
            )
            raise RetrievalException(f"向量插入失败：{str(e)}")
    
    async def similarity_search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        相似度搜索
        
        Args:
            query_vector: 查询向量（1536 维）
            top_k: 返回最相似的 K 个结果
            filter_dict: 过滤条件（如 document_id）
            include_metadata: 是否返回元数据
            
        Returns:
            List[Dict[str, Any]]: 搜索结果，按相似度降序排列
                示例：[{
                    "id": "chunk_123",
                    "score": 0.95,
                    "values": [...],  # 如果 include_values=True
                    "metadata": {...}  # 如果 include_metadata=True
                }]
        """
        try:
            result = await asyncio.to_thread(
                self.index.query,
                vector=query_vector,
                top_k=top_k,
                filter=filter_dict or {},
                include_metadata=include_metadata,
                include_values=False  # 默认不返回向量值，节省流量
            )
            
            matches = result.get('matches', [])
            
            logger.info(
                "pinecone_query_completed",
                top_k=top_k,
                results_count=len(matches),
                filter=filter_dict
            )
            
            return matches
            
        except Exception as e:
            logger.error(
                "pinecone_query_failed",
                error=str(e),
                exc_info=True
            )
            raise RetrievalException(f"向量检索失败：{str(e)}")
    
    async def delete_index(self):
        """
        删除 Index
        
        SDK v8+ API:
        - pc.delete_index(): 删除指定索引
        """
        try:
            existing_indexes = self.pc.list_indexes()
            index_names = [idx.name for idx in existing_indexes]
            
            if self.index_name in index_names:
                logger.info(
                    "deleting_pinecone_index",
                    index_name=self.index_name
                )
                
                self.pc.delete_index(self.index_name)
                
                logger.info(
                    "pinecone_index_deleted",
                    index_name=self.index_name
                )
            else:
                logger.warning(
                    "pinecone_index_not_found",
                    index_name=self.index_name
                )
                
        except Exception as e:
            logger.error(
                "pinecone_index_deletion_failed",
                index_name=self.index_name,
                error=str(e),
                sdk_version="v8+"
            )
            raise RetrievalException(f"删除 Pinecone Index 失败：{str(e)}")
    
    async def delete_vectors(
        self,
        ids: Optional[List[str]] = None,
        delete_all: bool = False,
        namespace: Optional[str] = None
    ):
        """
        删除向量
        
        Args:
            ids: 要删除的向量 ID 列表
            delete_all: 是否删除所有向量
            namespace: 命名空间
        """
        try:
            if delete_all:
                await asyncio.to_thread(
                    self.index.delete,
                    delete_all=True,
                    namespace=namespace or "default"
                )
                logger.info(
                    "pinecone_delete_all",
                    namespace=namespace
                )
            elif ids:
                await asyncio.to_thread(
                    self.index.delete,
                    ids=ids,
                    namespace=namespace or "default"
                )
                logger.info(
                    "pinecone_delete_ids",
                    count=len(ids),
                    namespace=namespace
                )
            
        except Exception as e:
            logger.error(
                "pinecone_delete_failed",
                error=str(e),
                exc_info=True
            )
            raise RetrievalException(f"删除向量失败：{str(e)}")
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """
        获取 Index 统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
                {
                    "total_vector_count": 10000,
                    "namespaces": {...}
                }
        """
        try:
            stats = await asyncio.to_thread(
                self.index.describe_index_stats
            )
            
            logger.debug(
                "pinecone_stats_retrieved",
                total_count=stats.get('total_vector_count', 0)
            )
            
            return stats
            
        except Exception as e:
            logger.error(
                "pinecone_stats_failed",
                error=str(e)
            )
            return {"total_vector_count": 0, "error": str(e)}
