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
        # 请求接收阶段 - INFO级别
        logger.info(f"[CHAT_QUERY] 收到查询请求 - 查询内容: {query_request.query[:100]}..., 对话ID: {query_request.conversation_id}")
        
        # 数据验证阶段 - DEBUG级别
        logger.debug(f"[CHAT_QUERY] 开始数据验证 - 请求参数: {{'query_length': {len(query_request.query)}, 'stream': {query_request.stream}}}")
        
        # 验证查询内容
        if not query_request.query.strip():
            logger.warning(f"[CHAT_QUERY] 数据验证失败 - 查询内容为空")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="查询内容不能为空"
            )
        
        logger.debug(f"[CHAT_QUERY] 数据验证通过 - 查询长度: {len(query_request.query)} 字符")
        
        # 业务逻辑处理阶段 - INFO级别
        logger.info(f"[CHAT_QUERY] 开始执行查询处理流程")
        response = await rag_service.query_documents(query_request)
        
        # 响应返回阶段 - INFO级别
        logger.info(f"[CHAT_QUERY] 查询处理完成 - 对话ID: {response.conversation_id}, 处理时间: {response.processing_time:.2f}s, 源文档数量: {len(response.sources)}")
        return response
        
    except HTTPException as he:
        # 异常处理 - ERROR级别
        logger.error(f"[CHAT_QUERY] HTTP异常 - 状态码: {he.status_code}, 详情: {he.detail}")
        raise
    except Exception as e:
        # 异常处理 - ERROR级别
        logger.error(f"[CHAT_QUERY] 查询处理失败 - 错误类型: {type(e).__name__}, 错误信息: {str(e)}", exc_info=True)
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
        # 请求接收阶段 - INFO级别
        logger.info(f"[CHAT_STREAM] 收到流式查询请求 - 查询内容: {query_request.query[:100]}..., 对话ID: {query_request.conversation_id}")
        
        # 数据验证阶段 - DEBUG级别
        logger.debug(f"[CHAT_STREAM] 开始数据验证 - 请求参数: {{'query_length': {len(query_request.query)}}}")
        
        # 验证查询内容
        if not query_request.query.strip():
            logger.warning(f"[CHAT_STREAM] 数据验证失败 - 查询内容为空")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="查询内容不能为空"
            )
        
        logger.debug(f"[CHAT_STREAM] 数据验证通过 - 查询长度: {len(query_request.query)} 字符")
        
        # 设置流式响应
        query_request.stream = True
        
        # 业务逻辑处理阶段 - INFO级别
        logger.info(f"[CHAT_STREAM] 开始流式查询处理流程")
        
        async def event_generator() -> AsyncGenerator[str, None]:
            """事件生成器"""
            try:
                logger.debug(f"[CHAT_STREAM] 启动事件生成器")
                start_time = time.time()
                chunk_count = 0
                
                async for chunk in rag_service.stream_query_documents(query_request):
                    chunk_count += 1
                    # 格式化为SSE格式
                    data = {
                        "type": chunk.type,
                        "content": chunk.content,
                        "sources": [s.dict() for s in chunk.sources] if chunk.sources else None,
                        "done": chunk.done
                    }
                    
                    # 外部服务调用阶段 - DEBUG级别（针对每个chunk）
                    if chunk.type == "answer":
                        logger.debug(f"[CHAT_STREAM] 流式响应chunk - 类型: {chunk.type}, 内容长度: {len(chunk.content)}")
                    elif chunk.type == "sources":
                        logger.debug(f"[CHAT_STREAM] 流式响应chunk - 类型: {chunk.type}, 源文档数量: {len(chunk.sources) if chunk.sources else 0}")
                    else:
                        logger.debug(f"[CHAT_STREAM] 流式响应chunk - 类型: {chunk.type}, 内容: {chunk.content[:50]}...")
                    
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                    
                    # 如果完成，发送结束信号
                    if chunk.done:
                        processing_time = time.time() - start_time
                        logger.info(f"[CHAT_STREAM] 流式处理完成 - 总chunk数: {chunk_count}, 处理时间: {processing_time:.2f}s")
                        yield "data: [DONE]\n\n"
                        break
                        
            except Exception as e:
                # 异常处理 - ERROR级别
                logger.error(f"[CHAT_STREAM] 流式响应生成失败 - 错误类型: {type(e).__name__}, 错误信息: {str(e)}", exc_info=True)
                error_data = {
                    "type": "error",
                    "content": f"处理过程中发生错误: {str(e)}",
                    "done": True
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        
        # 响应返回阶段 - INFO级别
        logger.info(f"[CHAT_STREAM] 返回流式响应 - Content-Type: text/event-stream")
        
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
        
    except HTTPException as he:
        # 异常处理 - ERROR级别
        logger.error(f"[CHAT_STREAM] HTTP异常 - 状态码: {he.status_code}, 详情: {he.detail}")
        raise
    except Exception as e:
        # 异常处理 - ERROR级别
        logger.error(f"[CHAT_STREAM] 流式查询启动失败 - 错误类型: {type(e).__name__}, 错误信息: {str(e)}", exc_info=True)
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
        # 请求接收阶段 - INFO级别
        logger.info(f"[CHAT_HISTORY_GET] 收到获取对话历史请求 - 对话ID: {conversation_id}")
        
        # 业务逻辑处理阶段 - DEBUG级别
        logger.debug(f"[CHAT_HISTORY_GET] 开始获取对话历史")
        history = await rag_service.get_conversation_history(conversation_id)
        
        # 响应返回阶段 - INFO级别
        logger.info(f"[CHAT_HISTORY_GET] 对话历史获取完成 - 对话ID: {conversation_id}, 消息数量: {len(history)}")
        
        return {
            "conversation_id": conversation_id,
            "messages": history,
            "message_count": len(history)
        }
        
    except Exception as e:
        # 异常处理 - ERROR级别
        logger.error(f"[CHAT_HISTORY_GET] 获取对话历史失败 - 对话ID: {conversation_id}, 错误类型: {type(e).__name__}, 错误信息: {str(e)}", exc_info=True)
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
        # 请求接收阶段 - INFO级别
        logger.info(f"[CHAT_HISTORY_DELETE] 收到清除对话历史请求 - 对话ID: {conversation_id}")
        
        # 业务逻辑处理阶段 - DEBUG级别
        logger.debug(f"[CHAT_HISTORY_DELETE] 开始清除对话历史")
        
        # 从RAG服务中移除对话历史
        if hasattr(rag_service, 'conversation_history'):
            removed_history = rag_service.conversation_history.pop(conversation_id, None)
            if removed_history is not None:
                logger.debug(f"[CHAT_HISTORY_DELETE] 成功移除对话历史 - 对话ID: {conversation_id}, 移除消息数: {len(removed_history)}")
            else:
                logger.debug(f"[CHAT_HISTORY_DELETE] 对话历史不存在 - 对话ID: {conversation_id}")
        
        # 响应返回阶段 - INFO级别
        logger.info(f"[CHAT_HISTORY_DELETE] 对话历史清除完成 - 对话ID: {conversation_id}")
        
        return {"message": f"对话历史 {conversation_id} 已清除"}
        
    except Exception as e:
        # 异常处理 - ERROR级别
        logger.error(f"[CHAT_HISTORY_DELETE] 清除对话历史失败 - 对话ID: {conversation_id}, 错误类型: {type(e).__name__}, 错误信息: {str(e)}", exc_info=True)
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
        # 请求接收阶段 - INFO级别
        logger.info(f"[CHAT_TEST] 收到连接测试请求")
        
        # 业务逻辑处理阶段 - DEBUG级别
        logger.debug(f"[CHAT_TEST] 开始执行连接测试")
        
        # 简单的测试查询
        test_query = QueryRequest(
            query="你好",
            stream=False
        )
        
        # 这里只是测试连接，不真正执行查询
        logger.debug(f"[CHAT_TEST] 连接测试准备完成")
        
        # 响应返回阶段 - INFO级别
        logger.info(f"[CHAT_TEST] 连接测试完成 - 状态: connected")
        
        return {
            "status": "connected",
            "message": "服务连接正常",
            "timestamp": "2026-03-02T10:00:00Z"
        }
        
    except Exception as e:
        # 异常处理 - ERROR级别
        logger.error(f"[CHAT_TEST] 连接测试失败 - 错误类型: {type(e).__name__}, 错误信息: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"连接测试失败: {str(e)}"
        )