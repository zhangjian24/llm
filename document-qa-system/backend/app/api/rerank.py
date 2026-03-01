from fastapi import APIRouter, HTTPException, Header, Depends
from typing import List, Optional, Dict, Any

from app.models.schemas import RerankRequest, RerankResponse, RerankResult
from app.services.reranker import reranker_service
from app.core.logging_config import logger
from app.core.exceptions import RerankError

router = APIRouter()

async def verify_api_key(authorization: Optional[str] = Header(None)):
    """验证Bearer Token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少认证信息")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="认证格式错误")
    
    token = authorization[7:]  # 移除 "Bearer " 前缀
    if not token:
        raise HTTPException(status_code=401, detail="无效的API密钥")
    
    return token

@router.post("/rerank", response_model=RerankResponse)
async def rerank_documents(
    request: RerankRequest,
    api_key: str = Depends(verify_api_key)
):
    """文档重排序接口 - Alibaba Cloud兼容API"""
    try:
        # 准备文档数据
        documents_data = []
        for i, doc in enumerate(request.documents):
            if isinstance(doc, str):
                documents_data.append({
                    'content': doc,
                    'document_id': f'doc_{i}',
                    'chunk_id': f'chunk_{i}'
                })
            elif isinstance(doc, dict):
                documents_data.append({
                    'content': doc.get('text', doc.get('content', '')),
                    'document_id': doc.get('document_id', f'doc_{i}'),
                    'chunk_id': doc.get('chunk_id', f'chunk_{i}'),
                    'metadata': doc.get('metadata', {})
                })
            else:
                documents_data.append({
                    'content': str(doc),
                    'document_id': f'doc_{i}',
                    'chunk_id': f'chunk_{i}'
                })
        
        # 执行重排序
        reranked_results = reranker_service.rerank_documents(
            query=request.query,
            documents=documents_data,
            top_k=request.top_n
        )
        
        # 构造响应数据
        results = []
        for i, result in enumerate(reranked_results):
            results.append(RerankResult(
                index=result.get('chunk_index', i),
                document=result.get('content', ''),
                relevance_score=result.get('score', 0.0),
                document_id=result.get('document_id', '')
            ))
        
        response = RerankResponse(
            id=f"rerank_{request.model}_{hash(request.query)}",
            results=results,
            usage={
                "total_tokens": len(request.query.split()) + sum(
                    len(doc.get('content', '').split()) for doc in documents_data
                )
            }
        )
        
        logger.info(f"重排序完成，返回 {len(results)} 个结果")
        return response
        
    except RerankError as e:
        logger.error(f"重排序错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"重排序时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@router.get("/rerank/models")
async def list_rerank_models(api_key: str = Depends(verify_api_key)):
    """列出可用的重排序模型"""
    try:
        models = [
            {
                "id": reranker_service.model,
                "object": "model",
                "owned_by": "alibaba-cloud",
                "capability": "document_reranking",
                "max_input_tokens": 32768,
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
        logger.error(f"获取重排序模型列表时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@router.post("/rerank/batch")
async def batch_rerank(
    requests: List[RerankRequest],
    api_key: str = Depends(verify_api_key)
):
    """批量文档重排序"""
    try:
        batch_results = []
        
        for req in requests:
            # 复用单个重排序逻辑
            documents_data = []
            for i, doc in enumerate(req.documents):
                if isinstance(doc, str):
                    documents_data.append({'content': doc})
                elif isinstance(doc, dict):
                    documents_data.append({
                        'content': doc.get('text', doc.get('content', '')),
                        'document_id': doc.get('document_id', f'doc_{i}')
                    })
                else:
                    documents_data.append({'content': str(doc)})
            
            reranked_results = reranker_service.rerank_documents(
                query=req.query,
                documents=documents_data,
                top_k=req.top_n
            )
            
            results = []
            for i, result in enumerate(reranked_results):
                results.append(RerankResult(
                    index=result.get('chunk_index', i),
                    document=result.get('content', ''),
                    relevance_score=result.get('score', 0.0),
                    document_id=result.get('document_id', '')
                ))
            
            batch_results.append({
                "query": req.query,
                "results": results
            })
        
        logger.info(f"批量重排序完成，处理 {len(requests)} 个请求")
        return {"batch_results": batch_results}
        
    except Exception as e:
        logger.error(f"批量重排序时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail="批量处理失败")