"""
RAG（检索增强生成）服务
负责完整的 RAG 流程：检索→重排序→回答生成
"""
from typing import List, Dict, Any, Optional, AsyncGenerator
from uuid import UUID
import structlog
from app.services.embedding_service import EmbeddingService
from app.services.pinecone_service import PineconeService
from app.services.rerank_service import RerankService
from app.core.config import get_settings
from app.exceptions import RetrievalException, GenerationException
import httpx

logger = structlog.get_logger()
settings = get_settings()


class RAGService:
    """
    RAG 检索增强生成服务
    
    流程:
    1. 将用户问题转换为向量
    2. 从 Pinecone 检索相似文档块
    3. 使用重排序模型优化结果
    4. 构建 Prompt 并调用 LLM 生成回答
    5. 流式输出回答
    """
    
    def __init__(
        self,
        embedding_svc: EmbeddingService,
        pinecone_svc: PineconeService,
        rerank_svc: RerankService
    ):
        """
        初始化 RAG 服务
        
        Args:
            embedding_svc: 嵌入向量化服务
            pinecone_svc: Pinecone 向量数据库服务
            rerank_svc: 重排序服务
        """
        self.embedding_svc = embedding_svc
        self.pinecone_svc = pinecone_svc
        self.rerank_svc = rerank_svc
        self.llm_base_url = settings.DASHSCOPE_BASE_URL
        self.llm_api_key = settings.DASHSCOPE_API_KEY
        self.llm_model = settings.LLM_MODEL
    
    async def query(
        self,
        question: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        top_k: int = None,
        rerank_top_k: int = None
    ) -> AsyncGenerator[str, None]:
        """
        RAG 查询主流程（流式响应）
        
        Args:
            question: 用户问题
            conversation_history: 对话历史（可选）
            top_k: 初始检索数量
            rerank_top_k: 重排序后保留数量
            
        Yields:
            str: 流式输出的 token
            
        Raises:
            RetrievalException: 检索失败时抛出
            GenerationException: 生成失败时抛出
        """
        top_k = top_k or settings.RAG_TOP_K
        rerank_top_k = rerank_top_k or settings.RERANK_TOP_K
        
        try:
            # Step 1: 将问题转换为向量
            logger.info("rag_query_started", question=question[:50])
            
            query_vector = await self._embed_question(question)
            
            # Step 2: 语义检索
            similar_chunks = await self._retrieve_similar_chunks(
                query_vector, 
                top_k=top_k
            )
            
            logger.info(
                "retrieval_completed",
                chunks_count=len(similar_chunks)
            )
            
            # Step 3: 重排序优化
            reranked_chunks = await self._rerank_results(
                similar_chunks,
                question,
                keep_top_k=rerank_top_k
            )
            
            logger.info(
                "rerank_completed",
                reranked_count=len(reranked_chunks)
            )
            
            # Step 4: 过滤低相关性结果
            filtered_chunks = [
                chunk for chunk in reranked_chunks
                if chunk.get('relevance_score', 0) >= settings.RELEVANCE_THRESHOLD
            ]
            
            logger.info(
                "filtering_completed",
                filtered_count=len(filtered_chunks),
                threshold=settings.RELEVANCE_THRESHOLD
            )
            
            # Step 5: 构建 Prompt
            prompt = self._build_prompt(
                question=question,
                context=filtered_chunks,
                history=conversation_history or []
            )
            
            # Step 6: 流式生成回答
            async for token in self._generate_stream(prompt):
                yield token
            
            logger.info(
                "rag_query_completed",
                question=question[:50],
                tokens_generated=True
            )
            
        except Exception as e:
            logger.error(
                "rag_query_failed",
                error=str(e),
                exc_info=True
            )
            raise
    
    async def _embed_question(self, question: str) -> List[float]:
        """
        将问题转换为向量
        
        Args:
            question: 用户问题
            
        Returns:
            List[float]: 1536 维向量
        """
        return await self.embedding_svc.embed_text(question)
    
    async def _retrieve_similar_chunks(
        self,
        query_vector: List[float],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        检索相似文档块
        
        Args:
            query_vector: 查询向量
            top_k: 返回数量
            
        Returns:
            List[Dict[str, Any]]: 相似块列表
        """
        matches = await self.pinecone_svc.similarity_search(
            query_vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )
        
        return matches
    
    async def _rerank_results(
        self,
        chunks: List[Dict[str, Any]],
        query: str,
        keep_top_k: int
    ) -> List[Dict[str, Any]]:
        """
        重排序检索结果
        
        Args:
            chunks: 初始检索结果
            query: 用户问题
            keep_top_k: 保留数量
            
        Returns:
            List[Dict[str, Any]]: 重排序后的结果
        """
        # 提取文本内容
        documents = [
            chunk['metadata'].get('content', '')
            for chunk in chunks
            if 'metadata' in chunk
        ]
        
        # 调用重排序 API
        reranked = await self.rerank_svc.rerank(
            query=query,
            documents=documents,
            top_k=keep_top_k
        )
        
        # 将分数附加回原始块
        results = []
        for item in reranked:
            original_idx = item['index']
            if original_idx < len(chunks):
                chunk_copy = chunks[original_idx].copy()
                chunk_copy['relevance_score'] = item['relevance_score']
                results.append(chunk_copy)
        
        return results
    
    def _build_prompt(
        self,
        question: str,
        context: List[Dict[str, Any]],
        history: List[Dict[str, str]]
    ) -> str:
        """
        构建 LLM Prompt
        
        Args:
            question: 用户问题
            context: 相关文档块
            history: 对话历史
            
        Returns:
            str: 完整的 Prompt
        """
        # 格式化上下文
        context_text = "\n\n".join([
            f"[来源 {i+1}]\n{chunk['metadata'].get('content', '无内容')}"
            for i, chunk in enumerate(context)
        ])
        
        # 格式化历史
        history_text = ""
        if history:
            history_parts = []
            for msg in history[-5:]:  # 只保留最近 5 轮
                role = "用户" if msg.get('role') == 'user' else "助手"
                history_parts.append(f"{role}: {msg.get('content', '')}")
            history_text = "\n".join(history_parts) + "\n\n"
        
        # 构建系统指令
        system_prompt = f"""你是一个专业的文档问答助手。请根据以下文档片段回答问题。

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
        
        return system_prompt
    
    async def _generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """
        流式生成回答
        
        Args:
            prompt: 输入 Prompt
            
        Yields:
            str: 流式输出的 token
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.llm_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.llm_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.llm_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": True
                    }
                )
                
                response.raise_for_status()
                
                # 处理 SSE 流
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # 去掉 "data: " 前缀
                        
                        if data.strip() == "[DONE]":
                            break
                        
                        import json
                        try:
                            chunk_data = json.loads(data)
                            choices = chunk_data.get('choices', [])
                            
                            if choices:
                                delta = choices[0].get('delta', {})
                                content = delta.get('content', '')
                                
                                if content:
                                    yield content
                                    
                        except json.JSONDecodeError:
                            continue
                            
        except httpx.RequestError as e:
            logger.error(
                "llm_generation_failed",
                error=str(e),
                exc_info=True
            )
            raise GenerationException(f"回答生成失败：{str(e)}")
        except Exception as e:
            logger.error(
                "stream_parsing_failed",
                error=str(e),
                exc_info=True
            )
            raise GenerationException(f"解析流响应失败：{str(e)}")
