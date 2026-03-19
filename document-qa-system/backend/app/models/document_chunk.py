"""
大文件分块存储模型
用于存储超过阈值的大文件分块数据
"""
from sqlalchemy import Column, Integer, DateTime, LargeBinary, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from datetime import datetime
from app.core.database import Base


class DocumentChunk(Base):
    """
    文档分块存储表
    
    Attributes:
        id: 分块唯一标识
        document_id: 所属文档ID
        chunk_index: 分块序号（从0开始）
        chunk_data: 分块二进制数据
        chunk_size: 分块大小（字节）
        created_at: 创建时间
    """
    __tablename__ = "document_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id'), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_data = Column(LargeBinary, nullable=False)
    chunk_size = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 关联关系
    document = relationship("Document", back_populates="document_chunks")
    
    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, index={self.chunk_index})>"