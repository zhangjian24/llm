from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # API配置
    PROJECT_NAME: str = "文档问答系统"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Pinecone配置
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str = "gcp-starter"
    PINECONE_INDEX_NAME: str = "document-qa-index"
    
    # 千问API配置
    DASHSCOPE_API_KEY: str
    
    # BGE嵌入模型配置
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-large-zh-v1.5"
    EMBEDDING_DIMENSION: int = 1024
    
    # 文档处理配置
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # 缓存配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()