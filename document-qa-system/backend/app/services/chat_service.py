"""
对话管理服务
负责对话历史的管理和持久化
"""
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from app.repositories.conversation_repository import ConversationRepository
from app.models.conversation import Conversation
import structlog

logger = structlog.get_logger()


class ChatService:
    """
    对话管理服务
    
    功能:
    - 创建新对话
    - 获取对话历史
    - 添加消息到对话
    - 删除对话
    - 管理对话上下文窗口
    """
    
    def __init__(self, repo: ConversationRepository):
        """
        初始化对话服务
        
        Args:
            repo: 对话数据访问仓库
        """
        self.repo = repo
    
    async def create_conversation(
        self,
        user_id: Optional[UUID] = None,
        first_message: Optional[str] = None
    ) -> UUID:
        """
        创建新对话
        
        Args:
            user_id: 用户 ID（可选，MVP 阶段为空）
            first_message: 第一条消息（用于生成标题）
            
        Returns:
            UUID: 对话 ID
        """
        conv_id = await self.repo.create_with_message(
            user_id=user_id,
            first_message=first_message
        )
        
        logger.info(
            "conversation_created",
            conversation_id=str(conv_id),
            has_first_message=bool(first_message)
        )
        
        return conv_id
    
    async def get_conversation(self, conv_id: UUID) -> Optional[Conversation]:
        """
        获取对话详情
        
        Args:
            conv_id: 对话 ID
            
        Returns:
            Optional[Conversation]: 对话实体，不存在返回 None
        """
        conversation = await self.repo.find_by_id(conv_id)
        
        if conversation:
            logger.debug(
                "conversation_retrieved",
                conversation_id=str(conv_id),
                title=conversation.title
            )
        
        return conversation
    
    async def get_conversations_list(
        self,
        limit: int = 10
    ) -> List[Conversation]:
        """
        获取对话列表
        
        Args:
            limit: 返回数量
            
        Returns:
            List[Conversation]: 对话列表
        """
        conversations = await self.repo.find_all(limit=limit)
        
        logger.info(
            "conversations_list_retrieved",
            count=len(conversations),
            limit=limit
        )
        
        return conversations
    
    async def add_message(
        self,
        conv_id: UUID,
        role: str,
        content: str,
        sources: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        添加消息到对话
        
        Args:
            conv_id: 对话 ID
            role: 角色（"user" 或 "assistant"）
            content: 消息内容
            sources: 引用来源（仅 assistant 需要）
            
        Returns:
            bool: 是否添加成功
        """
        # 获取现有消息
        conversation = await self.repo.find_by_id(conv_id)
        if not conversation:
            logger.warning(
                "conversation_not_found_for_message",
                conversation_id=str(conv_id)
            )
            return False
        
        messages = conversation.messages or []
        
        # 创建新消息
        new_message = {
            "role": role,
            "content": content,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # 如果是助手回答，添加引用来源
        if role == "assistant" and sources:
            new_message["sources"] = sources
        
        # 添加到消息列表
        messages.append(new_message)
        
        # 更新对话
        success = await self.repo.update_messages(conv_id, messages)
        
        if success:
            logger.info(
                "message_added",
                conversation_id=str(conv_id),
                role=role,
                message_count=len(messages)
            )
        
        return success
    
    async def delete_conversation(self, conv_id: UUID) -> bool:
        """
        删除对话
        
        Args:
            conv_id: 对话 ID
            
        Returns:
            bool: 是否删除成功
        """
        success = await self.repo.delete(conv_id)
        
        if success:
            logger.info(
                "conversation_deleted",
                conversation_id=str(conv_id)
            )
        else:
            logger.warning(
                "conversation_delete_failed",
                conversation_id=str(conv_id)
            )
        
        return success
    
    def truncate_context(
        self,
        messages: List[Dict[str, str]],
        max_turns: int = 10
    ) -> List[Dict[str, str]]:
        """
        截断对话历史，保留最近的 N 轮
        
        Args:
            messages: 完整消息列表
            max_turns: 最大轮数
            
        Returns:
            List[Dict[str, str]]: 截断后的消息列表
        """
        if len(messages) <= max_turns * 2:  # 每轮包含 user 和 assistant
            return messages
        
        # 保留最近的 N 轮
        truncated = messages[-max_turns * 2:]
        
        logger.debug(
            "context_truncated",
            original_count=len(messages),
            truncated_count=len(truncated),
            max_turns=max_turns
        )
        
        return truncated
    
    async def get_last_user_message(
        self,
        conv_id: UUID
    ) -> Optional[str]:
        """
        获取对话中最后一条用户消息
        
        Args:
            conv_id: 对话 ID
            
        Returns:
            Optional[str]: 用户消息内容
        """
        conversation = await self.repo.find_by_id(conv_id)
        if not conversation or not conversation.messages:
            return None
        
        # 从后往前找第一条用户消息
        for msg in reversed(conversation.messages):
            if msg.get('role') == 'user':
                return msg.get('content')
        
        return None
