"""
Pinecone向量数据库服务
负责文档向量化存储和语义检索
"""

import uuid
from typing import List, Dict, Any, Optional
# 暂时注释掉，后续根据新版API调整
# from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain_core.documents import Document as LangchainDocument

from ..core.config import settings
from ..core.logging import logger
from ..models.schemas import DocumentMetadata, SearchResult


class PineconeService:
    """Pinecone向量数据库服务类"""
    
    def __init__(self):
        self.client: Optional[Pinecone] = None
        self.index = None
        self.embeddings: Optional[OpenAIEmbeddings] = None
        self.vector_store = None
    
    async def initialize(self, embeddings: OpenAIEmbeddings) -> None:
        """
        初始化Pinecone服务
        
        Args:
            embeddings: 已初始化的嵌入模型
        """
        try:
            logger.info("正在初始化Pinecone服务...")
            
            # 保存嵌入模型引用
            self.embeddings = embeddings
            
            # 初始化Pinecone客户端
            self.client = Pinecone(api_key=settings.PINECONE_API_KEY)
            
            # 检查索引是否存在，如果不存在则创建
            await self._ensure_index_exists()
            
            # 获取索引
            self.index = self.client.Index(settings.PINECONE_INDEX_NAME)
            
            # 初始化Langchain向量存储
            self.vector_store = LangchainPinecone(
                index=self.index,
                embedding=embeddings,
                text_key="text"
            )
            
            logger.info("Pinecone服务初始化成功")
            
        except Exception as e:
            logger.error(f"Pinecone服务初始化失败: {str(e)}")
            raise
    
    async def _ensure_index_exists(self) -> None:
        """确保索引存在，不存在则创建"""
        try:
            indexes = self.client.list_indexes()
            index_names = [idx['name'] for idx in indexes]
            
            if settings.PINECONE_INDEX_NAME not in index_names:
                logger.info(f"创建新的Pinecone索引: {settings.PINECONE_INDEX_NAME}")
                
                # 创建索引 (text-embedding-v4的维度为1536)
                self.client.create_index(
                    name=settings.PINECONE_INDEX_NAME,
                    dimension=1536,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                logger.info("Pinecone索引创建成功")
            else:
                logger.info(f"Pinecone索引已存在: {settings.PINECONE_INDEX_NAME}")
                
        except Exception as e:
            logger.error(f"索引检查/创建失败: {str(e)}")
            raise
    
    async def store_document_chunks(
        self, 
        chunks: List[str], 
        metadata: DocumentMetadata
    ) -> List[str]:
        """
        存储文档分块到向量数据库
        
        Args:
            chunks: 文档分块列表
            metadata: 文档元数据
            
        Returns:
            分块ID列表
        """
        try:
            logger.info(f"正在存储文档分块: {metadata.filename}, 数量: {len(chunks)}")
            
            # 生成分块ID
            chunk_ids = [f"{metadata.doc_id}_{i}" for i in range(len(chunks))]
            
            # 创建Langchain文档对象
            documents = []
            for i, chunk in enumerate(chunks):
                doc = LangchainDocument(
                    page_content=chunk,
                    metadata={
                        "doc_id": metadata.doc_id,
                        "chunk_id": chunk_ids[i],
                        "filename": metadata.filename,
                        "chunk_index": i,
                        "upload_time": metadata.upload_time.isoformat()
                    }
                )
                documents.append(doc)
            
            # 批量存储到向量数据库
            self.vector_store.add_documents(documents, ids=chunk_ids)
            
            logger.info(f"文档分块存储成功: {len(chunk_ids)} 个分块")
            return chunk_ids
            
        except Exception as e:
            logger.error(f"文档分块存储失败: {str(e)}")
            raise
    
    async def search_similar_documents(
        self, 
        query: str, 
        top_k: int = 20
    ) -> List[SearchResult]:
        """
        搜索相似文档
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            搜索结果列表
        """
        try:
            logger.info(f"正在搜索相似文档，查询: {query[:50]}...")
            
            # 使用Langchain向量存储进行相似度搜索
            results = self.vector_store.similarity_search_with_score(
                query, 
                k=top_k
            )
            
            # 转换为SearchResult格式
            search_results = []
            for doc, score in results:
                result = SearchResult(
                    content=doc.page_content,
                    metadata=doc.metadata,
                    score=float(score),
                    doc_id=doc.metadata.get("doc_id", "")
                )
                search_results.append(result)
            
            logger.info(f"搜索完成，返回 {len(search_results)} 个结果")
            return search_results
            
        except Exception as e:
            logger.error(f"文档搜索失败: {str(e)}")
            raise
    
    async def delete_document(self, doc_id: str) -> bool:
        """
        删除文档的所有分块
        
        Args:
            doc_id: 文档ID
            
        Returns:
            删除是否成功
        """
        try:
            logger.info(f"正在删除文档: {doc_id}")
            
            # 查询该文档的所有分块
            query_filter = {"doc_id": {"$eq": doc_id}}
            
            # 删除操作
            # 注意：Pinecone的删除操作可能需要根据实际API调整
            # 这里假设可以通过过滤条件删除
            self.index.delete(filter=query_filter)
            
            logger.info(f"文档删除成功: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"文档删除失败: {str(e)}")
            return False
    
    async def get_document_list(self) -> List[DocumentMetadata]:
        """
        获取所有文档列表
        
        Returns:
            文档元数据列表
        """
        try:
            logger.info("正在获取文档列表...")
            
            # Pinecone本身不直接支持列出所有文档
            # 这里需要通过查询或其他方式实现
            # 暂时返回空列表，实际实现需要根据业务需求调整
            documents = []
            
            logger.info(f"文档列表获取完成，共 {len(documents)} 个文档")
            return documents
            
        except Exception as e:
            logger.error(f"文档列表获取失败: {str(e)}")
            raise
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        获取索引统计信息
        
        Returns:
            索引统计信息
        """
        try:
            if not self.index:
                return {"error": "索引未初始化"}
            
            stats = self.index.describe_index_stats()
            return {
                "dimension": stats.get("dimension", 0),
                "index_fullness": stats.get("index_fullness", 0),
                "namespaces": stats.get("namespaces", {}),
                "total_vector_count": stats.get("total_vector_count", 0)
            }
            
        except Exception as e:
            logger.error(f"获取索引统计失败: {str(e)}")
            return {"error": str(e)}