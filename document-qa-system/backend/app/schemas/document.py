"""
文档相关 Schema
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class DocumentDTO(BaseModel):
    """文档传输对象"""
    id: UUID
    filename: str
    file_size: int
    mime_type: str
    status: str
    chunks_count: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DocumentCreateDTO(BaseModel):
    """文档创建请求 DTO"""
    title: Optional[str] = Field(None, max_length=200)
    tags: list[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "员工手册",
                "tags": ["HR", "制度"]
            }
        }


class DocumentListDTO(BaseModel):
    """文档列表项 DTO"""
    id: UUID
    filename: str
    file_size: int
    mime_type: str
    status: str
    chunks_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
