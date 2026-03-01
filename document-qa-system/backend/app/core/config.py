from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Pinecone Configuration
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str = "document-qa-index"
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = "https://ollama.com"
    OLLAMA_API_KEY: str = ""
    EMBEDDING_MODEL: str = "bge-m3"
    LLM_MODEL: str = "gpt-oss:20b"
    
    # Application Settings
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    SERVER_HOST: str = "localhost"  # 新增字段
    SERVER_PORT: int = 8000        # 新增字段
    
    # Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: str = ".pdf,.txt,.docx,.doc,.html,.htm"
    UPLOAD_FOLDER: str = "./uploads"
    
    # Document Processing Settings
    CHUNK_SIZE: int = 512          # 新增字段
    CHUNK_OVERLAP: int = 77        # 新增字段
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",") if ext.strip()]
    
    # Vector Store Settings
    VECTOR_DIMENSION: int = 768
    TOP_K_RESULTS: int = 5
    SCORE_THRESHOLD: float = 0.7
    
    class Config:
        env_file = [".env.local", ".env"]  # 优先加载 .env.local，然后是 .env
        env_file_encoding = "utf-8"
        extra = "ignore"  # 忽略额外的环境变量

settings = Settings()