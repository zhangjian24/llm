"""
应用配置管理
使用 Pydantic Settings 进行类型安全的环境变量管理
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Set


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    APP_NAME: str = "RAG Document QA System"
    APP_ENV: str = "production"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://localhost/rag_qa"
    
    # 向量存储配置（PostgreSQL pgvector）
    # 向量维度（需与 embedding 模型输出维度一致）
    # text-embedding-v4 输出 1024 维向量
    VECTOR_DIMENSION: int = 1024
    # 向量索引类型（hnsw 或 ivfflat）
    VECTOR_INDEX_TYPE: str = "hnsw"
    # HNSW 索引参数
    HNSW_M: int = 16
    HNSW_EF_CONSTRUCTION: int = 64
    
    # 阿里云百炼配置
    DASHSCOPE_API_KEY: str = ""
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    # OpenAI 兼容配置（用于其他 LLM 服务）
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""
    
    # 模型配置
    LLM_MODEL: str = "qwen-turbo"  # 使用turbo模型（比flash更准，比max更快）
    EMBEDDING_MODEL: str = "text-embedding-v4"
    RERANK_MODEL: str = "qwen3-rerank"
    
    # LLM 超时配置
    LLM_TIMEOUT_SECONDS: int = 4  # 生成超时4秒
    
    # RAG 配置
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 200
    RAG_TOP_K: int = 15  # 平衡检索数量
    RERANK_TOP_K: int = 6  # 平衡rerank数量
    RELEVANCE_THRESHOLD: float = 0.08  # 降低阈值
    MAX_RETRIEVAL_DOCS: int = 15
    
    # LLM 超时配置
    LLM_TIMEOUT_SECONDS: int = 8  # 生成超时8秒
    
    # 文件上传配置
    MAX_FILE_SIZE_MB: int = 50
    MAX_FILE_SIZE: int = 52428800  # 字节
    ALLOWED_MIME_TYPES: Set[str] = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/markdown",
        "text/plain"
    }
    UPLOAD_DIR: str = "./uploads"
    
    # 存储配置
    STORAGE_PATH: str = "./backend/app/storage"
    
    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"
    
    # 速率限制配置
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    class Config:
        env_file = ".env.local"
        case_sensitive = True
        extra = "ignore"  # 忽略未知的环境变量


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置单例（使用 LRU 缓存）
    
    Returns:
        Settings: 配置对象
    """
    return Settings()
