import requests
import json
from typing import List, Dict, Any, Optional
import asyncio
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from app.core.config import settings
from app.core.logging_config import logger
from app.core.exceptions import LLMError
from app.services.vector_store import vector_store

class QAManager:
    """问答管理器 - 集成阿里巴巴云qwen-max模型和LangChain"""
    
    def __init__(self):
        self.qwen_api_key = settings.QWEN_API_KEY
        self.qwen_model = settings.QWEN_LLM_MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
        # 请求头配置
        self.headers = {
            "Authorization": f"Bearer {self.qwen_api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # 兼容旧版配置的降级机制
        self.use_legacy = not bool(self.qwen_api_key)
        self.legacy_llm = None
        if self.use_legacy:
            logger.warning("未配置QWEN_API_KEY，将使用Ollama作为后备方案")
        
        # 初始化LangChain组件
        self._initialize_langchain()
    
    def _initialize_langchain(self):
        """初始化LangChain组件"""
        try:
            if self.use_legacy:
                # 初始化Ollama后备模型
                try:
                    from langchain_ollama import OllamaLLM
                    self.llm = OllamaLLM(
                        model=settings.LLM_MODEL,
                        base_url=settings.OLLAMA_BASE_URL,
                        temperature=self.temperature,
                        headers={'Authorization': f'Bearer {settings.OLLAMA_API_KEY}'} if settings.OLLAMA_API_KEY else {}
                    )
                    logger.info("使用Ollama作为语言模型后备方案")
                except ImportError:
                    logger.error("无法导入Ollama模块，后备方案不可用")
                    self.llm = self._create_dummy_adapter()
            else:
                # 使用Qwen API，创建适配器
                self.llm = self._create_qwen_adapter()
                logger.info("使用阿里巴巴云qwen-max作为语言模型")
            
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
    
    def _create_qwen_adapter(self):
        """创建Qwen API适配器"""
        class QwenAdapter:
            def __init__(self, manager):
                self.manager = manager
            
            def invoke(self, prompt):
                return self.manager._call_qwen_api(prompt)
        
        return QwenAdapter(self)
    
    def _create_dummy_adapter(self):
        """创建虚拟适配器（用于降级情况）"""
        class DummyAdapter:
            def __init__(self, manager):
                self.manager = manager
            
            def invoke(self, prompt):
                return "抱歉，当前系统未配置有效的语言模型服务。请配置QWEN_API_KEY或确保Ollama服务正常运行。"
        
        return DummyAdapter(self)
    
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
    
    def _call_qwen_api(self, prompt: str) -> str:
        """调用阿里巴巴云Qwen API"""
        try:
            payload = {
                "model": self.qwen_model,
                "input": {
                    "prompt": prompt
                },
                "parameters": {
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "top_p": 0.8,
                    "stop": ["\n\n"]
                }
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                logger.error(f"Qwen API调用失败: {response.status_code} - {response.text}")
                if self.use_legacy and hasattr(self, '_call_legacy_llm'):
                    return self._call_legacy_llm(prompt)
                else:
                    raise LLMError(f"API调用失败: {response.status_code}")
            
            result = response.json()
            
            # 解析响应
            if 'output' in result and 'text' in result['output']:
                return result['output']['text'].strip()
            else:
                raise LLMError("API返回格式不正确")
                
        except Exception as e:
            logger.error(f"Qwen API调用异常: {str(e)}")
            if self.use_legacy:
                return self._call_legacy_llm(prompt)
            else:
                raise LLMError(f"Qwen API调用失败: {str(e)}")
    
    def _call_legacy_llm(self, prompt: str) -> str:
        """调用旧版Ollama模型（降级方案）"""
        try:
            if not hasattr(self, 'legacy_llm') or self.legacy_llm is None:
                # 动态导入并初始化Ollama模型
                from langchain_ollama import OllamaLLM
                self.legacy_llm = OllamaLLM(
                    model=settings.LLM_MODEL,
                    base_url=settings.OLLAMA_BASE_URL,
                    temperature=self.temperature,
                    headers={'Authorization': f'Bearer {settings.OLLAMA_API_KEY}'} if settings.OLLAMA_API_KEY else {}
                )
            
            return self.legacy_llm.invoke(prompt)
            
        except Exception as e:
            logger.error(f"旧版LLM调用失败: {str(e)}")
            return "抱歉，当前无法处理您的请求。"
    
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