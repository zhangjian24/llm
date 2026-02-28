from fastapi import HTTPException, status

class DocumentProcessingError(Exception):
    """文档处理错误"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class VectorStoreError(Exception):
    """向量存储错误"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class EmbeddingError(Exception):
    """嵌入模型错误"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class LLMError(Exception):
    """大语言模型错误"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

def handle_exception(exc: Exception) -> HTTPException:
    """统一异常处理"""
    if isinstance(exc, DocumentProcessingError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文档处理失败: {exc.message}"
        )
    elif isinstance(exc, VectorStoreError):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"向量存储错误: {exc.message}"
        )
    elif isinstance(exc, EmbeddingError):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"嵌入模型错误: {exc.message}"
        )
    elif isinstance(exc, LLMError):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"语言模型错误: {exc.message}"
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"未知错误: {str(exc)}"
        )