from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.core.logging_config import logger
from app.api.documents import router as documents_router
from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.core.exceptions import handle_exception

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("正在启动文档问答系统...")
    
    try:
        # 初始化向量数据库连接
        from app.services.vector_store import vector_store
        await vector_store.initialize()
        logger.info("向量数据库初始化成功")
        
        # 初始化嵌入模型
        from app.services.embedding import embedding_service
        await embedding_service.initialize()
        logger.info("嵌入模型初始化成功")
        
    except Exception as e:
        logger.error(f"系统初始化失败: {str(e)}")
        raise
    
    yield
    
    # 关闭时清理
    logger.info("正在关闭文档问答系统...")
    try:
        # 清理资源
        pass
    except Exception as e:
        logger.error(f"系统关闭时出错: {str(e)}")

# 创建FastAPI应用
app = FastAPI(
    title="文档问答系统API",
    description="基于向量检索和上下文注入的智能文档问答系统",
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.DEBUG
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(documents_router, prefix="/api/documents", tags=["documents"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {str(exc)}")
    return handle_exception(exc)

# 健康检查端点
@app.get("/", tags=["root"])
async def root():
    """根路径欢迎信息"""
    return {
        "message": "欢迎使用文档问答系统API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )