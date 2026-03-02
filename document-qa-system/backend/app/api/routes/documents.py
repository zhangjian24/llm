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
        # 请求接收阶段 - INFO级别
        logger.info(f"[DOCUMENT_UPLOAD] 收到文档上传请求 - 文件名: {file.filename}, 内容类型: {file.content_type}")
        
        # 数据验证阶段 - DEBUG级别
        logger.debug(f"[DOCUMENT_UPLOAD] 开始数据验证 - 文件大小: {file.size if hasattr(file, 'size') else 'unknown'} bytes")
        
        # 验证文件类型
        if not file.content_type or not file.content_type.startswith(('text/', 'application/pdf', 'application/msword')):
            logger.warning(f"[DOCUMENT_UPLOAD] 数据验证失败 - 不支持的文件类型: {file.content_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的文件类型"
            )
        
        logger.debug(f"[DOCUMENT_UPLOAD] 文件类型验证通过: {file.content_type}")
        
        # 生成文档ID
        doc_id = str(uuid.uuid4())
        logger.debug(f"[DOCUMENT_UPLOAD] 生成文档ID: {doc_id}")
        
        # 读取文件内容
        logger.debug(f"[DOCUMENT_UPLOAD] 开始读取文件内容")
        content = await file.read()
        content_text = content.decode('utf-8', errors='ignore')
        logger.debug(f"[DOCUMENT_UPLOAD] 文件内容读取完成 - 大小: {len(content)} bytes, 解码后长度: {len(content_text)} 字符")
        
        # 创建文档元数据
        metadata = DocumentMetadata(
            doc_id=doc_id,
            filename=file.filename,
            file_size=len(content),
            content_type=file.content_type
        )
        
        logger.debug(f"[DOCUMENT_UPLOAD] 文档元数据创建完成 - 元数据: {{'doc_id': '{doc_id}', 'filename': '{file.filename}', 'file_size': {len(content)}}}")
        
        # 业务逻辑处理阶段 - INFO级别
        logger.info(f"[DOCUMENT_UPLOAD] 开始文档处理流程 - 文档ID: {doc_id}")
        result = await rag_service.process_document(content_text, metadata)
        
        # 响应返回阶段 - INFO级别
        if result["success"]:
            logger.info(f"[DOCUMENT_UPLOAD] 文档上传成功 - 文档ID: {doc_id}, 文件名: {file.filename}, 处理时间: {result.get('processing_time', 0):.2f}s, 分块数量: {result.get('chunk_count', 0)}")
            return DocumentUploadResponse(
                doc_id=doc_id,
                filename=file.filename,
                status="success",
                message=result["message"]
            )
        else:
            logger.error(f"[DOCUMENT_UPLOAD] 文档处理失败 - 文档ID: {doc_id}, 错误信息: {result['message']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
            
    except HTTPException as he:
        # 异常处理 - ERROR级别
        logger.error(f"[DOCUMENT_UPLOAD] HTTP异常 - 状态码: {he.status_code}, 详情: {he.detail}")
        raise
    except Exception as e:
        # 异常处理 - ERROR级别
        logger.error(f"[DOCUMENT_UPLOAD] 文档上传失败 - 错误类型: {type(e).__name__}, 错误信息: {str(e)}", exc_info=True)
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
        # 请求接收阶段 - INFO级别
        logger.info(f"[DOCUMENT_LIST] 收到获取文档列表请求")
        
        # 业务逻辑处理阶段 - DEBUG级别
        logger.debug(f"[DOCUMENT_LIST] 开始获取文档列表")
        documents = await rag_service.get_document_list()
        
        # 响应返回阶段 - INFO级别
        logger.info(f"[DOCUMENT_LIST] 文档列表获取完成 - 文档总数: {len(documents)}")
        
        return DocumentListResponse(
            documents=documents,
            total_count=len(documents)
        )
        
    except Exception as e:
        # 异常处理 - ERROR级别
        logger.error(f"[DOCUMENT_LIST] 获取文档列表失败 - 错误类型: {type(e).__name__}, 错误信息: {str(e)}", exc_info=True)
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
        # 请求接收阶段 - INFO级别
        logger.info(f"[DOCUMENT_DELETE] 收到删除文档请求 - 文档ID: {doc_id}")
        
        # 业务逻辑处理阶段 - DEBUG级别
        logger.debug(f"[DOCUMENT_DELETE] 开始删除文档流程 - 文档ID: {doc_id}")
        success = await rag_service.delete_document(doc_id)
        
        # 响应返回阶段 - INFO级别
        if success:
            logger.info(f"[DOCUMENT_DELETE] 文档删除成功 - 文档ID: {doc_id}")
            return {"message": f"文档 {doc_id} 删除成功"}
        else:
            logger.warning(f"[DOCUMENT_DELETE] 文档删除失败 - 文档ID: {doc_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"文档 {doc_id} 删除失败或不存在"
            )
            
    except HTTPException as he:
        # 异常处理 - ERROR级别
        logger.error(f"[DOCUMENT_DELETE] HTTP异常 - 状态码: {he.status_code}, 详情: {he.detail}")
        raise
    except Exception as e:
        # 异常处理 - ERROR级别
        logger.error(f"[DOCUMENT_DELETE] 删除文档失败 - 文档ID: {doc_id}, 错误类型: {type(e).__name__}, 错误信息: {str(e)}", exc_info=True)
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
        # 请求接收阶段 - INFO级别
        logger.info(f"[DOCUMENT_INFO] 收到获取文档信息请求 - 文档ID: {doc_id}")
        
        # 业务逻辑处理阶段 - DEBUG级别
        logger.debug(f"[DOCUMENT_INFO] 开始获取文档信息 - 文档ID: {doc_id}")
        
        # 这里需要实现具体的文档信息查询逻辑
        # 暂时返回模拟数据
        documents = await rag_service.get_document_list()
        doc_info = next((doc for doc in documents if doc.doc_id == doc_id), None)
        
        # 响应返回阶段 - INFO级别
        if doc_info:
            logger.info(f"[DOCUMENT_INFO] 文档信息获取成功 - 文档ID: {doc_id}, 文件名: {doc_info.filename}")
            return doc_info
        else:
            logger.warning(f"[DOCUMENT_INFO] 文档不存在 - 文档ID: {doc_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"文档 {doc_id} 不存在"
            )
            
    except HTTPException as he:
        # 异常处理 - ERROR级别
        logger.error(f"[DOCUMENT_INFO] HTTP异常 - 状态码: {he.status_code}, 详情: {he.detail}")
        raise
    except Exception as e:
        # 异常处理 - ERROR级别
        logger.error(f"[DOCUMENT_INFO] 获取文档信息失败 - 文档ID: {doc_id}, 错误类型: {type(e).__name__}, 错误信息: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文档信息失败: {str(e)}"
        )