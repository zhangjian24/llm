"""
文档数据访问层
负责文档的 CRUD 操作
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from uuid import UUID
from datetime import datetime
from app.models.document import Document
from app.models.chunk import Chunk


class DocumentRepository:
    """
    文档数据访问类
    
    Methods:
        save: 保存文档
        find_by_id: 根据 ID 查询
        find_all: 分页查询所有文档
        delete: 删除文档
        update_status: 更新文档状态
    """
    
    def __init__(self, session: AsyncSession):
        """
        初始化
        
        Args:
            session: 数据库会话
        """
        self.session = session
    
    async def save(self, doc: Document) -> UUID:
        """
        保存文档
        
        Args:
            doc: 文档实体
            
        Returns:
            UUID: 文档 ID
        """
        self.session.add(doc)
        await self.session.flush()  # 获取生成的 ID
        return doc.id
    
    async def find_by_id(self, doc_id: UUID) -> Optional[Document]:
        """
        根据 ID 查询文档
        
        Args:
            doc_id: 文档 ID
            
        Returns:
            Optional[Document]: 文档实体，不存在返回 None
        """
        result = await self.session.execute(
            select(Document).where(Document.id == doc_id)
        )
        return result.scalar_one_or_none()
    
    async def find_all(
        self, 
        page: int = 1, 
        limit: int = 20,
        status: Optional[str] = None
    ) -> tuple[List[Document], int]:
        """
        分页查询文档
        
        Args:
            page: 页码（从 1 开始）
            limit: 每页数量
            status: 状态筛选
            
        Returns:
            tuple[List[Document], int]: (文档列表，总数)
        """
        # 构建查询
        query = select(Document)
        count_query = select(func.count(Document.id))
        
        # 状态筛选
        if status:
            query = query.where(Document.status == status)
            count_query = count_query.where(Document.status == status)
        
        # 获取总数
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()
        
        # 获取分页数据
        query = query.order_by(desc(Document.created_at))
        query = query.offset((page - 1) * limit).limit(limit)
        
        result = await self.session.execute(query)
        documents = result.scalars().all()
        
        return documents, total
    
    async def delete(self, doc_id: UUID) -> bool:
        """
        删除文档（级联删除 chunks）
        
        Args:
            doc_id: 文档 ID
            
        Returns:
            bool: 是否删除成功
        """
        doc = await self.find_by_id(doc_id)
        if not doc:
            return False
        
        await self.session.delete(doc)
        return True
    
    async def update_status(
        self, 
        doc_id: UUID, 
        status: str, 
        chunks_count: Optional[int] = None
    ) -> bool:
        """
        更新文档状态
        
        Args:
            doc_id: 文档 ID
            status: 新状态
            chunks_count: 分块数量（可选）
            
        Returns:
            bool: 是否更新成功
        """
        doc = await self.find_by_id(doc_id)
        if not doc:
            return False
        
        doc.status = status
        if chunks_count is not None:
            doc.chunks_count = chunks_count
        
        doc.updated_at = datetime.utcnow()
        return True
    
    async def save_chunk(self, chunk: Chunk) -> UUID:
        """
        保存文档块
        
        Args:
            chunk: 文档块实体
            
        Returns:
            UUID: 块 ID
        """
        self.session.add(chunk)
        await self.session.flush()
        return chunk.id
    
    async def find_chunks_by_document(self, doc_id: UUID) -> List[Chunk]:
        """
        查询文档的所有块
        
        Args:
            doc_id: 文档 ID
            
        Returns:
            List[Chunk]: 块列表
        """
        result = await self.session.execute(
            select(Chunk)
            .where(Chunk.document_id == doc_id)
            .order_by(Chunk.chunk_index)
        )
        return result.scalars().all()
