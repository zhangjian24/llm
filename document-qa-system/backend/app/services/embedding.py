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
        
        # 兼容旧版配置的降级机制
        self.use_legacy = not bool(self.api_key)
        self.legacy_client = None
        if self.use_legacy:
            logger.warning("未配置QWEN_API_KEY，将使用Ollama作为后备方案")
            self._init_legacy_client()
    
    def _init_legacy_client(self):
        """初始化旧版Ollama客户端（降级方案）"""
        try:
            import ollama
            # 确保 URL 格式正确
            base_url = settings.OLLAMA_BASE_URL.rstrip('/')
            if base_url.endswith('/api'):
                base_url = base_url[:-4]
                
            # 创建 Ollama 客户端
            if settings.OLLAMA_API_KEY:
                self.legacy_client = ollama.Client(
                    host=base_url,
                    headers={'Authorization': f'Bearer {settings.OLLAMA_API_KEY}'}
                )
            else:
                self.legacy_client = ollama.Client(host=base_url)
        except ImportError:
            logger.error("无法导入ollama模块，后备方案不可用")
            self.legacy_client = None
    
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
            
            if self.use_legacy:
                if self.legacy_client:
                    # 初始化Ollama后备服务
                    logger.info(f"正在连接到 Ollama 服务: {settings.OLLAMA_BASE_URL}")
                    models_info = self.legacy_client.list()
                    models = models_info.models if hasattr(models_info, 'models') else []
                    logger.info(f"Ollama可用模型数量: {len(models)}")
                    logger.info("使用Ollama作为嵌入服务后备方案")
                else:
                    logger.warning("未配置有效的嵌入服务，系统将以受限模式运行")
            
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
                    if self.legacy_client:
                        return self._get_legacy_embedding(text)
                    else:
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
            else:
                return self._get_legacy_embedding(text)
                
        except Exception as e:
            logger.error(f"嵌入生成失败: {str(e)}")
            raise EmbeddingError(f"嵌入生成失败: {str(e)}")
    
    def _get_legacy_embedding(self, text: str) -> List[float]:
        """使用旧版Ollama获取嵌入向量"""
        try:
            if not self.legacy_client:
                raise EmbeddingError("后备Ollama客户端未初始化")
            
            # 使用 Ollama SDK 的 embeddings 方法
            response = self.legacy_client.embeddings(model=settings.EMBEDDING_MODEL, prompt=text)
            
            embedding = response.embedding if hasattr(response, 'embedding') else response.get('embedding')
            if not embedding:
                raise EmbeddingError("未获取到有效的嵌入向量")
            
            # 确保维度正确
            if len(embedding) != self.dimension:
                logger.warning(f"嵌入维度不匹配: 期望{self.dimension}, 实际{len(embedding)}")
                if len(embedding) > self.dimension:
                    embedding = embedding[:self.dimension]
                else:
                    embedding.extend([0.0] * (self.dimension - len(embedding)))
            
            return embedding
            
        except Exception as e:
            logger.error(f"旧版嵌入生成失败: {str(e)}")
            raise EmbeddingError(f"旧版嵌入生成失败: {str(e)}")
    
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