"""
DocumentService 单元测试
"""
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, Mock, patch
from app.services.document_service import DocumentService
from app.exceptions import FileTooLargeError, UnsupportedFileTypeError
from app.models.document import Document


class TestDocumentService:
    """DocumentService 单元测试类"""
    
    @pytest.fixture
    def mock_repo(self):
        """模拟文档仓库"""
        repo = Mock()
        repo.save = AsyncMock(return_value=uuid4())
        repo.find_by_id = AsyncMock(return_value=None)
        repo.update_status = AsyncMock(return_value=True)
        repo.delete = AsyncMock(return_value=True)
        repo.save_chunk = AsyncMock()
        return repo
    
    @pytest.fixture
    def mock_embedding_svc(self):
        """模拟嵌入服务"""
        embedding_svc = Mock()
        embedding_svc.embed_text = AsyncMock(return_value=[0.1] * 1536)
        embedding_svc.embed_batch = AsyncMock(return_value=[[0.1] * 1536])
        return embedding_svc
    
    @pytest.fixture
    def service(self, mock_repo, mock_embedding_svc):
        """创建文档服务实例"""
        return DocumentService(mock_repo, mock_embedding_svc)
    
    @pytest.mark.asyncio
    async def test_upload_document_success(self, service, mock_repo):
        """测试文档上传成功"""
        # Arrange
        file_content = b"test content"
        filename = "test.pdf"
        mime_type = "application/pdf"
        file_size = 1024 * 100  # 100KB
        
        with patch('app.services.document_service.ParserRegistry') as mock_registry:
            mock_registry.is_supported.return_value = True
            
            # Act
            doc_id = await service.upload_document(
                file_content, filename, mime_type, file_size
            )
            
            # Assert
            assert doc_id is not None
            mock_repo.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_upload_document_file_too_large(self, service):
        """测试文件过大抛出异常"""
        # Arrange
        file_content = b"x" * (60 * 1024 * 1024)  # 60MB
        filename = "large.pdf"
        mime_type = "application/pdf"
        file_size = len(file_content)
        
        # Act & Assert
        with pytest.raises(FileTooLargeError):
            await service.upload_document(
                file_content, filename, mime_type, file_size
            )
    
    @pytest.mark.asyncio
    async def test_upload_document_unsupported_type(self, service):
        """测试不支持的文件类型"""
        # Arrange
        file_content = b"test"
        filename = "test.png"
        mime_type = "image/png"
        file_size = 1024
        
        with patch('app.services.document_service.ParserRegistry') as mock_registry:
            mock_registry.is_supported.return_value = False
            
            # Act & Assert
            with pytest.raises(UnsupportedFileTypeError):
                await service.upload_document(
                    file_content, filename, mime_type, file_size
                )
    
    @pytest.mark.asyncio
    async def test_get_document_list(self, service, mock_repo):
        """测试获取文档列表"""
        # Arrange
        mock_docs = [
            Document(
                id=uuid4(),
                filename="test1.pdf",
                file_path="/path/to/file1",
                file_size=1024,
                mime_type="application/pdf",
                status="ready"
            )
        ]
        mock_repo.find_all = AsyncMock(return_value=(mock_docs, 1))
        
        # Act
        docs, total = await service.get_document_list(page=1, limit=10)
        
        # Assert
        assert len(docs) == 1
        assert total == 1
        mock_repo.find_all.assert_called_once_with(1, 10, None)
    
    @pytest.mark.asyncio
    async def test_delete_document_success(self, service, mock_repo):
        """测试删除文档成功"""
        # Arrange
        doc_id = uuid4()
        mock_repo.delete = AsyncMock(return_value=True)
        
        # Act
        result = await service.delete_document(doc_id)
        
        # Assert
        assert result is True
        mock_repo.delete.assert_called_once_with(doc_id)
    
    @pytest.mark.asyncio
    async def test_document_processing_async(self, service, mock_repo):
        """测试异步处理文档流程"""
        # Arrange
        doc_id = uuid4()
        mock_doc = Document(
            id=doc_id,
            filename="test.pdf",
            file_path="/tmp/test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            status="processing"
        )
        mock_repo.find_by_id = AsyncMock(return_value=mock_doc)
        
        with patch('app.services.document_service.aiofiles'):
            with patch('app.services.document_service.ParserRegistry') as mock_registry:
                mock_parser = Mock()
                mock_parser.parse = AsyncMock(return_value="测试内容")
                mock_registry.get_parser.return_value = mock_parser
                
                # Act
                await service._process_document_async(doc_id)
                
                # Assert
                mock_repo.update_status.assert_called()
