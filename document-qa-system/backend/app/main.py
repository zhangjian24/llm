"""
FastAPI主应用入口
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from .core.config import settings
from .core.logging import logger
from .api.routes import health, documents, chat

# 创建FastAPI应用实例
app = FastAPI(
    title="文档问答系统API",
    description="基于RAG的企业级文档问答系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(health.router)
app.include_router(documents.router)
app.include_router(chat.router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理器"""
    logger.error(f"HTTP异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """请求验证异常处理器"""
    logger.error(f"请求验证异常: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "请求参数验证失败",
            "detail": exc.errors(),
            "status_code": 422
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理器"""
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "服务器内部错误",
            "detail": str(exc) if settings.DEBUG else "请联系管理员",
            "status_code": 500
        }
    )


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    # 请求接收阶段 - INFO级别
    logger.info(f"[APP_STARTUP] 文档问答系统API服务启动中...")
    
    # 数据验证阶段 - DEBUG级别
    logger.debug(f"[APP_STARTUP] 启动配置验证 - 环境: {settings.APP_ENV}, 调试模式: {settings.DEBUG}, 主机: {settings.HOST}:{settings.PORT}")
    
    # 业务逻辑处理阶段 - INFO级别
    logger.info(f"[APP_STARTUP] 系统配置信息 - 运行环境: {settings.APP_ENV}")
    logger.info(f"[APP_STARTUP] 调试配置 - 调试模式: {settings.DEBUG}")
    logger.info(f"[APP_STARTUP] 服务器配置 - 主机: {settings.HOST}, 端口: {settings.PORT}")
    logger.info(f"[APP_STARTUP] 模型配置 - 嵌入模型: {settings.EMBEDDING_MODEL}, 重排序模型: {settings.RERANK_MODEL}, 聊天模型: {settings.CHAT_MODEL}")
    logger.info(f"[APP_STARTUP] RAG参数 - 分块大小: {settings.CHUNK_SIZE}, 重叠: {settings.CHUNK_OVERLAP}, 检索Top-K: {settings.TOP_K_RETRIEVAL}, 重排序Top-N: {settings.TOP_N_RERANK}")
    
    # 响应返回阶段 - INFO级别
    logger.info(f"[APP_STARTUP] 服务启动完成 - 系统准备就绪")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    # 请求接收阶段 - INFO级别
    logger.info(f"[APP_SHUTDOWN] 文档问答系统API服务正在关闭...")
    
    # 业务逻辑处理阶段 - DEBUG级别
    logger.debug(f"[APP_SHUTDOWN] 执行清理操作")
    
    # 响应返回阶段 - INFO级别
    logger.info(f"[APP_SHUTDOWN] 服务关闭完成 - 系统已停止")


@app.get("/")
async def root():
    """根路径欢迎信息"""
    return {
        "message": "欢迎使用文档问答系统API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_check": "/health"
    }


@app.get("/config")
async def get_config():
    """获取配置信息（调试用）"""
    if not settings.DEBUG:
        raise HTTPException(status_code=403, detail="此端点仅在调试模式下可用")
    
    return {
        "app_env": settings.APP_ENV,
        "debug": settings.DEBUG,
        "host": settings.HOST,
        "port": settings.PORT,
        "models": {
            "embedding": settings.EMBEDDING_MODEL,
            "rerank": settings.RERANK_MODEL,
            "chat": settings.CHAT_MODEL
        },
        "rag_params": {
            "chunk_size": settings.CHUNK_SIZE,
            "chunk_overlap": settings.CHUNK_OVERLAP,
            "top_k_retrieval": settings.TOP_K_RETRIEVAL,
            "top_n_rerank": settings.TOP_N_RERANK
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )