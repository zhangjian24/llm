"""
RAG核心逻辑服务
实现完整的检索-增强-生成流程
"""

import time
import uuid
from typing import List, Dict, Any, Optional, AsyncGenerator
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..core.config import settings
from ..core.logging import logger
from ..models.schemas import (
    DocumentMetadata, 
    SearchResult, 
    QueryRequest, 
    QueryResponse,
    StreamChunk
)
from .pinecone_service import PineconeService
from .llm_service import LLMService


class RAGService:
    """RAG核心服务类"""
    
    def __init__(self, pinecone_service: PineconeService, llm_service: LLMService):
        self.pinecone_service = pinecone_service
        self.llm_service = llm_service
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}
    
    async def process_document(
        self, 
        content: str, 
        metadata: DocumentMetadata
    ) -> Dict[str, Any]:
        """
        处理文档：分块、向量化、存储
        
        Args:
            content: 文档内容
            metadata: 文档元数据
            
        Returns:
            处理结果
        """
        try:
            start_time = time.time()
            logger.info(f"开始处理文档: {metadata.filename}")
            
            # 1. 文本分块
            logger.info("正在进行文本分块...")
            chunks = self.text_splitter.split_text(content)
            metadata.chunk_count = len(chunks)
            logger.info(f"文本分块完成，共 {len(chunks)} 个分块")
            
            # 2. 向量化
            logger.info("正在进行文本向量化...")
            embeddings = await self.llm_service.generate_embeddings(chunks)
            logger.info("文本向量化完成")
            
            # 3. 存储到向量数据库
            logger.info("正在存储到向量数据库...")
            chunk_ids = await self.pinecone_service.store_document_chunks(chunks, metadata)
            logger.info("向量存储完成")
            
            processing_time = time.time() - start_time
            logger.info(f"文档处理完成，耗时: {processing_time:.2f}秒")
            
            return {
                "success": True,
                "doc_id": metadata.doc_id,
                "filename": metadata.filename,
                "chunk_count": len(chunks),
                "processing_time": processing_time,
                "message": f"文档 '{metadata.filename}' 处理成功"
            }
            
        except Exception as e:
            logger.error(f"文档处理失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"文档处理失败: {str(e)}"
            }
    
    async def query_documents(
        self, 
        query_request: QueryRequest
    ) -> QueryResponse:
        """
        查询文档并生成回答（同步模式）
        
        Args:
            query_request: 查询请求
            
        Returns:
            查询响应
        """
        try:
            start_time = time.time()
            logger.info(f"开始处理查询: {query_request.query}")
            
            # 1. 检索阶段：从向量数据库检索相关文档
            logger.info("正在进行文档检索...")
            search_results = await self.pinecone_service.search_similar_documents(
                query_request.query,
                top_k=settings.TOP_K_RETRIEVAL
            )
            logger.info(f"检索到 {len(search_results)} 个相关文档")
            
            # 2. 重排序阶段：使用rerank模型重排序
            logger.info("正在进行文档重排序...")
            reranked_results = await self.llm_service.rerank_documents(
                query_request.query,
                search_results
            )
            logger.info(f"重排序后保留 {len(reranked_results)} 个文档")
            
            # 3. 上下文构建：合并重排序后的文档内容
            logger.info("正在构建上下文...")
            context = self._build_context(reranked_results)
            logger.info(f"上下文构建完成，长度: {len(context)} 字符")
            
            # 4. 生成阶段：调用LLM生成回答
            logger.info("正在生成回答...")
            
            # 获取对话历史
            conversation_history = self.conversation_history.get(
                query_request.conversation_id, []
            ) if query_request.conversation_id else []
            
            answer = await self.llm_service.generate_answer(
                query_request.query,
                context,
                conversation_history
            )
            logger.info("回答生成完成")
            
            # 更新对话历史
            if query_request.conversation_id:
                self._update_conversation_history(
                    query_request.conversation_id,
                    query_request.query,
                    answer
                )
            
            processing_time = time.time() - start_time
            
            # 生成对话ID（如果没有提供）
            conversation_id = query_request.conversation_id or str(uuid.uuid4())
            
            response = QueryResponse(
                answer=answer,
                sources=reranked_results,
                conversation_id=conversation_id,
                processing_time=processing_time
            )
            
            logger.info(f"查询处理完成，总耗时: {processing_time:.2f}秒")
            return response
            
        except Exception as e:
            logger.error(f"查询处理失败: {str(e)}")
            raise
    
    async def stream_query_documents(
        self, 
        query_request: QueryRequest
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        流式查询文档并生成回答
        
        Args:
            query_request: 查询请求
            
        Yields:
            流式响应数据块
        """
        try:
            start_time = time.time()
            logger.info(f"开始流式处理查询: {query_request.query}")
            
            # 1. 检索阶段
            yield StreamChunk(
                type="status",
                content="正在检索相关文档...",
                done=False
            )
            
            search_results = await self.pinecone_service.search_similar_documents(
                query_request.query,
                top_k=settings.TOP_K_RETRIEVAL
            )
            
            # 2. 重排序阶段
            yield StreamChunk(
                type="status",
                content="正在优化检索结果...",
                done=False
            )
            
            reranked_results = await self.llm_service.rerank_documents(
                query_request.query,
                search_results
            )
            
            # 发送源文档信息
            yield StreamChunk(
                type="sources",
                sources=reranked_results,
                done=False
            )
            
            # 3. 上下文构建
            context = self._build_context(reranked_results)
            
            # 4. 流式生成回答
            yield StreamChunk(
                type="status",
                content="正在生成回答...",
                done=False
            )
            
            # 获取对话历史
            conversation_history = self.conversation_history.get(
                query_request.conversation_id, []
            ) if query_request.conversation_id else []
            
            answer_buffer = ""
            async for chunk in self.llm_service.stream_answer(
                query_request.query,
                context,
                conversation_history
            ):
                answer_buffer += chunk
                yield StreamChunk(
                    type="answer",
                    content=chunk,
                    done=False
                )
            
            # 更新对话历史
            if query_request.conversation_id:
                self._update_conversation_history(
                    query_request.conversation_id,
                    query_request.query,
                    answer_buffer
                )
            
            # 结束标记
            processing_time = time.time() - start_time
            yield StreamChunk(
                type="end",
                content=f"\n\n回答完成，耗时: {processing_time:.2f}秒",
                done=True
            )
            
            logger.info(f"流式查询处理完成，总耗时: {processing_time:.2f}秒")
            
        except Exception as e:
            logger.error(f"流式查询处理失败: {str(e)}")
            yield StreamChunk(
                type="error",
                content=f"处理过程中发生错误: {str(e)}",
                done=True
            )
    
    def _build_context(self, search_results: List[SearchResult]) -> str:
        """
        构建上下文字符串
        
        Args:
            search_results: 检索结果列表
            
        Returns:
            上下文字符串
        """
        context_parts = []
        for i, result in enumerate(search_results, 1):
            context_part = f"文档 {i} (相关性得分: {result.score:.3f}):\n{result.content}"
            context_parts.append(context_part)
        
        return "\n\n---\n\n".join(context_parts)
    
    def _update_conversation_history(
        self, 
        conversation_id: str, 
        query: str, 
        answer: str
    ) -> None:
        """
        更新对话历史
        
        Args:
            conversation_id: 对话ID
            query: 用户查询
            answer: 助手回答
        """
        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = []
        
        # 添加用户消息
        self.conversation_history[conversation_id].append({
            "role": "user",
            "content": query
        })
        
        # 添加助手消息
        self.conversation_history[conversation_id].append({
            "role": "assistant", 
            "content": answer
        })
        
        # 限制历史长度（最多保留10轮对话）
        if len(self.conversation_history[conversation_id]) > 20:
            self.conversation_history[conversation_id] = \
                self.conversation_history[conversation_id][-20:]
    
    async def get_conversation_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """
        获取对话历史
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            对话历史列表
        """
        return self.conversation_history.get(conversation_id, [])
    
    async def delete_document(self, doc_id: str) -> bool:
        """
        删除文档
        
        Args:
            doc_id: 文档ID
            
        Returns:
            删除是否成功
        """
        try:
            logger.info(f"正在删除文档: {doc_id}")
            success = await self.pinecone_service.delete_document(doc_id)
            
            if success:
                logger.info(f"文档删除成功: {doc_id}")
            else:
                logger.warning(f"文档删除失败: {doc_id}")
                
            return success
            
        except Exception as e:
            logger.error(f"删除文档时发生错误: {str(e)}")
            return False
    
    async def get_document_list(self) -> List[DocumentMetadata]:
        """
        获取文档列表
        
        Returns:
            文档元数据列表
        """
        try:
            return await self.pinecone_service.get_document_list()
        except Exception as e:
            logger.error(f"获取文档列表失败: {str(e)}")
            raise