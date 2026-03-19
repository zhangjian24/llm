"""
嵌入向量化服务
调用阿里云百炼 text-embedding-v4 API
"""
import httpx
from typing import List
import structlog
from app.core.config import get_settings
from app.exceptions import RetrievalException

logger = structlog.get_logger()
settings = get_settings()


class EmbeddingService:
    """
    嵌入向量化服务
    
    使用阿里云百炼的 text-embedding-v4 模型
    输出维度：1536
    """
    
    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY
        self.base_url = settings.DASHSCOPE_BASE_URL
        self.model = settings.EMBEDDING_MODEL
    
    async def embed_text(self, text: str) -> List[float]:
        """
        将文本转换为向量
        
        Args:
            text: 输入文本
            
        Returns:
            List[float]: 1536 维向量
            
        Raises:
            RetrievalException: API 调用失败时抛出
        """
        logger.debug(
            "embedding_request_started",
            text_length=len(text),
            text_preview=text[:100] if text else "EMPTY_TEXT",
            model=self.model,
            api_url=self.base_url
        )
        
        try:
            async with httpx.AsyncClient() as client:
                request_payload = {
                    "model": self.model,
                    "input": text
                }
                
                logger.debug(
                    "sending_embedding_request",
                    payload_size=len(str(request_payload)),
                    timeout=30.0
                )
                
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=request_payload,
                    timeout=30.0
                )
                
                logger.debug(
                    "embedding_api_response_received",
                    status_code=response.status_code,
                    response_time_ms=response.elapsed.total_seconds() * 1000,
                    response_size_bytes=len(response.content),
                    headers=dict(response.headers)
                )
                
                if response.status_code != 200:
                    logger.error(
                        "embedding_api_error",
                        status_code=response.status_code,
                        response_body=response.text[:500],
                        request_payload=request_payload
                    )
                    raise RetrievalException(f"Embedding API 返回错误：{response.status_code}")
                
                data = response.json()
                
                logger.debug(
                    "embedding_response_parsed",
                    data_keys=list(data.keys()),
                    usage=data.get('usage', {})
                )
                
                embedding = data['data'][0]['embedding']
                
                logger.info(
                    "embedding_success",
                    vector_dimension=len(embedding),
                    vector_sample_first_5=embedding[:5],
                    vector_sample_last_5=embedding[-5:],
                    vector_min=min(embedding),
                    vector_max=max(embedding),
                    usage=data.get('usage', {})
                )
                
                return embedding
                
        except httpx.RequestError as e:
            logger.error(
                "embedding_request_failed",
                error=str(e),
                error_type=type(e).__name__,
                request_url=f"{self.base_url}/embeddings",
                timeout=getattr(e, 'request', None),
                exc_info=True
            )
            raise RetrievalException(f"Embedding API 请求失败：{str(e)}")
        except KeyError as e:
            logger.error(
                "embedding_response_format_error",
                error=str(e),
                response_data=data if 'data' in locals() else None,
                exc_info=True
            )
            raise RetrievalException(f"Embedding 响应格式错误：{str(e)}")
        except Exception as e:
            logger.error(
                "embedding_processing_failed",
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True
            )
            raise RetrievalException(f"Embedding 处理失败：{str(e)}")
    
    async def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        批量向量化（减少 API 调用次数）
        
        Args:
            texts: 文本列表
            batch_size: 批次大小
            
        Returns:
            List[List[float]]: 向量列表
        """
        all_embeddings = []
        
        # 分批处理
        batches = [
            texts[i:i + batch_size] 
            for i in range(0, len(texts), batch_size)
        ]
        
        for batch in batches:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/embeddings",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": self.model,
                            "input": batch
                        },
                        timeout=60.0
                    )
                    
                    if response.status_code != 200:
                        raise RetrievalException(f"Embedding API 返回错误：{response.status_code}")
                    
                    data = response.json()
                    embeddings = [item['embedding'] for item in data['data']]
                    all_embeddings.extend(embeddings)
                    
            except Exception as e:
                raise RetrievalException(f"批量 Embedding 失败：{str(e)}")
        
        return all_embeddings
