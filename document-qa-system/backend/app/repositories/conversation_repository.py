"""
对话数据访问层
负责对话的 CRUD 操作
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from uuid import UUID
from datetime import datetime
from app.models.conversation import Conversation


class ConversationRepository:
    """
    对话数据访问类
    
    Methods:
        save: 保存对话
        find_by_id: 根据 ID 查询
        find_all: 查询对话列表
        update_messages: 更新消息列表
        delete: 删除对话
    """
    
    def __init__(self, session: AsyncSession):
        """
        初始化
        
        Args:
            session: 数据库会话
        """
        self.session = session
    
    async def save(self, conversation: Conversation) -> UUID:
        """
        保存对话
        
        Args:
            conversation: 对话实体
            
        Returns:
            UUID: 对话 ID
        """
        self.session.add(conversation)
        await self.session.flush()
        return conversation.id
    
    async def find_by_id(self, conv_id: UUID) -> Optional[Conversation]:
        """
        根据 ID 查询对话
        
        Args:
            conv_id: 对话 ID
            
        Returns:
            Optional[Conversation]: 对话实体
        """
        result = await self.session.execute(
            select(Conversation).where(Conversation.id == conv_id)
        )
        return result.scalar_one_or_none()
    
    async def find_all(
        self, 
        limit: int = 10
    ) -> List[Conversation]:
        """
        查询对话列表（按最近活动时间排序）
        
        Args:
            limit: 返回数量
            
        Returns:
            List[Conversation]: 对话列表
        """
        result = await self.session.execute(
            select(Conversation)
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def update_messages(
        self, 
        conv_id: UUID, 
        messages: List[Dict[str, Any]]
    ) -> bool:
        """
        更新对话消息列表
        
        Args:
            conv_id: 对话 ID
            messages: 消息列表（JSONB）
            
        Returns:
            bool: 是否更新成功
        """
        conv = await self.find_by_id(conv_id)
        if not conv:
            return False
        
        conv.messages = messages
        conv.updated_at = datetime.utcnow()
        
        # 自动生成标题（从第一条用户消息）
        if not conv.title and messages:
            for msg in messages:
                if msg.get('role') == 'user':
                    conv.title = msg.get('content', '')[:50]
                    break
        
        return True
    
    async def create_with_message(
        self,
        user_id: Optional[UUID] = None,
        first_message: Optional[str] = None
    ) -> UUID:
        """
        创建新对话并添加第一条消息
        
        Args:
            user_id: 用户 ID（可选）
            first_message: 第一条消息
            
        Returns:
            UUID: 对话 ID
        """
        messages = []
        title = None
        
        if first_message:
            messages = [{
                "role": "user",
                "content": first_message,
                "created_at": datetime.utcnow().isoformat()
            }]
            title = first_message[:50]
        
        conversation = Conversation(
            user_id=user_id,
            title=title,
            messages=messages if messages else None
        )
        
        return await self.save(conversation)
    
    async def delete(self, conv_id: UUID) -> bool:
        """
        删除对话
        
        Args:
            conv_id: 对话 ID
            
        Returns:
            bool: 是否删除成功
        """
        conv = await self.find_by_id(conv_id)
        if not conv:
            return False
        
        await self.session.delete(conv)
        return True
