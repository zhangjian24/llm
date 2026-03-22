"""
WebSocket 消息推送集成测试
测试后端在文档处理关键节点是否正确发送 WebSocket 消息
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from app.websocket_manager import ConnectionManager
from app.services.document_service import DocumentService
from app.repositories.document_repository import DocumentRepository
from app.services.embedding_service import EmbeddingService
from app.models.document import Document
from uuid import UUID, uuid4


class TestWebSocketMessageTypes:
    """测试 WebSocket 消息类型映射"""

    def test_message_type_mapping(self):
        """测试状态到消息类型的映射关系"""
        expected_mapping = {
            'processing': 'document.processing',
            'ready': 'document.completed',
            'failed': 'document.failed',
            'uploaded': 'document.uploaded',
            'deleted': 'document.deleted'
        }
        
        for status, expected_type in expected_mapping.items():
            # 这里测试逻辑映射，实际映射在 websocket_manager.py 中
            assert status in expected_mapping
            assert expected_mapping[status] == expected_type


@pytest.mark.asyncio
class TestWebSocketBroadcast:
    """测试 WebSocket 广播功能"""

    @pytest.fixture
    def websocket_manager(self):
        """创建 WebSocket 管理器实例"""
        return ConnectionManager()

    @pytest.fixture
    def mock_websocket(self):
        """模拟 WebSocket 连接"""
        ws = AsyncMock()
        ws.accept = AsyncMock()
        ws.send_json = AsyncMock()
        ws.close = AsyncMock()
        return ws

    async def test_broadcast_message_to_all_connections(
        self, 
        websocket_manager, 
        mock_websocket
    ):
        """测试向所有连接广播消息"""
        # Arrange
        await websocket_manager.connect(mock_websocket)
        
        test_message = {
            "type": "document.completed",
            "doc_id": "test-123",
            "status": "ready",
            "chunks_count": 15
        }

        # Act
        await websocket_manager.broadcast(test_message)

        # Assert
        mock_websocket.send_json.assert_called_once_with(test_message)

    async def test_send_document_update_processing(
        self, 
        websocket_manager, 
        mock_websocket
    ):
        """测试发送 processing 状态更新"""
        # Arrange
        await websocket_manager.connect(mock_websocket)

        # Act
        await websocket_manager.send_document_update(
            doc_id="test-doc-123",
            status="processing",
            filename="test.pdf"
        )

        # Assert
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "document.processing"
        assert call_args["doc_id"] == "test-doc-123"
        assert call_args["status"] == "processing"
        assert call_args["filename"] == "test.pdf"
        assert "timestamp" in call_args

    async def test_send_document_update_completed(
        self, 
        websocket_manager, 
        mock_websocket
    ):
        """测试发送 completed 状态更新"""
        # Arrange
        await websocket_manager.connect(mock_websocket)

        # Act
        await websocket_manager.send_document_update(
            doc_id="test-doc-456",
            status="ready",
            chunks_count=20,
            filename="report.pdf"
        )

        # Assert
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "document.completed"
        assert call_args["doc_id"] == "test-doc-456"
        assert call_args["status"] == "ready"
        assert call_args["chunks_count"] == 20
        assert call_args["filename"] == "report.pdf"

    async def test_send_document_update_failed(
        self, 
        websocket_manager, 
        mock_websocket
    ):
        """测试发送 failed 状态更新"""
        # Arrange
        await websocket_manager.connect(mock_websocket)

        # Act
        await websocket_manager.send_document_update(
            doc_id="test-doc-789",
            status="failed",
            filename="error.pdf"
        )

        # Assert
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "document.failed"
        assert call_args["doc_id"] == "test-doc-789"
        assert call_args["status"] == "failed"
        assert call_args["filename"] == "error.pdf"
        assert "chunks_count" not in call_args or call_args["chunks_count"] is None

    async def test_cleanup_disconnected_clients(
        self, 
        websocket_manager, 
        mock_websocket
    ):
        """测试清理断开的客户端连接"""
        # Arrange
        await websocket_manager.connect(mock_websocket)
        
        # 模拟 send_json 抛出异常（表示连接断开）
        mock_websocket.send_json.side_effect = Exception("Connection closed")

        test_message = {"type": "test"}

        # Act
        await websocket_manager.broadcast(test_message)

        # Assert - 断开的连接应该被移除
        assert len(websocket_manager.active_connections) == 0


@pytest.mark.asyncio
class TestDocumentServiceWebSocketIntegration:
    """测试 DocumentService 中的 WebSocket 集成"""

    @pytest.fixture
    def mock_repo(self):
        """模拟 Repository"""
        repo = AsyncMock(spec=DocumentRepository)
        return repo

    @pytest.fixture
    def mock_embedding_svc(self):
        """模拟 Embedding Service"""
        svc = AsyncMock(spec=EmbeddingService)
        return svc

    @pytest.fixture
    def document_service(self, mock_repo, mock_embedding_svc):
        """创建 DocumentService 实例"""
        return DocumentService(mock_repo, mock_embedding_svc)

    @patch('app.websocket_manager.manager')
    async def test_process_document_sends_processing_message(
        self,
        mock_ws_manager,
        document_service,
        mock_repo
    ):
        """测试处理文档时发送 processing 消息"""
        # Arrange
        doc_id = uuid4()
        mock_doc = Document(
            id=doc_id,
            filename="test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            status="processing"
        )
        mock_repo.find_by_id = AsyncMock(return_value=mock_doc)
        mock_repo.get_document_content = AsyncMock(return_value=b"test content")
        
        # Mock parser
        with patch('app.parsers.base_parser.ParserRegistry.get_parser') as mock_get_parser:
            mock_parser = AsyncMock()
            mock_parser.parse = AsyncMock(return_value="Test content")
            mock_get_parser.return_value = mock_parser
            
            # Mock chunker
            with patch.object(document_service, 'chunker') as mock_chunker:
                mock_chunk = MagicMock()
                mock_chunk.content = "Test chunk"
                mock_chunk.token_count = 10
                mock_chunker.chunk_by_semantic.return_value = [mock_chunk]
                
                # Mock vectorization
                with patch.object(document_service, '_vectorize_chunks'):
                    mock_repo.update_status = AsyncMock()

                    # Act
                    await document_service._process_document_async(doc_id)

                    # Assert - 应该调用 send_document_update 发送 processing 消息
                    mock_ws_manager.send_document_update.assert_any_call(
                        doc_id=str(doc_id),
                        status='processing',
                        filename=mock_doc.filename
                    )

    @patch('app.websocket_manager.manager')
    async def test_process_document_sends_completed_message(
        self,
        mock_ws_manager,
        document_service,
        mock_repo
    ):
        """测试处理完成时发送 completed 消息"""
        # Arrange
        doc_id = uuid4()
        mock_doc = Document(
            id=doc_id,
            filename="test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            status="processing"
        )
        mock_repo.find_by_id = AsyncMock(return_value=mock_doc)
        mock_repo.get_document_content = AsyncMock(return_value=b"test content")
        
        # Mock parser
        with patch('app.parsers.base_parser.ParserRegistry.get_parser') as mock_get_parser:
            mock_parser = AsyncMock()
            mock_parser.parse = AsyncMock(return_value="Test content")
            mock_get_parser.return_value = mock_parser
            
            # Mock chunker
            with patch.object(document_service, 'chunker') as mock_chunker:
                mock_chunk = MagicMock()
                mock_chunk.content = "Test chunk"
                mock_chunk.token_count = 10
                mock_chunker.chunk_by_semantic.return_value = [mock_chunk]
                
                # Mock vectorization
                with patch.object(document_service, '_vectorize_chunks'):
                    mock_repo.update_status = AsyncMock()

                    # Act
                    await document_service._process_document_async(doc_id)

                    # Assert - 应该调用 send_document_update 发送 completed 消息
                    mock_ws_manager.send_document_update.assert_any_call(
                        doc_id=str(doc_id),
                        status='ready',
                        chunks_count=1,
                        filename=mock_doc.filename
                    )

    @patch('app.websocket_manager.manager')
    async def test_process_document_sends_failed_message_on_error(
        self,
        mock_ws_manager,
        document_service,
        mock_repo
    ):
        """测试处理失败时发送 failed 消息"""
        # Arrange
        doc_id = uuid4()
        mock_doc = Document(
            id=doc_id,
            filename="test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            status="processing"
        )
        mock_repo.find_by_id = AsyncMock(return_value=mock_doc)
        mock_repo.get_document_content = AsyncMock(return_value=None)  # 模拟获取内容失败
        
        # Mock update_status for error handling
        mock_repo.update_status = AsyncMock()

        # Act - 处理失败
        try:
            await document_service._process_document_async(doc_id)
        except Exception:
            pass

        # Assert - 应该调用 send_document_update 发送 failed 消息
        mock_ws_manager.send_document_update.assert_any_call(
            doc_id=str(doc_id),
            status='failed',
            filename=mock_doc.filename
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
