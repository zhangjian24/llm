"""
向量服务适配器
提供统一的向量服务接口，隐藏底层实现细节（Pinecone vs PostgreSQL）
"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import structlog
from app.exceptions import RetrievalException

# 为了避免循环导入，在函数内部导入具体实现
class PostgreSQLVectorService:  # 类型提示用
    pass

logger = structlog.get_logger()


class VectorServiceInterface(ABC):
    """向量服务接口定义"""
    
    @abstractmethod
    async def similarity_search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """相似度搜索接口"""
        pass
    
    @abstractmethod
    async def upsert_vectors(
        self,
        session,
        vectors: List[Dict[str, Any]],
        namespace: Optional[str] = None
    ):
        """插入或更新向量"""
        pass
    
    @abstractmethod
    async def delete_vectors(
        self,
        ids: Optional[List[str]] = None,
        delete_all: bool = False,
        namespace: Optional[str] = None
    ):
        """删除向量"""
        pass
    
    @abstractmethod
    async def get_index_stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        pass


class VectorServiceAdapter(VectorServiceInterface):
    """
    向量服务适配器
    根据配置自动选择合适的向量服务实现
    """
    
    def __init__(self, service_impl):
        """
        初始化适配器
        
        Args:
            service_impl: 实际的向量服务实现（PostgreSQL 或 Pinecone）
        """
        self.service_impl = service_impl
        self.service_type = type(service_impl).__name__
        logger.info(
            "vector_service_adapter_initialized",
            service_type=self.service_type
        )
    
    async def similarity_search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """相似度搜索 - 适配不同实现的接口差异"""
        try:
            # 记录搜索参数
            logger.info(
                "vector_search_started",
                service_type=self.service_type,
                top_k=top_k,
                filter=filter_dict,
                vector_dimension=len(query_vector) if query_vector else 0
            )
            
            # 调用具体实现
            if type(self.service_impl).__name__ == 'PostgreSQLVectorService':
                # PostgreSQL 实现需要 session 参数
                from app.core.database import AsyncSessionLocal
                from app.services.postgresql_vector_service import PostgreSQLVectorService
                async with AsyncSessionLocal() as session:
                    result = await self.service_impl.similarity_search(
                        session=session,
                        query_vector=query_vector,
                        top_k=top_k,
                        filter_dict=filter_dict,
                        include_metadata=include_metadata
                    )
            else:
                # Pinecone 实现
                result = await self.service_impl.similarity_search(
                    query_vector=query_vector,
                    top_k=top_k,
                    filter_dict=filter_dict,
                    include_metadata=include_metadata
                )
            
            logger.info(
                "vector_search_completed",
                service_type=self.service_type,
                results_count=len(result)
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "vector_search_failed",
                service_type=self.service_type,
                error=str(e),
                exc_info=True
            )
            raise RetrievalException(f"向量搜索失败[{self.service_type}]：{str(e)}")
    
    async def upsert_vectors(
        self,
        session,
        vectors: List[Dict[str, Any]],
        namespace: Optional[str] = None
    ):
        """插入或更新向量 - 适配不同实现的接口差异"""
        try:
            logger.info(
                "vector_upsert_started",
                service_type=self.service_type,
                vectors_count=len(vectors),
                namespace=namespace
            )
                
            # 📝 关键：根据 service_type（类名）选择正确的调用方式
            if type(self.service_impl).__name__ == 'PostgreSQLVectorService':
                # PostgreSQL 实现需要 session
                await self.service_impl.upsert_vectors(
                    session=session,
                    vectors=vectors,
                    namespace=namespace  # ✅ 传递 namespace（虽然不使用）
                )
            else:
                # Pinecone 实现不需要 session
                await self.service_impl.upsert_vectors(
                    vectors=vectors,
                    namespace=namespace
                )
                
            logger.info(
                "vector_upsert_completed",
                service_type=self.service_type,
                vectors_count=len(vectors)
            )
                
        except Exception as e:
            logger.error(
                "vector_upsert_failed",
                service_type=self.service_type,
                error=str(e),
                exc_info=True
            )
            raise RetrievalException(f"向量插入失败 [{self.service_type}]：{str(e)}")
    
    async def delete_vectors(
        self,
        ids: Optional[List[str]] = None,
        delete_all: bool = False,
        namespace: Optional[str] = None
    ):
        """删除向量 - 适配不同实现的接口差异"""
        try:
            logger.info(
                "vector_delete_started",
                service_type=self.service_type,
                ids_count=len(ids) if ids else 0,
                delete_all=delete_all,
                namespace=namespace
            )
            
            # 调用具体实现
            if hasattr(self.service_impl, 'session'):
                # PostgreSQL 实现
                from app.core.database import AsyncSessionLocal
                async with AsyncSessionLocal() as session:
                    await self.service_impl.delete_vectors(
                        session=session,
                        ids=ids,
                        delete_all=delete_all,
                        filter_dict={"namespace": namespace} if namespace else None
                    )
            else:
                # Pinecone 实现
                await self.service_impl.delete_vectors(
                    ids=ids,
                    delete_all=delete_all,
                    namespace=namespace
                )
            
            logger.info(
                "vector_delete_completed",
                service_type=self.service_type
            )
            
        except Exception as e:
            logger.error(
                "vector_delete_failed",
                service_type=self.service_type,
                error=str(e),
                exc_info=True
            )
            raise RetrievalException(f"向量删除失败[{self.service_type}]：{str(e)}")
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """获取索引统计信息 - 适配不同实现的接口差异"""
        try:
            logger.info(
                "vector_stats_requested",
                service_type=self.service_type
            )
            
            # 调用具体实现
            if hasattr(self.service_impl, 'session'):
                # PostgreSQL 实现
                from app.core.database import AsyncSessionLocal
                async with AsyncSessionLocal() as session:
                    result = await self.service_impl.get_index_stats(session)
            else:
                # Pinecone 实现
                result = await self.service_impl.get_index_stats()
            
            logger.info(
                "vector_stats_retrieved",
                service_type=self.service_type,
                stats=result
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "vector_stats_failed",
                service_type=self.service_type,
                error=str(e),
                exc_info=True
            )
            return {"error": str(e), "service_type": self.service_type}


# 便利函数
def create_vector_service(config: Dict[str, Any]) -> VectorServiceAdapter:
    """
    根据配置创建向量服务
    
    Args:
        config: 配置字典，包含 'vector_store_type' 键
        
    Returns:
        VectorServiceAdapter: 向量服务适配器实例
    """
    vector_store_type = config.get('vector_store_type', 'postgresql').lower()
    
    if vector_store_type == 'postgresql':
        from app.services.postgresql_vector_service import PostgreSQLVectorService
        service_impl = PostgreSQLVectorService()
        logger.info("using_postgresql_vector_service")
    elif vector_store_type == 'pinecone':
        from app.services.pinecone_service import PineconeService
        service_impl = PineconeService()
        logger.info("using_pinecone_vector_service")
    else:
        raise ValueError(f"不支持的向量存储类型：{vector_store_type}")
    
    return VectorServiceAdapter(service_impl)