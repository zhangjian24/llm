import requests
import os
import json
import struct
import hashlib
from typing import List, Optional
from app.core.config import settings
from app.core.logging_config import logger
from app.core.exceptions import EmbeddingError

# 导入 Ollama 官方 SDK
import ollama

class OllamaEmbeddings:
    """基于Ollama的BGE嵌入模型"""
    
    def __init__(self):
        self.model = settings.EMBEDDING_MODEL
        self.dimension = settings.VECTOR_DIMENSION
        
        # 确保 URL 格式正确（不以 /api 结尾）
        base_url = settings.OLLAMA_BASE_URL.rstrip('/')
        if base_url.endswith('/api'):
            base_url = base_url[:-4]  # 移除末尾的 /api
            
        # 创建 Ollama 客户端
        if settings.OLLAMA_API_KEY:
            self.client = ollama.Client(
                host=base_url,
                headers={'Authorization': f'Bearer {settings.OLLAMA_API_KEY}'}
            )
        else:
            self.client = ollama.Client(host=base_url)
    
    async def initialize(self):
        """初始化嵌入模型"""
        try:
            # 检查Ollama服务是否可用
            logger.info(f"正在连接到 Ollama 服务: {self.client._client._base_url}")
            models_info = self.client.list()
            logger.info(f"Ollama服务返回的可用模型列表: {models_info}")
            
            # 正确访问模型列表 - 使用对象属性而不是字典键
            models = models_info.models if hasattr(models_info, 'models') else []
            model_names = [model.model for model in models]  # 使用 .model 属性
            
            logger.info(f"提取的模型名称列表: {model_names}")
            
            # 检查模型是否存在
            model_found = False
            for model_obj in models:
                model_name = model_obj.model  # 使用 .model 属性
                # 精确匹配或基础名称匹配
                base_name = model_name.split(':')[0]
                if base_name == self.model or model_name == self.model:
                    model_found = True
                    logger.info(f"找到模型: {model_name}")
                    break
            
            if not model_found:
                logger.warning(f"模型 {self.model} 未找到，尝试拉取...")
                try:
                    # 拉取模型
                    self.client.pull(self.model)
                    logger.info(f"模型 {self.model} 拉取成功")
                except Exception as e:
                    raise EmbeddingError(f"模型拉取失败: {str(e)}")
            
            logger.info("BGE嵌入模型初始化成功")
            
        except Exception as e:
            logger.error(f"嵌入模型初始化失败: {str(e)}")
            raise EmbeddingError(f"嵌入模型初始化失败: {str(e)}")
    
    def _get_embedding(self, text: str) -> List[float]:
        """获取单个文本的嵌入向量"""
        try:
            # 使用 Ollama SDK 的 embeddings 方法
            response = self.client.embeddings(model=self.model, prompt=text)
            
            embedding = response.embedding if hasattr(response, 'embedding') else response.get('embedding')
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
            
        except Exception as e:
            logger.error(f"嵌入生成失败: {str(e)}")
            raise EmbeddingError(f"嵌入生成失败: {str(e)}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入文档"""
        try:
            embeddings = []
            for text in texts:
                embedding = self._get_embedding(text)
                embeddings.append(embedding)
            return embeddings
        except Exception as e:
            logger.error(f"批量嵌入失败: {str(e)}")
            raise EmbeddingError(f"批量嵌入失败: {str(e)}")

# 创建全局实例
embedding_service = OllamaEmbeddings()