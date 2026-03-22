"""
PostgreSQL 向量字段类型支持
提供 SQLAlchemy 的 VECTOR 类型支持
"""

from sqlalchemy.types import TypeDecorator, Float
from sqlalchemy.dialects.postgresql import ARRAY
import numpy as np
from typing import Any, Optional, List


class Vector(TypeDecorator):
    """
    PostgreSQL VECTOR 类型包装器
    用于在 SQLAlchemy 中使用 pgvector 的 VECTOR 类型
    """
    
    impl = ARRAY(Float)
    cache_ok = True
    
    def __init__(self, dimension: int):
        """
        初始化向量类型
        
        Args:
            dimension: 向量维度
        """
        self.dimension = dimension
        super().__init__()
    
    def load_dialect_impl(self, dialect):
        """加载方言特定的实现"""
        if dialect.name == 'postgresql':
            # 对于 PostgreSQL，使用 pgvector 的 VECTOR 类型
            try:
                from pgvector.sqlalchemy import Vector as PGVector
                return dialect.type_descriptor(PGVector(self.dimension))
            except ImportError:
                # pgvector 扩展不可用，使用 ARRAY(Float) 作为后备
                return dialect.type_descriptor(ARRAY(Float, dimensions=1))
        else:
            # 非 PostgreSQL 数据库使用 ARRAY(Float)
            return dialect.type_descriptor(ARRAY(Float, dimensions=1))
    
    def process_bind_param(self, value: Any, dialect) -> Optional[List[float]]:
        """
        将 Python 对象转换为数据库值
        
        Args:
            value: Python 对象（list, tuple, numpy.ndarray）
            dialect: SQLAlchemy 方言
            
        Returns:
            数据库可接受的值（list of floats）
        """
        if value is None:
            return None
            
        if isinstance(value, (list, tuple)):
            if len(value) != self.dimension:
                raise ValueError(f"向量维度不匹配：期望 {self.dimension}，得到 {len(value)}")
            return [float(x) for x in value]
        elif isinstance(value, np.ndarray):
            if value.shape != (self.dimension,):
                raise ValueError(f"向量维度不匹配：期望 {self.dimension}，得到 {value.shape}")
            return value.astype(float).tolist()
        else:
            raise TypeError(f"不支持的向量类型：{type(value)}")
    
    def process_result_value(self, value: Any, dialect) -> Optional[np.ndarray]:
        """
        将数据库值转换为 Python 对象
        
        Args:
            value: 数据库值
            dialect: SQLAlchemy 方言
            
        Returns:
            numpy.ndarray 向量
        """
        if value is None:
            return None
            
        if isinstance(value, (list, tuple)):
            return np.array([float(x) for x in value], dtype=np.float32)
        elif isinstance(value, np.ndarray):
            return value.astype(np.float32)
        else:
            raise TypeError(f"不支持的数据库向量类型：{type(value)}")


# 便利函数
def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    计算两个向量的余弦相似度
    
    Args:
        vec1: 第一个向量
        vec2: 第二个向量
        
    Returns:
        余弦相似度值 (-1 到 1 之间)
    """
    if vec1.shape != vec2.shape:
        raise ValueError(f"向量维度不匹配：{vec1.shape} vs {vec2.shape}")
    
    # 归一化向量
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    # 计算余弦相似度
    similarity = np.dot(vec1, vec2) / (norm1 * norm2)
    
    # 确保结果在 [-1, 1] 范围内（由于浮点精度问题）
    return np.clip(similarity, -1.0, 1.0)


def euclidean_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    计算两个向量的欧氏距离
    
    Args:
        vec1: 第一个向量
        vec2: 第二个向量
        
    Returns:
        欧氏距离
    """
    if vec1.shape != vec2.shape:
        raise ValueError(f"向量维度不匹配：{vec1.shape} vs {vec2.shape}")
    
    return np.linalg.norm(vec1 - vec2)


def normalize_vector(vec: np.ndarray) -> np.ndarray:
    """
    归一化向量（使其长度为1）
    
    Args:
        vec: 输入向量
        
    Returns:
        归一化后的向量
    """
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec
    return vec / norm