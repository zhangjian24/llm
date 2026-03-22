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
from app.models.document_chunk import DocumentChunk
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

        # 📝 重要说明：
        # 这里不再自动启动异步处理任务，因为当前事务还未提交
        # 异步任务需要由调用者在事务提交后手动启动
        # 参考：app/api/v1/documents.py 中的 upload_document 端点

        # 5. 返回文档 ID，由调用者负责在事务提交后启动异步任务
        logger.info(
            "document_ready_for_processing",
            doc_id=str(doc_id),
            note="Call _process_document_async(doc_id) after transaction commit"
        )

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

                # 📢 发送 WebSocket 通知：开始处理
                from app.websocket_manager import manager
                await manager.send_document_update(
                    doc_id=str(doc_id),
                    status='processing',
                    filename=doc.filename
                )

                # 2. 获取文件内容
                # 📝 关键日志：记录获取文件内容的过程
                logger.debug(
                    "fetching_document_content",
                    doc_id=str(doc_id),
                    doc_file_content_is_null=doc.file_content is None,
                    doc_file_size=doc.file_size,
                    using_repo_method="get_document_content"
                )
                                
                # 注意：这里使用新创建的 repo（异步任务中创建的）
                # 因为 self.repo 绑定的是上传时的 session，可能已关闭
                file_content = await repo.get_document_content(doc_id)
                                
                logger.info(
                    "document_content_fetched",
                    doc_id=str(doc_id),
                    content_size=len(file_content) if file_content else 0,
                    content_is_null=file_content is None
                )
                                
                if file_content is None:
                    # 如果是大文件分块存储，需要合并内容
                    logger.warning(
                        "document_content_not_found",
                        doc_id=str(doc_id),
                        suggestion="可能是大文件分块存储，需要检查 document_chunks 表",
                        doc_file_content_field=doc.file_content,
                        doc_chunk_count=doc.chunk_count
                    )
                                    
                    # 尝试从 DocumentChunk 表合并内容（针对大文件）
                    if doc.chunk_count and doc.chunk_count > 0:
                        logger.info(
                            "attempting_to_merge_large_file_chunks",
                            doc_id=str(doc_id),
                            chunk_count=doc.chunk_count
                        )
                                        
                        # 查询 document_chunks 表
                        chunks_result = await session.execute(
                            select(DocumentChunk.chunk_data)
                            .where(DocumentChunk.document_id == doc_id)
                            .order_by(DocumentChunk.chunk_index)
                        )
                        chunks = chunks_result.scalars().all()
                                        
                        if chunks:
                            file_content = b''.join(chunks)
                            logger.info(
                                "large_file_chunks_merged",
                                doc_id=str(doc_id),
                                merged_size=len(file_content),
                                chunk_count=len(chunks)
                            )
                        else:
                            logger.error(
                                "no_chunks_found_for_large_file",
                                doc_id=str(doc_id),
                                chunk_count=doc.chunk_count
                            )
                                    
                    # 如果仍然没有内容，抛出异常
                    if file_content is None:
                        logger.error(
                            "document_content_really_not_found",
                            doc_id=str(doc_id),
                            fatal=True
                        )
                        raise DocumentNotFoundException(f"文档内容未找到：{doc_id}")

                # 3. 解析文档
                logger.debug(
                    "parsing_document",
                    doc_id=str(doc_id),
                    mime_type=doc.mime_type,
                    content_size=len(file_content) if file_content else 0
                )
                
                parser = ParserRegistry.get_parser(doc.mime_type)
                text_content = await parser.parse(file_content)

                logger.info(
                    "document_parsed",
                    doc_id=str(doc_id),
                    text_length=len(text_content),
                    parser_type=type(parser).__name__
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
                await self._vectorize_chunks(repo, chunks, doc_id, doc.filename, session)

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

    async def _vectorize_chunks(self, repo: DocumentRepository, chunks, doc_id: UUID, filename: str = "", session=None):
        """
        向量化文档块并存储到 Pinecone 和数据库
    
        Args:
            repo: 文档仓库
            chunks: 文本块列表
            doc_id: 文档 ID
            filename: 文件名（用于 metadata）
            session: 数据库会话（可选，用于事务一致性）
        """
        logger.info(
            "vectorize_chunks_started",
            doc_id=str(doc_id),
            chunks_count=len(chunks),
            filename=filename
        )
    
        # 1. 首先保存到数据库
        logger.info(
            "saving_chunks_to_database",
            doc_id=str(doc_id),
            chunks_count=len(chunks)
        )
            
        # 📝 关键：创建 chunk_index 到 db_chunk_id 的映射
        chunk_id_map = {}
        
        for idx, chunk in enumerate(chunks):
            try:
                db_chunk = Chunk(
                    document_id=doc_id,
                    chunk_index=idx,
                    content=chunk.content,
                    token_count=chunk.token_count
                )
                    
                # 📝 关键日志：记录每个 chunk 的初始状态
                logger.debug(
                    "chunk_object_created",
                    doc_id=str(doc_id),
                    chunk_index=idx,
                    has_content=bool(db_chunk.content),
                    content_length=len(db_chunk.content) if db_chunk.content else 0,
                    has_metadata=db_chunk.metadata is not None,
                    has_embedding=db_chunk.embedding is not None,
                    metadata_value=db_chunk.metadata,
                    embedding_value=db_chunk.embedding
                )
                    
                await repo.save_chunk(db_chunk)
                
                # 📝 关键：保存 chunk_id 映射
                chunk_id_map[idx] = str(db_chunk.id)
                    
                # 📝 关键日志：确认保存后的状态
                logger.debug(
                    "chunk_saved_to_database",
                    doc_id=str(doc_id),
                    chunk_index=idx,
                    chunk_id=str(db_chunk.id),
                    has_metadata=db_chunk.metadata is not None,
                    has_embedding=db_chunk.embedding is not None
                )
                    
            except Exception as chunk_error:
                logger.error(
                    "chunk_save_failed",
                    doc_id=str(doc_id),
                    chunk_index=idx,
                    error=str(chunk_error),
                    error_type=type(chunk_error).__name__,
                    exc_info=True
                )
                raise
    
        logger.info(
            "chunks_saved_to_database_completed",
            doc_id=str(doc_id),
            chunks_count=len(chunks)
        )

        # 2. 向量化并存储到向量数据库
        logger.info(
            "starting_vectorization_process",
            doc_id=str(doc_id),
            chunks_count=len(chunks)
        )
                
        try:
            vector_svc = create_vector_service(
                {'vector_store_type': 'postgresql'})
            embedding_svc = EmbeddingService()
        
            # 准备向量数据
            vectors = []
            successful_embeddings = 0
            failed_embeddings = 0
                    
            for idx, chunk in enumerate(chunks):
                logger.debug(
                    "processing_chunk_for_embedding",
                    doc_id=str(doc_id),
                    chunk_index=idx,
                    content_preview=chunk.content[:50] if chunk.content else "NO_CONTENT"
                )
                        
                # 📝 关键：使用已保存的 Chunk UUID
                vector_id = chunk_id_map.get(idx)
                if not vector_id:
                    logger.error(
                        "chunk_id_not_found_in_map",
                        doc_id=str(doc_id),
                        chunk_index=idx
                    )
                    continue
        
                # 获取文本向量
                try:
                    logger.debug(
                        "calling_embedding_api",
                        doc_id=str(doc_id),
                        chunk_index=idx,
                        text_length=len(chunk.content) if chunk.content else 0
                    )
                            
                    vector_values = await embedding_svc.embed_text(chunk.content)
        
                    logger.debug(
                        "embedding_received",
                        doc_id=str(doc_id),
                        chunk_index=idx,
                        vector_dimension=len(vector_values),
                        vector_sample=vector_values[:3]
                    )
        
                    # 准备 metadata
                    metadata = {
                        "document_id": str(doc_id),
                        "chunk_index": idx,
                        "content": chunk.content[:500],  # 只存储前 500 字符
                        "filename": filename,
                        "token_count": chunk.token_count
                    }
                            
                    logger.debug(
                        "metadata_prepared",
                        doc_id=str(doc_id),
                        chunk_index=idx,
                        metadata_keys=list(metadata.keys()),
                        content_preview=metadata["content"][:50]
                    )
        
                    vectors.append({
                        "id": vector_id,
                        "values": vector_values,
                        "metadata": metadata
                    })
                            
                    successful_embeddings += 1
                    logger.debug(
                        "vector_data_prepared",
                        doc_id=str(doc_id),
                        chunk_index=idx,
                        total_vectors_so_far=len(vectors)
                    )
        
                except Exception as embed_error:
                    failed_embeddings += 1
                    logger.error(
                        "embedding_failed_for_chunk",
                        doc_id=str(doc_id),
                        chunk_index=idx,
                        error=str(embed_error),
                        error_type=type(embed_error).__name__,
                        exc_info=True
                    )
                    # 继续处理其他 chunks，不中断整个流程
                    continue
                    
            logger.info(
                "embedding_phase_completed",
                doc_id=str(doc_id),
                total_chunks=len(chunks),
                successful=successful_embeddings,
                failed=failed_embeddings,
                vectors_to_upsert=len(vectors)
            )
        
            if vectors:
                # 📝 关键日志：批量 upsert 前的最终检查
                logger.info(
                    "upsert_vectors_validation",
                    doc_id=str(doc_id),
                    vectors_count=len(vectors),
                    sample_vector={
                        "id": vectors[0]["id"],
                        "has_values": "values" in vectors[0],
                        "values_dimension": len(vectors[0].get("values", [])),
                        "has_metadata": "metadata" in vectors[0],
                        "metadata_sample": vectors[0].get("metadata", {})
                    } if vectors else None
                )
                        
                # 批量 upsert 到向量数据库
                logger.info(
                    "calling_upsert_vectors",
                    doc_id=str(doc_id),
                    vectors_count=len(vectors)
                )
                        
                await vector_svc.upsert_vectors(
                    session=session,  # ✅ 使用外部传入的 session
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
                error_type=type(e).__name__,
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
        
        处理流程:
        1. 查询文档
        2. 从向量数据库删除向量
        3. 删除数据库记录（级联删除 document_chunks）
        
        Args:
            doc_id: 文档 ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            # 1. 查询文档
            doc = await self.repo.find_by_id(doc_id)
            if not doc:
                logger.warning(
                    "document_not_found_for_deletion",
                    doc_id=str(doc_id)
                )
                return False
            
            # 1.5 检查文档状态，处理中禁止删除
            if doc.status == 'processing':
                logger.warning(
                    "document_deletion_rejected_processing",
                    doc_id=str(doc_id),
                    status=doc.status
                )
                raise ValueError("文档处理中，禁止删除")
            
            logger.info(
                "document_deletion_started",
                doc_id=str(doc_id),
                filename=doc.filename
            )
            
            # 2. 删除向量数据库中的向量
            try:
                logger.debug(
                    "deleting_vectors_from_vector_db",
                    doc_id=str(doc_id)
                )
                
                # 使用 vector_service_adapter 删除
                from app.services.vector_service_adapter import create_vector_service
                vector_svc = create_vector_service({'vector_store_type': 'postgresql'})
                
                # 使用 self.repo 的 session 进行向量删除
                await vector_svc.delete_vectors(
                    session=self.repo.session,  # 使用同一个 session
                    ids=None,
                    delete_all=False,
                    namespace=str(doc_id)
                )
                
                logger.info(
                    "vectors_deleted_successfully",
                    doc_id=str(doc_id)
                )
                
            except Exception as vector_error:
                logger.error(
                    "vector_deletion_failed",
                    doc_id=str(doc_id),
                    error=str(vector_error),
                    error_type=type(vector_error).__name__,
                    exc_info=True
                )
                # 向量删除失败不阻断整个流程，继续删除数据库记录
            
            # 3. 删除数据库记录（级联删除 document_chunks）
            logger.debug(
                "deleting_document_from_database",
                doc_id=str(doc_id)
            )
            
            # 在同一个事务中删除向量和文档记录
            success = await self.repo.delete(doc_id)
            
            # 提交事务（包含向量删除和文档删除）
            if success:
                await self.repo.session.commit()
            
            if success:
                logger.info(
                    "document_deleted_successfully",
                    doc_id=str(doc_id),
                    filename=doc.filename
                )
                
                # 📢 发送 WebSocket 通知（如果需要）
                try:
                    from app.websocket_manager import manager
                    await manager.send_document_update(
                        doc_id=str(doc_id),
                        status='deleted',
                        filename=doc.filename
                    )
                except Exception as ws_error:
                    logger.warning(
                        "websocket_notification_failed",
                        doc_id=str(doc_id),
                        error=str(ws_error)
                    )
            else:
                logger.error(
                    "database_deletion_failed",
                    doc_id=str(doc_id),
                    filename=doc.filename
                )
            
            return success
            
        except Exception as e:
            logger.error(
                "delete_document_exception",
                doc_id=str(doc_id),
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True
            )
            return False
    
    async def reprocess_document(self, doc_id: UUID) -> bool:
        """
        重新处理文档
        
        处理流程:
        1. 查询文档并验证状态
        2. 清空旧的 chunk 数据和向量
        3. 重置状态为 processing
        4. 重新启动异步处理流程
        
        Args:
            doc_id: 文档 ID
            
        Returns:
            bool: 是否成功启动重新处理流程
            
        Raises:
            DocumentNotFoundException: 文档不存在
            ValueError: 文档状态不允许重新处理
        """
        try:
            # 1. 查询文档
            doc = await self.repo.find_by_id(doc_id)
            if not doc:
                logger.warning(
                    "document_not_found_for_reprocessing",
                    doc_id=str(doc_id)
                )
                raise DocumentNotFoundException(f"文档不存在：{doc_id}")
            
            logger.info(
                "document_reprocessing_started",
                doc_id=str(doc_id),
                filename=doc.filename,
                current_status=doc.status
            )
            
            # 2. 验证状态（仅允许 failed/ready 状态的文档重新处理）
            if doc.status not in ['failed', 'ready']:
                logger.warning(
                    "invalid_status_for_reprocessing",
                    doc_id=str(doc_id),
                    current_status=doc.status,
                    allowed_statuses=['failed', 'ready']
                )
                raise ValueError(
                    f"当前状态 ({doc.status}) 不允许重新处理，仅支持 failed 或 ready 状态"
                )
            
            # 3. 清空旧的 chunk 数据
            logger.debug(
                "clearing_old_chunks",
                doc_id=str(doc_id)
            )
            
            chunks_cleared = await self._clear_old_chunks(doc_id)
            if not chunks_cleared:
                logger.warning(
                    "clear_chunks_failed_but_continuing",
                    doc_id=str(doc_id)
                )
            
            # 4. 删除向量数据库中的向量
            try:
                logger.debug(
                    "deleting_vectors_for_reprocessing",
                    doc_id=str(doc_id)
                )
                
                from app.services.vector_service_adapter import create_vector_service
                from app.core.database import AsyncSessionLocal
                vector_svc = create_vector_service({'vector_store_type': 'postgresql'})
                
                async with AsyncSessionLocal() as session:
                    await vector_svc.delete_vectors(
                        session=session,
                        ids=None,
                        delete_all=False,
                        namespace=str(doc_id)
                    )
                    await session.commit()
                
                logger.info(
                    "vectors_deleted_for_reprocessing",
                    doc_id=str(doc_id)
                )
                
            except Exception as vector_error:
                logger.error(
                    "vector_deletion_failed_for_reprocessing",
                    doc_id=str(doc_id),
                    error=str(vector_error),
                    error_type=type(vector_error).__name__,
                    exc_info=True
                )
                # 向量删除失败不阻断整个流程
            
            # 5. 重置状态为 processing 并提交
            logger.debug(
                "resetting_status_to_processing",
                doc_id=str(doc_id)
            )
            
            await self.repo.update_status(doc_id, 'processing', chunks_count=None)
            
            # 提交状态更新到数据库
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as commit_session:
                try:
                    # 使用新的 session 重新获取文档并更新
                    from app.repositories.document_repository import DocumentRepository
                    repo = DocumentRepository(commit_session)
                    doc_to_update = await repo.find_by_id(doc_id)
                    if doc_to_update:
                        doc_to_update.status = 'processing'
                        doc_to_update.chunks_count = None
                        await commit_session.commit()
                        
                        logger.info(
                            "status_reset_committed",
                            doc_id=str(doc_id)
                        )
                        
                        # 6. 启动异步处理任务
                        logger.info(
                            "starting_async_reprocessing",
                            doc_id=str(doc_id),
                            after_commit=True
                        )
                        asyncio.create_task(self._process_document_async(doc_id))
                        
                        # 发送 WebSocket 通知
                        try:
                            from app.websocket_manager import manager
                            await manager.send_document_update(
                                doc_id=str(doc_id),
                                status='processing',
                                filename=doc.filename
                            )
                        except Exception as ws_error:
                            logger.warning(
                                "websocket_notification_failed",
                                doc_id=str(doc_id),
                                error=str(ws_error)
                            )
                        
                        return True
                    else:
                        logger.error(
                            "document_not_found_when_resetting",
                            doc_id=str(doc_id)
                        )
                        return False
                        
                except Exception as commit_error:
                    logger.error(
                        "commit_failed_for_reprocessing",
                        doc_id=str(doc_id),
                        error=str(commit_error),
                        exc_info=True
                    )
                    await commit_session.rollback()
                    raise
        
        except DocumentNotFoundException:
            # 重新抛出文档未找到异常
            raise
        except ValueError:
            # 重新抛出状态非法异常
            raise
        except Exception as e:
            logger.error(
                "reprocess_document_exception",
                doc_id=str(doc_id),
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True
            )
            return False
    
    async def _clear_old_chunks(self, doc_id: UUID) -> bool:
        """
        清空旧的 chunk 记录
        
        Args:
            doc_id: 文档 ID
            
        Returns:
            bool: 是否清空成功
        """
        try:
            logger.debug(
                "clearing_old_chunks",
                doc_id=str(doc_id)
            )
            
            # 使用 Repository 层方法删除 chunks
            success = await self.repo.delete_chunks_by_document(doc_id)
            
            if success:
                logger.info(
                    "old_chunks_cleared",
                    doc_id=str(doc_id)
                )
            else:
                logger.warning(
                    "clear_old_chunks_failed",
                    doc_id=str(doc_id)
                )
            
            return success
            
        except Exception as e:
            logger.error(
                "clear_old_chunks_exception",
                doc_id=str(doc_id),
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True
            )
            return False
