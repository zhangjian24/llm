"""
FastAPI 应用主入口
"""
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from starlette.websockets import WebSocketDisconnect
from app.core.database import init_db, close_db
from app.core.config import get_settings
from app.utils.logger import setup_logging
from app.websocket_manager import manager
import structlog

settings = get_settings()
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    Yields:
        None
    """
    # 启动时初始化
    logger.info("Application starting up...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # 关闭时清理
    logger.info("Application shutting down...")
    await close_db()
    logger.info("Database connections closed")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "version": settings.VERSION}


@app.get("/")
async def root():
    """根路径"""
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": "/docs"
    }


# WebSocket 路由：实时推送文档状态
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket 端点，用于实时推送文档状态更新
    
    客户端连接后会：
    1. 接受连接
    2. 保持连接活跃
    3. 接收并忽略心跳消息（如果有）
    4. 断开时清理资源
    """
    connection_id = await manager.connect(websocket)
    try:
        # 发送欢迎消息
        await websocket.send_json({
            "type": "connected",
            "connection_id": connection_id,
            "message": "已连接到文档状态推送服务"
        })
        
        # 保持连接活跃
        while True:
            # 接收客户端消息（心跳或控制消息）
            data = await websocket.receive_text()
            
            # 可以处理客户端的控制消息
            # 这里暂时只记录日志
            logger.debug("websocket_message_received", message=data)
            
    except WebSocketDisconnect as e:
        logger.info(
            "websocket_disconnected",
            connection_id=connection_id,
            code=e.code,
            reason=e.reason
        )
    except Exception as e:
        logger.error(
            "websocket_error",
            connection_id=connection_id,
            error=str(e),
            exc_info=True
        )
    finally:
        manager.disconnect(websocket)


# 导入并注册路由
from app.api.v1 import documents, chat, conversations

app.include_router(documents.router, prefix="/api/v1/documents", tags=["文档管理"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["对话聊天"])
app.include_router(conversations.router, prefix="/api/v1/conversations", tags=["对话历史"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
