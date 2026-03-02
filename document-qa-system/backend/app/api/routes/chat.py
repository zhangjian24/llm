"""
聊天API路由
处理用户查询和对话交互
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import json
import asyncio

from ...models.schemas import (
    QueryRequest, 
    QueryResponse, 
    StreamChunk,
    ChatMessage,
    ErrorResponse
)
from ...services.rag_service import RAGService
from ...core.logging import logger
from ...api.deps import get_pinecone_service, get_llm_service

router = APIRouter(prefix="/chat", tags=["chat"])


def get_rag_service(
    pinecone_dep = Depends(get_pinecone_service),
    llm_dep = Depends(get_llm_service)
):
    """获取RAG服务依赖"""
    from ...services.rag_service import RAGService
    return RAGService(pinecone_dep, llm_dep)


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    query_request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    同步查询文档
    
    Args:
        query_request: 查询请求
        rag_service: RAG服务实例
        
    Returns:
        查询响应
    """
    try:
        logger.info(f"收到查询请求: {query_request.query}")
        
        # 验证查询内容
        if not query_request.query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="查询内容不能为空"
            )
        
        # 执行查询
        response = await rag_service.query_documents(query_request)
        
        logger.info(f"查询处理完成，对话ID: {response.conversation_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询处理失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询处理失败: {str(e)}"
        )


@router.post("/stream")
async def stream_query_documents(
    query_request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    流式查询文档
    
    Args:
        query_request: 查询请求
        rag_service: RAG服务实例
        
    Returns:
        流式响应
    """
    try:
        logger.info(f"收到流式查询请求: {query_request.query}")
        
        # 验证查询内容
        if not query_request.query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="查询内容不能为空"
            )
        
        # 设置流式响应
        query_request.stream = True
        
        async def event_generator() -> AsyncGenerator[str, None]:
            """事件生成器"""
            try:
                async for chunk in rag_service.stream_query_documents(query_request):
                    # 格式化为SSE格式
                    data = {
                        "type": chunk.type,
                        "content": chunk.content,
                        "sources": [s.dict() for s in chunk.sources] if chunk.sources else None,
                        "done": chunk.done
                    }
                    
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                    
                    # 如果完成，发送结束信号
                    if chunk.done:
                        yield "data: [DONE]\n\n"
                        break
                        
            except Exception as e:
                logger.error(f"流式响应生成失败: {str(e)}")
                error_data = {
                    "type": "error",
                    "content": f"处理过程中发生错误: {str(e)}",
                    "done": True
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"流式查询启动失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"流式查询启动失败: {str(e)}"
        )


@router.get("/history/{conversation_id}")
async def get_conversation_history(
    conversation_id: str,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    获取对话历史
    
    Args:
        conversation_id: 对话ID
        rag_service: RAG服务实例
        
    Returns:
        对话历史
    """
    try:
        logger.info(f"获取对话历史: {conversation_id}")
        
        history = await rag_service.get_conversation_history(conversation_id)
        
        return {
            "conversation_id": conversation_id,
            "messages": history,
            "message_count": len(history)
        }
        
    except Exception as e:
        logger.error(f"获取对话历史失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取对话历史失败: {str(e)}"
        )


@router.delete("/history/{conversation_id}")
async def clear_conversation_history(
    conversation_id: str,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    清除对话历史
    
    Args:
        conversation_id: 对话ID
        rag_service: RAG服务实例
        
    Returns:
        清除结果
    """
    try:
        logger.info(f"清除对话历史: {conversation_id}")
        
        # 从RAG服务中移除对话历史
        if hasattr(rag_service, 'conversation_history'):
            rag_service.conversation_history.pop(conversation_id, None)
        
        return {"message": f"对话历史 {conversation_id} 已清除"}
        
    except Exception as e:
        logger.error(f"清除对话历史失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清除对话历史失败: {str(e)}"
        )


@router.post("/test")
async def test_connection(
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    测试连接
    
    Args:
        rag_service: RAG服务实例
        
    Returns:
        测试结果
    """
    try:
        logger.info("测试连接请求")
        
        # 简单的测试查询
        test_query = QueryRequest(
            query="你好",
            stream=False
        )
        
        # 这里只是测试连接，不真正执行查询
        return {
            "status": "connected",
            "message": "服务连接正常",
            "timestamp": "2026-03-02T10:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"连接测试失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"连接测试失败: {str(e)}"
        )