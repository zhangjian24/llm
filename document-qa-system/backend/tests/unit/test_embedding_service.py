"""
EmbeddingService 单元测试
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import httpx
from app.services.embedding_service import EmbeddingService
from app.exceptions import RetrievalException


class TestEmbeddingService:
    """EmbeddingService 单元测试"""
    
    @pytest.fixture
    def embedding_service(self):
        """创建 EmbeddingService 实例"""
        return EmbeddingService()
    
    @pytest.mark.asyncio
    async def test_embed_text_success(self, embedding_service):
        """测试单文本向量化成功"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {'embedding': [0.1] * 1536}
            ]
        }
        
        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            # Act
            embedding = await embedding_service.embed_text("测试文本")
            
            # Assert
            assert len(embedding) == 1536
            assert all(isinstance(v, float) for v in embedding)
            mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_embed_text_api_error(self, embedding_service):
        """测试 API 返回错误"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 401
        
        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            # Act & Assert
            with pytest.raises(RetrievalException) as exc_info:
                await embedding_service.embed_text("测试文本")
            
            assert "Embedding API 返回错误" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_embed_text_network_error(self, embedding_service):
        """测试网络请求失败"""
        # Arrange
        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.RequestError("Network error")
            
            # Act & Assert
            with pytest.raises(RetrievalException) as exc_info:
                await embedding_service.embed_text("测试文本")
            
            assert "Embedding API 请求失败" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_embed_batch_success(self, embedding_service):
        """测试批量向量化成功"""
        # Arrange
        texts = ["文本 1", "文本 2", "文本 3"]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {'embedding': [0.1] * 1536},
                {'embedding': [0.2] * 1536},
                {'embedding': [0.3] * 1536}
            ]
        }
        
        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            # Act
            embeddings = await embedding_service.embed_batch(texts)
            
            # Assert
            assert len(embeddings) == 3
            assert all(len(emb) == 1536 for emb in embeddings)
            assert embeddings[0][0] == 0.1
            assert embeddings[1][0] == 0.2
            assert embeddings[2][0] == 0.3
    
    @pytest.mark.asyncio
    async def test_embed_batch_large_input(self, embedding_service):
        """测试大批量输入（需要分批处理）"""
        # Arrange
        texts = [f"文本{i}" for i in range(70)]  # 超过 batch_size=32
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [{'embedding': [0.1] * 1536} for _ in range(32)]
        }
        
        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            # Act
            embeddings = await embedding_service.embed_batch(texts, batch_size=32)
            
            # Assert
            assert len(embeddings) == 70
            # 应该调用 3 次 API (32+32+6)
            assert mock_post.call_count == 3
    
    @pytest.mark.asyncio
    async def test_embed_batch_partial_failure(self, embedding_service):
        """测试批量处理中某批次失败"""
        # Arrange
        texts = ["文本 1", "文本 2"]
        
        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            # 第一次成功，第二次失败
            mock_response1 = Mock()
            mock_response1.status_code = 200
            mock_response1.json.return_value = {'data': [{'embedding': [0.1] * 1536}]}
            
            mock_post.side_effect = [
                mock_response1,
                httpx.RequestError("Timeout")
            ]
            
            # Act & Assert
            with pytest.raises(RetrievalException) as exc_info:
                await embedding_service.embed_batch(texts)
            
            assert "批量 Embedding 失败" in str(exc_info.value)
    
    def test_embedding_service_initialization(self, embedding_service):
        """测试服务初始化"""
        # Assert
        assert embedding_service.api_key is not None
        assert embedding_service.base_url is not None
        assert embedding_service.model == "text-embedding-v4"
