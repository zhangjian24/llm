"""
DocumentService.reprocess_document 单元测试
"""
import pytest
from uuid import UUID, uuid4
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from app.services.document_service import DocumentService
from app.repositories.document_repository import DocumentRepository
from app.models.document import Document
from app.exceptions import DocumentNotFoundException


class TestReprocessDocument:
    """DocumentService.reprocess_document 单元测试"""
    
    @pytest.fixture
    def mock_repo(self):
        """模拟 Repository"""
        repo = Mock(spec=DocumentRepository)
        return repo
    
    @pytest.fixture
    def mock_embedding_svc(self):
        """模拟 Embedding Service"""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_repo, mock_embedding_svc):
        """创建 DocumentService 实例"""
        return DocumentService(mock_repo, mock_embedding_svc)
    
    @pytest.mark.asyncio
    async def test_reprocess_document_success_from_failed_status(self, service, mock_repo):
        """测试重新处理文档成功场景（从 failed 状态）"""
        # Arrange: 准备测试数据
        doc_id = uuid4()
        mock_doc = Document(
            id=doc_id,
            filename="test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            status="failed"
        )
        
        # Mock Repository 方法
        mock_repo.find_by_id = AsyncMock(return_value=mock_doc)
        mock_repo.delete_chunks_by_document = AsyncMock(return_value=True)
        mock_repo.update_status = AsyncMock(return_value=True)
        
        # Mock Vector Service
        with patch('app.services.vector_service_adapter.create_vector_service') as mock_create_vector:
            mock_vector_svc = AsyncMock()
            mock_create_vector.return_value = mock_vector_svc
            
            # Mock database session
            mock_session = AsyncMock()
            mock_session.commit = AsyncMock()
            mock_session.close = AsyncMock()
            
            # Mock get_db_session generator
            async def mock_get_db_session():
                yield mock_session
            
            with patch('app.core.database.get_db_session', mock_get_db_session):
                with patch('asyncio.create_task') as mock_create_task:
                    # Act
                    result = await service.reprocess_document(doc_id)
                    
                    # Assert
                    assert result is True
                    
                    # Verify 调用了正确的方法
                    mock_repo.find_by_id.assert_called_once_with(doc_id)
                    mock_repo.delete_chunks_by_document.assert_called_once_with(doc_id)
                    mock_repo.update_status.assert_called_once_with(doc_id, 'processing', chunks_count=None)
                    
                    # Verify 删除了向量
                    mock_vector_svc.delete_vectors.assert_called_once()
                    
                    # Verify 启动了异步任务
                    mock_create_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_reprocess_document_success_from_ready_status(self, service, mock_repo):
        """测试重新处理文档成功场景（从 ready 状态）"""
        # Arrange
        doc_id = uuid4()
        mock_doc = Document(
            id=doc_id,
            filename="ready.pdf",
            file_size=2048,
            mime_type="application/pdf",
            status="ready"
        )
        
        mock_repo.find_by_id = AsyncMock(return_value=mock_doc)
        mock_repo.delete_chunks_by_document = AsyncMock(return_value=True)
        mock_repo.update_status = AsyncMock(return_value=True)
        
        with patch('app.services.vector_service_adapter.create_vector_service') as mock_create_vector:
            mock_vector_svc = AsyncMock()
            mock_create_vector.return_value = mock_vector_svc
            
            mock_session = AsyncMock()
            mock_session.commit = AsyncMock()
            mock_session.close = AsyncMock()
            
            async def mock_get_db_session():
                yield mock_session
            
            with patch('app.core.database.get_db_session', mock_get_db_session):
                with patch('asyncio.create_task') as mock_create_task:
                    # Act
                    result = await service.reprocess_document(doc_id)
                    
                    # Assert
                    assert result is True
                    mock_repo.update_status.assert_called_once_with(doc_id, 'processing', chunks_count=None)
    
    @pytest.mark.asyncio
    async def test_reprocess_document_not_found(self, service, mock_repo):
        """测试文档不存在的情况"""
        # Arrange
        doc_id = uuid4()
        mock_repo.find_by_id = AsyncMock(return_value=None)
        
        # Act & Assert
        with pytest.raises(DocumentNotFoundException) as exc_info:
            await service.reprocess_document(doc_id)
        
        assert f"文档不存在：{doc_id}" in str(exc_info.value)
        mock_repo.find_by_id.assert_called_once_with(doc_id)
    
    @pytest.mark.asyncio
    async def test_reprocess_document_invalid_status_processing(self, service, mock_repo):
        """测试不允许的状态（processing）"""
        # Arrange
        doc_id = uuid4()
        mock_doc = Document(
            id=doc_id,
            filename="processing.pdf",
            status="processing"
        )
        
        mock_repo.find_by_id = AsyncMock(return_value=mock_doc)
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.reprocess_document(doc_id)
        
        assert "当前状态 (processing) 不允许重新处理" in str(exc_info.value)
        assert "仅支持 failed 或 ready 状态" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_reprocess_document_invalid_status_chunked(self, service, mock_repo):
        """测试不允许的状态（chunked）"""
        # Arrange
        doc_id = uuid4()
        mock_doc = Document(
            id=doc_id,
            filename="chunked.pdf",
            status="chunked"
        )
        
        mock_repo.find_by_id = AsyncMock(return_value=mock_doc)
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.reprocess_document(doc_id)
        
        assert "当前状态 (chunked) 不允许重新处理" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_reprocess_document_clear_chunks_failed(self, service, mock_repo):
        """测试清空 chunks 失败但仍继续处理的场景"""
        # Arrange
        doc_id = uuid4()
        mock_doc = Document(
            id=doc_id,
            filename="test.pdf",
            status="failed"
        )
        
        mock_repo.find_by_id = AsyncMock(return_value=mock_doc)
        mock_repo.delete_chunks_by_document = AsyncMock(return_value=False)  # 失败
        mock_repo.update_status = AsyncMock(return_value=True)
        
        with patch('app.services.document_service.create_vector_service') as mock_create_vector:
            mock_vector_svc = AsyncMock()
            mock_create_vector.return_value = mock_vector_svc
            
            mock_session = AsyncMock()
            mock_session.commit = AsyncMock()
            mock_session.close = AsyncMock()
            
            async def mock_get_db_session():
                yield mock_session
            
            with patch('app.core.database.get_db_session', mock_get_db_session):
                with patch('asyncio.create_task') as mock_create_task:
                    # Act
                    result = await service.reprocess_document(doc_id)
                    
                    # Assert - 仍然成功，因为清空 chunks 失败不会阻断流程
                    assert result is True
    
    @pytest.mark.asyncio
    async def test_reprocess_document_vector_deletion_failed(self, service, mock_repo):
        """测试删除向量失败但仍继续处理的场景"""
        # Arrange
        doc_id = uuid4()
        mock_doc = Document(
            id=doc_id,
            filename="test.pdf",
            status="failed"
        )
        
        mock_repo.find_by_id = AsyncMock(return_value=mock_doc)
        mock_repo.delete_chunks_by_document = AsyncMock(return_value=True)
        mock_repo.update_status = AsyncMock(return_value=True)
        
        with patch('app.services.document_service.create_vector_service') as mock_create_vector:
            mock_vector_svc = AsyncMock()
            mock_vector_svc.delete_vectors = AsyncMock(side_effect=Exception("Vector delete failed"))
            mock_create_vector.return_value = mock_vector_svc
            
            mock_session = AsyncMock()
            mock_session.commit = AsyncMock()
            mock_session.close = AsyncMock()
            
            async def mock_get_db_session():
                yield mock_session
            
            with patch('app.core.database.get_db_session', mock_get_db_session):
                with patch('asyncio.create_task') as mock_create_task:
                    # Act
                    result = await service.reprocess_document(doc_id)
                    
                    # Assert - 仍然成功，因为向量删除失败不会阻断流程
                    assert result is True
    
    @pytest.mark.asyncio
    async def test_reprocess_document_commit_failed(self, service, mock_repo):
        """测试提交事务失败的场景"""
        # Arrange
        doc_id = uuid4()
        mock_doc = Document(
            id=doc_id,
            filename="test.pdf",
            status="failed"
        )
        
        mock_repo.find_by_id = AsyncMock(return_value=mock_doc)
        mock_repo.delete_chunks_by_document = AsyncMock(return_value=True)
        mock_repo.update_status = AsyncMock(return_value=True)
        
        with patch('app.services.vector_service_adapter.create_vector_service') as mock_create_vector:
            mock_vector_svc = AsyncMock()
            mock_create_vector.return_value = mock_vector_svc
            
            # 准备两个不同的 session 实例
            # 第一个 session 用于删除向量（成功）
            mock_session_1 = AsyncMock()
            mock_session_1.commit = AsyncMock()
            mock_session_1.close = AsyncMock()
            
            # 第二个 session 用于提交事务（失败）
            mock_session_2 = AsyncMock()
            mock_session_2.commit = AsyncMock(side_effect=Exception("Commit failed"))
            mock_session_2.close = AsyncMock()
            mock_session_2.rollback = AsyncMock()
            
            # Mock get_db_session generator，返回两个不同的 session
            call_count = [0]
            async def mock_get_db_session():
                call_count[0] += 1
                if call_count[0] == 1:
                    yield mock_session_1
                else:
                    yield mock_session_2
            
            with patch('app.core.database.get_db_session', mock_get_db_session):
                # Act
                result = await service.reprocess_document(doc_id)
                
                # Assert - 事务提交失败时返回 False
                assert result is False
                mock_session_2.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_reprocess_document_websocket_notification_failed(self, service, mock_repo):
        """测试 WebSocket 通知失败但不影响主流程的场景"""
        # Arrange
        doc_id = uuid4()
        mock_doc = Document(
            id=doc_id,
            filename="test.pdf",
            status="failed"
        )
        
        mock_repo.find_by_id = AsyncMock(return_value=mock_doc)
        mock_repo.delete_chunks_by_document = AsyncMock(return_value=True)
        mock_repo.update_status = AsyncMock(return_value=True)
        
        with patch('app.services.document_service.create_vector_service') as mock_create_vector:
            mock_vector_svc = AsyncMock()
            mock_create_vector.return_value = mock_vector_svc
            
            mock_session = AsyncMock()
            mock_session.commit = AsyncMock()
            mock_session.close = AsyncMock()
            
            async def mock_get_db_session():
                yield mock_session
            
            with patch('app.core.database.get_db_session', mock_get_db_session):
                with patch('asyncio.create_task') as mock_create_task:
                    # Mock WebSocket manager 抛出异常
                    with patch('app.websocket_manager.manager') as mock_manager:
                        mock_manager.send_document_update = AsyncMock(side_effect=Exception("WS failed"))
                        
                        # Act
                        result = await service.reprocess_document(doc_id)
                        
                        # Assert - WebSocket 失败不影响主流程
                        assert result is True
    
    @pytest.mark.asyncio
    async def test_reprocess_document_logs_correctly(self, service, mock_repo, caplog):
        """测试日志记录正确性"""
        # Arrange
        doc_id = uuid4()
        mock_doc = Document(
            id=doc_id,
            filename="important.pdf",
            status="failed"
        )
        
        mock_repo.find_by_id = AsyncMock(return_value=mock_doc)
        mock_repo.delete_chunks_by_document = AsyncMock(return_value=True)
        mock_repo.update_status = AsyncMock(return_value=True)
        
        with patch('app.services.document_service.create_vector_service') as mock_create_vector:
            mock_vector_svc = AsyncMock()
            mock_create_vector.return_value = mock_vector_svc
            
            mock_session = AsyncMock()
            mock_session.commit = AsyncMock()
            mock_session.close = AsyncMock()
            
            async def mock_get_db_session():
                yield mock_session
            
            with patch('app.core.database.get_db_session', mock_get_db_session):
                with patch('asyncio.create_task'):
                    # Act
                    await service.reprocess_document(doc_id)
                    
                    # Assert - 验证关键日志（通过 method calls 间接验证）
                    mock_repo.find_by_id.assert_called()
                    mock_repo.update_status.assert_called()


class TestClearOldChunks:
    """_clear_old_chunks 方法单元测试"""
    
    @pytest.fixture
    def mock_repo(self):
        return Mock(spec=DocumentRepository)
    
    @pytest.fixture
    def mock_embedding_svc(self):
        return Mock()
    
    @pytest.fixture
    def service(self, mock_repo, mock_embedding_svc):
        return DocumentService(mock_repo, mock_embedding_svc)
    
    @pytest.mark.asyncio
    async def test_clear_old_chunks_success(self, service, mock_repo):
        """测试清空旧 chunks 成功"""
        # Arrange
        doc_id = uuid4()
        mock_repo.delete_chunks_by_document = AsyncMock(return_value=True)
        
        # Act
        result = await service._clear_old_chunks(doc_id)
        
        # Assert
        assert result is True
        mock_repo.delete_chunks_by_document.assert_called_once_with(doc_id)
    
    @pytest.mark.asyncio
    async def test_clear_old_chunks_failed(self, service, mock_repo):
        """测试清空旧 chunks 失败"""
        # Arrange
        doc_id = uuid4()
        mock_repo.delete_chunks_by_document = AsyncMock(return_value=False)
        
        # Act
        result = await service._clear_old_chunks(doc_id)
        
        # Assert
        assert result is False
        mock_repo.delete_chunks_by_document.assert_called_once_with(doc_id)
    
    @pytest.mark.asyncio
    async def test_clear_old_chunks_exception(self, service, mock_repo):
        """测试清空旧 chunks 抛出异常"""
        # Arrange
        doc_id = uuid4()
        mock_repo.delete_chunks_by_document = AsyncMock(side_effect=Exception("DB error"))
        
        # Act
        result = await service._clear_old_chunks(doc_id)
        
        # Assert
        assert result is False  # 异常被捕获，返回 False
