from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.models.schemas import ChatRequest, ChatResponse, SearchResult
from app.services.qa_engine import qa_engine
from app.services.vector_store import vector_store
from app.core.exceptions import LLMException, VectorStoreException
from app.core.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/query", response_model=ChatResponse)
async def chat_query(request: ChatRequest):
    """处理聊天查询"""
    try:
        logger.info(f"收到聊天查询: {request.query}")
        
        # 执行问答
        result = await qa_engine.answer_question(
            query=request.query,
            document_ids=request.document_ids,
            history=request.history
        )
        
        logger.info(f"问答完成，置信度: {result['confidence']:.2f}")
        return ChatResponse(**result)
        
    except LLMException as e:
        logger.error(f"LLM调用失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI服务暂时不可用: {str(e)}")
    except VectorStoreException as e:
        logger.error(f"向量检索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文档检索失败: {str(e)}")
    except Exception as e:
        logger.error(f"聊天查询处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@router.post("/search", response_model=List[SearchResult])
async def semantic_search(query: str, top_k: int = 10, 
                         document_ids: Optional[List[str]] = None):
    """语义搜索"""
    try:
        logger.info(f"执行语义搜索: {query}")
        
        # 执行向量搜索
        results = await qa_engine.search_similar_documents(
            query=query,
            top_k=top_k,
            document_ids=document_ids
        )
        
        search_results = [
            SearchResult(
                document_id=result['document_id'],
                content=result['content'],
                score=result['score'],
                metadata=result['metadata']
            ) for result in results
        ]
        
        logger.info(f"搜索完成，返回 {len(search_results)} 个结果")
        return search_results
        
    except VectorStoreException as e:
        logger.error(f"向量搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"搜索服务暂时不可用: {str(e)}")
    except Exception as e:
        logger.error(f"搜索处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@router.get("/suggestions")
async def get_query_suggestions(prefix: str, limit: int = 5):
    """获取查询建议"""
    try:
        # 这里可以实现基于历史查询的建议功能
        suggestions = [
            f"{prefix}是什么意思？",
            f"{prefix}如何使用？",
            f"{prefix}的相关概念"
        ][:limit]
        
        return {"suggestions": suggestions}
        
    except Exception as e:
        logger.error(f"查询建议生成失败: {str(e)}")
        return {"suggestions": []}

@router.post("/feedback")
async def submit_feedback(feedback_data: dict):
    """提交反馈"""
    try:
        # 这里可以实现用户反馈收集功能
        logger.info(f"收到用户反馈: {feedback_data}")
        
        # 可以保存到数据库或发送到分析服务
        return {"message": "反馈提交成功"}
        
    except Exception as e:
        logger.error(f"反馈提交失败: {str(e)}")
        raise HTTPException(status_code=500, detail="反馈提交失败")