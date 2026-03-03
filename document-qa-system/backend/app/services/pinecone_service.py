"""
Pinecone向量数据库服务
负责文档向量化存储和语义检索
"""

import uuid
import time
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
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
            # 请求接收阶段 - INFO级别
            logger.info(f"[PINECONE_INIT] 开始初始化Pinecone服务 - 索引名称: {settings.PINECONE_INDEX_NAME}")
            
            # 数据验证阶段 - DEBUG级别
            logger.debug(f"[PINECONE_INIT] 初始化参数验证 - API密钥长度: {len(settings.PINECONE_API_KEY) if settings.PINECONE_API_KEY else 0}")
            
            # 保存嵌入模型引用
            self.embeddings = embeddings
            logger.debug(f"[PINECONE_INIT] 嵌入模型引用保存完成")
            
            # 初始化Pinecone客户端 - 外部服务调用阶段
            logger.info(f"[PINECONE_INIT] 正在初始化Pinecone客户端")
            client_init_start = time.time()
            self.client = Pinecone(api_key=settings.PINECONE_API_KEY)
            client_init_time = time.time() - client_init_start
            logger.info(f"[PINECONE_INIT] Pinecone客户端初始化完成 - 耗时: {client_init_time:.2f}s")
            
            # 检查索引是否存在，如果不存在则创建 - 外部服务调用阶段
            logger.info(f"[PINECONE_INIT] 检查索引存在性")
            await self._ensure_index_exists()
            
            # 获取索引 - 外部服务调用阶段
            logger.info(f"[PINECONE_INIT] 正在获取索引: {settings.PINECONE_INDEX_NAME}")
            index_get_start = time.time()
            self.index = self.client.Index(settings.PINECONE_INDEX_NAME)
            index_get_time = time.time() - index_get_start
            logger.info(f"[PINECONE_INIT] 索引获取完成 - 耗时: {index_get_time:.2f}s")
            
            # 初始化 Langchain 向量存储 - 业务逻辑处理阶段
            logger.info(f"[PINECONE_INIT] 正在初始化 Langchain 向量存储")
            vector_store_init_start = time.time()
                        
            # 使用 Pinecone v5+ 的新 API，避免 langchain_community 的版本检查问题
            # 直接使用 index 对象，不通过 LangchainPinecone 包装
            self.vector_store = None  # 暂时不使用 LangchainPinecone
                        
            vector_store_init_time = time.time() - vector_store_init_start
            logger.info(f"[PINECONE_INIT] Pinecone 索引准备完成 - 耗时：{vector_store_init_time:.2f}s")
            
            # 响应返回阶段 - INFO级别
            total_time = client_init_time + index_get_time + vector_store_init_time
            logger.info(f"[PINECONE_INIT] Pinecone服务初始化成功 - 总耗时: {total_time:.2f}s")
            
        except Exception as e:
            # 异常处理 - ERROR级别
            logger.error(f"[PINECONE_INIT] Pinecone服务初始化失败 - 错误类型: {type(e).__name__}, 错误信息: {str(e)}", exc_info=True)
            raise
    
    async def _ensure_index_exists(self) -> None:
        """确保索引存在，不存在则创建"""
        try:
            # 外部服务调用阶段
            logger.info(f"[PINECONE_ENSURE_INDEX] 正在检查索引存在性 - 目标索引: {settings.PINECONE_INDEX_NAME}")
            list_indexes_start = time.time()
            indexes = self.client.list_indexes()
            index_names = [idx['name'] for idx in indexes]
            list_indexes_time = time.time() - list_indexes_start
            logger.info(f"[PINECONE_ENSURE_INDEX] 索引列表获取完成 - 现有索引数: {len(index_names)}, 耗时: {list_indexes_time:.2f}s")
            
            if settings.PINECONE_INDEX_NAME not in index_names:
                logger.info(f"[PINECONE_ENSURE_INDEX] 创建新的Pinecone索引: {settings.PINECONE_INDEX_NAME}")
                
                # 创建索引 (text-embedding-v4的维度为1536) - 外部服务调用阶段
                create_index_start = time.time()
                self.client.create_index(
                    name=settings.PINECONE_INDEX_NAME,
                    dimension=1536,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                create_index_time = time.time() - create_index_start
                logger.info(f"[PINECONE_ENSURE_INDEX] Pinecone索引创建成功 - 维度: 1536, 距离度量: cosine, 耗时: {create_index_time:.2f}s")
            else:
                logger.info(f"[PINECONE_ENSURE_INDEX] Pinecone索引已存在: {settings.PINECONE_INDEX_NAME}")
                
        except Exception as e:
            # 异常处理 - ERROR级别
            logger.error(f"[PINECONE_ENSURE_INDEX] 索引检查/创建失败 - 错误类型: {type(e).__name__}, 错误信息: {str(e)}", exc_info=True)
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
            # 请求接收阶段 - INFO级别
            logger.info(f"[PINECONE_STORE_CHUNKS] 开始存储文档分块 - 文件名: {metadata.filename}, 分块数量: {len(chunks)}, 文档ID: {metadata.doc_id}")
            
            # 数据验证阶段 - DEBUG级别
            logger.debug(f"[PINECONE_STORE_CHUNKS] 存储参数验证 - 分块详情: {{'avg_chunk_length': {sum(len(chunk) for chunk in chunks)//len(chunks) if chunks else 0}, 'total_chars': sum(len(chunk) for chunk in chunks)}}")
            
            # 生成分块ID - 业务逻辑处理阶段
            logger.debug(f"[PINECONE_STORE_CHUNKS] 正在生成分块ID")
            chunk_ids = [f"{metadata.doc_id}_{i}" for i in range(len(chunks))]
            logger.debug(f"[PINECONE_STORE_CHUNKS] 分块ID生成完成 - 数量: {len(chunk_ids)}")
            
            # 创建Langchain文档对象 - 业务逻辑处理阶段
            logger.debug(f"[PINECONE_STORE_CHUNKS] 正在创建Langchain文档对象")
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
            logger.debug(f"[PINECONE_STORE_CHUNKS] Langchain文档对象创建完成 - 数量: {len(documents)}")
            
            # 批量存储到向量数据库 - 外部服务调用阶段
            logger.info(f"[PINECONE_STORE_CHUNKS] 正在批量存储到向量数据库")
            storage_start = time.time()
                        
            # 使用 Pinecone v5+ 原生 API 直接上传向量
            # 需要先生成向量
            vectors_to_upsert = []
            for i, (chunk, chunk_id) in enumerate(zip(chunks, chunk_ids)):
                # 生成该 chunk 的向量 (使用 embeddings)
                embedding = await embeddings.aembed_query(chunk)
                            
                vector_record = {
                    "id": chunk_id,
                    "values": embedding,
                    "metadata": {
                        "doc_id": metadata.doc_id,
                        "chunk_id": chunk_id,
                        "filename": metadata.filename,
                        "chunk_index": i,
                        "upload_time": metadata.upload_time.isoformat(),
                        "text": chunk  # 存储原始文本
                    }
                }
                vectors_to_upsert.append(vector_record)
                        
            logger.debug(f"[PINECONE_STORE_CHUNKS] 向量准备完成 - 数量：{len(vectors_to_upsert)}")
                        
            # 批量上传到 Pinecone
            self.index.upsert(vectors=vectors_to_upsert)
                        
            storage_time = time.time() - storage_start
            logger.info(f"[PINECONE_STORE_CHUNKS] 文档分块存储成功 - 存储分块数：{len(chunk_ids)}, 耗时：{storage_time:.2f}s")
            
            # 响应返回阶段 - INFO级别
            logger.info(f"[PINECONE_STORE_CHUNKS] 存储流程完成 - 文档ID: {metadata.doc_id}, 总耗时: {storage_time:.2f}s")
            return chunk_ids
            
        except Exception as e:
            # 异常处理 - ERROR级别
            logger.error(f"[PINECONE_STORE_CHUNKS] 文档分块存储失败 - 文档ID: {metadata.doc_id}, 错误类型: {type(e).__name__}, 错误信息: {str(e)}", exc_info=True)
            raise
    
    async def search_similar_documents(
        self, 
        query: str, 
        embeddings: OpenAIEmbeddings,
        top_k: int = 20
    ) -> List[SearchResult]:
        """
        搜索相似文档
        
        Args:
            query: 查询文本
            embeddings: 嵌入模型实例
            top_k: 返回结果数量
            
        Returns:
            搜索结果列表
        """
        try:
            # 请求接收阶段 - INFO级别
            logger.info(f"[PINECONE_SEARCH] 开始搜索相似文档 - 查询内容: {query[:50]}..., Top-K: {top_k}")
            
            # 数据验证阶段 - DEBUG级别
            logger.debug(f"[PINECONE_SEARCH] 搜索参数验证 - 查询长度: {len(query)} 字符, 返回数量: {top_k}")
            
            # 使用 Langchain 向量存储进行相似度搜索 - 外部服务调用阶段
            logger.info(f"[PINECONE_SEARCH] 正在执行向量相似度搜索")
            search_start = time.time()
                        
            # 使用 Pinecone v5+ 原生 API 进行搜索
            # 首先生成查询的向量
            query_embedding = await embeddings.aembed_query(query)
                        
            # 在 Pinecone 中搜索
            search_response = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                include_values=False
            )
                        
            search_time = time.time() - search_start
            logger.info(f"[PINECONE_SEARCH] 向量相似度搜索完成 - 耗时：{search_time:.2f}s")
                        
            # 转换为 SearchResult 格式 - 业务逻辑处理阶段
            logger.debug(f"[PINECONE_SEARCH] 正在转换搜索结果格式")
            search_results = []
            for match in search_response.matches:
                result = SearchResult(
                    content=match.metadata.get("text", "") if match.metadata else "",
                    metadata=match.metadata or {},
                    score=match.score,
                    doc_id=match.metadata.get("doc_id", "") if match.metadata else ""
                )
                search_results.append(result)
            
            logger.debug(f"[PINECONE_SEARCH] 搜索结果转换完成 - 结果数量: {len(search_results)}")
            
            # 响应返回阶段 - INFO级别
            if search_results:
                scores = [r.score for r in search_results]
                logger.info(f"[PINECONE_SEARCH] 搜索完成 - 返回 {len(search_results)} 个结果, 最高得分: {max(scores):.3f}, 平均得分: {sum(scores)/len(scores):.3f}, 耗时: {search_time:.2f}s")
            else:
                logger.info(f"[PINECONE_SEARCH] 搜索完成 - 未找到相关结果, 耗时: {search_time:.2f}s")
            
            return search_results
            
        except Exception as e:
            # 异常处理 - ERROR级别
            logger.error(f"[PINECONE_SEARCH] 文档搜索失败 - 查询内容: {query[:50]}..., 错误类型: {type(e).__name__}, 错误信息: {str(e)}", exc_info=True)
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
            # 请求接收阶段 - INFO级别
            logger.info(f"[PINECONE_DELETE] 开始删除文档 - 文档ID: {doc_id}")
            
            # 数据验证阶段 - DEBUG级别
            logger.debug(f"[PINECONE_DELETE] 删除参数验证 - 文档ID长度: {len(doc_id)}")
            
            # 查询该文档的所有分块 - 外部服务调用阶段
            logger.debug(f"[PINECONE_DELETE] 准备删除过滤条件")
            query_filter = {"doc_id": {"$eq": doc_id}}
            
            # 删除操作 - 外部服务调用阶段
            logger.info(f"[PINECONE_DELETE] 正在执行文档删除操作")
            delete_start = time.time()
            # 注意：Pinecone的删除操作可能需要根据实际API调整
            # 这里假设可以通过过滤条件删除
            self.index.delete(filter=query_filter)
            delete_time = time.time() - delete_start
            
            # 响应返回阶段 - INFO级别
            logger.info(f"[PINECONE_DELETE] 文档删除成功 - 文档ID: {doc_id}, 耗时: {delete_time:.2f}s")
            return True
            
        except Exception as e:
            # 异常处理 - ERROR级别
            logger.error(f"[PINECONE_DELETE] 文档删除失败 - 文档ID: {doc_id}, 错误类型: {type(e).__name__}, 错误信息: {str(e)}", exc_info=True)
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