from fastapi import APIRouter, HTTPException
from typing import List, Optional
import asyncio

from app.models.schemas import QueryRequest, QueryResponse
from app.services.qa_engine import qa_manager
from app.core.logging_config import logger
from app.core.exceptions import LLMError, VectorStoreError

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """基于文档的问答查询"""
    try:
        # 调用问答引擎
        result = await qa_manager.answer_question(
            query=request.query,
            document_ids=request.document_ids,
            top_k=request.top_k
        )
        
        return QueryResponse(
            query=result["query"],
            answer=result["answer"],
            sources=result["sources"],
            confidence=result["confidence"]
        )
        
    except LLMError as e:
        logger.error(f"语言模型错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except VectorStoreError as e:
        logger.error(f"向量存储错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"问答查询时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

@router.post("/chat")
async def chat_conversation(request: QueryRequest):
    """对话式问答（支持上下文）"""
    try:
        # TODO: 实现带历史对话的问答
        # 这里可以存储和管理对话历史
        
        result = await qa_manager.answer_question(
            query=request.query,
            document_ids=request.document_ids,
            top_k=request.top_k
        )
        
        return {
            "query": result["query"],
            "answer": result["answer"],
            "sources": result["sources"],
            "confidence": result["confidence"],
            "conversation_id": "temp_conv_id"  # TODO: 实际的会话ID管理
        }
        
    except Exception as e:
        logger.error(f"对话问答时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail="对话服务暂时不可用")

@router.get("/suggestions")
async def get_query_suggestions(document_ids: Optional[List[str]] = None):
    """获取查询建议"""
    try:
        # TODO: 基于文档内容生成查询建议
        suggestions = [
            "文档的主要内容是什么？",
            "文档中提到了哪些关键技术？",
            "文档的结论部分说了什么？"
        ]
        
        return {"suggestions": suggestions}
        
    except Exception as e:
        logger.error(f"获取查询建议时发生错误: {str(e)}")
        return {"suggestions": []}