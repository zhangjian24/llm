"""
QueryExpander服务 - 扩展用户查询以提高检索质量
"""
import httpx
import structlog
from typing import List, Optional
from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


QUERY_EXPANSION_PROMPT = """你是一个专业的查询扩展助手。请根据用户的问题，生成3-5个相关的查询变体，以帮助检索到更相关的文档。

要求：
1. 生成与原问题语义相关的查询变体
2. 可以包括同义词、相关术语、上位概念、下位概念
3. 每个查询变体应该能独立检索
4. 返回JSON数组格式，不要添加任何解释

原始问题：{question}

请返回一个JSON数组，例如：["query1", "query2", "query3"]"""


class QueryExpander:
    """查询扩展器"""
    
    def __init__(
        self,
        llm_base_url: str = None,
        llm_api_key: str = None,
        llm_model: str = "qwen-max"
    ):
        self.llm_base_url = llm_base_url or settings.DASHSCOPE_BASE_URL
        self.llm_api_key = llm_api_key or settings.DASHSCOPE_API_KEY
        self.llm_model = llm_model or settings.LLM_MODEL
    
    async def expand(
        self,
        question: str,
        max_expansions: int = 5
    ) -> List[str]:
        """
        扩展用户查询
        
        Args:
            question: 用户原始问题
            max_expansions: 最大扩展数量
            
        Returns:
            List[str]: 扩展后的查询列表
        """
        if not self.llm_api_key:
            logger.warning("LLM API key not set, returning original query")
            return [question]
        
        try:
            prompt = QUERY_EXPANSION_PROMPT.format(question=question)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.llm_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.llm_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.llm_model,
                        "messages": [
                            {"role": "system", "content": "你是一个专业的查询扩展助手。"},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3
                    }
                )
                
                response.raise_for_status()
                result = response.json()
                
                content = result["choices"][0]["message"]["content"]
                
                # 解析JSON数组
                import json
                import re
                
                # 尝试提取JSON数组
                json_match = re.search(r'\[[^\]]+\]', content, re.DOTALL)
                if json_match:
                    expansions = json.loads(json_match.group())
                    # 确保包含原始查询
                    if question not in expansions:
                        expansions = [question] + expansions
                    return expansions[:max_expansions]
                
                # 如果解析失败，返回原始查询
                logger.warning(f"无法解析扩展结果: {content}")
                return [question]
                
        except Exception as e:
            logger.error(f"查询扩展失败: {e}")
            return [question]
    
    async def expand_multi_way(
        self,
        question: str
    ) -> List[str]:
        """
        多路查询扩展 - 生成多个不同的查询角度
        
        Args:
            question: 用户原始问题
            
        Returns:
            List[str]: 多角度的查询列表
        """
        return await self.expand(question, max_expansions=5)
