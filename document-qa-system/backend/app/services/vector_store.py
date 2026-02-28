from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any, Optional
import asyncio
import uuid
from datetime import datetime

from app.core.config import settings
from app.core.logging_config import logger
from app.core.exceptions import VectorStoreError
from app.services.embedding import embedding_service

class PineconeVectorStore:
    """Pinecone向量数据库存储"""
    
    def __init__(self):
        self.api_key = settings.PINECONE_API_KEY
        self.index_name = settings.PINECONE_INDEX_NAME
        self.dimension = settings.VECTOR_DIMENSION
        self.top_k = settings.TOP_K_RESULTS
        self.score_threshold = settings.SCORE_THRESHOLD
        self.pc = None
        self.index = None
        
    async def initialize(self):
        """初始化Pinecone连接和索引"""
        try:
            # 初始化Pinecone客户端
            self.pc = Pinecone(api_key=self.api_key)
            
            # 检查索引是否存在
            existing_indexes = self.pc.list_indexes().names()
            if self.index_name not in existing_indexes:
                logger.info(f"创建新的向量索引: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                await asyncio.sleep(5)  # 等待索引创建完成
            
            # 连接到索引
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Pinecone向量数据库初始化成功: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Pinecone初始化失败: {str(e)}")
            raise VectorStoreError(f"向量数据库初始化失败: {str(e)}")
    
    async def store_document_chunks(self, document_id: str, chunks: List[str], 
                                  metadata: Optional[Dict[str, Any]] = None) -> List[str]:
        """存储文档chunks到向量数据库"""
        try:
            if not self.index:
                raise VectorStoreError("向量数据库未初始化")
            
            # 生成向量嵌入
            embeddings = await embedding_service.batch_embed_documents(chunks)
            
            # 准备数据用于存储
            vectors_to_upsert = []
            chunk_ids = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_id = f"{document_id}_{i}"
                chunk_ids.append(chunk_id)
                
                # 构建元数据
                chunk_metadata = {
                    "document_id": document_id,
                    "chunk_index": i,
                    "chunk_text": chunk,
                    "created_at": datetime.now().isoformat(),
                    **(metadata or {})
                }
                
                vectors_to_upsert.append({
                    "id": chunk_id,
                    "values": embedding,
                    "metadata": chunk_metadata
                })
            
            # 批量插入向量
            if vectors_to_upsert:
                self.index.upsert(vectors=vectors_to_upsert)
                logger.info(f"文档chunks存储成功: {document_id}, 数量: {len(vectors_to_upsert)}")
            
            return chunk_ids
            
        except Exception as e:
            logger.error(f"文档chunks存储失败: {str(e)}")
            raise VectorStoreError(f"文档存储失败: {str(e)}")
    
    async def search_similar_chunks(self, query: str, top_k: Optional[int] = None,
                                  document_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """搜索相似的文档chunks"""
        try:
            if not self.index:
                raise VectorStoreError("向量数据库未初始化")
            
            # 获取查询的向量嵌入
            query_embedding = embedding_service.embed_query(query)
            
            # 构建过滤条件
            filter_dict = {}
            if document_ids:
                filter_dict["document_id"] = {"$in": document_ids}
            
            # 执行相似性搜索
            search_results = self.index.query(
                vector=query_embedding,
                top_k=top_k or self.top_k,
                include_metadata=True,
                filter=filter_dict if filter_dict else None
            )
            
            # 处理搜索结果
            similar_chunks = []
            for match in search_results.matches:
                if match.score >= self.score_threshold:
                    chunk_info = {
                        "chunk_id": match.id,
                        "document_id": match.metadata.get("document_id"),
                        "chunk_text": match.metadata.get("chunk_text"),
                        "chunk_index": match.metadata.get("chunk_index"),
                        "score": match.score,
                        "metadata": match.metadata
                    }
                    similar_chunks.append(chunk_info)
            
            logger.info(f"相似性搜索完成，找到 {len(similar_chunks)} 个相关chunks")
            return similar_chunks
            
        except Exception as e:
            logger.error(f"相似性搜索失败: {str(e)}")
            raise VectorStoreError(f"向量搜索失败: {str(e)}")
    
    async def delete_document_chunks(self, document_id: str) -> bool:
        """删除文档的所有chunks"""
        try:
            if not self.index:
                raise VectorStoreError("向量数据库未初始化")
            
            # 查询该文档的所有chunks
            query_filter = {"document_id": {"$eq": document_id}}
            query_result = self.index.query(
                vector=[0] * self.dimension,  # 使用零向量查询
                top_k=10000,  # 获取所有匹配项
                include_metadata=True,
                filter=query_filter
            )
            
            # 提取chunk IDs
            chunk_ids = [match.id for match in query_result.matches]
            
            # 删除chunks
            if chunk_ids:
                self.index.delete(ids=chunk_ids)
                logger.info(f"文档chunks删除成功: {document_id}, 数量: {len(chunk_ids)}")
            
            return True
            
        except Exception as e:
            logger.error(f"文档chunks删除失败: {str(e)}")
            raise VectorStoreError(f"文档删除失败: {str(e)}")
    
    async def get_document_chunk_count(self, document_id: str) -> int:
        """获取文档的chunk数量"""
        try:
            if not self.index:
                raise VectorStoreError("向量数据库未初始化")
            
            query_filter = {"document_id": {"$eq": document_id}}
            query_result = self.index.query(
                vector=[0] * self.dimension,
                top_k=10000,
                include_metadata=False,
                filter=query_filter
            )
            
            return len(query_result.matches)
            
        except Exception as e:
            logger.error(f"获取文档chunk数量失败: {str(e)}")
            return 0
    
    async def list_documents(self) -> List[Dict[str, Any]]:
        """列出所有文档信息"""
        try:
            if not self.index:
                raise VectorStoreError("向量数据库未初始化")
            
            # 获取所有唯一的document_id
            query_result = self.index.query(
                vector=[0] * self.dimension,
                top_k=10000,
                include_metadata=True
            )
            
            # 提取唯一文档信息
            documents = {}
            for match in query_result.matches:
                doc_id = match.metadata.get("document_id")
                if doc_id and doc_id not in documents:
                    documents[doc_id] = {
                        "document_id": doc_id,
                        "filename": match.metadata.get("filename", "Unknown"),
                        "created_at": match.metadata.get("created_at"),
                        "chunk_count": 0
                    }
                if doc_id:
                    documents[doc_id]["chunk_count"] += 1
            
            return list(documents.values())
            
        except Exception as e:
            logger.error(f"列出文档失败: {str(e)}")
            return []

# 创建全局实例
vector_store = PineconeVectorStore()