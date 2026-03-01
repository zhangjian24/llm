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

class EmbeddingRequest(BaseModel):
    """嵌入请求"""
    input: List[str] = Field(..., description="输入文本列表")
    model: str = Field("text-embedding-v4", description="模型名称")

class TextEmbedding(BaseModel):
    """单个文本嵌入"""
    object: str = Field("embedding", description="对象类型")
    embedding: List[float] = Field(..., description="嵌入向量")
    index: int = Field(..., description="索引位置")

class EmbeddingResponse(BaseModel):
    """嵌入响应"""
    object: str = Field("list", description="对象类型")
    data: List[TextEmbedding] = Field(..., description="嵌入数据")
    model: str = Field(..., description="模型名称")
    usage: Dict[str, int] = Field(..., description="使用统计")

class QueryEmbeddingRequest(BaseModel):
    """查询嵌入请求"""
    query: str = Field(..., description="查询文本", min_length=1)

class RerankRequest(BaseModel):
    """重排序请求"""
    model: str = Field("rerank-v3", description="模型名称")
    query: str = Field(..., description="查询文本", min_length=1)
    documents: List[Any] = Field(..., description="文档列表")
    top_n: Optional[int] = Field(10, description="返回top N结果", ge=1, le=100)

class RerankResult(BaseModel):
    """重排序结果"""
    index: int = Field(..., description="原始索引")
    document: str = Field(..., description="文档内容")
    relevance_score: float = Field(..., description="相关性分数", ge=0, le=1)
    document_id: str = Field("", description="文档ID")

class RerankResponse(BaseModel):
    """重排序响应"""
    id: str = Field(..., description="请求ID")
    results: List[RerankResult] = Field(..., description="重排序结果")
    usage: Dict[str, int] = Field(..., description="使用统计")