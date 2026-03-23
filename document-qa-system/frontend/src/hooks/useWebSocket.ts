/**
 * WebSocket Hook 用于实时接收文档状态更新
 * 
 * 支持的消息类型:
 * - document.processing: 文档开始处理
 * - document.completed: 文档处理完成
 * - document.failed: 文档处理失败
 * - document.uploaded: 新文档上传成功 (可选)
 * - document.deleted: 文档被删除
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
  const reconnectTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttempts = useRef(0); // 重连次数计数器
  const { updateDocumentStatus, removeDocument } = useDocumentStore();

  // 指数退避策略计算延迟
  const calculateBackoffDelay = useCallback((attempt: number): number => {
    // 基础延迟 1 秒，指数增长，最大 30 秒
    const baseDelay = 1000;
    const maxDelay = 30000;
    const exponentialDelay = baseDelay * Math.pow(2, attempt);
    // 添加随机抖动 (±10%) 避免多个客户端同时重连
    const jitter = Math.random() * 0.2 - 0.1;
    return Math.min(exponentialDelay * (1 + jitter), maxDelay);
  }, []);

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
            case 'document.processing':
              // 文档开始处理
              if (message.status === 'processing') {
                updateDocumentStatus(
                  message.doc_id,
                  'processing',
                  undefined
                );
                console.log(`🔄 Document ${message.doc_id} is processing`);
              }
              break;

            case 'document.completed':
              // 文档处理完成，更新状态为就绪并设置块数
              updateDocumentStatus(
                message.doc_id,
                'ready',
                message.chunks_count
              );
              console.log(`✅ Document ${message.doc_id} completed with ${message.chunks_count} chunks`);
              break;

            case 'document.failed':
              // 文档处理失败
              updateDocumentStatus(
                message.doc_id,
                'failed',
                0
              );
              console.error(`❌ Document ${message.doc_id} failed`);
              break;

            case 'document.uploaded':
              // 新文档上传成功（可选功能）
              if (message.filename) {
                console.log(`📄 New document uploaded: ${message.filename}`);
                // 注意：这里不直接添加到列表，因为后端会触发 processing
                // 前端会通过 document.processing 消息更新状态
              }
              break;

            case 'document.deleted':
              // 文档被删除，从列表中移除
              removeDocument(message.doc_id);
              console.log(`🗑️ Document ${message.doc_id} deleted`);
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
        // 记录错误但不重连，让 onclose 处理重连逻辑
      };

      ws.current.onclose = (event) => {
        console.log(`🔌 WebSocket closed: ${event.code} ${event.reason}`);
        
        // 自动重连（指数退避策略）
        if (event.code !== 1000) { // 不是正常关闭
          reconnectAttempts.current += 1;
          const delay = calculateBackoffDelay(reconnectAttempts.current);
          
          console.log(
            `🔁 Reconnecting in ${delay}ms... (attempt ${reconnectAttempts.current})`
          );
          
          reconnectTimeout.current = setTimeout(() => {
            connect();
          }, delay);
        } else {
          // 正常关闭，重置重连计数
          reconnectAttempts.current = 0;
        }
      };

    } catch (error) {
      console.error('❌ Failed to create WebSocket:', error);
    }
  }, [url, updateDocumentStatus, removeDocument]);

  // 断开连接
  const disconnect = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
      reconnectTimeout.current = null;
    }

    // 重置重连计数
    reconnectAttempts.current = 0;

    if (ws.current) {
      // 使用 1000 状态码表示正常关闭，触发 onclose 但不会重连
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
    // 延迟 500ms 连接，避免页面加载时立即连接导致的问题
    const initialConnectTimeout = setTimeout(() => {
      connect();
    }, 500);

    // 心跳定时器（每30秒）
    const heartbeatInterval = setInterval(sendHeartbeat, 30000);

    return () => {
      clearTimeout(initialConnectTimeout);
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
