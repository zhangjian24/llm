"""
文档管理 API 路由
"""
import asyncio
from fastapi import APIRouter, Depends, Query, HTTPException, File, BackgroundTasks
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
    background_tasks: BackgroundTasks = None
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

        # 1. 上传文档（此时不启动异步任务）
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
            status="waiting_for_commit"
        )

        # 2. 添加到后台任务队列，事务提交后执行
        if background_tasks:
            background_tasks.add_task(service._process_document_async, doc_id)
            logger.info(
                "background_task_added",
                doc_id=str(doc_id),
                note="Will execute after response is sent"
            )
        
        # 3. 立即返回响应
        return SuccessResponse(
            data=DocumentDTO(
                id=doc_id,
                filename=filename,
                file_size=file_size,
                mime_type=mime_type,
                status="processing"
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

    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
