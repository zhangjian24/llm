"""
文档重新处理 API 集成测试
"""
import pytest
from uuid import UUID, uuid4
from httpx import AsyncClient
from app.main import app
from app.repositories.document_repository import DocumentRepository
from app.models.document import Document


class TestReprocessDocumentAPI:
    """文档重新处理 API 集成测试"""
    
    @pytest.mark.asyncio
    async def test_reprocess_document_success_from_failed_status(self, client, db_session):
        """测试重新处理文档成功（从 failed 状态）"""
        # Arrange: 创建失败状态的文档
        repo = DocumentRepository(db_session)
        doc = Document(
            filename="failed_doc.pdf",
            file_size=1024,
            mime_type="application/pdf",
            status="failed"
        )
        doc_id = await repo.save(doc)
        await db_session.commit()
        
        # Act
        response = await client.post(f"/api/v1/documents/{doc_id}/reprocess")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "已开始重新处理" in data["message"]
        
        # Verify 文档状态已更新为 processing
        updated_doc = await repo.find_by_id(doc_id)
        assert updated_doc is not None
        assert updated_doc.status == "processing"
    
    @pytest.mark.asyncio
    async def test_reprocess_document_success_from_ready_status(self, client, db_session):
        """测试重新处理文档成功（从 ready 状态）"""
        # Arrange: 创建就绪状态的文档
        repo = DocumentRepository(db_session)
        doc = Document(
            filename="ready_doc.pdf",
            file_size=2048,
            mime_type="application/pdf",
            status="ready"
        )
        doc_id = await repo.save(doc)
        await db_session.commit()
        
        # Act
        response = await client.post(f"/api/v1/documents/{doc_id}/reprocess")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        
        # Verify 状态变更
        updated_doc = await repo.find_by_id(doc_id)
        assert updated_doc.status == "processing"
    
    @pytest.mark.asyncio
    async def test_reprocess_document_not_found(self, client, db_session):
        """测试重新处理不存在的文档"""
        # Arrange
        non_existent_id = uuid4()
        
        # Act
        response = await client.post(f"/api/v1/documents/{non_existent_id}/reprocess")
        
        # Assert
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_reprocess_document_invalid_status_processing(self, client, db_session):
        """测试不允许的状态（processing）"""
        # Arrange: 创建处理中的文档
        repo = DocumentRepository(db_session)
        doc = Document(
            filename="processing_doc.pdf",
            file_size=512,
            mime_type="application/pdf",
            status="processing"
        )
        doc_id = await repo.save(doc)
        await db_session.commit()
        
        # Act
        response = await client.post(f"/api/v1/documents/{doc_id}/reprocess")
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "当前状态 (processing) 不允许重新处理" in data["detail"]
        assert "仅支持 failed 或 ready 状态" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_reprocess_document_invalid_status_chunked(self, client, db_session):
        """测试不允许的状态（chunked）"""
        # Arrange: 创建 chunked 状态的文档
        repo = DocumentRepository(db_session)
        doc = Document(
            filename="chunked_doc.pdf",
            file_size=1024,
            mime_type="application/pdf",
            status="chunked"
        )
        doc_id = await repo.save(doc)
        await db_session.commit()
        
        # Act
        response = await client.post(f"/api/v1/documents/{doc_id}/reprocess")
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "当前状态 (chunked) 不允许重新处理" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_reprocess_document_clears_old_chunks(self, client, db_session):
        """测试重新处理会清空旧的 chunks"""
        # Arrange: 创建已处理的文档
        repo = DocumentRepository(db_session)
        doc = Document(
            filename="with_chunks.pdf",
            file_size=1024,
            mime_type="application/pdf",
            status="ready",
            chunks_count=10
        )
        doc_id = await repo.save(doc)
        await db_session.commit()
        
        # 手动创建一些 chunks（模拟已处理）
        from app.models.chunk import Chunk
        for i in range(5):
            chunk = Chunk(
                document_id=doc_id,
                chunk_index=i,
                content=f"Chunk content {i}",
                token_count=100
            )
            await repo.save_chunk(chunk)
        await db_session.commit()
        
        # 验证 chunks 存在
        chunks_before = await repo.find_chunks_by_document(doc_id)
        assert len(chunks_before) == 5
        
        # Act: 重新处理
        response = await client.post(f"/api/v1/documents/{doc_id}/reprocess")
        assert response.status_code == 200
        
        # Wait a bit for async operations
        import asyncio
        await asyncio.sleep(0.1)
        
        # Assert: chunks 应该被清空
        chunks_after = await repo.find_chunks_by_document(doc_id)
        assert len(chunks_after) == 0
        
        # Verify 状态变为 processing
        updated_doc = await repo.find_by_id(doc_id)
        assert updated_doc.status == "processing"
        assert updated_doc.chunks_count is None
    
    @pytest.mark.asyncio
    async def test_reprocess_document_multiple_times(self, client, db_session):
        """测试多次重新处理同一文档"""
        # Arrange: 创建失败状态的文档
        repo = DocumentRepository(db_session)
        doc = Document(
            filename="multi_reprocess.pdf",
            file_size=1024,
            mime_type="application/pdf",
            status="failed"
        )
        doc_id = await repo.save(doc)
        await db_session.commit()
        
        # Act: 第一次重新处理
        response1 = await client.post(f"/api/v1/documents/{doc_id}/reprocess")
        assert response1.status_code == 200
        
        # 等待状态更新
        import asyncio
        await asyncio.sleep(0.1)
        
        # 现在状态是 processing，不能再次重新处理
        response2 = await client.post(f"/api/v1/documents/{doc_id}/reprocess")
        
        # Assert
        assert response2.status_code == 400
        assert "当前状态 (processing) 不允许重新处理" in response2.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_reprocess_document_response_format(self, client, db_session):
        """测试响应格式符合 SuccessResponse 规范"""
        # Arrange
        repo = DocumentRepository(db_session)
        doc = Document(
            filename="response_test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            status="failed"
        )
        doc_id = await repo.save(doc)
        await db_session.commit()
        
        # Act
        response = await client.post(f"/api/v1/documents/{doc_id}/reprocess")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应结构
        assert "code" in data
        assert "message" in data
        assert data["code"] == 0
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 0
    
    @pytest.mark.asyncio
    async def test_reprocess_document_concurrent_requests(self, client, db_session):
        """测试并发重新处理请求"""
        # Arrange
        repo = DocumentRepository(db_session)
        doc = Document(
            filename="concurrent_test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            status="failed"
        )
        doc_id = await repo.save(doc)
        await db_session.commit()
        
        # Act: 并发发送多个请求
        import asyncio
        tasks = [
            client.post(f"/api/v1/documents/{doc_id}/reprocess")
            for _ in range(3)
        ]
        responses = await asyncio.gather(*tasks)
        
        # Assert: 第一个成功，后续的可能失败（因为状态已变为 processing）
        success_count = sum(1 for r in responses if r.status_code == 200)
        fail_count = sum(1 for r in responses if r.status_code == 400)
        
        assert success_count >= 1
        assert fail_count >= 0  # 可能有竞态条件
    
    @pytest.mark.asyncio
    async def test_reprocess_document_with_large_chunks_count(self, client, db_session):
        """测试重新处理有大量 chunks 的文档"""
        # Arrange
        repo = DocumentRepository(db_session)
        doc = Document(
            filename="large_chunks.pdf",
            file_size=5 * 1024 * 1024,  # 5MB
            mime_type="application/pdf",
            status="ready",
            chunks_count=100
        )
        doc_id = await repo.save(doc)
        await db_session.commit()
        
        # 创建大量 chunks
        from app.models.chunk import Chunk
        for i in range(100):
            chunk = Chunk(
                document_id=doc_id,
                chunk_index=i,
                content=f"Large chunk content {i}",
                token_count=500
            )
            await repo.save_chunk(chunk)
        await db_session.commit()
        
        # Act
        response = await client.post(f"/api/v1/documents/{doc_id}/reprocess")
        
        # Assert
        assert response.status_code == 200
        
        # Verify chunks 被清空
        import asyncio
        await asyncio.sleep(0.1)
        
        chunks_after = await repo.find_chunks_by_document(doc_id)
        assert len(chunks_after) == 0


class TestReprocessDocumentEdgeCases:
    """边界情况测试"""
    
    @pytest.mark.asyncio
    async def test_reprocess_document_uuid_format_invalid(self, client):
        """测试 UUID 格式不正确的情况"""
        # Arrange
        invalid_uuid = "not-a-uuid"
        
        # Act
        response = await client.post(f"/api/v1/documents/{invalid_uuid}/reprocess")
        
        # Assert
        # FastAPI 会自动验证 UUID 格式，返回 422 验证错误
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_reprocess_document_method_not_allowed(self, client, db_session):
        """测试使用错误的方法（GET/PUT/DELETE）"""
        # Arrange
        repo = DocumentRepository(db_session)
        doc = Document(
            filename="method_test.pdf",
            status="failed"
        )
        doc_id = await repo.save(doc)
        await db_session.commit()
        
        # Act & Assert
        # GET 方法不应该被允许
        get_response = await client.get(f"/api/v1/documents/{doc_id}/reprocess")
        assert get_response.status_code == 405
        
        # PUT 方法不应该被允许
        put_response = await client.put(f"/api/v1/documents/{doc_id}/reprocess")
        assert put_response.status_code == 405
        
        # DELETE 方法不应该被允许
        delete_response = await client.delete(f"/api/v1/documents/{doc_id}/reprocess")
        assert delete_response.status_code == 405
