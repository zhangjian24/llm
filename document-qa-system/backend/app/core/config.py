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
    
    # Pinecone 配置
    PINECONE_API_KEY: str = ""
    PINECONE_HOST: str = ""
    PINECONE_INDEX_NAME: str = "rag-documents"
    
    # 阿里云百炼配置
    DASHSCOPE_API_KEY: str = ""
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/api/v1"
    
    # OpenAI 兼容配置（用于其他 LLM 服务）
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""
    
    # 模型配置
    LLM_MODEL: str = "qwen-max"
    EMBEDDING_MODEL: str = "text-embedding-v4"
    RERANK_MODEL: str = "rerank-v3"
    
    # RAG 配置
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150
    RAG_TOP_K: int = 10
    RERANK_TOP_K: int = 5
    RELEVANCE_THRESHOLD: float = 0.7
    MAX_RETRIEVAL_DOCS: int = 10
    
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


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置单例（使用 LRU 缓存）
    
    Returns:
        Settings: 配置对象
    """
    return Settings()
