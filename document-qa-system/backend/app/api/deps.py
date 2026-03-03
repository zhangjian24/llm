"""
依赖注入模块
管理 FastAPI 的依赖项，包括数据库连接和服务客户端
"""

from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status

from ..core.config import settings
from ..core.logging import logger
from ..services.llm_service import LLMService as FullLLMService
from ..services.pinecone_service import PineconeService as FullPineconeService


# 全局服务实例
pinecone_service = FullPineconeService()
llm_service = FullLLMService()


async def get_pinecone_service() -> AsyncGenerator[FullPineconeService, None]:
    """获取 Pinecone 服务依赖"""
    # 需要先初始化 LLM服务获取 embeddings
    await llm_service.initialize()
    await pinecone_service.initialize(llm_service.embedding_model)
    yield pinecone_service


async def get_llm_service() -> AsyncGenerator[FullLLMService, None]:
    """获取 LLM服务依赖"""
    await llm_service.initialize()
    yield llm_service


# 依赖注入快捷方式
PineconeDep = Depends(get_pinecone_service)
LLMDep = Depends(get_llm_service)