"""
文档服务层
负责文档上传、解析、分块、向量化的编排
"""
import asyncio
import aiofiles
from pathlib import Path
from uuid import UUID
from typing import Optional
from app.repositories.document_repository import DocumentRepository
from app.parsers.base_parser import ParserRegistry
from app.chunkers.semantic_chunker import TextChunker
from app.services.embedding_service import EmbeddingService
from app.models.document import Document
from app.models.chunk import Chunk
from app.core.config import get_settings
from app.exceptions import (
    FileTooLargeError, 
    UnsupportedFileTypeError,
    DocumentParseError,
    DocumentNotFoundException
)
import structlog

logger = structlog.get_logger()
settings = get_settings()


class DocumentService:
    """
    文档处理服务
    
    职责:
    - 文档上传验证
    - 文档解析编排
    - 文本分块
    - 向量化处理
    - 文档状态管理
    """
    
    def __init__(
        self, 
        repo: DocumentRepository,
        embedding_svc: EmbeddingService
    ):
        """
        初始化文档服务
        
        Args:
            repo: 文档数据访问仓库
            embedding_svc: 嵌入向量化服务
        """
        self.repo = repo
        self.embedding_svc = embedding_svc
        self.chunker = TextChunker(
            chunk_size=settings.CHUNK_SIZE,
            overlap=settings.CHUNK_OVERLAP
        )
        self.storage_path = Path(settings.STORAGE_PATH)
        
        # 确保存储目录存在
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    async def upload_document(
        self, 
        file_content: bytes,
        filename: str,
        mime_type: str,
        file_size: int
    ) -> UUID:
        """
        上传并处理文档
        
        Args:
            file_content: 文件二进制内容
            filename: 文件名
            mime_type: MIME 类型
            file_size: 文件大小
            
        Returns:
            UUID: 文档 ID
            
        Raises:
            FileTooLargeError: 文件过大
            UnsupportedFileTypeError: 文件格式不支持
        """
        # 1. 验证文件大小
        max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size > max_size:
            raise FileTooLargeError(file_size, max_size)
        
        # 2. 验证文件类型：从配置文件读取支持的 MIME 类型
        if mime_type not in settings.ALLOWED_MIME_TYPES:
            logger.warning(
                "unsupported_mime_type",
                mime_type=mime_type,
                allowed_types=settings.ALLOWED_MIME_TYPES
            )
            raise UnsupportedFileTypeError(mime_type)
        
        # 3. 额外验证：确保解析器已注册（双重检查）
        if not ParserRegistry.is_supported(mime_type):
            logger.error(
                "parser_not_registered",
                mime_type=mime_type,
                suggestion="Check if parsers are properly registered in app/parsers/__init__.py"
            )
            raise UnsupportedFileTypeError(mime_type)
        
        # 4. 保存文件到本地
        file_path = await self._save_file(file_content, filename, mime_type)
        
        # 4. 创建文档记录
        doc = Document(
            filename=filename,
            file_path=str(file_path),
            file_size=file_size,
            mime_type=mime_type,
            status='processing'
        )
        
        doc_id = await self.repo.save(doc)
        
        logger.info(
            "document_uploaded",
            doc_id=str(doc_id),
            filename=filename,
            size_mb=file_size / 1024 / 1024
        )
        
        # 5. 异步处理文档（不阻塞响应）
        asyncio.create_task(self._process_document_async(doc_id))
        
        return doc_id
    
    async def _save_file(
        self, 
        content: bytes, 
        filename: str,
        mime_type: str
    ) -> Path:
        """
        保存文件到本地存储
        
        Args:
            content: 文件内容
            filename: 文件名
            mime_type: MIME 类型
            
        Returns:
            Path: 文件路径
        """
        import uuid
        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = self.storage_path / mime_type.replace('/', '_') / unique_filename
        
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        return file_path
    
    async def _process_document_async(self, doc_id: UUID):
        """
        异步处理文档（解析→分块→向量化）
        
        Args:
            doc_id: 文档 ID
        """
        try:
            # 1. 获取文档信息
            doc = await self.repo.find_by_id(doc_id)
            if not doc:
                raise DocumentNotFoundException(str(doc_id))
            
            logger.info(
                "document_processing_started",
                doc_id=str(doc_id),
                filename=doc.filename
            )
            
            # 2. 读取文件内容
            async with aiofiles.open(doc.file_path, 'rb') as f:
                file_content = await f.read()
            
            # 3. 解析文档
            parser = ParserRegistry.get_parser(doc.mime_type)
            text_content = await parser.parse(file_content)
            
            logger.info(
                "document_parsed",
                doc_id=str(doc_id),
                text_length=len(text_content)
            )
            
            # 4. 文本分块
            chunks = self.chunker.chunk_by_semantic(text_content)
            
            logger.info(
                "text_chunked",
                doc_id=str(doc_id),
                chunks_count=len(chunks)
            )
            
            # 5. 向量化并存储
            await self._vectorize_chunks(chunks, doc_id)
            
            # 6. 更新状态为 ready
            await self.repo.update_status(doc_id, 'ready', len(chunks))
            
            logger.info(
                "document_vectorized",
                doc_id=str(doc_id),
                chunks_count=len(chunks)
            )
            
        except Exception as e:
            logger.error(
                "document_processing_failed",
                doc_id=str(doc_id),
                error=str(e),
                exc_info=True
            )
            await self.repo.update_status(doc_id, 'failed')
            raise
    
    async def _vectorize_chunks(self, chunks, doc_id: UUID):
        """
        向量化文档块并存储到 Pinecone
        
        Args:
            chunks: 文本块列表
            doc_id: 文档 ID
        """
        # TODO: 实现 Pinecone 向量化存储
        # 这里暂时只保存到数据库
        for idx, chunk in enumerate(chunks):
            db_chunk = Chunk(
                document_id=doc_id,
                chunk_index=idx,
                content=chunk.content,
                token_count=chunk.token_count
            )
            await self.repo.save_chunk(db_chunk)
    
    async def get_document_list(
        self, 
        page: int = 1, 
        limit: int = 20,
        status: Optional[str] = None
    ):
        """
        获取文档列表
        
        Args:
            page: 页码
            limit: 每页数量
            status: 状态筛选
            
        Returns:
            tuple: (文档列表，总数)
        """
        return await self.repo.find_all(page, limit, status)
    
    async def delete_document(self, doc_id: UUID) -> bool:
        """
        删除文档
        
        Args:
            doc_id: 文档 ID
            
        Returns:
            bool: 是否删除成功
        """
        # TODO: 同时删除 Pinecone 中的向量
        return await self.repo.delete(doc_id)
