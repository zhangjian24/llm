"""
对话相关 Schema
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class ChatQueryDTO(BaseModel):
    """对话查询请求 DTO"""
    query: str = Field(..., min_length=1, description="用户问题")
    top_k: int = Field(default=5, ge=1, le=20, description="检索数量")
    stream: bool = Field(default=True, description="是否流式输出")
    conversation_id: Optional[UUID] = Field(None, description="对话 ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "如何申请年假？",
                "top_k": 5,
                "stream": True,
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class ChatMessageDTO(BaseModel):
    """对话消息 DTO"""
    role: str  # "user" or "assistant"
    content: str
    sources: Optional[List[Dict[str, Any]]] = None  # 引用来源
    created_at: Optional[datetime] = None


class ChatResponseDTO(BaseModel):
    """对话响应 DTO"""
    answer: str
    conversation_id: UUID
    sources: Optional[List[Dict[str, Any]]] = None  # 引用来源
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "根据公司规定，申请年假需要...",
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "sources": [
                    {
                        "filename": "员工手册.pdf",
                        "content": "年假申请流程...",
                        "page": 5
                    }
                ]
            }
        }


class ConversationDTO(BaseModel):
    """对话历史 DTO"""
    id: UUID
    title: Optional[str] = None
    last_message: Optional[str] = None
    turns: int = 0  # 对话轮数
    updated_at: datetime
    
    class Config:
        from_attributes = True
