from fastapi import APIRouter, HTTPException, Header, Depends
from typing import List, Optional
import asyncio

from app.models.schemas import (
    EmbeddingRequest, EmbeddingResponse, 
    TextEmbedding, QueryEmbeddingRequest
)
from app.services.embedding import embedding_service
from app.core.logging_config import logger
from app.core.exceptions import EmbeddingError

router = APIRouter()

async def verify_api_key(authorization: Optional[str] = Header(None)):
    """验证Bearer Token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少认证信息")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="认证格式错误")
    
    token = authorization[7:]  # 移除 "Bearer " 前缀
    # 这里可以添加实际的API密钥验证逻辑
    # 目前简单验证非空
    if not token:
        raise HTTPException(status_code=401, detail="无效的API密钥")
    
    return token

@router.post("/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(
    request: EmbeddingRequest,
    api_key: str = Depends(verify_api_key)
):
    """创建文本嵌入向量 - OpenAI兼容API"""
    try:
        # 批量生成嵌入向量
        embeddings = await embedding_service.batch_embed_documents(request.input)
        
        # 构造响应数据
        data = []
        for i, (text, embedding) in enumerate(zip(request.input, embeddings)):
            data.append(TextEmbedding(
                object="embedding",
                embedding=embedding,
                index=i
            ))
        
        response = EmbeddingResponse(
            object="list",
            data=data,
            model=embedding_service.model,
            usage={
                "prompt_tokens": sum(len(text.split()) for text in request.input),
                "total_tokens": sum(len(text.split()) for text in request.input)
            }
        )
        
        logger.info(f"成功生成 {len(data)} 个文本嵌入向量")
        return response
        
    except EmbeddingError as e:
        logger.error(f"嵌入生成错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"生成嵌入向量时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@router.post("/embeddings/query")
async def create_query_embedding(
    request: QueryEmbeddingRequest,
    api_key: str = Depends(verify_api_key)
):
    """为查询创建嵌入向量"""
    try:
        # 生成查询嵌入向量
        embedding = embedding_service.embed_query(request.query)
        
        response = {
            "object": "embedding",
            "data": [{
                "object": "embedding",
                "embedding": embedding,
                "index": 0
            }],
            "model": embedding_service.model,
            "usage": {
                "prompt_tokens": len(request.query.split()),
                "total_tokens": len(request.query.split())
            }
        }
        
        logger.info("成功生成查询嵌入向量")
        return response
        
    except EmbeddingError as e:
        logger.error(f"查询嵌入生成错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"生成查询嵌入向量时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@router.get("/embeddings/models")
async def list_embedding_models(api_key: str = Depends(verify_api_key)):
    """列出可用的嵌入模型"""
    try:
        models = [
            {
                "id": embedding_service.model,
                "object": "model",
                "owned_by": "alibaba-cloud",
                "permission": [{
                    "id": "modelperm-default",
                    "object": "model_permission",
                    "created": 1686935002,
                    "allow_create_engine": False,
                    "allow_sampling": True,
                    "allow_logprobs": True,
                    "allow_search_indices": True,
                    "allow_view": True,
                    "allow_fine_tuning": False,
                    "organization": "*",
                    "group": None,
                    "is_blocking": False
                }]
            }
        ]
        
        return {
            "object": "list",
            "data": models
        }
        
    except Exception as e:
        logger.error(f"获取模型列表时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")