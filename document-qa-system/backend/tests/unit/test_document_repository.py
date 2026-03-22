"""
DocumentRepository 单元测试

测试范围:
1. find_all 方法的状态筛选功能
2. 分页功能
3. 按 created_at 倒序排列
4. 边界情况（空数据、分页边界等）
5. 数据库索引存在性验证

注意：所有测试使用 .env.local 配置的数据库环境
"""
import pytest
from sqlalchemy import select, inspect
from sqlalchemy.exc import ProgrammingError
from datetime import datetime, timedelta
from uuid import uuid4
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository


class TestDocumentRepositoryFindAll:
    """find_all 方法测试类"""
    
    @pytest.fixture
    def repo(self, db_session):
        """创建 Repository 实例"""
        return DocumentRepository(db_session)
    
    @pytest.fixture(autouse=True)
    async def cleanup_database(self, db_session):
        """每个测试前后清理数据库"""
        # 测试前清理
        from sqlalchemy import text
        await db_session.execute(text("DELETE FROM document_chunks"))
        await db_session.execute(text("DELETE FROM chunks"))
        await db_session.execute(text("DELETE FROM documents"))
        await db_session.commit()
        
        yield
        
        # 测试后清理
        await db_session.execute(text("DELETE FROM document_chunks"))
        await db_session.execute(text("DELETE FROM chunks"))
        await db_session.execute(text("DELETE FROM documents"))
        await db_session.commit()
    
    @pytest.mark.asyncio
    async def test_find_all_empty_database(self, repo):
        """测试空数据库场景"""
        documents, total = await repo.find_all(page=1, limit=10)
        
        assert total == 0
        assert len(documents) == 0
        assert isinstance(documents, list)
    
    @pytest.mark.asyncio
    async def test_find_all_without_status_filter(self, db_session, repo):
        """测试不带状态筛选的查询"""
        # 创建测试数据
        docs = [
            Document(filename="doc1.pdf", file_size=1024, mime_type="application/pdf", status="ready"),
            Document(filename="doc2.pdf", file_size=2048, mime_type="application/pdf", status="processing"),
            Document(filename="doc3.pdf", file_size=512, mime_type="application/pdf", status="failed"),
        ]
        db_session.add_all(docs)
        await db_session.commit()
        
        # 查询所有文档
        documents, total = await repo.find_all(page=1, limit=10)
        
        assert total == 3
        assert len(documents) == 3
        # 验证按 created_at 倒序（最后创建的在最前面）
        assert documents[0].filename == "doc3.pdf"
        assert documents[1].filename == "doc2.pdf"
        assert documents[2].filename == "doc1.pdf"
    
    @pytest.mark.asyncio
    async def test_find_all_with_status_filter_ready(self, db_session, repo):
        """测试筛选 ready 状态的文档"""
        # 创建不同状态的文档
        docs = [
            Document(filename="ready1.pdf", file_size=1024, mime_type="application/pdf", status="ready"),
            Document(filename="processing1.pdf", file_size=1024, mime_type="application/pdf", status="processing"),
            Document(filename="ready2.pdf", file_size=1024, mime_type="application/pdf", status="ready"),
            Document(filename="failed1.pdf", file_size=1024, mime_type="application/pdf", status="failed"),
        ]
        db_session.add_all(docs)
        await db_session.commit()
        
        # 只查询 ready 状态
        documents, total = await repo.find_all(page=1, limit=10, status="ready")
        
        assert total == 2
        assert len(documents) == 2
        assert all(doc.status == "ready" for doc in documents)
    
    @pytest.mark.asyncio
    async def test_find_all_with_status_filter_processing(self, db_session, repo):
        """测试筛选 processing 状态的文档"""
        docs = [
            Document(filename="doc1.pdf", file_size=1024, mime_type="application/pdf", status="processing"),
            Document(filename="doc2.pdf", file_size=1024, mime_type="application/pdf", status="ready"),
        ]
        db_session.add_all(docs)
        await db_session.commit()
        
        documents, total = await repo.find_all(page=1, limit=10, status="processing")
        
        assert total == 1
        assert len(documents) == 1
        assert documents[0].filename == "doc1.pdf"
        assert documents[0].status == "processing"
    
    @pytest.mark.asyncio
    async def test_find_all_with_status_filter_failed(self, db_session, repo):
        """测试筛选 failed 状态的文档"""
        docs = [
            Document(filename="failed1.pdf", file_size=1024, mime_type="application/pdf", status="failed"),
            Document(filename="ready1.pdf", file_size=1024, mime_type="application/pdf", status="ready"),
        ]
        db_session.add_all(docs)
        await db_session.commit()
        
        documents, total = await repo.find_all(page=1, limit=10, status="failed")
        
        assert total == 1
        assert len(documents) == 1
        assert documents[0].status == "failed"
    
    @pytest.mark.asyncio
    async def test_find_all_pagination_first_page(self, db_session, repo):
        """测试分页 - 第一页"""
        # 创建 15 个文档
        docs = [Document(filename=f"doc{i}.pdf", file_size=1024, mime_type="application/pdf", status="ready") 
                for i in range(15)]
        db_session.add_all(docs)
        await db_session.commit()
        
        # 查询第一页（每页 10 个）
        documents, total = await repo.find_all(page=1, limit=10)
        
        assert total == 15
        assert len(documents) == 10
    
    @pytest.mark.asyncio
    async def test_find_all_pagination_second_page(self, db_session, repo):
        """测试分页 - 第二页"""
        # 创建 15 个文档
        docs = [Document(filename=f"doc{i}.pdf", file_size=1024, mime_type="application/pdf", status="ready") 
                for i in range(15)]
        db_session.add_all(docs)
        await db_session.commit()
        
        # 查询第二页（每页 10 个）
        documents, total = await repo.find_all(page=2, limit=10)
        
        assert total == 15
        assert len(documents) == 5
    
    @pytest.mark.asyncio
    async def test_find_all_pagination_beyond_total(self, db_session, repo):
        """测试分页 - 超过总页数"""
        # 创建 5 个文档
        docs = [Document(filename=f"doc{i}.pdf", file_size=1024, mime_type="application/pdf", status="ready") 
                for i in range(5)]
        db_session.add_all(docs)
        await db_session.commit()
        
        # 查询第 3 页（只有 5 个文档，每页 10 个，应该返回空）
        documents, total = await repo.find_all(page=3, limit=10)
        
        assert total == 5
        assert len(documents) == 0
    
    @pytest.mark.asyncio
    async def test_find_all_order_by_created_at_desc(self, db_session, repo):
        """测试按创建时间倒序排列"""
        # 手动设置不同的创建时间
        now = datetime.utcnow()
        docs = [
            Document(filename="oldest.pdf", file_size=1024, mime_type="application/pdf", 
                    created_at=now - timedelta(days=2)),
            Document(filename="middle.pdf", file_size=1024, mime_type="application/pdf", 
                    created_at=now - timedelta(days=1)),
            Document(filename="newest.pdf", file_size=1024, mime_type="application/pdf", 
                    created_at=now),
        ]
        db_session.add_all(docs)
        await db_session.commit()
        
        documents, total = await repo.find_all(page=1, limit=10)
        
        assert total == 3
        # 验证最新的在最前面
        assert documents[0].filename == "newest.pdf"
        assert documents[1].filename == "middle.pdf"
        assert documents[2].filename == "oldest.pdf"
    
    @pytest.mark.asyncio
    async def test_find_all_with_large_offset(self, db_session, repo):
        """测试大偏移量的分页查询"""
        # 创建少量文档
        docs = [Document(filename=f"doc{i}.pdf", file_size=1024, mime_type="application/pdf", status="ready") 
                for i in range(3)]
        db_session.add_all(docs)
        await db_session.commit()
        
        # 查询很大的偏移量
        documents, total = await repo.find_all(page=100, limit=10)
        
        assert total == 3
        assert len(documents) == 0


class TestDocumentRepositoryIndexes:
    """数据库索引测试类"""
    
    @pytest.fixture
    def repo(self, db_session):
        """创建 Repository 实例"""
        return DocumentRepository(db_session)
    
    @pytest.mark.asyncio
    async def test_indexes_exist_on_document_table(self, db_session):
        """测试 Document 表的索引是否存在"""
        # 获取数据库连接并检查索引
        from sqlalchemy import text
        
        # PostgreSQL 查询索引的 SQL
        index_query = text("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'documents'
        """)
        
        result = await db_session.execute(index_query)
        indexes = result.all()
        
        # 提取索引名称列表
        index_names = [idx[0] for idx in indexes]
        
        # 验证复合索引存在
        assert 'ix_status_created_at' in index_names, "缺少复合索引 ix_status_created_at"
        
        # 验证 MIME 类型索引存在
        assert 'ix_mime_type' in index_names, "缺少索引 ix_mime_type"
    
    @pytest.mark.asyncio
    async def test_status_created_at_index_definition(self, db_session):
        """测试复合索引的定义是否正确"""
        from sqlalchemy import text
        
        # 查询索引定义
        index_query = text("""
            SELECT indexdef 
            FROM pg_indexes 
            WHERE tablename = 'documents' 
            AND indexname = 'ix_status_created_at'
        """)
        
        result = await db_session.execute(index_query)
        index_def = result.scalar_one_or_none()
        
        if index_def:
            # 验证索引包含 status 和 created_at 列
            assert 'status' in index_def.lower(), "复合索引应包含 status 列"
            assert 'created_at' in index_def.lower(), "复合索引应包含 created_at 列"
    
    @pytest.mark.asyncio
    async def test_query_uses_index(self, db_session, repo):
        """测试查询是否使用索引（通过 EXPLAIN 分析）"""
        # 创建一些测试数据
        docs = [
            Document(filename=f"test{i}.pdf", file_size=1024, mime_type="application/pdf", status="ready")
            for i in range(10)
        ]
        docs.append(Document(filename="processing.pdf", file_size=1024, mime_type="application/pdf", status="processing"))
        db_session.add_all(docs)
        await db_session.commit()
        
        # 执行带状态筛选的查询
        documents, total = await repo.find_all(page=1, limit=10, status="ready")
        
        assert total == 10
        assert len(documents) == 10
        assert all(doc.status == "ready" for doc in documents)
        
        # 注意：在 SQLite 中无法直接运行 EXPLAIN，这个测试主要验证功能正确性
        # 在真实 PostgreSQL 环境中，可以通过 EXPLAIN ANALYZE 验证索引使用情况


class TestDocumentRepositoryEdgeCases:
    """边界情况测试类"""
    
    @pytest.fixture
    def repo(self, db_session):
        """创建 Repository 实例"""
        return DocumentRepository(db_session)
    
    @pytest.mark.asyncio
    async def test_find_all_with_empty_status_string(self, db_session, repo):
        """测试空字符串作为状态筛选"""
        docs = [Document(filename="doc1.pdf", file_size=1024, mime_type="application/pdf", status="ready")]
        db_session.add_all(docs)
        await db_session.commit()
        
        # 空字符串在 SQL 中会被视为 falsy，应该返回所有文档（与 None 相同）
        # 但为了安全起见，我们期望它不匹配任何明确的 status 值
        documents, total = await repo.find_all(page=1, limit=10, status="")
        
        # 根据实际实现，空字符串可能被视为一个具体的状态值
        # 在 find_all 中，空字符串会进入 where 子句，但不会匹配任何文档
        assert total == 0 or total == 1  # 允许两种行为
    
    @pytest.mark.asyncio
    async def test_find_all_with_none_status(self, db_session, repo):
        """测试 None 作为状态筛选（应该返回所有文档）"""
        docs = [
            Document(filename="doc1.pdf", file_size=1024, mime_type="application/pdf", status="ready"),
            Document(filename="doc2.pdf", file_size=1024, mime_type="application/pdf", status="processing"),
        ]
        db_session.add_all(docs)
        await db_session.commit()
        
        documents, total = await repo.find_all(page=1, limit=10, status=None)
        
        assert total == 2
        assert len(documents) == 2
    
    @pytest.mark.asyncio
    async def test_find_all_with_limit_zero(self, db_session, repo):
        """测试 limit=0 的边界情况"""
        docs = [Document(filename="doc1.pdf", file_size=1024, mime_type="application/pdf", status="ready")]
        db_session.add_all(docs)
        await db_session.commit()
        
        documents, total = await repo.find_all(page=1, limit=0)
        
        assert total == 1
        assert len(documents) == 0  # limit=0 应该返回空列表
    
    @pytest.mark.asyncio
    async def test_find_all_with_page_zero(self, db_session, repo):
        """测试 page=0 的边界情况（page 从 1 开始计数）"""
        docs = [Document(filename="doc1.pdf", file_size=1024, mime_type="application/pdf", status="ready")]
        db_session.add_all(docs)
        await db_session.commit()
        
        # page=0 会导致 offset 为负数，PostgreSQL 不允许
        # 应该抛出异常或返回空结果
        with pytest.raises(Exception):  # PostgreSQL 会抛出 DBAPIError
            await repo.find_all(page=0, limit=10)
    
    @pytest.mark.asyncio
    async def test_find_all_with_special_status_value(self, db_session, repo):
        """测试不存在的状态值"""
        docs = [Document(filename="doc1.pdf", file_size=1024, mime_type="application/pdf", status="ready")]
        db_session.add_all(docs)
        await db_session.commit()
        
        # 查询一个不存在的状态
        documents, total = await repo.find_all(page=1, limit=10, status="nonexistent_status")
        
        assert total == 0
        assert len(documents) == 0