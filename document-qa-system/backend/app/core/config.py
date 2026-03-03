"""
应用配置管理模块
负责加载和管理系统配置
"""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    应用配置类
    
    从环境变量加载配置，优先级顺序：
    1. 环境变量 (操作系统)
    2. .env.local 文件
    3. 默认值
    """

    # OpenAI兼容接口配置
    OPENAI_BASE_URL: str = Field(
        default="https://api.openai.com/v1",
        description="OpenAI兼容接口的基础URL"
    )
    OPENAI_API_KEY: str = Field(
        ...,
        description="API密钥"
    )

    # Pinecone配置
    PINECONE_API_KEY: str = Field(
        ...,
        description="Pinecone API密钥"
    )
    PINECONE_INDEX_NAME: str = Field(
        default="document-qa-index",
        description="Pinecone索引名称"
    )
    PINECONE_ENVIRONMENT: Optional[str] = Field(
        default=None,
        description="Pinecone环境(对于serverless可为空)"
    )

    # 应用配置
    APP_ENV: str = Field(
        default="development",
        description="应用环境"
    )
    DEBUG: bool = Field(
        default=True,
        description="调试模式"
    )
    LOG_LEVEL: str = Field(
        default="INFO",
        description="日志级别"
    )

    # 服务器配置
    HOST: str = Field(
        default="localhost",
        description="服务器主机"
    )
    PORT: int = Field(
        default=8000,
        description="服务器端口"
    )

    # RAG配置参数
    CHUNK_SIZE: int = Field(
        default=1000,
        description="文本分块大小"
    )
    CHUNK_OVERLAP: int = Field(
        default=200,
        description="文本分块重叠大小"
    )
    TOP_K_RETRIEVAL: int = Field(
        default=20,
        description="检索阶段返回的文档数量"
    )
    TOP_N_RERANK: int = Field(
        default=5,
        description="重排序后保留的文档数量"
    )

    # 模型配置
    EMBEDDING_MODEL: str = Field(
        default="qwen3-embeddings",
        description="嵌入模型名称"
    )
    RERANK_MODEL: str = Field(
        default="rerank-v3",
        description="重排序模型名称"
    )
    CHAT_MODEL: str = Field(
        default="qwen-max",
        description="聊天模型名称"
    )

    class Config:
        env_file = ".env.local"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局配置实例
settings = Settings()