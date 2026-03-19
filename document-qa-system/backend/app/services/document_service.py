"""
文档服务层
负责文档上传、解析、分块、向量化的编排
"""
import asyncio
import hashlib
from uuid import UUID
from typing import Optional, List
from app.repositories.document_repository import DocumentRepository
from app.parsers.base_parser import ParserRegistry
from app.chunkers.semantic_chunker import TextChunker
from app.services.embedding_service import EmbeddingService
from app.services.vector_service_adapter import create_vector_service
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
        # 设置大文件阈值（10MB）
        self.large_file_threshold = 10 * 1024 * 1024  # 10MB

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

        # 4. 计算文件内容哈希用于去重检测
        content_hash = hashlib.sha256(file_content).hexdigest()

        # 4. 检查是否已存在相同内容的文档
        existing_doc = await self.repo.find_by_content_hash(content_hash)
        if existing_doc:
            logger.info(
                "duplicate_document_detected",
                doc_id=str(existing_doc.id),
                filename=filename,
                content_hash=content_hash
            )
            return existing_doc.id

        # 5. 创建文档记录
        doc = Document(
            filename=filename,
            file_content=file_content if file_size <= self.large_file_threshold else None,
            content_hash=content_hash,
            file_size=file_size,
            mime_type=mime_type,
            status='processing'
        )

        doc_id = await self.repo.save(doc)

        # 如果是大文件，先处理分块存储
        if file_size > self.large_file_threshold:
            logger.info(
                "large_file_detected",
                doc_id=str(doc_id),
                filename=filename,
                size_mb=file_size / 1024 / 1024
            )
            # 异步处理大文件分块
            asyncio.create_task(
                self._handle_large_file_async(doc_id, file_content))

        logger.info(
            "document_uploaded",
            doc_id=str(doc_id),
            filename=filename,
            size_mb=file_size / 1024 / 1024,
            is_large_file=(file_size > self.large_file_threshold)
        )

        # 5. 异步处理文档（不阻塞响应）
        # 注意：不能直接传递 self.repo，因为它是当前请求的 session
        # 需要在异步任务中创建新的 session
        asyncio.create_task(self._process_document_async(doc_id))

        return doc_id

    async def _handle_large_file(self, doc_id: UUID, file_content: bytes) -> bool:
        """
        处理大文件分块存储

        Args:
            doc_id: 文档ID
            file_content: 文件二进制内容

        Returns:
            bool: 是否处理成功
        """
        try:
            # 将大文件分割成块（每块5MB）
            chunk_size = 5 * 1024 * 1024  # 5MB
            chunks = []

            for i in range(0, len(file_content), chunk_size):
                chunk_data = file_content[i:i + chunk_size]
                chunks.append(chunk_data)

            # 保存分块到数据库
            success = await self.repo.save_large_document_chunks(
                doc_id, chunks, len(chunks)
            )

            if success:
                logger.info(
                    "large_file_chunked",
                    doc_id=str(doc_id),
                    chunk_count=len(chunks),
                    total_size=len(file_content)
                )

            return success

        except Exception as e:
            logger.error(
                "large_file_handling_failed",
                doc_id=str(doc_id),
                error=str(e)
            )
            return False

    async def _process_document_async(self, doc_id: UUID):
        """
        异步处理文档（解析→分块→向量化）

        Args:
            doc_id: 文档 ID
        """
        # ✅ 创建新的数据库会话用于异步任务
        from app.core.database import get_db_session
        from app.repositories.document_repository import DocumentRepository

        async for session in get_db_session():
            try:
                repo = DocumentRepository(session)

                # 1. 获取文档信息
                doc = await repo.find_by_id(doc_id)
                if not doc:
                    raise DocumentNotFoundException(str(doc_id))

                logger.info(
                    "document_processing_started",
                    doc_id=str(doc_id),
                    filename=doc.filename
                )

                # 2. 获取文件内容
                file_content = await self.repo.get_document_content(doc_id)
                if file_content is None:
                    # 如果是大文件分块存储，需要合并内容
                    logger.warning(
                        "document_content_not_found",
                        doc_id=str(doc_id),
                        suggestion="可能是大文件分块存储，需要实现合并逻辑"
                    )
                    raise DocumentNotFoundException(f"文档内容未找到: {doc_id}")

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
                logger.info(
                    "vectorizing_chunks",
                    doc_id=str(doc_id),
                    chunks_count=len(chunks)
                )
                await self._vectorize_chunks(repo, chunks, doc_id, doc.filename)

                # 6. 更新状态为 ready
                logger.info(
                    "updating_status_to_ready",
                    doc_id=str(doc_id)
                )
                await repo.update_status(doc_id, 'ready', len(chunks))

                # 7. 更新文档内容和哈希（如果是小文件且内容为空）
                if doc.file_content is None and file_content and len(file_content) <= self.large_file_threshold:
                    content_hash = hashlib.sha256(file_content).hexdigest()
                    await repo.update_document_content(doc_id, file_content, content_hash)

                # ✅ 提交事务到数据库
                await session.commit()

                # 📢 发送 WebSocket 通知
                from app.websocket_manager import manager
                await manager.send_document_update(
                    doc_id=str(doc_id),
                    status='ready',
                    chunks_count=len(chunks),
                    filename=doc.filename
                )

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
                # 失败时也要提交状态更新
                try:
                    await repo.update_status(doc_id, 'failed')
                    await session.commit()

                    # 📢 发送失败通知
                    from app.websocket_manager import manager
                    await manager.send_document_update(
                        doc_id=str(doc_id),
                        status='failed',
                        filename=doc.filename if 'doc' in locals() else None
                    )
                except Exception as commit_error:
                    logger.error(
                        "failed_to_commit_failure_status",
                        doc_id=str(doc_id),
                        error=commit_error
                    )
                raise
            finally:
                await session.close()

    async def _handle_large_file_async(self, doc_id: UUID, file_content: bytes):
        """
        异步处理大文件分块存储

        Args:
            doc_id: 文档ID
            file_content: 文件二进制内容
        """
        from app.core.database import get_db_session
        from app.repositories.document_repository import DocumentRepository

        async for session in get_db_session():
            try:
                repo = DocumentRepository(session)

                success = await self._handle_large_file(doc_id, file_content)
                if success:
                    # 更新文档状态为已分块
                    await repo.update_status(doc_id, 'chunked')
                    await session.commit()

                    logger.info(
                        "large_file_processed",
                        doc_id=str(doc_id)
                    )

            except Exception as e:
                logger.error(
                    "large_file_async_processing_failed",
                    doc_id=str(doc_id),
                    error=str(e)
                )
            finally:
                await session.close()

    async def _vectorize_chunks(self, repo: DocumentRepository, chunks, doc_id: UUID, filename: str = ""):
        """
        向量化文档块并存储到 Pinecone 和数据库

        Args:
            repo: 文档仓库
            chunks: 文本块列表
            doc_id: 文档 ID
            filename: 文件名（用于metadata）
        """
        logger.info(
            "vectorize_chunks_started",
            doc_id=str(doc_id),
            chunks_count=len(chunks),
            filename=filename
        )

        # 1. 首先保存到数据库
        for idx, chunk in enumerate(chunks):
            db_chunk = Chunk(
                document_id=doc_id,
                chunk_index=idx,
                content=chunk.content,
                token_count=chunk.token_count
            )
            await repo.save_chunk(db_chunk)

        logger.info(
            "chunks_saved_to_database",
            doc_id=str(doc_id),
            chunks_count=len(chunks)
        )

        # 2. 向量化并存储到向量数据库
        try:
            vector_svc = create_vector_service(
                {'vector_store_type': 'postgresql'})
            embedding_svc = EmbeddingService()

            # 准备向量数据
            vectors = []
            for idx, chunk in enumerate(chunks):
                # 生成向量ID
                vector_id = f"{str(doc_id)}_chunk_{idx}"

                # 获取文本向量
                try:
                    vector_values = await embedding_svc.embed_text(chunk.content)

                    # 准备metadata
                    metadata = {
                        "document_id": str(doc_id),
                        "chunk_index": idx,
                        "content": chunk.content[:500],  # 只存储前500字符
                        "filename": filename,
                        "token_count": chunk.token_count
                    }

                    vectors.append({
                        "id": vector_id,
                        "values": vector_values,
                        "metadata": metadata
                    })

                except Exception as embed_error:
                    logger.error(
                        "embedding_failed_for_chunk",
                        doc_id=str(doc_id),
                        chunk_index=idx,
                        error=str(embed_error)
                    )
                    # 继续处理其他chunks，不中断整个流程
                    continue

            if vectors:
                # 批量upsert到向量数据库
                await vector_svc.upsert_vectors(
                    vectors=vectors
                )

                logger.info(
                    "vectors_upserted_to_vector_db",
                    doc_id=str(doc_id),
                    vectors_count=len(vectors)
                )
            else:
                logger.warning(
                    "no_vectors_to_upsert",
                    doc_id=str(doc_id),
                    reason="embedding_failed_for_all_chunks"
                )

        except Exception as e:
            logger.error(
                "pinecone_upsert_failed",
                doc_id=str(doc_id),
                error=str(e),
                exc_info=True
            )
            # 注意：这里不抛出异常，因为数据库已经保存成功
            # 可以选择重试或将失败信息记录到数据库

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
