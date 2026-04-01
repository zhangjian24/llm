"""
RAG（检索增强生成）服务
负责完整的 RAG 流程：检索→重排序→回答生成
"""
from typing import List, Dict, Any, Optional, AsyncGenerator
from uuid import UUID
import structlog
from app.services.embedding_service import EmbeddingService
# 使用向量服务适配器替代具体的 PineconeService
from app.services.vector_service_adapter import VectorServiceAdapter
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
        vector_svc: VectorServiceAdapter,
        rerank_svc: RerankService
    ):
        """
        初始化 RAG 服务
        
        Args:
            embedding_svc: 嵌入向量化服务
            vector_svc: 向量数据库服务（通过适配器）
            rerank_svc: 重排序服务
        """
        self.embedding_svc = embedding_svc
        self.vector_svc = vector_svc
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
        
        # 记录完整请求参数
        logger.info(
            "rag_query_started",
            question=question[:100],
            question_length=len(question),
            top_k=top_k,
            rerank_top_k=rerank_top_k,
            history_length=len(conversation_history) if conversation_history else 0
        )
        
        try:
            # Step 1: 将问题转换为向量
            logger.info("step1_embedding_started", question=question[:50])
            
            query_vector = await self._embed_question(question)
            
            logger.info(
                "step1_embedding_completed",
                vector_dimension=len(query_vector),
                vector_sample=query_vector[:5] if query_vector else None
            )
            
            # Step 2: 语义检索
            logger.info("step2_retrieval_started", top_k=top_k)
            
            similar_chunks = await self._retrieve_similar_chunks(
                query_vector, 
                top_k=top_k
            )
            
            logger.info(
                "step2_retrieval_completed",
                chunks_count=len(similar_chunks),
                chunks_details=[
                    {
                        "id": chunk.get("id", "unknown"),
                        "score": chunk.get("score", 0),
                        "content_preview": chunk.get("metadata", {}).get("content", "")[:50] if chunk.get("metadata") else ""
                    }
                    for chunk in similar_chunks[:3]
                ] if similar_chunks else []
            )
            
            # 如果没有检索到文档，给出友好提示
            if not similar_chunks:
                logger.warning(
                    "no_relevant_documents_found",
                    question=question[:100],
                    suggestion="Pinecone索引可能为空或文档未向量化"
                )
                yield "抱歉，我没有找到相关的文档内容来回答您的问题。请先上传一些文档，然后我会基于这些文档为您提供准确的回答。"
                return
            
            # Step 3: 重排序优化
            logger.info("step3_rerank_started", chunks_count=len(similar_chunks))
            
            try:
                reranked_chunks = await self._rerank_results(
                    similar_chunks,
                    question,
                    keep_top_k=rerank_top_k
                )
                
                logger.info(
                    "step3_rerank_completed",
                    reranked_count=len(reranked_chunks),
                    rerank_scores=[
                        {
                            "index": i,
                            "score": chunk.get("relevance_score", 0),
                            "original_score": chunk.get("score", 0)
                        }
                        for i, chunk in enumerate(reranked_chunks[:5])
                    ]
                )
            except Exception as rerank_error:
                logger.warning(
                    "rerank_failed_fallback_to_similarity",
                    error=str(rerank_error),
                    error_type=type(rerank_error).__name__
                )
                # 重排序失败时，使用原始相似度结果
                # 将向量相似度 score 复制到 relevance_score 字段
                reranked_chunks = []
                for chunk in similar_chunks[:rerank_top_k]:
                    chunk_copy = chunk.copy()
                    # 如果没有 relevance_score，使用原始 score
                    if 'relevance_score' not in chunk_copy:
                        chunk_copy['relevance_score'] = chunk_copy.get('score', 0)
                    reranked_chunks.append(chunk_copy)
            
            # Step 4: 过滤低相关性结果
            logger.info(
                "step4_filtering_started",
                chunks_before_filter=len(reranked_chunks),
                threshold=settings.RELEVANCE_THRESHOLD
            )
            
            filtered_chunks = [
                chunk for chunk in reranked_chunks
                if chunk.get('relevance_score', 0) >= settings.RELEVANCE_THRESHOLD
            ]
            
            logger.info(
                "step4_filtering_completed",
                chunks_after_filter=len(filtered_chunks),
                filtered_out=len(reranked_chunks) - len(filtered_chunks),
                threshold=settings.RELEVANCE_THRESHOLD
            )
            
            # 如果过滤后没有文档，给出提示
            if not filtered_chunks:
                logger.warning(
                    "all_chunks_filtered_out",
                    threshold=settings.RELEVANCE_THRESHOLD,
                    suggestion="降低RELEVANCE_THRESHOLD或检查文档相关性"
                )
                yield "抱歉，找到的文档内容与问题相关性较低。请尝试用不同的方式提问，或上传更多相关文档。"
                return
            
            # Step 5: 构建 Prompt
            logger.info("step5_build_prompt_started", context_chunks=len(filtered_chunks))
            
            prompt = self._build_prompt(
                question=question,
                context=filtered_chunks,
                history=conversation_history or []
            )
            
            logger.info(
                "step5_build_prompt_completed",
                prompt_length=len(prompt),
                prompt_preview=prompt[:200] + "..." if len(prompt) > 200 else prompt
            )
            
            # Step 6: 流式生成回答
            logger.info("step6_generation_started")
            
            token_count = 0
            async for token in self._generate_stream(prompt):
                yield token
                token_count += 1
            
            logger.info(
                "step6_generation_completed",
                total_tokens=token_count
            )
            
            logger.info(
                "rag_query_completed",
                question=question[:100],
                total_tokens_generated=token_count,
                context_chunks_used=len(filtered_chunks)
            )
            
        except Exception as e:
            logger.error(
                "rag_query_failed",
                error=str(e),
                error_type=type(e).__name__,
                question=question[:100],
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
        matches = await self.vector_svc.similarity_search(
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
        
        # 构建系统指令 (优化版 - 精简指令)
        system_prompt = f"""你是一个专业的文档问答助手。

要求：
1. 只基于【文档内容】回答，不要编造
2. 如需引用，格式：[来源X]
3. 回答简洁，不超过3句话
4. 不知道的问题明确说明

【文档】{context_text}
【历史】{history_text}
【问题】{question}

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
            async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
                response = await client.post(
                    f"{self.llm_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.llm_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.llm_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": True,
                        "max_tokens": 200,  # 限制生成token数量
                        "temperature": 0.3  # 降低随机性
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
