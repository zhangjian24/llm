"""
文档实体模型
对应数据库的 documents 表
"""
from sqlalchemy import Column, String, Integer, DateTime, func, LargeBinary
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from uuid import uuid4
from datetime import datetime
from app.core.database import Base


class Document(Base):
    """
    文档元数据表
    
    Attributes:
        id: 文档唯一标识 (UUID)
        filename: 原始文件名
        file_path: 本地存储路径
        file_size: 文件大小 (字节)
        mime_type: MIME 类型
        status: 处理状态 (processing/ready/failed)
        chunks_count: 分块数量
        doc_metadata: 额外元数据（页数、字数等）
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    filename = Column(String(255), nullable=False)
    file_content = Column(LargeBinary, nullable=True)  # 存储文件二进制内容
    content_hash = Column(String(64), nullable=True, unique=True)  # 内容SHA256哈希，用于去重
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default='processing')
    chunks_count = Column(Integer, nullable=True)
    chunk_count = Column(Integer, nullable=True)  # 大文件分块数量
    # 使用 'doc_metadata' 避免 SQLAlchemy 保留字冲突，数据库列名仍为 'metadata'
    doc_metadata = Column(JSONB, nullable=True, name="metadata")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
    document_chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', status='{self.status}')>"
