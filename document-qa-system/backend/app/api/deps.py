"""
依赖注入模块
管理FastAPI的依赖项，包括数据库连接和服务客户端
"""

from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
# 暂时注释掉，后续根据新版API调整
# from pinecone import Pinecone, ServerlessSpec
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone as LangchainPinecone

from ..core.config import settings
from ..core.logging import logger


class PineconeService:
    """Pinecone服务封装"""
    
    def __init__(self):
        self.client = None
        self.index = None
        self.vector_store = None
    
    async def initialize(self) -> None:
        """初始化Pinecone客户端"""
        try:
            logger.info("正在初始化Pinecone客户端...")
            
            # 初始化Pinecone客户端
            self.client = Pinecone(api_key=settings.PINECONE_API_KEY)
            
            # 检查索引是否存在，如果不存在则创建
            indexes = self.client.list_indexes()
            index_names = [idx['name'] for idx in indexes]
            
            if settings.PINECONE_INDEX_NAME not in index_names:
                logger.info(f"创建新的Pinecone索引: {settings.PINECONE_INDEX_NAME}")
                self.client.create_index(
                    name=settings.PINECONE_INDEX_NAME,
                    dimension=1536,  # text-embedding-v4的维度
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1")
                )
            
            # 获取索引
            self.index = self.client.Index(settings.PINECONE_INDEX_NAME)
            logger.info("Pinecone客户端初始化成功")
            
        except Exception as e:
            logger.error(f"Pinecone初始化失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Pinecone初始化失败: {str(e)}"
            )
    
    def get_index(self):
        """获取Pinecone索引"""
        if not self.index:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Pinecone索引未初始化"
            )
        return self.index


class LLMService:
    """LLM服务封装"""
    
    def __init__(self):
        self.chat_model = None
        self.embedding_model = None
        self.rerank_client = None
    
    async def initialize(self) -> None:
        """初始化LLM客户端"""
        try:
            logger.info("正在初始化LLM客户端...")
            
            # 初始化聊天模型
            self.chat_model = ChatOpenAI(
                model=settings.CHAT_MODEL,
                openai_api_base=settings.OPENAI_BASE_URL,
                openai_api_key=settings.OPENAI_API_KEY,
                streaming=True,
                temperature=0.7
            )
            
            # 初始化嵌入模型
            self.embedding_model = OpenAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                openai_api_base=settings.OPENAI_BASE_URL,
                openai_api_key=settings.OPENAI_API_KEY
            )
            
            logger.info("LLM客户端初始化成功")
            
        except Exception as e:
            logger.error(f"LLM初始化失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"LLM初始化失败: {str(e)}"
            )
    
    def get_chat_model(self):
        """获取聊天模型"""
        if not self.chat_model:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="聊天模型未初始化"
            )
        return self.chat_model
    
    def get_embedding_model(self):
        """获取嵌入模型"""
        if not self.embedding_model:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="嵌入模型未初始化"
            )
        return self.embedding_model


# 全局服务实例
pinecone_service = PineconeService()
llm_service = LLMService()


async def get_pinecone_service() -> AsyncGenerator[PineconeService, None]:
    """获取Pinecone服务依赖"""
    await pinecone_service.initialize()
    yield pinecone_service


async def get_llm_service() -> AsyncGenerator[LLMService, None]:
    """获取LLM服务依赖"""
    await llm_service.initialize()
    yield llm_service


# 依赖注入快捷方式
PineconeDep = Depends(get_pinecone_service)
LLMDep = Depends(get_llm_service)