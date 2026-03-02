"""
Pydantic数据模型定义
用于API请求/响应的数据验证和序列化
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """文档元数据模型"""
    filename: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小(字节)")
    content_type: str = Field(..., description="文件类型")
    upload_time: datetime = Field(default_factory=datetime.now, description="上传时间")
    chunk_count: int = Field(default=0, description="分块数量")
    doc_id: str = Field(..., description="文档唯一标识")


class DocumentUploadRequest(BaseModel):
    """文档上传请求模型"""
    pass  # 文件上传使用multipart/form-data，不需要JSON body


class DocumentUploadResponse(BaseModel):
    """文档上传响应模型"""
    doc_id: str = Field(..., description="文档ID")
    filename: str = Field(..., description="文件名")
    status: str = Field(..., description="处理状态")
    message: str = Field(..., description="处理消息")


class DocumentListResponse(BaseModel):
    """文档列表响应模型"""
    documents: List[DocumentMetadata] = Field(..., description="文档列表")
    total_count: int = Field(..., description="文档总数")


class SearchResult(BaseModel):
    """检索结果模型"""
    content: str = Field(..., description="文档内容片段")
    metadata: Dict[str, Any] = Field(..., description="文档元数据")
    score: float = Field(..., description="相关性得分")
    doc_id: str = Field(..., description="文档ID")


class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str = Field(..., description="角色(user/assistant)")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class QueryRequest(BaseModel):
    """查询请求模型"""
    query: str = Field(..., min_length=1, max_length=1000, description="查询内容")
    conversation_id: Optional[str] = Field(None, description="对话ID")
    stream: bool = Field(default=False, description="是否流式响应")


class QueryResponse(BaseModel):
    """查询响应模型"""
    answer: str = Field(..., description="回答内容")
    sources: List[SearchResult] = Field(..., description="引用来源")
    conversation_id: str = Field(..., description="对话ID")
    processing_time: float = Field(..., description="处理耗时(秒)")


class StreamChunk(BaseModel):
    """流式响应数据块"""
    type: str = Field(..., description="数据块类型(answer/sources/end)")
    content: Optional[str] = Field(None, description="内容")
    sources: Optional[List[SearchResult]] = Field(None, description="引用来源")
    done: bool = Field(default=False, description="是否结束")


class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    timestamp: datetime = Field(default_factory=datetime.now, description="检查时间")
    version: str = Field(..., description="应用版本")
    services: Dict[str, str] = Field(..., description="各服务状态")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str = Field(..., description="错误信息")
    detail: Optional[str] = Field(None, description="详细信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误时间")


# 用于内部处理的模型
class ProcessedDocument(BaseModel):
    """已处理的文档模型"""
    doc_id: str = Field(..., description="文档ID")
    chunks: List[str] = Field(..., description="文档分块")
    embeddings: List[List[float]] = Field(..., description="向量嵌入")
    metadata: DocumentMetadata = Field(..., description="文档元数据")