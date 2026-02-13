from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import documents, chat, health
from app.core.exceptions import (
    document_qa_exception_handler,
    http_exception_handler,
    general_exception_handler,
    DocumentQABaseException
)
from app.core.logging_config import setup_logging
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import os

# 设置日志
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="文档问答系统API",
    description="基于向量检索和上下文注入的智能文档问答系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册异常处理器
app.add_exception_handler(DocumentQABaseException, document_qa_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 注册路由
app.include_router(health.router, prefix="/api/v1", tags=["健康检查"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["文档管理"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["聊天问答"])

@app.get("/")
async def root():
    logger.info("API根路径被访问")
    return {"message": "欢迎使用文档问答系统API"}

@app.on_event("startup")
async def startup_event():
    logger.info("文档问答系统API启动成功")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("文档问答系统API正在关闭")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)