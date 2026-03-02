"""
健康检查API路由
提供服务状态监控和健康检查功能
"""

from fastapi import APIRouter, Depends
from typing import Dict

from ...models.schemas import HealthCheckResponse
from ...core.config import settings
from ...core.logging import logger

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthCheckResponse)
async def health_check():
    """
    健康检查端点
    
    Returns:
        健康检查响应
    """
    logger.info("健康检查请求")
    
    return HealthCheckResponse(
        status="healthy",
        version="1.0.0",
        services={
            "api": "running",
            "database": "connected"  # 实际应该检查真实连接状态
        }
    )


@router.get("/ready")
async def readiness_check():
    """
    就绪检查端点
    检查服务是否准备好接收流量
    
    Returns:
        就绪状态
    """
    # 这里可以添加更详细的就绪检查逻辑
    # 比如检查数据库连接、缓存连接等
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    """
    存活检查端点
    检查服务进程是否存活
    
    Returns:
        存活状态
    """
    return {"status": "alive"}