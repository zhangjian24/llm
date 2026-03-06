"""
对话实体模型
对应数据库的 conversations 表
"""
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from uuid import uuid4
from datetime import datetime
from app.core.database import Base


class Conversation(Base):
    """
    对话表
    
    Attributes:
        id: 对话唯一标识 (UUID)
        user_id: 用户 ID (MVP 阶段可选)
        title: 对话标题 (自动生成)
        messages: 完整消息列表 (JSONB)
        created_at: 创建时间
        updated_at: 最后更新时间
    """
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)  # MVP 阶段为空
    title = Column(String(200), nullable=True)
    messages = Column(JSONB, nullable=True)  # 存储完整对话历史
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, title='{self.title}')>"
