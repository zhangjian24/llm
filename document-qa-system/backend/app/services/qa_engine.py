import dashscope
from typing import List, Dict, Any, Optional
import asyncio
from app.core.config import settings
from app.services.vector_store import vector_store
from app.services.embedding import encoder
from app.models.schemas import ChatMessage
from app.core.exceptions import LLMException, VectorStoreException
from app.core.logging_config import get_logger
from app.utils.helpers import truncate_text

logger = get_logger(__name__)

class QAEngine:
    """问答引擎"""
    
    def __init__(self):
        self.model_name = "qwen-max"
        dashscope.api_key = settings.DASHSCOPE_API_KEY
        self.prompt_template = """
你是一个专业的文档问答助手。请根据提供的文档内容回答用户的问题。

文档内容：
{context}

用户问题：{question}

请根据以上文档内容回答问题。如果文档中没有相关信息，请明确说明。
回答要求：
1. 准确、简洁地回答问题
2. 引用相关的文档内容作为依据
3. 如果不确定答案，请如实说明
"""
    
    async def search_similar_documents(self, query: str, top_k: int = 5, 
                                     document_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """搜索相似文档"""
        try:
            # 生成查询向量
            query_embedding = encoder.bge_encoder.encode_single(query)
            
            # 构建过滤条件
            filter_dict = None
            if document_ids:
                filter_dict = {"document_id": {"$in": document_ids}}
            
            # 执行向量搜索
            search_results = vector_store.query_vectors(
                query_vector=query_embedding.tolist(),
                top_k=top_k,
                filter_dict=filter_dict
            )
            
            # 处理结果
            results = []
            for result in search_results:
                results.append({
                    'document_id': result['metadata']['document_id'],
                    'filename': result['metadata']['filename'],
                    'content': result['metadata']['text'],
                    'score': result['score'],
                    'chunk_index': result['metadata']['chunk_index'],
                    'metadata': result['metadata']
                })
            
            logger.info(f"向量搜索完成，找到 {len(results)} 个相关文档片段")
            return results
            
        except Exception as e:
            logger.error(f"文档搜索失败: {str(e)}")
            raise VectorStoreException(f"文档搜索失败: {str(e)}")
    
    def _build_context(self, search_results: List[Dict[str, Any]], max_tokens: int = 2000) -> str:
        """构建上下文"""
        context_parts = []
        total_tokens = 0
        
        for result in search_results:
            content = result['content']
            tokens = len(content) // 4  # 粗略估算token数
            
            if total_tokens + tokens > max_tokens:
                # 截断最后一个内容以适应token限制
                remaining_tokens = max_tokens - total_tokens
                if remaining_tokens > 50:  # 至少保留一些内容
                    truncated_content = truncate_text(content, remaining_tokens * 4)
                    context_parts.append(f"[来自 {result['filename']}]: {truncated_content}")
                break
            
            context_parts.append(f"[来自 {result['filename']}]: {content}")
            total_tokens += tokens
        
        return "\n\n".join(context_parts)
    
    def _format_history(self, history: Optional[List[ChatMessage]]) -> str:
        """格式化对话历史"""
        if not history:
            return ""
        
        history_text = "对话历史：\n"
        for msg in history[-5:]:  # 只保留最近5轮对话
            role = "用户" if msg.role == "user" else "助手"
            history_text += f"{role}: {msg.content}\n"
        
        return history_text + "\n"
    
    async def answer_question(self, query: str, document_ids: Optional[List[str]] = None,
                            history: Optional[List[ChatMessage]] = None) -> Dict[str, Any]:
        """回答问题"""
        try:
            logger.info(f"开始处理问题: {query}")
            
            # 搜索相关文档
            search_results = await self.search_similar_documents(query, top_k=10, document_ids=document_ids)
            
            if not search_results:
                return {
                    'answer': "抱歉，在文档中没有找到相关信息来回答您的问题。",
                    'sources': [],
                    'confidence': 0.0
                }
            
            # 构建上下文
            context = self._build_context(search_results)
            
            # 构建完整提示词
            prompt = self.prompt_template.format(
                context=context,
                question=query
            )
            
            # 添加对话历史（如果有）
            if history:
                history_text = self._format_history(history)
                prompt = history_text + prompt
            
            # 调用千问API
            logger.info("调用千问API...")
            response = dashscope.Generation.call(
                model=self.model_name,
                prompt=prompt,
                max_tokens=1000,
                temperature=0.7
            )
            
            if response.status_code != 200:
                raise LLMException(f"API调用失败: {response.message}")
            
            answer = response.output.text.strip()
            
            # 提取引用源
            sources = []
            for result in search_results[:3]:  # 最多返回3个引用源
                sources.append({
                    'document_id': result['document_id'],
                    'filename': result['filename'],
                    'content': truncate_text(result['content'], 200),
                    'score': result['score']
                })
            
            # 计算置信度（基于搜索结果的相似度）
            avg_score = sum(result['score'] for result in search_results) / len(search_results)
            confidence = min(avg_score * 1.2, 1.0)  # 调整置信度范围
            
            logger.info(f"问题回答完成，置信度: {confidence:.2f}")
            
            return {
                'answer': answer,
                'sources': sources,
                'confidence': confidence
            }
            
        except LLMException:
            raise
        except VectorStoreException:
            raise
        except Exception as e:
            logger.error(f"问答处理失败: {str(e)}")
            raise LLMException(f"问答处理失败: {str(e)}")
    
    async def batch_answer_questions(self, questions: List[str], 
                                   document_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """批量回答问题"""
        tasks = [
            self.answer_question(question, document_ids)
            for question in questions
        ]
        return await asyncio.gather(*tasks)

# 全局问答引擎实例
qa_engine = QAEngine()