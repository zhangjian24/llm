"""
pytest 测试配置
"""
import pytest
from unittest.mock import AsyncMock, Mock
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


@pytest.fixture
def mock_db_session():
    """模拟数据库会话"""
    session = Mock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.add = Mock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_embedding_service():
    """模拟嵌入向量化服务"""
    service = Mock()
    service.embed_text = AsyncMock(return_value=[0.1] * 1536)
    service.embed_batch = AsyncMock(return_value=[[0.1] * 1536])
    return service


@pytest.fixture
def mock_parser_registry():
    """模拟解析器注册表"""
    registry = Mock()
    parser_instance = Mock()
    parser_instance.parse = AsyncMock(return_value="测试文本内容")
    registry.get_parser = Mock(return_value=parser_instance)
    registry.is_supported = Mock(return_value=True)
    return registry
