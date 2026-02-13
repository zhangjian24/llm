from fastapi import APIRouter, Depends
from app.models.schemas import HealthCheck
from app.core.config import settings
from datetime import datetime

router = APIRouter()

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """健康检查端点"""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now(),
        version=settings.VERSION
    )

@router.get("/ready")
async def readiness_check():
    """就绪检查端点"""
    # 这里可以添加数据库连接、外部服务等检查逻辑
    return {"status": "ready"}