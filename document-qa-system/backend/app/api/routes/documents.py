"""
文档管理API路由
处理文档上传、列表查询、删除等操作
"""

import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
import tempfile
import os

from ...models.schemas import (
    DocumentUploadResponse, 
    DocumentListResponse, 
    DocumentMetadata,
    ErrorResponse
)
from ...services.rag_service import RAGService
from ...core.logging import logger
from ...api.deps import get_pinecone_service, get_llm_service

router = APIRouter(prefix="/documents", tags=["documents"])


def get_rag_service(
    pinecone_dep = Depends(get_pinecone_service),
    llm_dep = Depends(get_llm_service)
):
    """获取RAG服务依赖"""
    from ...services.rag_service import RAGService
    return RAGService(pinecone_dep, llm_dep)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    上传文档
    
    Args:
        file: 上传的文件
        rag_service: RAG服务实例
        
    Returns:
        上传结果
    """
    try:
        logger.info(f"收到文档上传请求: {file.filename}")
        
        # 验证文件类型
        if not file.content_type or not file.content_type.startswith(('text/', 'application/pdf', 'application/msword')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的文件类型"
            )
        
        # 生成文档ID
        doc_id = str(uuid.uuid4())
        
        # 读取文件内容
        content = await file.read()
        content_text = content.decode('utf-8', errors='ignore')
        
        # 创建文档元数据
        metadata = DocumentMetadata(
            doc_id=doc_id,
            filename=file.filename,
            file_size=len(content),
            content_type=file.content_type
        )
        
        # 处理文档
        result = await rag_service.process_document(content_text, metadata)
        
        if result["success"]:
            return DocumentUploadResponse(
                doc_id=doc_id,
                filename=file.filename,
                status="success",
                message=result["message"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文档上传失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文档上传失败: {str(e)}"
        )


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    获取文档列表
    
    Args:
        rag_service: RAG服务实例
        
    Returns:
        文档列表
    """
    try:
        logger.info("获取文档列表")
        
        documents = await rag_service.get_document_list()
        
        return DocumentListResponse(
            documents=documents,
            total_count=len(documents)
        )
        
    except Exception as e:
        logger.error(f"获取文档列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文档列表失败: {str(e)}"
        )


@router.delete("/{doc_id}", response_model=dict)
async def delete_document(
    doc_id: str,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    删除文档
    
    Args:
        doc_id: 文档ID
        rag_service: RAG服务实例
        
    Returns:
        删除结果
    """
    try:
        logger.info(f"删除文档: {doc_id}")
        
        success = await rag_service.delete_document(doc_id)
        
        if success:
            return {"message": f"文档 {doc_id} 删除成功"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"文档 {doc_id} 删除失败或不存在"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除文档失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文档失败: {str(e)}"
        )


@router.get("/{doc_id}/info", response_model=DocumentMetadata)
async def get_document_info(
    doc_id: str,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    获取文档详细信息
    
    Args:
        doc_id: 文档ID
        rag_service: RAG服务实例
        
    Returns:
        文档元数据
    """
    try:
        logger.info(f"获取文档信息: {doc_id}")
        
        # 这里需要实现具体的文档信息查询逻辑
        # 暂时返回模拟数据
        documents = await rag_service.get_document_list()
        doc_info = next((doc for doc in documents if doc.doc_id == doc_id), None)
        
        if doc_info:
            return doc_info
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"文档 {doc_id} 不存在"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文档信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文档信息失败: {str(e)}"
        )