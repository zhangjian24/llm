from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class DocumentUploadRequest(BaseModel):
    """文档上传请求"""
    filename: str = Field(..., description="文件名")
    content_type: str = Field(..., description="文件类型")

class DocumentUploadResponse(BaseModel):
    """文档上传响应"""
    document_id: str = Field(..., description="文档ID")
    filename: str = Field(..., description="文件名")
    status: str = Field(..., description="处理状态")
    message: str = Field(..., description="处理消息")

class QueryRequest(BaseModel):
    """查询请求"""
    query: str = Field(..., description="查询内容", min_length=1, max_length=1000)
    document_ids: Optional[List[str]] = Field(None, description="限定文档范围")
    top_k: Optional[int] = Field(5, description="返回结果数量", ge=1, le=20)

class QueryResponse(BaseModel):
    """查询响应"""
    query: str = Field(..., description="查询内容")
    answer: str = Field(..., description="回答内容")
    sources: List[Dict[str, Any]] = Field(..., description="来源文档信息")
    confidence: float = Field(..., description="置信度", ge=0, le=1)

class DocumentInfo(BaseModel):
    """文档信息"""
    document_id: str = Field(..., description="文档ID")
    filename: str = Field(..., description="文件名")
    upload_time: datetime = Field(..., description="上传时间")
    status: str = Field(..., description="处理状态")
    size: int = Field(..., description="文件大小")

class DocumentListResponse(BaseModel):
    """文档列表响应"""
    documents: List[DocumentInfo] = Field(..., description="文档列表")
    total: int = Field(..., description="总文档数")

class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态")
    timestamp: datetime = Field(..., description="检查时间")
    services: Dict[str, str] = Field(..., description="各服务状态")