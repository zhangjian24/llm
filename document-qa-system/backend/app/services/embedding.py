import requests
import json
from typing import List, Optional
from app.core.config import settings
from app.core.logging_config import logger
from app.core.exceptions import EmbeddingError

class QwenEmbeddings:
    """基于阿里巴巴云text-embedding-v4的嵌入服务"""
    
    def __init__(self):
        self.api_key = settings.QWEN_API_KEY
        self.model = settings.QWEN_EMBEDDING_MODEL
        self.dimension = settings.VECTOR_DIMENSION
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-embedding"
        
        # 请求头配置
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # 系统必须配置QWEN_API_KEY
        self.use_legacy = False
        if not self.api_key:
            logger.error("未配置QWEN_API_KEY，系统无法初始化嵌入服务")
            raise EmbeddingError("必须配置QWEN_API_KEY才能使用嵌入服务")
    

    
    async def initialize(self):
        """初始化嵌入服务"""
        try:
            if not self.use_legacy:
                # 验证Qwen API密钥有效性
                test_payload = {
                    "model": self.model,
                    "input": {
                        "texts": ["测试文本"]
                    }
                }
                
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=test_payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    logger.info(f"Qwen嵌入服务初始化成功: {self.model}")
                else:
                    logger.warning(f"Qwen嵌入服务验证失败: {response.status_code}")
                    self.use_legacy = True
            
            # 系统必须配置有效的API密钥
            if not self.api_key:
                raise EmbeddingError("未配置有效的嵌入服务，必须配置QWEN_API_KEY")
            
        except Exception as e:
            logger.error(f"嵌入服务初始化失败: {str(e)}")
            raise EmbeddingError(f"嵌入服务初始化失败: {str(e)}")
    
    def _get_embedding(self, text: str) -> List[float]:
        """获取单个文本的嵌入向量"""
        try:
            if not self.use_legacy:
                # 使用阿里巴巴云API
                payload = {
                    "model": self.model,
                    "input": {
                        "texts": [text]
                    }
                }
                
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code != 200:
                    logger.error(f"Qwen嵌入API调用失败: {response.status_code} - {response.text}")
                    raise EmbeddingError(f"API调用失败: {response.status_code}")
                
                result = response.json()
                
                # 解析嵌入向量
                if 'output' in result and 'embeddings' in result['output']:
                    embedding = result['output']['embeddings'][0]['embedding']
                    # 确保维度正确
                    if len(embedding) != self.dimension:
                        logger.warning(f"嵌入维度不匹配: 期望{self.dimension}, 实际{len(embedding)}")
                        if len(embedding) > self.dimension:
                            embedding = embedding[:self.dimension]
                        else:
                            embedding.extend([0.0] * (self.dimension - len(embedding)))
                    return embedding
                else:
                    raise EmbeddingError("API返回格式不正确")

                
        except Exception as e:
            logger.error(f"嵌入生成失败: {str(e)}")
            raise EmbeddingError(f"嵌入生成失败: {str(e)}")
    

    
    async def batch_embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入文档（异步版本）"""
        try:
            embeddings = []
            for text in texts:
                embedding = self._get_embedding(text)
                embeddings.append(embedding)
            return embeddings
        except Exception as e:
            logger.error(f"批量嵌入失败: {str(e)}")
            raise EmbeddingError(f"批量嵌入失败: {str(e)}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入文档（同步版本，向后兼容）"""
        return self.batch_embed_documents(texts)
    
    def embed_query(self, query: str) -> List[float]:
        """为查询生成嵌入向量"""
        return self._get_embedding(query)

# 创建全局实例
embedding_service = QwenEmbeddings()