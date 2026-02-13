from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"

class DocumentUploadRequest(BaseModel):
    filename: str = Field(..., description="文件名")
    content_type: str = Field(..., description="文件类型")

class DocumentResponse(BaseModel):
    id: str = Field(..., description="文档ID")
    filename: str = Field(..., description="文件名")
    content_type: str = Field(..., description="文件类型")
    size: int = Field(..., description="文件大小(字节)")
    status: DocumentStatus = Field(..., description="处理状态")
    created_at: datetime = Field(..., description="创建时间")
    processed_at: Optional[datetime] = Field(None, description="处理完成时间")

class ChatMessage(BaseModel):
    role: str = Field(..., description="角色(user/assistant)")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatRequest(BaseModel):
    query: str = Field(..., description="用户查询")
    document_ids: Optional[List[str]] = Field(None, description="相关文档IDs")
    history: Optional[List[ChatMessage]] = Field(None, description="对话历史")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="回答内容")
    sources: List[Dict[str, Any]] = Field(..., description="引用来源")
    confidence: float = Field(..., description="置信度", ge=0, le=1)

class SearchResult(BaseModel):
    document_id: str = Field(..., description="文档ID")
    content: str = Field(..., description="相关内容")
    score: float = Field(..., description="相似度得分")
    metadata: Dict[str, Any] = Field(..., description="元数据")

class HealthCheck(BaseModel):
    status: str = Field(..., description="服务状态")
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = Field(..., description="版本号")