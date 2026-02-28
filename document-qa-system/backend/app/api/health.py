from fastapi import APIRouter
from datetime import datetime
import asyncio

from app.models.schemas import HealthCheckResponse
from app.core.config import settings
from app.core.logging_config import logger

router = APIRouter()

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """健康检查端点"""
    try:
        # 检查各个服务状态
        services_status = {}
        
        # 检查向量数据库
        try:
            from app.services.vector_store import vector_store
            if vector_store.index:
                services_status["vector_store"] = "healthy"
            else:
                services_status["vector_store"] = "uninitialized"
        except Exception:
            services_status["vector_store"] = "error"
        
        # 检查嵌入模型服务
        try:
            import requests
            response = requests.get(f"{settings.OLLAMA_BASE_URL}/tags", timeout=10)
            if response.status_code == 200:
                services_status["embedding_service"] = "healthy"
            else:
                services_status["embedding_service"] = "unreachable"
        except Exception:
            services_status["embedding_service"] = "error"
        
        # 检查Ollama LLM服务
        try:
            import requests
            headers = {}
            if settings.OLLAMA_API_KEY:
                headers['Authorization'] = f'Bearer {settings.OLLAMA_API_KEY}'
            response = requests.get(f"{settings.OLLAMA_BASE_URL}/tags", headers=headers, timeout=10)
            if response.status_code == 200:
                services_status["llm_service"] = "healthy"
            else:
                services_status["llm_service"] = "unreachable"
        except Exception as e:
            logger.error(f"LLM服务检查失败: {str(e)}")
            services_status["llm_service"] = "error"
        
        # 检查文件上传目录
        try:
            import os
            if os.path.exists(settings.UPLOAD_FOLDER):
                services_status["file_storage"] = "healthy"
            else:
                services_status["file_storage"] = "directory_missing"
        except Exception:
            services_status["file_storage"] = "error"
        
        # 确定整体状态
        overall_status = "healthy"
        if any(status == "error" for status in services_status.values()):
            overall_status = "degraded"
        elif any(status in ["uninitialized", "unreachable", "directory_missing"] 
                for status in services_status.values()):
            overall_status = "warning"
        
        return HealthCheckResponse(
            status=overall_status,
            timestamp=datetime.now(),
            services=services_status
        )
        
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return HealthCheckResponse(
            status="error",
            timestamp=datetime.now(),
            services={"system": "error"}
        )

@router.get("/version")
async def get_version():
    """获取系统版本信息"""
    return {
        "version": "1.0.0",
        "name": "文档问答系统",
        "description": "基于向量检索和上下文注入的智能文档问答系统"
    }

@router.get("/stats")
async def get_system_stats():
    """获取系统统计信息"""
    try:
        # TODO: 实现实际的统计信息收集
        stats = {
            "total_documents": 0,
            "total_queries": 0,
            "uptime": "0 days",
            "memory_usage": "0 MB"
        }
        
        # 从向量数据库获取文档统计
        try:
            from app.services.vector_store import vector_store
            documents = await vector_store.list_documents()
            stats["total_documents"] = len(documents)
        except Exception:
            pass
        
        return stats
        
    except Exception as e:
        logger.error(f"获取系统统计失败: {str(e)}")
        return {"error": "无法获取统计信息"}