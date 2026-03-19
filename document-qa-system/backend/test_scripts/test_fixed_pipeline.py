"""
简化版完整流程测试 - 修复后
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import get_db_session
from app.repositories.document_repository import DocumentRepository
from app.services.document_service import DocumentService
from app.models.chunk import Chunk
from sqlalchemy import select, func


async def test_fixed_pipeline():
    """测试修复后的完整流程"""
    print("="*60)
    print("Fixed Pipeline Test")
    print("="*60)
    
    # 测试文档内容
    test_content = "人工智能是计算机科学的重要分支，致力于模拟人类智能。机器学习是 AI 的核心技术。".encode('utf-8')
    
    async for session in get_db_session():
        try:
            repo = DocumentRepository(session)
            embedding_svc = None  # 延迟初始化
            doc_service = None
            
            print("\n[1/4] Creating document record...")
            
            # 1. 创建文档
            from app.models.document import Document
            import hashlib
            from datetime import datetime, timezone
            import uuid
            
            doc_id = uuid.uuid4()
            content_hash = hashlib.sha256(test_content).hexdigest()
            
            doc = Document(
                id=doc_id,
                filename="test_fix.txt",
                file_content=test_content,
                content_hash=content_hash,
                file_size=len(test_content),
                mime_type="text/plain",
                status='pending',
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            await repo.save(doc)
            await session.commit()  # 先提交文档记录
            print(f"   Document created: {doc_id}")
            
            # 2. 重新获取文档（使用同一个 session）
            print("\n[2/4] Processing document...")
            
            # 初始化服务
            embedding_svc = embedding_svc or EmbeddingService()
            doc_service = doc_service or DocumentService(repo, embedding_svc)
            
            # 处理文档
            await doc_service._process_document_async(doc_id)
            
            # 3. 检查结果
            print("\n[3/4] Checking results...")
            
            updated_doc = await repo.find_by_id(doc_id)
            print(f"   Status: {updated_doc.status}")
            print(f"   Chunks count: {updated_doc.chunks_count}")
            
            # 查询 chunks
            total_chunks = await session.execute(
                select(func.count(Chunk.id)).where(Chunk.document_id == doc_id)
            )
            chunk_count = total_chunks.scalar()
            print(f"   Database chunks: {chunk_count}")
            
            # 检查有 embedding 的 chunks
            chunks_with_embedding = await session.execute(
                select(func.count(Chunk.id))
                .where(Chunk.document_id == doc_id)
                .where(Chunk.embedding.isnot(None))
            )
            embedding_count = chunks_with_embedding.scalar()
            print(f"   Chunks with embedding: {embedding_count}")
            
            if embedding_count > 0:
                print("\n   SUCCESS! Chunks have embeddings.")
                
                # 取一个示例
                sample = await session.execute(
                    select(Chunk).where(Chunk.document_id == doc_id).limit(1)
                )
                chunk = sample.scalar_one_or_none()
                
                if chunk:
                    print(f"   Sample chunk ID: {chunk.id}")
                    print(f"   Content preview: {chunk.content[:50]}...")
                    print(f"   Embedding dimension: {len(chunk.embedding)}")
                    
                    # 测试向量搜索
                    print("\n[4/4] Testing vector search...")
                    
                    from app.services.postgresql_vector_service import PostgreSQLVectorService
                    
                    vector_svc = PostgreSQLVectorService()
                    query_vector = await embedding_svc.embed_text("什么是人工智能")
                    
                    results = await vector_svc.similarity_search(
                        session=session,
                        query_vector=query_vector,
                        top_k=3
                    )
                    
                    print(f"   Search results: {len(results)} chunks found")
                    
                    if results:
                        for i, result in enumerate(results, 1):
                            print(f"   [{i}] Score: {result['score']:.4f}")
                            print(f"       Content: {result['metadata'].get('content', '')[:60]}...")
            
            else:
                print("\n   FAILED! No embeddings found.")
            
            print("\n" + "="*60)
            print("Test completed")
            print("="*60)
            
        except Exception as e:
            print(f"\nTest failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await session.close()


if __name__ == "__main__":
    from app.services.embedding_service import EmbeddingService
    asyncio.run(test_fixed_pipeline())
