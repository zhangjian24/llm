"""
自定义异常类
所有业务异常都继承自 BaseAppException
"""
from typing import Optional, Dict


class BaseAppException(Exception):
    """
    应用基础异常类
    
    Attributes:
        code: 错误码（用于前端展示）
        message: 错误消息（对用户友好）
        details: 详细错误信息（用于调试）
        status_code: HTTP 状态码
    """
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: Optional[Dict] = None,
        status_code: int = 500
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)


class DocumentException(BaseAppException):
    """文档处理相关异常"""
    pass


class FileTooLargeError(DocumentException):
    """文件过大异常"""
    def __init__(self, file_size: int, max_size: int = 50 * 1024 * 1024):
        super().__init__(
            message=f"文件大小 {file_size / 1024 / 1024:.2f}MB，超过限制 {max_size / 1024 / 1024:.2f}MB",
            code="FILE_TOO_LARGE",
            status_code=413
        )


class UnsupportedFileTypeError(DocumentException):
    """不支持的文件类型"""
    def __init__(self, mime_type: str):
        super().__init__(
            message=f"不支持的文件格式：{mime_type}",
            code="UNSUPPORTED_FILE_TYPE",
            status_code=400
        )


class DocumentParseError(DocumentException):
    """文档解析失败"""
    def __init__(self, reason: str):
        super().__init__(
            message=f"文档解析失败：{reason}",
            code="DOCUMENT_PARSE_ERROR",
            status_code=400
        )


class DocumentNotFoundException(DocumentException):
    """文档未找到"""
    def __init__(self, doc_id: str):
        super().__init__(
            message=f"文档不存在：{doc_id}",
            code="DOCUMENT_NOT_FOUND",
            status_code=404
        )


class DocumentProcessingConflictError(DocumentException):
    """文档正在处理中"""
    def __init__(self, doc_id: str):
        super().__init__(
            message=f"文档正在处理中：{doc_id}",
            code="DOCUMENT_PROCESSING_CONFLICT",
            status_code=409
        )


class RetrievalException(BaseAppException):
    """检索失败异常"""
    def __init__(self, reason: str):
        super().__init__(
            message="文档检索失败",
            code="RETRIEVAL_FAILED",
            details={"reason": reason},
            status_code=500
        )


class VectorizationException(DocumentException):
    """向量化失败异常"""
    def __init__(self, reason: str):
        super().__init__(
            message=f"文档向量化失败：{reason}",
            code="VECTORIZATION_FAILED",
            status_code=500
        )


class GenerationException(BaseAppException):
    """生成失败异常"""
    def __init__(self, reason: str):
        super().__init__(
            message="回答生成失败",
            code="GENERATION_FAILED",
            details={"reason": reason},
            status_code=500
        )


class InternalError(BaseAppException):
    """服务器内部错误"""
    def __init__(self, details: Optional[str] = None):
        super().__init__(
            message="服务器内部错误，请稍后重试",
            code="INTERNAL_ERROR",
            details={"details": details} if details else None,
            status_code=500
        )
