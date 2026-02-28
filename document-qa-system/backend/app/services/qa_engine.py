import openai
from typing import List, Dict, Any, Optional
import asyncio
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from app.core.config import settings
from app.core.logging_config import logger
from app.core.exceptions import LLMError
from app.services.vector_store import vector_store

class QAManager:
    """问答管理器 - 集成Ollama gpt-oss:20b模型和LangChain"""
    
    def __init__(self):
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.ollama_api_key = settings.OLLAMA_API_KEY
        self.llm_model = settings.LLM_MODEL
        
        # 初始化LangChain组件
        self._initialize_langchain()
    
    def _initialize_langchain(self):
        """初始化LangChain组件"""
        try:
            # 初始化Ollama模型
            self.llm = OllamaLLM(
                model=self.llm_model,
                base_url=self.ollama_base_url,
                temperature=0.7,
                headers={'Authorization': f'Bearer {self.ollama_api_key}'} if self.ollama_api_key else {}
            )
            
            # 定义Prompt模板
            self.prompt_template = PromptTemplate.from_template(
                """你是一个专业的文档问答助手。请根据以下文档内容回答用户的问题。

文档内容：
{context}

用户问题：{question}

请根据上述文档内容，给出准确、详细的回答。如果文档中没有相关信息，请明确说明。
回答："""
            )
            
            logger.info("LangChain组件初始化成功")
            
        except Exception as e:
            logger.error(f"LangChain初始化失败: {str(e)}")
            raise LLMError(f"LangChain初始化失败: {str(e)}")
    
    async def answer_question(self, query: str, document_ids: Optional[List[str]] = None,
                            top_k: int = 5) -> Dict[str, Any]:
        """回答用户问题"""
        try:
            # 1. 从向量数据库检索相关文档chunks
            similar_chunks = await vector_store.search_similar_chunks(
                query=query,
                top_k=top_k,
                document_ids=document_ids
            )
            
            if not similar_chunks:
                return {
                    "query": query,
                    "answer": "抱歉，我没有找到相关的文档内容来回答您的问题。",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # 2. 构建上下文
            context = self._build_context(similar_chunks)
            
            # 3. 使用LangChain链生成回答
            chain = (
                {"context": lambda x: context, "question": lambda x: query}
                | self.prompt_template
                | self.llm
                | StrOutputParser()
            )
            
            answer = await chain.ainvoke({})
            
            # 4. 构建响应
            sources = self._format_sources(similar_chunks)
            confidence = self._calculate_confidence(similar_chunks)
            
            return {
                "query": query,
                "answer": answer,
                "sources": sources,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"问答处理失败: {str(e)}")
            raise LLMError(f"问答处理失败: {str(e)}")
    
    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """构建问答上下文"""
        context_parts = []
        for chunk in chunks:
            chunk_text = chunk.get("chunk_text", "")
            if chunk_text:
                context_parts.append(f"[文档片段 {chunk['chunk_index']}]: {chunk_text}")
        
        return "\n\n".join(context_parts)
    
    def _format_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """格式化来源信息"""
        sources = []
        processed_docs = set()
        
        for chunk in chunks:
            doc_id = chunk.get("document_id")
            if doc_id and doc_id not in processed_docs:
                sources.append({
                    "document_id": doc_id,
                    "filename": chunk.get("metadata", {}).get("filename", "Unknown"),
                    "score": chunk.get("score", 0),
                    "chunk_count": len([c for c in chunks if c.get("document_id") == doc_id])
                })
                processed_docs.add(doc_id)
        
        # 按分数排序
        sources.sort(key=lambda x: x["score"], reverse=True)
        return sources
    
    def _calculate_confidence(self, chunks: List[Dict[str, Any]]) -> float:
        """计算回答置信度"""
        if not chunks:
            return 0.0
        
        # 基于最高分计算置信度
        max_score = max(chunk.get("score", 0) for chunk in chunks)
        
        # 考虑匹配的chunks数量
        match_count = len(chunks)
        count_factor = min(match_count / 3.0, 1.0)  # 最多3个chunks认为是满分
        
        # 综合置信度计算
        confidence = max_score * 0.7 + count_factor * 0.3
        return round(confidence, 3)
    
    async def get_chat_history_summary(self, query: str, history: List[Dict[str, str]]) -> str:
        """获取对话历史摘要（用于上下文增强）"""
        try:
            if not history:
                return ""
            
            # 构建历史对话摘要提示
            history_text = "\n".join([
                f"用户: {item['query']}\n助手: {item['answer']}" 
                for item in history[-3:]  # 只取最近3轮对话
            ])
            
            summary_prompt = f"""请总结以下对话历史的关键信息：

{history_text}

用户当前问题: {query}

请简要总结对话主题和关键信息，帮助更好地理解当前问题的背景。"""

            # 对于对话历史摘要，我们使用相同的Ollama模型
            response = self.llm.invoke(summary_prompt)
            return response.strip()
            
        except Exception as e:
            logger.warning(f"对话历史摘要生成失败: {str(e)}")
            return ""

# 创建全局实例
qa_manager = QAManager()