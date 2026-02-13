from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List
import uuid
from datetime import datetime
from app.models.schemas import DocumentResponse, DocumentStatus
from app.services.document_processor import document_processor
from app.services.embedding import encoder
from app.services.vector_store import vector_store
from app.utils.helpers import generate_document_id
from app.core.exceptions import DocumentProcessingException, VectorStoreException
from app.core.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)

# 内存中的文档存储（实际项目中应该使用数据库）
documents_db = {}

async def process_document_background(document_id: str, file_content: bytes, 
                                    filename: str, content_type: str):
    """后台处理文档"""
    try:
        logger.info(f"开始后台处理文档: {document_id}")
        
        # 更新文档状态为处理中
        documents_db[document_id]['status'] = DocumentStatus.PROCESSING
        
        # 处理文档
        processed_data = document_processor.process_document(
            file_content, filename, content_type
        )
        
        # 生成向量嵌入
        texts = [chunk['text'] for chunk in processed_data['chunks']]
        encoded_chunks = encoder.batch_encode_with_ids(texts)
        
        # 准备向量数据
        vectors = []
        for chunk_data, encoded_chunk in zip(processed_data['chunks'], encoded_chunks):
            vector_data = {
                'id': encoded_chunk['id'],
                'values': encoded_chunk['embedding'],
                'metadata': {
                    'document_id': document_id,
                    'filename': filename,
                    'chunk_index': chunk_data['chunk_index'],
                    'total_chunks': chunk_data['total_chunks'],
                    'text': chunk_data['text']
                }
            }
            vectors.append(vector_data)
        
        # 存储到向量数据库
        vector_store.upsert_vectors(vectors)
        
        # 更新文档状态为已处理
        documents_db[document_id].update({
            'status': DocumentStatus.PROCESSED,
            'processed_at': datetime.now(),
            'chunk_count': len(processed_data['chunks']),
            'total_tokens': processed_data['total_tokens']
        })
        
        logger.info(f"文档处理完成: {document_id}")
        
    except Exception as e:
        logger.error(f"文档处理失败 {document_id}: {str(e)}")
        documents_db[document_id]['status'] = DocumentStatus.FAILED
        documents_db[document_id]['error_message'] = str(e)

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """上传文档"""
    try:
        # 验证文件类型
        allowed_types = [
            'application/pdf',
            'text/plain',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword'
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file.content_type}"
            )
        
        # 读取文件内容
        file_content = await file.read()
        
        # 生成文档ID
        document_id = generate_document_id(file.filename, file_content)
        
        # 检查文档是否已存在
        if document_id in documents_db:
            return DocumentResponse(**documents_db[document_id])
        
        # 创建文档记录
        document_record = {
            'id': document_id,
            'filename': file.filename,
            'content_type': file.content_type,
            'size': len(file_content),
            'status': DocumentStatus.UPLOADED,
            'created_at': datetime.now(),
            'processed_at': None
        }
        
        documents_db[document_id] = document_record
        
        # 添加后台处理任务
        background_tasks.add_task(
            process_document_background,
            document_id,
            file_content,
            file.filename,
            file.content_type
        )
        
        logger.info(f"文档上传成功: {document_id}")
        return DocumentResponse(**document_record)
        
    except Exception as e:
        logger.error(f"文档上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """获取文档信息"""
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="文档未找到")
    
    return DocumentResponse(**documents_db[document_id])

@router.get("/", response_model=List[DocumentResponse])
async def list_documents():
    """列出所有文档"""
    documents = [
        DocumentResponse(**doc) for doc in documents_db.values()
    ]
    return sorted(documents, key=lambda x: x.created_at, reverse=True)

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """删除文档"""
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="文档未找到")
    
    try:
        # 从向量数据库删除相关向量
        # 这里需要实现根据document_id查找并删除相关向量的逻辑
        pass
        
        # 删除文档记录
        del documents_db[document_id]
        
        logger.info(f"文档删除成功: {document_id}")
        return {"message": "文档删除成功"}
        
    except Exception as e:
        logger.error(f"文档删除失败 {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}/stats")
async def get_document_stats(document_id: str):
    """获取文档统计信息"""
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="文档未找到")
    
    document = documents_db[document_id]
    
    # 获取向量统计
    try:
        vector_stats = vector_store.get_stats()
        # 这里可以添加更具体的文档相关统计
    except Exception as e:
        vector_stats = {"error": str(e)}
    
    return {
        "document": document,
        "vector_stats": vector_stats
    }