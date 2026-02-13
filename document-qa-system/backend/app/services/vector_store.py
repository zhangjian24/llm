import pinecone
from typing import List, Dict, Any, Optional
import numpy as np
from app.core.config import settings
from app.core.exceptions import VectorStoreException
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class PineconeVectorStore:
    """Pinecone向量数据库服务"""
    
    def __init__(self):
        self.index_name = settings.PINECONE_INDEX_NAME
        self.dimension = settings.EMBEDDING_DIMENSION
        self.metric = "cosine"
        
        try:
            # 初始化Pinecone客户端
            pinecone.init(
                api_key=settings.PINECONE_API_KEY,
                environment=settings.PINECONE_ENVIRONMENT
            )
            logger.info("Pinecone客户端初始化成功")
        except Exception as e:
            logger.error(f"Pinecone初始化失败: {str(e)}")
            raise VectorStoreException(f"Pinecone初始化失败: {str(e)}")
    
    def create_index(self, recreate: bool = False) -> bool:
        """创建向量索引"""
        try:
            # 检查索引是否存在
            if self.index_name in pinecone.list_indexes():
                if recreate:
                    logger.info(f"删除现有索引: {self.index_name}")
                    pinecone.delete_index(self.index_name)
                else:
                    logger.info(f"索引 {self.index_name} 已存在")
                    return True
            
            # 创建新索引
            logger.info(f"创建索引: {self.index_name}")
            pinecone.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=self.metric,
                pod_type="p1.x1"
            )
            
            # 等待索引就绪
            logger.info("等待索引就绪...")
            pinecone.describe_index(self.index_name)
            
            logger.info(f"索引 {self.index_name} 创建成功")
            return True
            
        except Exception as e:
            logger.error(f"创建索引失败: {str(e)}")
            raise VectorStoreException(f"创建索引失败: {str(e)}")
    
    def get_index(self):
        """获取索引实例"""
        try:
            return pinecone.Index(self.index_name)
        except Exception as e:
            logger.error(f"获取索引失败: {str(e)}")
            raise VectorStoreException(f"获取索引失败: {str(e)}")
    
    def upsert_vectors(self, vectors: List[Dict[str, Any]]) -> bool:
        """插入或更新向量"""
        try:
            index = self.get_index()
            
            # 准备批量插入数据
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                upsert_data = []
                
                for vector_data in batch:
                    upsert_data.append({
                        'id': vector_data['id'],
                        'values': vector_data['values'].tolist() if isinstance(vector_data['values'], np.ndarray) else vector_data['values'],
                        'metadata': vector_data.get('metadata', {})
                    })
                
                index.upsert(upsert_data)
                logger.info(f"已插入批次 {i//batch_size + 1}/{(len(vectors)-1)//batch_size + 1}")
            
            logger.info(f"成功插入 {len(vectors)} 个向量")
            return True
            
        except Exception as e:
            logger.error(f"向量插入失败: {str(e)}")
            raise VectorStoreException(f"向量插入失败: {str(e)}")
    
    def query_vectors(self, query_vector: List[float], top_k: int = 10, 
                     filter_dict: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """查询相似向量"""
        try:
            index = self.get_index()
            
            # 执行查询
            query_result = index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                include_values=False,
                filter=filter_dict
            )
            
            # 处理查询结果
            results = []
            for match in query_result.matches:
                results.append({
                    'id': match.id,
                    'score': match.score,
                    'metadata': match.metadata
                })
            
            logger.info(f"查询返回 {len(results)} 个结果")
            return results
            
        except Exception as e:
            logger.error(f"向量查询失败: {str(e)}")
            raise VectorStoreException(f"向量查询失败: {str(e)}")
    
    def delete_vectors(self, ids: List[str]) -> bool:
        """删除向量"""
        try:
            index = self.get_index()
            index.delete(ids=ids)
            logger.info(f"成功删除 {len(ids)} 个向量")
            return True
            
        except Exception as e:
            logger.error(f"向量删除失败: {str(e)}")
            raise VectorStoreException(f"向量删除失败: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        try:
            index = self.get_index()
            stats = index.describe_index_stats()
            return {
                'dimension': stats.dimension,
                'index_fullness': stats.index_fullness,
                'namespaces': stats.namespaces,
                'total_vector_count': sum(ns.vector_count for ns in stats.namespaces.values()) if stats.namespaces else 0
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            raise VectorStoreException(f"获取统计信息失败: {str(e)}")

# 全局向量存储实例
vector_store = PineconeVectorStore()