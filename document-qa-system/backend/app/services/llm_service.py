"""
LLM服务封装
管理OpenAI兼容接口的各种模型调用
"""

import json
import time
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
import httpx
from openai import AsyncOpenAI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from ..core.config import settings
from ..core.logging import logger
from ..models.schemas import SearchResult


class LLMService:
    """LLM服务封装类"""
    
    def __init__(self):
        self.client: Optional[AsyncOpenAI] = None
        self.chat_model: Optional[ChatOpenAI] = None
        self.embedding_model: Optional[OpenAIEmbeddings] = None
        self.http_client: Optional[httpx.AsyncClient] = None
    
    async def initialize(self) -> None:
        """初始化LLM服务"""
        try:
            # 请求接收阶段 - INFO级别
            logger.info(f"[LLM_INIT] 开始初始化LLM服务")
            
            # 数据验证阶段 - DEBUG级别
            logger.debug(f"[LLM_INIT] 初始化参数验证 - 基础URL: {settings.OPENAI_BASE_URL}, API密钥长度: {len(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else 0}")
            
            # 初始化OpenAI客户端 - 外部服务调用阶段
            logger.info(f"[LLM_INIT] 正在初始化OpenAI客户端 - 模型配置: {{'embedding': '{settings.EMBEDDING_MODEL}', 'rerank': '{settings.RERANK_MODEL}', 'chat': '{settings.CHAT_MODEL}'}}")
            client_init_start = time.time()
            self.client = AsyncOpenAI(
                base_url=settings.OPENAI_BASE_URL,
                api_key=settings.OPENAI_API_KEY,
                timeout=30.0
            )
            client_init_time = time.time() - client_init_start
            logger.info(f"[LLM_INIT] OpenAI客户端初始化完成 - 耗时: {client_init_time:.2f}s")
            
            # 初始化聊天模型 - 业务逻辑处理阶段
            logger.info(f"[LLM_INIT] 正在初始化聊天模型 - 模型: {settings.CHAT_MODEL}")
            chat_model_init_start = time.time()
            self.chat_model = ChatOpenAI(
                model=settings.CHAT_MODEL,
                openai_api_base=settings.OPENAI_BASE_URL,
                openai_api_key=settings.OPENAI_API_KEY,
                streaming=True,
                temperature=0.7,
                max_tokens=2048
            )
            chat_model_init_time = time.time() - chat_model_init_start
            logger.info(f"[LLM_INIT] 聊天模型初始化完成 - 耗时: {chat_model_init_time:.2f}s")
            
            # 初始化嵌入模型 - 业务逻辑处理阶段
            logger.info(f"[LLM_INIT] 正在初始化嵌入模型 - 模型: {settings.EMBEDDING_MODEL}")
            embedding_model_init_start = time.time()
            self.embedding_model = OpenAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                openai_api_base=settings.OPENAI_BASE_URL,
                openai_api_key=settings.OPENAI_API_KEY
            )
            embedding_model_init_time = time.time() - embedding_model_init_start
            logger.info(f"[LLM_INIT] 嵌入模型初始化完成 - 耗时: {embedding_model_init_time:.2f}s")
            
            # 初始化HTTP客户端用于自定义API调用 - 业务逻辑处理阶段
            logger.info(f"[LLM_INIT] 正在初始化HTTP客户端")
            http_client_init_start = time.time()
            self.http_client = httpx.AsyncClient(timeout=30.0)
            http_client_init_time = time.time() - http_client_init_start
            logger.info(f"[LLM_INIT] HTTP客户端初始化完成 - 耗时: {http_client_init_time:.2f}s")
            
            # 响应返回阶段 - INFO级别
            total_time = client_init_time + chat_model_init_time + embedding_model_init_time + http_client_init_time
            logger.info(f"[LLM_INIT] LLM服务初始化成功 - 总耗时: {total_time:.2f}s")
            
        except Exception as e:
            # 异常处理 - ERROR级别
            logger.error(f"[LLM_INIT] LLM服务初始化失败 - 错误类型: {type(e).__name__}, 错误信息: {str(e)}", exc_info=True)
            raise
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        生成文本嵌入向量
        
        Args:
            texts: 文本列表
            
        Returns:
            嵌入向量列表
        """
        try:
            # 请求接收阶段 - INFO 级别
            logger.info(f"[LLM_EMBEDDING] 开始生成文本嵌入向量 - 文本数量：{len(texts)}, 使用模型：{settings.EMBEDDING_MODEL}")
            
            # 数据验证阶段 - DEBUG 级别
            if not self.embedding_model:
                logger.error(f"[LLM_EMBEDDING] 嵌入模型未初始化")
                raise ValueError("嵌入模型未初始化")
            
            logger.debug(f"[LLM_EMBEDDING] 输入文本验证 - 平均长度：{sum(len(text) for text in texts)//len(texts) if texts else 0} 字符，总字符数：{sum(len(text) for text in texts)}")
            
            # 外部服务调用阶段 - 带重试机制
            logger.info(f"[LLM_EMBEDDING] 正在调用嵌入模型 API")
            embedding_start = time.time()
            
            # 实现重试逻辑，处理临时错误
            max_retries = 3
            retry_delay = 2.0  # 秒
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    embeddings = await self.embedding_model.aembed_documents(texts)
                    embedding_time = time.time() - embedding_start
                    
                    # 响应返回阶段 - INFO 级别
                    logger.info(f"[LLM_EMBEDDING] 嵌入向量生成完成 - 向量数量：{len(embeddings)}, 向量维度：{len(embeddings[0]) if embeddings else 0}, 耗时：{embedding_time:.2f}s")
                    return embeddings
                    
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"[LLM_EMBEDDING] 第 {attempt + 1} 次尝试失败，{retry_delay}秒后重试 - 错误：{str(e)}")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # 指数退避
                    else:
                        raise
            
            # 如果所有重试都失败
            raise last_exception
            
        except Exception as e:
            # 异常处理 - ERROR 级别
            logger.error(f"[LLM_EMBEDDING] 嵌入向量生成失败 - 文本数量：{len(texts)}, 错误类型：{type(e).__name__}, 错误信息：{str(e)}", exc_info=True)
            raise
    
    async def rerank_documents(
        self, 
        query: str, 
        documents: List[SearchResult]
    ) -> List[SearchResult]:
        """
        使用rerank模型对文档进行重排序
        
        Args:
            query: 查询文本
            documents: 待重排序的文档列表
            
        Returns:
            重排序后的文档列表
        """
        try:
            # 请求接收阶段 - INFO级别
            logger.info(f"[LLM_RERANK] 开始文档重排序 - 查询内容: {query[:50]}..., 文档数量: {len(documents)}, 使用模型: {settings.RERANK_MODEL}")
            
            # 数据验证阶段 - DEBUG级别
            logger.debug(f"[LLM_RERANK] 重排序参数验证 - 查询长度: {len(query)} 字符, 文档详情: {{'avg_doc_length': {sum(len(doc.content) for doc in documents)//len(documents) if documents else 0}, 'top_scores': sorted([doc.score for doc in documents], reverse=True)[:3] if documents else []}}")
            
            # 准备rerank请求数据 - 业务逻辑处理阶段
            logger.debug(f"[LLM_RERANK] 准备rerank请求数据")
            rerank_data = {
                "model": settings.RERANK_MODEL,
                "query": query,
                "documents": [doc.content for doc in documents],
                "top_n": settings.TOP_N_RERANK
            }
            
            # 调用rerank API - 外部服务调用阶段
            logger.info(f"[LLM_RERANK] 正在调用rerank API")
            rerank_start = time.time()
            response = await self.http_client.post(
                f"{settings.OPENAI_BASE_URL}/rerank",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=rerank_data
            )
            rerank_time = time.time() - rerank_start
            
            if response.status_code == 200:
                result = response.json()
                reranked_indices = [item["index"] for item in result.get("results", [])]
                
                # 根据重排序结果重新排列文档 - 业务逻辑处理阶段
                reranked_docs = [documents[i] for i in reranked_indices]
                logger.info(f"[LLM_RERANK] 文档重排序完成 - 重排序后保留 {len(reranked_docs)} 个文档, 耗时: {rerank_time:.2f}s")
                
                # 响应返回阶段 - DEBUG级别
                if reranked_docs:
                    new_scores = [reranked_docs[i].score for i in range(min(3, len(reranked_docs)))]
                    logger.debug(f"[LLM_RERANK] 重排序结果详情 - 前3个文档得分: {[f'{score:.3f}' for score in new_scores]}")
                
                return reranked_docs
            else:
                logger.warning(f"[LLM_RERANK] Rerank API调用失败，使用原始排序 - 状态码: {response.status_code}, 耗时: {rerank_time:.2f}s")
                # 如果rerank失败，返回前N个原始结果
                return documents[:settings.TOP_N_RERANK]
                
        except Exception as e:
            # 异常处理 - WARNING级别
            logger.warning(f"[LLM_RERANK] 文档重排序失败，使用原始排序 - 错误类型: {type(e).__name__}, 错误信息: {str(e)}")
            # 如果rerank失败，返回前N个原始结果
            return documents[:settings.TOP_N_RERANK]
    
    async def generate_answer(
        self, 
        query: str, 
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        生成基于上下文的回答
        
        Args:
            query: 用户查询
            context: 检索到的上下文
            conversation_history: 对话历史
            
        Returns:
            生成的回答
        """
        try:
            # 请求接收阶段 - INFO级别
            logger.info(f"[LLM_GENERATE_ANSWER] 开始生成回答 - 查询内容: {query[:50]}..., 使用模型: {settings.CHAT_MODEL}")
            
            # 数据验证阶段 - DEBUG级别
            if not self.chat_model:
                logger.error(f"[LLM_GENERATE_ANSWER] 聊天模型未初始化")
                raise ValueError("聊天模型未初始化")
            
            logger.debug(f"[LLM_GENERATE_ANSWER] 输入参数验证 - 查询长度: {len(query)} 字符, 上下文长度: {len(context)} 字符, 历史消息数: {len(conversation_history) if conversation_history else 0}")
            
            # 构建提示词模板 - 业务逻辑处理阶段
            logger.debug(f"[LLM_GENERATE_ANSWER] 正在构建提示词模板")
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """你是一个专业的文档问答助手。请基于提供的上下文信息准确回答用户的问题。

规则：
1. 仅基于提供的上下文信息回答问题
2. 如果上下文中没有相关信息，请明确说明
3. 回答应简洁明了，重点突出
4. 可以适当引用上下文中的具体内容"""),
                ("human", """上下文信息：
{context}

对话历史：
{history}

用户问题：{query}

请根据上述信息回答用户问题：""")
            ])
            
            # 准备对话历史 - 业务逻辑处理阶段
            history_str = ""
            if conversation_history:
                logger.debug(f"[LLM_GENERATE_ANSWER] 处理对话历史 - 保留最近3轮对话")
                for msg in conversation_history[-3:]:  # 只保留最近3轮对话
                    role = "用户" if msg["role"] == "user" else "助手"
                    history_str += f"{role}: {msg['content']}\n"
            
            # 生成回答 - 外部服务调用阶段
            logger.info(f"[LLM_GENERATE_ANSWER] 正在调用LLM生成回答")
            generation_start = time.time()
            response = await self.chat_model.ainvoke(
                prompt_template.format_messages(
                    context=context,
                    history=history_str,
                    query=query
                )
            )
            generation_time = time.time() - generation_start
            
            answer = response.content
            
            # 响应返回阶段 - INFO级别
            logger.info(f"[LLM_GENERATE_ANSWER] 回答生成完成 - 回答长度: {len(answer)} 字符, 耗时: {generation_time:.2f}s")
            logger.debug(f"[LLM_GENERATE_ANSWER] 回答内容预览: {answer[:100]}...")
            return answer
            
        except Exception as e:
            # 异常处理 - ERROR级别
            logger.error(f"[LLM_GENERATE_ANSWER] 回答生成失败 - 查询内容: {query[:50]}..., 错误类型: {type(e).__name__}, 错误信息: {str(e)}", exc_info=True)
            raise
    
    async def stream_answer(
        self, 
        query: str, 
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncGenerator[str, None]:
        """
        流式生成回答
        
        Args:
            query: 用户查询
            context: 检索到的上下文
            conversation_history: 对话历史
            
        Yields:
            生成的文本片段
        """
        try:
            # 请求接收阶段 - INFO级别
            logger.info(f"[LLM_STREAM_ANSWER] 开始流式生成回答 - 查询内容: {query[:50]}..., 使用模型: {settings.CHAT_MODEL}")
            
            # 数据验证阶段 - DEBUG级别
            if not self.chat_model:
                logger.error(f"[LLM_STREAM_ANSWER] 聊天模型未初始化")
                raise ValueError("聊天模型未初始化")
            
            logger.debug(f"[LLM_STREAM_ANSWER] 流式输入参数验证 - 查询长度: {len(query)} 字符, 上下文长度: {len(context)} 字符")
            
            # 构建提示词 - 业务逻辑处理阶段
            logger.debug(f"[LLM_STREAM_ANSWER] 正在构建流式提示词")
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", "你是一个专业的文档问答助手。请基于提供的上下文信息准确回答用户的问题。"),
                ("human", "上下文信息：\n{context}\n\n用户问题：{query}\n\n请回答：")
            ])
            
            # 流式调用 - 外部服务调用阶段
            logger.info(f"[LLM_STREAM_ANSWER] 正在执行流式调用")
            stream_start = time.time()
            chunk_count = 0
            
            async for chunk in self.chat_model.astream(
                prompt_template.format_messages(context=context, query=query)
            ):
                if chunk.content:
                    chunk_count += 1
                    # 外部服务调用阶段 - DEBUG级别（针对每个chunk）
                    logger.debug(f"[LLM_STREAM_ANSWER] 流式chunk生成 - 第{chunk_count}个chunk, 长度: {len(chunk.content)} 字符")
                    yield chunk.content
            
            stream_time = time.time() - stream_start
            
            # 响应返回阶段 - INFO级别
            logger.info(f"[LLM_STREAM_ANSWER] 流式回答生成完成 - 总chunk数: {chunk_count}, 总耗时: {stream_time:.2f}s")
                    
        except Exception as e:
            # 异常处理 - ERROR级别
            logger.error(f"[LLM_STREAM_ANSWER] 流式回答生成失败 - 查询内容: {query[:50]}..., 错误类型: {type(e).__name__}, 错误信息: {str(e)}", exc_info=True)
            yield f"抱歉，生成回答时出现错误：{str(e)}"
    
    async def tokenize_text(self, text: str) -> List[str]:
        """
        对文本进行分词（使用tiktoken）
        
        Args:
            text: 待分词的文本
            
        Returns:
            分词结果
        """
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")  # 使用通用编码
            tokens = encoding.encode(text)
            return [encoding.decode([token]) for token in tokens]
        except Exception as e:
            logger.warning(f"分词失败，使用简单分割: {str(e)}")
            return text.split()
    
    async def get_token_count(self, text: str) -> int:
        """
        获取文本的token数量
        
        Args:
            text: 待计算的文本
            
        Returns:
            token数量
        """
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            return len(encoding.encode(text))
        except Exception as e:
            logger.warning(f"Token计数失败: {str(e)}")
            # 简单估算：每个中文字符约1个token，每4个英文字符约1个token
            chinese_chars = len([c for c in text if ord(c) > 127])
            english_chars = len(text) - chinese_chars
            return chinese_chars + (english_chars // 4)
    
    async def close(self) -> None:
        """关闭服务连接"""
        try:
            if self.http_client:
                await self.http_client.aclose()
            logger.info("LLM服务连接已关闭")
        except Exception as e:
            logger.error(f"关闭LLM服务连接失败: {str(e)}")