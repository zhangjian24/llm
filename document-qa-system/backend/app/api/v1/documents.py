"""
文档管理 API 路由
"""
import asyncio
from fastapi import APIRouter, Depends, Query, HTTPException, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from app.core.database import get_db_session
from app.repositories.document_repository import DocumentRepository
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService
from app.schemas.document import DocumentDTO, DocumentListDTO
from app.schemas.common import PageDTO, SuccessResponse
import structlog

logger = structlog.get_logger()

router = APIRouter()


# 依赖注入
def get_document_service(session: AsyncSession = Depends(get_db_session)) -> DocumentService:
    """获取 DocumentService 实例"""
    repo = DocumentRepository(session)
    embedding_svc = EmbeddingService()
    return DocumentService(repo, embedding_svc)


@router.post("/upload")
async def upload_document(
    file: bytes = File(..., description="上传的文件"),
    mime_type: str = Query(..., description="文件 MIME 类型"),
    filename: str = Query(..., description="文件名"),
    service: DocumentService = Depends(get_document_service),
    session: AsyncSession = Depends(get_db_session)  # 获取 session 用于提交事务
):
    """
    上传文档

    - **file**: 文件二进制内容
    - **mime_type**: 文件 MIME 类型
    - **filename**: 文件名

    返回:
    - 文档 ID 和处理状态
    """
    try:
        file_size = len(file)

        # 1. 上传文档（创建文档记录）
        doc_id = await service.upload_document(
            file_content=file,
            filename=filename,
            mime_type=mime_type,
            file_size=file_size
        )

        logger.info(
            "document_uploaded_api",
            doc_id=str(doc_id),
            filename=filename,
            status="processing"
        )

        # 2. 显式提交事务，确保文档记录已写入数据库
        await session.commit()
        
        logger.info(
            "transaction_committed",
            doc_id=str(doc_id)
        )

        # 3. 事务提交后再启动异步处理任务
        logger.info(
            "starting_async_processing",
            doc_id=str(doc_id),
            after_commit=True
        )
        asyncio.create_task(service._process_document_async(doc_id))

        return SuccessResponse(
            data=DocumentDTO(
                id=doc_id,
                filename=filename,
                file_size=file_size,
                mime_type=mime_type,
                status="processing",
                created_at=None,
                updated_at=None
            )
        )

    except Exception as e:
        logger.error("upload_failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=SuccessResponse[PageDTO[DocumentListDTO]])
async def get_documents(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="状态筛选"),
    service: DocumentService = Depends(get_document_service)
):
    """
    获取文档列表

    - **page**: 页码（从 1 开始）
    - **limit**: 每页数量
    - **status**: 状态筛选（processing/ready/failed）
    """
    try:
        docs, total = await service.get_document_list(
            page=page,
            limit=limit,
            status=status
        )

        total_pages = (total + limit - 1) // limit

        items = [
            DocumentListDTO(
                id=doc.id,
                filename=doc.filename,
                file_size=doc.file_size,
                mime_type=doc.mime_type,
                status=doc.status,
                chunks_count=doc.chunks_count,
                created_at=doc.created_at,
                updated_at=doc.updated_at
            )
            for doc in docs
        ]

        return SuccessResponse(
            data=PageDTO(
                total=total,
                items=items,
                page=page,
                limit=limit,
                total_pages=total_pages
            )
        )

    except Exception as e:
        logger.error("get_list_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{doc_id}", status_code=204)
async def delete_document(
    doc_id: UUID,
    service: DocumentService = Depends(get_document_service)
):
    """
    删除文档

    - **doc_id**: 文档 ID
    """
    try:
        success = await service.delete_document(doc_id)

        if not success:
            raise HTTPException(status_code=404, detail="文档不存在")

        logger.info("document_deleted", doc_id=str(doc_id))

    except ValueError as e:
        # 状态非法（处理中禁止删除）
        logger.warning(
            "delete_invalid_status",
            doc_id=str(doc_id),
            error=str(e)
        )
        raise HTTPException(status_code=400, detail=str(e))

    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{doc_id}/reprocess")
async def reprocess_document(
    doc_id: UUID,
    service: DocumentService = Depends(get_document_service)
):
    """
    重新处理文档

    仅允许状态为 "failed" 或 "ready" 的文档重新处理。
    重新处理会清空旧的 chunk 数据和向量，然后重新启动异步处理流程。

    - **doc_id**: 文档 ID

    返回:
    - 成功消息
    """
    try:
        # 尝试重新处理文档
        success = await service.reprocess_document(doc_id)

        if not success:
            raise HTTPException(status_code=500, detail="重新处理失败")

        logger.info(
            "document_reprocessing_requested",
            doc_id=str(doc_id),
            message="已启动重新处理流程"
        )

        return SuccessResponse(message="已开始重新处理")

    except ValueError as e:
        # 状态非法
        logger.warning(
            "reprocess_invalid_status",
            doc_id=str(doc_id),
            error=str(e)
        )
        raise HTTPException(status_code=400, detail=str(e))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("reprocess_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
