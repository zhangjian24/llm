"""
LLM服务封装
管理OpenAI兼容接口的各种模型调用
"""

import json
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
            logger.info("正在初始化LLM服务...")
            
            # 初始化OpenAI客户端
            self.client = AsyncOpenAI(
                base_url=settings.OPENAI_BASE_URL,
                api_key=settings.OPENAI_API_KEY,
                timeout=30.0
            )
            
            # 初始化聊天模型
            self.chat_model = ChatOpenAI(
                model=settings.CHAT_MODEL,
                openai_api_base=settings.OPENAI_BASE_URL,
                openai_api_key=settings.OPENAI_API_KEY,
                streaming=True,
                temperature=0.7,
                max_tokens=2048
            )
            
            # 初始化嵌入模型
            self.embedding_model = OpenAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                openai_api_base=settings.OPENAI_BASE_URL,
                openai_api_key=settings.OPENAI_API_KEY
            )
            
            # 初始化HTTP客户端用于自定义API调用
            self.http_client = httpx.AsyncClient(timeout=30.0)
            
            logger.info("LLM服务初始化成功")
            
        except Exception as e:
            logger.error(f"LLM服务初始化失败: {str(e)}")
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
            if not self.embedding_model:
                raise ValueError("嵌入模型未初始化")
            
            logger.info(f"正在生成 {len(texts)} 个文本的嵌入向量...")
            embeddings = await self.embedding_model.aembed_documents(texts)
            logger.info("嵌入向量生成完成")
            return embeddings
            
        except Exception as e:
            logger.error(f"嵌入向量生成失败: {str(e)}")
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
            logger.info(f"正在重排序 {len(documents)} 个文档...")
            
            # 准备rerank请求数据
            rerank_data = {
                "model": settings.RERANK_MODEL,
                "query": query,
                "documents": [doc.content for doc in documents],
                "top_n": settings.TOP_N_RERANK
            }
            
            # 调用rerank API
            response = await self.http_client.post(
                f"{settings.OPENAI_BASE_URL}/rerank",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=rerank_data
            )
            
            if response.status_code == 200:
                result = response.json()
                reranked_indices = [item["index"] for item in result.get("results", [])]
                
                # 根据重排序结果重新排列文档
                reranked_docs = [documents[i] for i in reranked_indices]
                logger.info(f"文档重排序完成，返回前 {len(reranked_docs)} 个结果")
                return reranked_docs
            else:
                logger.warning(f"Rerank API调用失败，使用原始排序: {response.status_code}")
                # 如果rerank失败，返回前N个原始结果
                return documents[:settings.TOP_N_RERANK]
                
        except Exception as e:
            logger.warning(f"文档重排序失败，使用原始排序: {str(e)}")
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
            if not self.chat_model:
                raise ValueError("聊天模型未初始化")
            
            logger.info(f"正在生成回答，查询: {query[:50]}...")
            
            # 构建提示词模板
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
            
            # 准备对话历史
            history_str = ""
            if conversation_history:
                for msg in conversation_history[-3:]:  # 只保留最近3轮对话
                    role = "用户" if msg["role"] == "user" else "助手"
                    history_str += f"{role}: {msg['content']}\n"
            
            # 生成回答
            response = await self.chat_model.ainvoke(
                prompt_template.format_messages(
                    context=context,
                    history=history_str,
                    query=query
                )
            )
            
            answer = response.content
            logger.info("回答生成完成")
            return answer
            
        except Exception as e:
            logger.error(f"回答生成失败: {str(e)}")
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
            if not self.chat_model:
                raise ValueError("聊天模型未初始化")
            
            logger.info(f"正在流式生成回答，查询: {query[:50]}...")
            
            # 构建提示词
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", "你是一个专业的文档问答助手。请基于提供的上下文信息准确回答用户的问题。"),
                ("human", "上下文信息：\n{context}\n\n用户问题：{query}\n\n请回答：")
            ])
            
            # 流式调用
            async for chunk in self.chat_model.astream(
                prompt_template.format_messages(context=context, query=query)
            ):
                if chunk.content:
                    yield chunk.content
                    
        except Exception as e:
            logger.error(f"流式回答生成失败: {str(e)}")
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