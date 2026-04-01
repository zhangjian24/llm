"""
重排序服务
调用阿里云百炼 qwen3-rerank API 对检索结果进行重排序
"""
import httpx
from typing import List, Dict, Any
import structlog
from app.core.config import get_settings
from app.exceptions import RetrievalException

logger = structlog.get_logger()
settings = get_settings()


class RerankService:
    """
    重排序服务
    
    使用阿里云百炼的 qwen3-rerank 模型
    对初始检索结果进行相关性重排序
    """
    
    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY
        self.base_url = "https://dashscope.aliyuncs.com/compatible-api/v1"
        self.model = "qwen3-rerank"
    
    async def rerank(
        self, 
        query: str, 
        documents: List[str], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        对文档列表进行重排序
        
        Args:
            query: 用户问题
            documents: 候选文档列表
            top_k: 返回前 K 个最相关结果
            
        Returns:
            List[Dict[str, Any]]: 重排序后的结果，包含 index 和 relevance_score
            
        Raises:
            RetrievalException: API 调用失败时抛出
        """
        if not documents:
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/reranks",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "query": query,
                        "documents": documents,
                        "top_n": top_k
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise RetrievalException(f"Rerank API 返回错误：{response.status_code} - {response.text}")
                
                data = response.json()
                
                results = data.get('results', [])
                
                if not results:
                    logger.warning("rerank_returned_empty_results", query=query[:30])
                    return []
                
                reranked_results = []
                for item in results:
                    reranked_results.append({
                        'index': item['index'],
                        'relevance_score': item['relevance_score']
                    })
                
                return reranked_results

        except httpx.RequestError as e:
            raise RetrievalException(f"Rerank API 请求失败：{str(e)}")
        except KeyError as e:
            raise RetrievalException(f"Rerank API 响应解析失败：{str(e)}")
        except Exception as e:
            raise RetrievalException(f"Rerank 处理失败：{str(e)}")
