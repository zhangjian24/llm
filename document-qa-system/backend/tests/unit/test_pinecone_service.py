"""
PineconeService 单元测试（完全 Mock 模式）

注意：由于 Pinecone SDK v8 API 重大变更，本测试使用完全 Mock 模式
不依赖实际 Pinecone SDK，专注于业务逻辑验证
"""
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from app.exceptions import RetrievalException


class TestPineconeService:
    """PineconeService 单元测试"""
    
    @pytest.fixture
    def mock_index(self):
        """Mock Pinecone Index"""
        index = MagicMock()
        # 同步方法直接返回值（会被 asyncio.to_thread 调用）
        index.upsert.return_value = {'upserted_count': 2}
        index.query.return_value = {'matches': []}
        index.delete.return_value = None
        index.describe_index_stats.return_value = {'total_vector_count': 12345}
        return index
    
    @pytest.fixture
    def mock_client(self, mock_index):
        """Mock Pinecone Client"""
        client = MagicMock()
        # 关键修复：让 Index() 方法返回配置好的 mock_index
        client.Index = MagicMock(return_value=mock_index)
        client.list_indexes = Mock(return_value=[])
        client.create_index = Mock()
        return client
    
    @pytest.fixture
    def pinecone_service(self, mock_client):
        """创建 PineconeService 实例（使用完全 Mock）"""
        # 在导入前就 Mock 掉 pinecone 模块
        import sys
        sys.modules['pinecone'] = MagicMock()
        sys.modules['pinecone'].Pinecone = MagicMock(return_value=mock_client)
        sys.modules['pinecone'].ServerlessSpec = MagicMock()
        
        # 现在可以安全导入了
        from app.services.pinecone_service import PineconeService
        service = PineconeService()
        yield service
    
    def test_initialization(self, pinecone_service):
        """测试服务初始化"""
        assert pinecone_service.api_key is not None
        assert pinecone_service.index_name is not None
        assert pinecone_service.dimension == 1024  # text-embedding-v4 实际输出维度
    
    def test_index_lazy_loading(self, pinecone_service, mock_index):
        """测试 Index 懒加载"""
        # 初始时 _index 应该为 None
        assert pinecone_service._index is None
        
        # 访问 index 属性时触发懒加载
        result = pinecone_service.index
        
        # 验证返回了 mock_index
        assert result is mock_index
        assert pinecone_service._index is mock_index
    
    @pytest.mark.asyncio
    async def test_create_index_if_not_exists_new(self, pinecone_service, mock_client):
        """测试创建新 Index"""
        # 模拟 Index 不存在
        mock_client.list_indexes.return_value = []
        
        # Act
        await pinecone_service.create_index_if_not_exists()
        
        # Assert
        mock_client.create_index.assert_called_once()
        call_args = mock_client.create_index.call_args
        assert call_args[1]['name'] == pinecone_service.index_name
        assert call_args[1]['dimension'] == 1024  # text-embedding-v4 实际输出维度
        assert call_args[1]['metric'] == "cosine"
    
    @pytest.mark.asyncio
    async def test_create_index_if_not_exists_already_exists(self, pinecone_service, mock_client):
        """测试 Index 已存在的情况"""
        # 模拟 Index 已存在
        existing_index = MagicMock()
        existing_index.name = pinecone_service.index_name
        mock_client.list_indexes.return_value = [existing_index]
        
        # Act
        await pinecone_service.create_index_if_not_exists()
        
        # Assert - 不应调用 create_index
        mock_client.create_index.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_upsert_vectors_success(self, pinecone_service, mock_index):
        """测试向量 upsert 成功"""
        vectors = [
            {"id": "chunk_1", "values": [0.1] * 1536, "metadata": {"text": "测试 1"}},
            {"id": "chunk_2", "values": [0.2] * 1536, "metadata": {"text": "测试 2"}}
        ]
        
        # Act
        await pinecone_service.upsert_vectors(vectors)
        
        # Assert
        mock_index.upsert.assert_called_once_with(
            vectors=vectors,
            namespace="default"
        )
    
    @pytest.mark.asyncio
    async def test_upsert_vectors_custom_namespace(self, pinecone_service, mock_index):
        """测试自定义 namespace 的 upsert"""
        vectors = [{"id": "chunk_1", "values": [0.1] * 1536}]
        
        # Act
        await pinecone_service.upsert_vectors(vectors, namespace="custom_ns")
        
        # Assert
        mock_index.upsert.assert_called_once_with(
            vectors=vectors,
            namespace="custom_ns"
        )
    
    @pytest.mark.asyncio
    async def test_query_similar_success(self, pinecone_service, mock_index):
        """测试相似度搜索成功"""
        query_vector = [0.1] * 1536
        mock_response = {
            'matches': [
                {'id': 'chunk_1', 'score': 0.95, 'metadata': {'text': '相关文档 1'}},
                {'id': 'chunk_2', 'score': 0.85, 'metadata': {'text': '相关文档 2'}}
            ]
        }
        mock_index.query.return_value = mock_response
        
        # Act
        results = await pinecone_service.similarity_search(
            query_vector=query_vector, 
            top_k=2,
            filter_dict=None
        )
        
        # Assert
        assert len(results) == 2
        assert results[0]['id'] == 'chunk_1'
        assert results[0]['score'] == 0.95
        mock_index.query.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_query_similar_with_filter(self, pinecone_service, mock_index):
        """测试带过滤条件的相似度搜索"""
        query_vector = [0.1] * 1536
        filter_condition = {"doc_id": {"$eq": "doc_123"}}
        mock_index.query.return_value = {'matches': []}
        
        # Act
        await pinecone_service.similarity_search(
            query_vector=query_vector, 
            top_k=5, 
            filter_dict=filter_condition
        )
        
        # Assert
        call_args = mock_index.query.call_args
        assert call_args[1]['filter'] == filter_condition
        # similarity_search 方法不直接传递 namespace，而是通过 index 属性访问
    
    @pytest.mark.asyncio
    async def test_delete_vectors_by_ids_success(self, pinecone_service, mock_index):
        """测试按 ID 删除向量"""
        vector_ids = ["chunk_1", "chunk_2", "chunk_3"]
        
        # Act
        await pinecone_service.delete_vectors(vector_ids)
        
        # Assert
        mock_index.delete.assert_called_once_with(
            ids=vector_ids,
            namespace="default"
        )
    
    @pytest.mark.asyncio
    async def test_delete_vectors_all(self, pinecone_service, mock_index):
        """测试删除所有向量"""
        # Act
        await pinecone_service.delete_vectors(delete_all=True)
        
        # Assert
        mock_index.delete.assert_called_once_with(
            delete_all=True,
            namespace="default"
        )
    
    @pytest.mark.asyncio
    async def test_get_index_stats(self, pinecone_service, mock_index):
        """测试获取 Index 统计信息"""
        # 设置 mock 返回值
        mock_index.describe_index_stats.return_value = {'total_vector_count': 12345}
        
        # Act
        stats = await pinecone_service.get_index_stats()
        
        # Assert
        assert stats['total_vector_count'] == 12345
        mock_index.describe_index_stats.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_similarity_search_error_handling(self, pinecone_service, mock_index):
        """测试相似度搜索的错误处理"""
        # 模拟 Pinecone API 错误
        mock_index.query.side_effect = Exception("Pinecone error")
        
        # Act & Assert
        with pytest.raises(RetrievalException) as exc_info:
            await pinecone_service.similarity_search([0.1] * 1024)
        
        # 检查异常类型和根本原因
        assert isinstance(exc_info.value, RetrievalException)
        assert "检索失败" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_index_error_handling(self, pinecone_service, mock_client):
        """测试创建 Index 的错误处理"""
        # 模拟创建失败
        mock_client.list_indexes.side_effect = Exception("API error")
        
        # Act & Assert
        with pytest.raises(RetrievalException) as exc_info:
            await pinecone_service.create_index_if_not_exists()
        
        # 检查异常类型 - 只要是 RetrievalException 即可
        assert isinstance(exc_info.value, RetrievalException)
