"""
文档管理 API 集成测试
"""
import pytest
from httpx import AsyncClient
from app.main import app
from app.repositories.document_repository import DocumentRepository
from app.models.document import Document


class TestDocumentsAPI:
    """文档管理 API 集成测试"""
    
    @pytest.mark.asyncio
    async def test_get_documents_list_success(self, client, db_session):
        """测试获取文档列表成功场景"""
        # Arrange: 准备测试数据
        repo = DocumentRepository(db_session)
        await repo.save(Document(
            filename="test_doc.pdf",
            file_size=1024,
            mime_type="application/pdf",
            status="ready"
        ))
        await db_session.commit()
        
        # Act
        response = await client.get("/api/v1/documents?page=1&limit=20")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "total" in data["data"]
        assert "items" in data["data"]
        assert len(data["data"]["items"]) >= 1
    
    @pytest.mark.asyncio
    async def test_get_documents_with_status_filter(self, client, db_session):
        """测试状态筛选功能"""
        # Arrange: 创建不同状态的文档
        repo = DocumentRepository(db_session)
        await repo.save(Document(filename="ready1.pdf", status="ready"))
        await repo.save(Document(filename="ready2.pdf", status="ready"))
        await repo.save(Document(filename="processing1.pdf", status="processing"))
        await repo.save(Document(filename="failed1.pdf", status="failed"))
        await db_session.commit()
        
        # Act: 筛选 ready 状态
        response = await client.get("/api/v1/documents?status=ready")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert all(doc["status"] == "ready" for doc in data["data"]["items"])
        assert data["data"]["total"] == 2
    
    @pytest.mark.asyncio
    async def test_delete_document_success(self, client, db_session):
        """测试删除文档成功场景"""
        # Arrange
        repo = DocumentRepository(db_session)
        doc = Document(
            filename="to_delete.pdf",
            file_size=512,
            mime_type="application/pdf",
            status="ready"
        )
        doc_id = await repo.save(doc)
        await db_session.commit()
        
        # Act
        response = await client.delete(f"/api/v1/documents/{doc_id}")
        
        # Assert
        assert response.status_code == 204
        
        # Verify deleted
        deleted_doc = await repo.find_by_id(doc_id)
        assert deleted_doc is None
    
    @pytest.mark.asyncio
    async def test_delete_document_not_found(self, client, db_session):
        """测试删除不存在的文档"""
        # Arrange
        import uuid
        non_existent_id = uuid.uuid4()
        
        # Act
        response = await client.delete(f"/api/v1/documents/{non_existent_id}")
        
        # Assert
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_documents_pagination(self, client, db_session):
        """测试分页功能"""
        # Arrange: 创建 25 个文档
        repo = DocumentRepository(db_session)
        for i in range(25):
            await repo.save(Document(filename=f"doc_{i}.pdf", status="ready"))
        await db_session.commit()
        
        # Act: 第 1 页
        response1 = await client.get("/api/v1/documents?page=1&limit=20")
        data1 = response1.json()
        
        # Act: 第 2 页
        response2 = await client.get("/api/v1/documents?page=2&limit=20")
        data2 = response2.json()
        
        # Assert
        assert data1["data"]["total"] == 25
        assert len(data1["data"]["items"]) == 20
        assert data2["data"]["total"] == 25
        assert len(data2["data"]["items"]) == 5
        assert data1["data"]["page"] == 1
        assert data2["data"]["page"] == 2
    
    @pytest.mark.asyncio
    async def test_get_documents_empty(self, client, db_session):
        """测试空文档列表"""
        # Arrange: 确保数据库为空
        pass  # 测试框架会自动清理
        
        # Act
        response = await client.get("/api/v1/documents")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 0
        assert data["data"]["items"] == []
    
    @pytest.mark.asyncio
    async def test_delete_document_success(self, client, db_session):
        """测试删除文档成功场景"""
        # Arrange: 准备测试数据
        repo = DocumentRepository(db_session)
        doc = Document(
            filename="to_delete.pdf",
            file_size=512,
            mime_type="application/pdf",
            status="ready"
        )
        doc_id = await repo.save(doc)
        await db_session.commit()
        
        # Act
        response = await client.delete(f"/api/v1/documents/{doc_id}")
        
        # Assert
        assert response.status_code == 204
        
        # Verify deleted
        deleted_doc = await repo.find_by_id(doc_id)
        assert deleted_doc is None
    
    @pytest.mark.asyncio
    async def test_delete_document_not_found(self, client, db_session):
        """测试删除不存在的文档"""
        # Arrange
        import uuid
        non_existent_id = uuid.uuid4()
        
        # Act
        response = await client.delete(f"/api/v1/documents/{non_existent_id}")
        
        # Assert
        assert response.status_code == 404
