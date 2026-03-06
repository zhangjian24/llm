"""
对话聊天 API 路由
支持 SSE 流式响应
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional, Dict, Any
import json
from app.core.database import get_db_session
from app.repositories.conversation_repository import ConversationRepository
from app.services.chat_service import ChatService
from app.services.embedding_service import EmbeddingService
from app.services.pinecone_service import PineconeService
from app.services.rerank_service import RerankService
from app.services.rag_service import RAGService
from app.schemas.chat import ChatQueryDTO, ChatResponseDTO, ConversationDTO
from app.schemas.common import SuccessResponse
import structlog

logger = structlog.get_logger()

router = APIRouter()


def get_chat_service(session: AsyncSession) -> ChatService:
    """获取 ChatService 实例"""
    repo = ConversationRepository(session)
    return ChatService(repo)


def get_rag_service() -> RAGService:
    """获取 RAGService 实例"""
    embedding_svc = EmbeddingService()
    pinecone_svc = PineconeService()
    rerank_svc = RerankService()
    return RAGService(embedding_svc, pinecone_svc, rerank_svc)


@router.post("/")
async def chat(
    request: ChatQueryDTO,
    chat_svc: ChatService = Depends(get_chat_service),
    rag_svc: RAGService = Depends(get_rag_service)
):
    """
    发起对话（支持 SSE 流式）
    
    - **query**: 用户问题
    - **top_k**: 检索数量
    - **stream**: 是否流式输出
    - **conversation_id**: 对话 ID（可选）
    """
    try:
        conversation_id = request.conversation_id
        
        # 如果没有对话 ID，创建新对话
        if not conversation_id:
            conversation_id = await chat_svc.create_conversation(
                first_message=request.query
            )
        
        # 保存用户消息
        await chat_svc.add_message(
            conv_id=conversation_id,
            role="user",
            content=request.query
        )
        
        # 获取对话历史
        conversation = await chat_svc.get_conversation(conversation_id)
        history = conversation.messages if conversation else []
        
        # SSE 流式响应
        async def generate_stream():
            try:
                full_answer = ""
                
                async for token in rag_svc.query(
                    question=request.query,
                    conversation_history=history[-10:],  # 保留最近 10 轮
                    top_k=request.top_k
                ):
                    full_answer += token
                    
                    # 发送 SSE 数据
                    yield f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"
                
                # 保存助手回答
                await chat_svc.add_message(
                    conv_id=conversation_id,
                    role="assistant",
                    content=full_answer
                )
                
                # 发送完成信号
                yield f"data: {json.dumps({'done': True, 'conversation_id': str(conversation_id)}, ensure_ascii=False)}\n\n"
                
            except Exception as e:
                logger.error("stream_generation_failed", error=str(e))
                yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
        
        if request.stream:
            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream"
            )
        else:
            # 非流式：收集完整回答
            full_answer = ""
            async for token in rag_svc.query(
                question=request.query,
                conversation_history=history[-10:],
                top_k=request.top_k
            ):
                full_answer += token
            
            # 保存回答
            await chat_svc.add_message(
                conv_id=conversation_id,
                role="assistant",
                content=full_answer
            )
            
            return SuccessResponse(
                data=ChatResponseDTO(
                    answer=full_answer,
                    conversation_id=conversation_id
                )
            )
            
    except Exception as e:
        logger.error("chat_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations", response_model=SuccessResponse[list[ConversationDTO]])
async def get_conversations(
    limit: int = Query(10, ge=1, le=100),
    chat_svc: ChatService = Depends(get_chat_service)
):
    """
    获取对话历史列表
    
    - **limit**: 返回数量
    """
    try:
        conversations = await chat_svc.get_conversations_list(limit=limit)
        
        items = [
            ConversationDTO(
                id=conv.id,
                title=conv.title or "新对话",
                last_message=(conv.messages[-1]['content'] if conv.messages else None),
                turns=len(conv.messages) // 2 if conv.messages else 0,
                updated_at=conv.updated_at
            )
            for conv in conversations
        ]
        
        return SuccessResponse(data=items)
        
    except Exception as e:
        logger.error("get_conversations_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conv_id}", status_code=204)
async def delete_conversation(
    conv_id: UUID,
    chat_svc: ChatService = Depends(get_chat_service)
):
    """
    删除对话
    
    - **conv_id**: 对话 ID
    """
    try:
        success = await chat_svc.delete_conversation(conv_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="对话不存在")
        
        logger.info("conversation_deleted", conv_id=str(conv_id))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_conversation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
