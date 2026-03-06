"""
PineconeService v8 单元测试
测试 Pinecone SDK v8 (5.1+) 的重构代码

注意：此测试使用完全 Mock 模式，避免数据库和外部服务依赖
"""
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
import sys
from app.exceptions import RetrievalException


class TestPineconeServiceV8:
    """PineconeService v8 单元测试"""
    
    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """在所有测试前设置 Mock"""
        # Mock pinecone 模块的 v8 API
        mock_pinecone_module = MagicMock()
        mock_client = MagicMock()
        mock_index = MagicMock()
        
        # 设置同步方法（Pinecone SDK v8 的 Index 方法是同步的）
        mock_index.upsert = MagicMock(return_value={'upserted_count': 2})
        mock_index.query = MagicMock(return_value={'matches': []})
        mock_index.delete = MagicMock()
        mock_index.describe_index_stats = MagicMock(return_value={'total_vector_count': 12345})
        
        mock_client.Index.return_value = mock_index
        mock_client.list_indexes = MagicMock(return_value=[])
        mock_client.create_index = MagicMock()
        
        mock_pinecone_module.Pinecone = MagicMock(return_value=mock_client)
        mock_pinecone_module.ServerlessSpec = MagicMock()
        mock_pinecone_module.CloudProvider = MagicMock()
        mock_pinecone_module.AwsRegion = MagicMock()
        mock_pinecone_module.VectorType = MagicMock()
        
        # Mock pinecone 模块
        self.pinecone_patcher = patch.dict('sys.modules', {'pinecone': mock_pinecone_module})
        self.pinecone_patcher.start()
        
        # Store mocks for test access
        self.mock_client = mock_client
        self.mock_index = mock_index
        
        yield
        
        self.pinecone_patcher.stop()
    
    @pytest.fixture
    def pinecone_service_v8(self):
        """创建 PineconeService v8 实例"""
        from app.services.pinecone_service import PineconeService
        service = PineconeService()
        yield service
    
    def test_initialization_v8(self, pinecone_service_v8):
        """测试 v8 SDK 服务初始化"""
        assert pinecone_service_v8.api_key is not None
        assert pinecone_service_v8.index_name is not None
        assert pinecone_service_v8.dimension == 1536
    
    def test_sdk_v8_imports(self, pinecone_service_v8):
        """测试 v8 SDK 的正确导入"""
        # 验证 v8 API 组件已正确导入
        assert hasattr(pinecone_service_v8, 'Pinecone')
        assert hasattr(pinecone_service_v8, 'ServerlessSpec')
        assert hasattr(pinecone_service_v8, 'CloudProvider')
        assert hasattr(pinecone_service_v8, 'AwsRegion')
        assert hasattr(pinecone_service_v8, 'VectorType')
    
    def test_index_lazy_loading_v8(self, pinecone_service_v8):
        """测试 Index 懒加载（v8 API）"""
        # 初始时 _index 应该为 None
        assert pinecone_service_v8._index is None
        
        # 访问 index 属性时触发懒加载
        result = pinecone_service_v8.index
        
        # 验证返回了 mock_index
        assert result is self.mock_index
        assert pinecone_service_v8._index is self.mock_index
    
    @pytest.mark.asyncio
    async def test_create_index_v8_api(self, pinecone_service_v8):
        """测试使用 v8 API 创建索引"""
        # 模拟 Index 不存在
        self.mock_client.list_indexes.return_value = []
        
        # Act
        await pinecone_service_v8.create_index_if_not_exists()
        
        # Assert - 验证调用了 create_index
        self.mock_client.create_index.assert_called_once()
        call_args = self.mock_client.create_index.call_args
        
        # 验证 v8 API 参数
        assert call_args[1]['name'] == pinecone_service_v8.index_name
        assert call_args[1]['dimension'] == 1536
        assert call_args[1]['metric'] == "cosine"
        assert 'spec' in call_args[1]
        assert 'vector_type' in call_args[1]
    
    @pytest.mark.asyncio
    async def test_upsert_vectors_v8(self, pinecone_service_v8):
        """测试向量 upsert（v8 API）"""
        vectors = [
            ("chunk_1", [0.1] * 1536, {"metadata": "value1"}),
            ("chunk_2", [0.2] * 1536, {"metadata": "value2"})
        ]
        
        # Act
        await pinecone_service_v8.upsert_vectors(vectors)
        
        # Assert
        self.mock_index.upsert.assert_called_once_with(vectors=vectors, namespace="default")
    
    @pytest.mark.asyncio
    async def test_query_similar_v8(self, pinecone_service_v8):
        """测试相似度搜索（v8 API）"""
        query_vector = [0.1] * 1536
        mock_response = {
            'matches': [
                {'id': 'chunk_1', 'score': 0.95, 'metadata': {'text': '相关文档 1'}},
                {'id': 'chunk_2', 'score': 0.85, 'metadata': {'text': '相关文档 2'}}
            ]
        }
        self.mock_index.query.return_value = mock_response
        
        # Act
        results = await pinecone_service_v8.similarity_search(query_vector, top_k=2)
        
        # Assert
        assert len(results) == 2
        assert results[0]['id'] == 'chunk_1'
        assert results[0]['score'] == 0.95
        self.mock_index.query.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_vectors_v8(self, pinecone_service_v8):
        """测试删除向量（v8 API）"""
        vector_ids = ["chunk_1", "chunk_2", "chunk_3"]
        
        # Act
        await pinecone_service_v8.delete_vectors(ids=vector_ids)
        
        # Assert
        self.mock_index.delete.assert_called_once_with(ids=vector_ids, namespace="default")
    
    @pytest.mark.asyncio
    async def test_get_vector_count_v8(self, pinecone_service_v8):
        """测试获取向量数量（v8 API）"""
        # Act
        stats = await pinecone_service_v8.get_index_stats()
        
        # Assert
        assert stats['total_vector_count'] == 12345
        self.mock_index.describe_index_stats.assert_called_once()
