from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
import asyncio
from typing import List, Optional
from datetime import datetime

from app.models.schemas import (
    DocumentUploadRequest, DocumentUploadResponse, 
    DocumentListResponse, DocumentInfo
)
from app.services.document_processor import document_processor
from app.services.vector_store import vector_store
from app.core.logging_config import logger
from app.core.exceptions import DocumentProcessingError, VectorStoreError

router = APIRouter()

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """上传并处理文档"""
    try:
        # 验证文件大小
        if file.size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="文件大小超过限制(10MB)")
        
        # 验证文件类型
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        extension = "." + file.filename.split(".")[-1].lower()
        if extension not in [ext.lower() for ext in [".pdf", ".txt", ".docx", ".doc", ".html", ".htm"]]:
            raise HTTPException(status_code=400, detail=f"不支持的文件格式: {extension}")
        
        # 读取文件内容
        file_content = await file.read()
        
        # 保存文件
        file_path = document_processor.save_uploaded_file(file_content, file.filename)
        
        # 异步处理文档
        processing_result = await document_processor.process_document(file_path, file.filename)
        
        # 存储到向量数据库
        metadata = {
            "filename": file.filename,
            "file_size": len(file_content),
            "upload_time": datetime.now().isoformat()
        }
        
        chunk_ids = await vector_store.store_document_chunks(
            document_id=processing_result['document_id'],
            chunks=processing_result['chunks'],
            metadata=metadata
        )
        
        return DocumentUploadResponse(
            document_id=processing_result['document_id'],
            filename=file.filename,
            status="success",
            message=f"文档上传并处理成功，共生成 {len(chunk_ids)} 个文本块"
        )
        
    except DocumentProcessingError as e:
        logger.error(f"文档处理错误: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except VectorStoreError as e:
        logger.error(f"向量存储错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"上传文档时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@router.get("/list", response_model=DocumentListResponse)
async def list_documents():
    """列出所有已上传的文档"""
    try:
        documents_info = await vector_store.list_documents()
        
        documents = []
        for doc_info in documents_info:
            # 获取实际文件信息
            chunk_count = await vector_store.get_document_chunk_count(doc_info["document_id"])
            
            documents.append(DocumentInfo(
                document_id=doc_info["document_id"],
                filename=doc_info["filename"],
                upload_time=datetime.fromisoformat(doc_info["created_at"]) if doc_info["created_at"] else datetime.now(),
                status="processed",
                size=0  # TODO: 从元数据中获取实际文件大小
            ))
        
        return DocumentListResponse(
            documents=documents,
            total=len(documents)
        )
        
    except VectorStoreError as e:
        logger.error(f"获取文档列表错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"获取文档列表时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """删除指定文档"""
    try:
        # 从向量数据库删除
        await vector_store.delete_document_chunks(document_id)
        
        # TODO: 从文件系统删除实际文件
        # 这需要在文档元数据中存储文件路径
        
        return JSONResponse(
            status_code=200,
            content={"message": f"文档 {document_id} 删除成功"}
        )
        
    except VectorStoreError as e:
        logger.error(f"删除文档错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"删除文档时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@router.get("/{document_id}/info")
async def get_document_info(document_id: str):
    """获取文档详细信息"""
    try:
        chunk_count = await vector_store.get_document_chunk_count(document_id)
        
        if chunk_count == 0:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # TODO: 返回更详细的文档信息
        return JSONResponse(
            status_code=200,
            content={
                "document_id": document_id,
                "chunk_count": chunk_count,
                "status": "processed"
            }
        )
        
    except VectorStoreError as e:
        logger.error(f"获取文档信息错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"获取文档信息时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")