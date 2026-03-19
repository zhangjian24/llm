"""
WebSocket 连接管理器
用于广播文档状态更新到所有连接的客户端
"""
from fastapi import WebSocket
from typing import List, Dict
import structlog

logger = structlog.get_logger()


class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        # 存储所有活跃的 WebSocket 连接
        self.active_connections: List[WebSocket] = []
        # 按文档 ID 分组的连接（可选优化）
        self.document_subscribers: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket) -> str:
        """
        接受并注册新的 WebSocket 连接
        
        Returns:
            str: 连接 ID（这里简单返回客户端数量）
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        
        connection_id = f"connection_{len(self.active_connections)}"
        logger.info(
            "websocket_connected",
            connection_id=connection_id,
            total_connections=len(self.active_connections)
        )
        
        return connection_id
    
    def disconnect(self, websocket: WebSocket):
        """断开并移除 WebSocket 连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
        # 从所有订阅中移除
        for doc_id in list(self.document_subscribers.keys()):
            if websocket in self.document_subscribers[doc_id]:
                self.document_subscribers[doc_id].remove(websocket)
            if not self.document_subscribers[doc_id]:
                del self.document_subscribers[doc_id]
        
        logger.info(
            "websocket_disconnected",
            total_connections=len(self.active_connections)
        )
    
    async def broadcast(self, message: dict):
        """
        广播消息到所有连接的客户端
        
        Args:
            message: 要广播的消息字典
        """
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(
                    "failed_to_send_message",
                    error=str(e),
                    exc_info=True
                )
                disconnected.append(connection)
        
        # 清理断开的连接
        for conn in disconnected:
            self.disconnect(conn)
    
    async def send_document_update(
        self, 
        doc_id: str, 
        status: str, 
        chunks_count: int = None,
        filename: str = None
    ):
        """
        发送文档状态更新消息
        
        Args:
            doc_id: 文档 ID
            status: 新状态 (ready/processing/failed)
            chunks_count: 分块数量
            filename: 文件名（可选）
        """
        message = {
            "type": "document_status_updated",
            "doc_id": doc_id,
            "status": status,
            "chunks_count": chunks_count,
            "timestamp": self._get_timestamp()
        }
        
        if filename:
            message["filename"] = filename
        
        logger.info(
            "broadcasting_document_update",
            doc_id=doc_id,
            status=status,
            chunks_count=chunks_count
        )
        
        await self.broadcast(message)
    
    @staticmethod
    def _get_timestamp() -> str:
        """获取 ISO 格式时间戳"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"


# 创建全局单例
manager = ConnectionManager()
