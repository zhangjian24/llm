from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

class DocumentQABaseException(Exception):
    """文档问答系统基础异常类"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class DocumentNotFoundException(DocumentQABaseException):
    """文档未找到异常"""
    def __init__(self, document_id: str):
        super().__init__(f"文档 {document_id} 未找到", 404)

class DocumentProcessingException(DocumentQABaseException):
    """文档处理异常"""
    def __init__(self, message: str):
        super().__init__(f"文档处理失败: {message}", 400)

class VectorStoreException(DocumentQABaseException):
    """向量存储异常"""
    def __init__(self, message: str):
        super().__init__(f"向量存储操作失败: {message}", 500)

class LLMException(DocumentQABaseException):
    """大语言模型异常"""
    def __init__(self, message: str):
        super().__init__(f"LLM调用失败: {message}", 500)

async def document_qa_exception_handler(request, exc: DocumentQABaseException):
    """自定义异常处理器"""
    logger.error(f"DocumentQA异常: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

async def http_exception_handler(request, exc: StarletteHTTPException):
    """HTTP异常处理器"""
    logger.error(f"HTTP异常 {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

async def general_exception_handler(request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误"}
    )