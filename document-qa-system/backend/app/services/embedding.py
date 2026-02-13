from sentence_transformers import SentenceTransformer
import torch
from typing import List, Union
import numpy as np
from app.core.config import settings
from app.core.exceptions import VectorStoreException
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class BGEEncoder:
    """BGE嵌入编码器"""
    
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL_NAME
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加载BGE模型"""
        try:
            logger.info(f"正在加载BGE模型: {self.model_name}")
            logger.info(f"使用设备: {self.device}")
            
            self.model = SentenceTransformer(
                self.model_name,
                device=self.device
            )
            
            # 预热模型
            self.model.encode(["测试文本"])
            logger.info("BGE模型加载成功")
            
        except Exception as e:
            logger.error(f"BGE模型加载失败: {str(e)}")
            raise VectorStoreException(f"BGE模型加载失败: {str(e)}")
    
    def encode_single(self, text: str, normalize: bool = True) -> np.ndarray:
        """编码单个文本"""
        try:
            if not text.strip():
                raise ValueError("输入文本不能为空")
            
            embedding = self.model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=normalize
            )
            
            return embedding
            
        except Exception as e:
            logger.error(f"文本编码失败: {str(e)}")
            raise VectorStoreException(f"文本编码失败: {str(e)}")
    
    def encode_batch(self, texts: List[str], batch_size: int = 32, 
                    normalize: bool = True) -> List[np.ndarray]:
        """批量编码文本"""
        try:
            if not texts:
                return []
            
            # 过滤空文本
            valid_texts = [text for text in texts if text.strip()]
            if not valid_texts:
                raise ValueError("没有有效的输入文本")
            
            embeddings = self.model.encode(
                valid_texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                normalize_embeddings=normalize,
                show_progress_bar=True
            )
            
            # 转换为列表格式
            if isinstance(embeddings, np.ndarray):
                return [embeddings[i] for i in range(len(embeddings))]
            else:
                return embeddings
                
        except Exception as e:
            logger.error(f"批量文本编码失败: {str(e)}")
            raise VectorStoreException(f"批量文本编码失败: {str(e)}")
    
    def get_embedding_dimension(self) -> int:
        """获取嵌入维度"""
        return self.model.get_sentence_embedding_dimension()
    
    def similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        try:
            emb1 = self.encode_single(text1)
            emb2 = self.encode_single(text2)
            
            # 计算余弦相似度
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            return float(similarity)
            
        except Exception as e:
            logger.error(f"相似度计算失败: {str(e)}")
            raise VectorStoreException(f"相似度计算失败: {str(e)}")

class HybridEncoder:
    """混合编码器（支持多种编码方式）"""
    
    def __init__(self):
        self.bge_encoder = BGEEncoder()
        self.dimension = self.bge_encoder.get_embedding_dimension()
    
    def encode_with_metadata(self, text: str, metadata: dict = None) -> dict:
        """编码文本并附带元数据"""
        try:
            embedding = self.bge_encoder.encode_single(text)
            
            result = {
                'text': text,
                'embedding': embedding,
                'dimension': self.dimension
            }
            
            if metadata:
                result['metadata'] = metadata
                
            return result
            
        except Exception as e:
            logger.error(f"带元数据编码失败: {str(e)}")
            raise VectorStoreException(f"带元数据编码失败: {str(e)}")
    
    def batch_encode_with_ids(self, texts: List[str], 
                            ids: List[str] = None) -> List[dict]:
        """批量编码并生成ID"""
        try:
            if not texts:
                return []
            
            embeddings = self.bge_encoder.encode_batch(texts)
            
            results = []
            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                result = {
                    'id': ids[i] if ids and i < len(ids) else f"chunk_{i}",
                    'text': text,
                    'embedding': embedding,
                    'dimension': self.dimension
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"批量编码失败: {str(e)}")
            raise VectorStoreException(f"批量编码失败: {str(e)}")

# 全局编码器实例
encoder = HybridEncoder()