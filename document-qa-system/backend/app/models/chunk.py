"""
文档块实体模型
对应数据库的 chunks 表
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from uuid import uuid4
from app.core.database import Base


class Chunk(Base):
    """
    文档块表
    
    Attributes:
        id: 块唯一标识 (UUID)
        document_id: 所属文档 ID (外键)
        chunk_index: 块索引序号
        content: 原始文本内容
        token_count: Token 数量
        chunk_metadata: 位置信息（章节、页码）
    """
    __tablename__ = "chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False)
    # 使用 'chunk_metadata' 避免 SQLAlchemy 保留字冲突，数据库列名仍为 'metadata'
    chunk_metadata = Column(JSONB, nullable=True, name="metadata")
    
    # 关联关系
    document = relationship("Document", back_populates="chunks")
    
    def __repr__(self):
        return f"<Chunk(id={self.id}, document_id={self.document_id}, index={self.chunk_index})>"
