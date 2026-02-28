import requests
import json
from typing import List, Dict, Any, Optional
import asyncio
from langchain.embeddings.base import Embeddings

from app.core.config import settings
from app.core.logging_config import logger
from app.core.exceptions import EmbeddingError

class OllamaEmbeddings(Embeddings):
    """基于Ollama的BGE嵌入模型"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.EMBEDDING_MODEL
        self.dimension = settings.VECTOR_DIMENSION
        
    async def initialize(self):
        """初始化嵌入模型"""
        try:
            # 检查Ollama服务是否可用
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code != 200:
                raise EmbeddingError("无法连接到Ollama服务")
            
            # 检查模型是否存在（支持带标签的模型名匹配）
            models_data = response.json()
            models = models_data.get('models', [])
            model_names = [model['name'] for model in models]
            
            # 打印可用模型列表用于调试
            logger.info(f"Ollama服务返回的可用模型列表: {model_names}")
            logger.debug(f"完整模型信息: {models_data}")
            
            # 检查精确匹配或基础名称匹配
            model_found = False
            for model_name in model_names:
                # 精确匹配
                if model_name == self.model:
                    model_found = True
                    break
                # 基础名称匹配（忽略标签部分）
                base_name = model_name.split(':')[0]
                if base_name == self.model:
                    model_found = True
                    logger.info(f"通过基础名称匹配找到模型: {model_name}")
                    break
            
            if not model_found:
                logger.warning(f"模型 {self.model} 未找到，尝试拉取...")
                self._pull_model()
            
            logger.info(f"BGE嵌入模型初始化成功: {self.model}")
            
        except Exception as e:
            logger.error(f"嵌入模型初始化失败: {str(e)}")
            raise EmbeddingError(f"嵌入模型初始化失败: {str(e)}")
    
    def _pull_model(self):
        """拉取模型"""
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": self.model},
                timeout=300  # 5分钟超时
            )
            if response.status_code != 200:
                raise EmbeddingError(f"模型拉取失败: {response.text}")
            logger.info(f"模型 {self.model} 拉取成功")
        except Exception as e:
            raise EmbeddingError(f"模型拉取过程中出错: {str(e)}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入文档"""
        try:
            embeddings = []
            for text in texts:
                embedding = self._get_embedding(text)
                embeddings.append(embedding)
            return embeddings
        except Exception as e:
            logger.error(f"文档嵌入失败: {str(e)}")
            raise EmbeddingError(f"文档嵌入失败: {str(e)}")
    
    def embed_query(self, text: str) -> List[float]:
        """嵌入查询文本"""
        try:
            return self._get_embedding(text)
        except Exception as e:
            logger.error(f"查询嵌入失败: {str(e)}")
            raise EmbeddingError(f"查询嵌入失败: {str(e)}")
    
    def _get_embedding(self, text: str) -> List[float]:
        """获取单个文本的嵌入向量"""
        try:
            payload = {
                "model": self.model,
                "prompt": text
            }
            
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                raise EmbeddingError(f"嵌入API调用失败: {response.text}")
            
            result = response.json()
            embedding = result.get('embedding')
            
            if not embedding:
                raise EmbeddingError("未获取到有效的嵌入向量")
            
            # 确保维度正确
            if len(embedding) != self.dimension:
                logger.warning(f"嵌入维度不匹配: 期望{self.dimension}, 实际{len(embedding)}")
                # 截断或填充到正确维度
                if len(embedding) > self.dimension:
                    embedding = embedding[:self.dimension]
                else:
                    embedding.extend([0.0] * (self.dimension - len(embedding)))
            
            return embedding
            
        except requests.exceptions.RequestException as e:
            raise EmbeddingError(f"网络请求失败: {str(e)}")
        except Exception as e:
            raise EmbeddingError(f"嵌入生成失败: {str(e)}")
    
    async def batch_embed_documents(self, texts: List[str], batch_size: int = 10) -> List[List[float]]:
        """批量嵌入文档（异步版本）"""
        try:
            embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeddings = await asyncio.gather(*[
                    asyncio.to_thread(self._get_embedding, text) for text in batch
                ])
                embeddings.extend(batch_embeddings)
            return embeddings
        except Exception as e:
            logger.error(f"批量文档嵌入失败: {str(e)}")
            raise EmbeddingError(f"批量文档嵌入失败: {str(e)}")

# 创建全局实例
embedding_service = OllamaEmbeddings()