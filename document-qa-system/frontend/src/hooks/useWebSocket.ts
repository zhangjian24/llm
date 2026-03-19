/**
 * WebSocket Hook 用于实时接收文档状态更新
 */
import { useEffect, useRef, useCallback } from 'react';
import { useDocumentStore } from '../stores/documentStore';

interface WebSocketMessage {
  type: string;
  doc_id: string;
  status: string;
  chunks_count?: number;
  filename?: string;
  timestamp: string;
  connection_id?: string;
  message?: string;
}

export const useWebSocket = (url: string) => {
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);
  const { updateDocumentStatus } = useDocumentStore();

  // 连接 WebSocket
  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    try {
      console.log('Connecting to WebSocket...', url);
      ws.current = new WebSocket(url);

      ws.current.onopen = () => {
        console.log('✅ WebSocket connected');
      };

      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log('📥 Received WebSocket message:', message);

          // 处理不同类型的事件
          switch (message.type) {
            case 'connected':
              console.log('🎉 Connected to document status service:', message.message);
              break;

            case 'document_status_updated':
              // 更新文档状态
              updateDocumentStatus(
                message.doc_id,
                message.status as any,
                message.chunks_count || undefined
              );
              console.log(`🔄 Updated document ${message.doc_id} status to ${message.status}`);
              break;

            default:
              console.log('Unknown message type:', message.type);
          }
        } catch (error) {
          console.error('❌ Failed to parse WebSocket message:', error);
        }
      };

      ws.current.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
      };

      ws.current.onclose = (event) => {
        console.log(`🔌 WebSocket closed: ${event.code} ${event.reason}`);
        
        // 自动重连（指数退避）
        if (event.code !== 1000) { // 不是正常关闭
          const delay = Math.min(1000 * Math.pow(2, (reconnectTimeout.current?.toString().length || 0)), 30000);
          console.log(`🔁 Reconnecting in ${delay}ms...`);
          
          reconnectTimeout.current = setTimeout(() => {
            connect();
          }, delay);
        }
      };

    } catch (error) {
      console.error('❌ Failed to create WebSocket:', error);
    }
  }, [url, updateDocumentStatus]);

  // 断开连接
  const disconnect = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
      reconnectTimeout.current = null;
    }

    if (ws.current) {
      ws.current.close(1000, 'Client disconnect');
      ws.current = null;
    }
  }, []);

  // 发送心跳（保持连接活跃）
  const sendHeartbeat = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send('ping');
    }
  }, []);

  // 组件挂载时连接，卸载时断开
  useEffect(() => {
    connect();

    // 心跳定时器（每30秒）
    const heartbeatInterval = setInterval(sendHeartbeat, 30000);

    return () => {
      clearInterval(heartbeatInterval);
      disconnect();
    };
  }, [connect, disconnect, sendHeartbeat]);

  return {
    isConnected: ws.current?.readyState === WebSocket.OPEN,
    reconnect: connect,
    disconnect
  };
};
