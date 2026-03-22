"""
pytest 配置和 fixtures
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db_session
from typing import AsyncGenerator
import os


# 测试数据库 URL (优先使用 PostgreSQL，与生产环境一致)
# 从 .env.local 读取 DATABASE_URL 配置
import os
from dotenv import load_dotenv

# 加载 .env.local 配置
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))

# 使用实际配置的数据库 URL（PostgreSQL）
TEST_DATABASE_URL = os.getenv("DATABASE_URL")

# 如果没有配置，则使用内存中的 SQLite（仅用于简单测试，不支持 JSONB）
if not TEST_DATABASE_URL:
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    print("⚠️ 警告：未找到 DATABASE_URL 配置，使用 SQLite 进行测试（部分功能可能不可用）")
else:
    print(f"✅ 使用 PostgreSQL 数据库进行测试：{TEST_DATABASE_URL[:50]}...")


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_engine():
    """创建测试数据库引擎"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )
    
    # 创建所有表
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # 清理
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """创建测试数据库会话"""
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()  # 确保不回滚影响其他测试


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """创建测试客户端"""
    # 覆盖依赖注入的数据库会话
    async def override_get_db_session():
        yield db_session
    
    app.dependency_overrides[get_db_session] = override_get_db_session
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    # 清理依赖覆盖
    app.dependency_overrides.clear()
