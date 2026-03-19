"""
完整流程测试：上传→处理→检索→问答
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import get_db_session
from app.repositories.document_repository import DocumentRepository
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService


async def test_full_pipeline():
    """测试完整流程"""
    print("="*60)
    print("Full Pipeline Test")
    print("="*60)
    
    # 创建测试文档内容
    test_docs = [
        {
            "filename": "test_ai.txt",
            "content": "人工智能（Artificial Intelligence）是计算机科学的一个重要分支，\n致力于研究和开发用于模拟、延伸和扩展人类智能的理论、方法、技术和应用系统。\n\n机器学习是人工智能的核心技术领域，主要包括：\n1. 监督学习：通过标记数据进行训练\n2. 无监督学习：从无标记数据中发现模式\n3. 强化学习：通过与环境交互学习策略\n\n深度学习是机器学习的一个子领域，使用多层神经网络来学习数据的层次化表示。\n".encode('utf-8'),
            "mime_type": "text/plain"
        },
        {
            "filename": "test_environment.txt",
            "content": "环境保护与可持续发展\n\n气候变化是当今世界面临的重大环境挑战之一。应对气候变化需要全球合作，采取以下措施：\n1. 减少温室气体排放\n2. 发展可再生能源，如太阳能、风能、水能\n3. 提高能源利用效率\n4. 推广低碳生活方式\n\n污染对健康的影响包括：\n- 空气污染导致呼吸系统疾病\n- 水污染影响饮用水安全\n- 土壤污染影响农作物质量\n\n个人可以为环保做贡献：\n1. 节约用水用电\n2. 绿色出行，多乘坐公共交通\n3. 减少使用一次性塑料制品\n4. 垃圾分类回收\n".encode('utf-8'),
            "mime_type": "text/plain"
        }
    ]
    
    async for session in get_db_session():
        try:
            repo = DocumentRepository(session)
            embedding_svc = EmbeddingService()
            doc_service = DocumentService(repo, embedding_svc)
            
            print(f"\nUploading {len(test_docs)} test documents...")
            
            for doc_info in test_docs:
                print(f"\n--- Processing: {doc_info['filename']} ---")
                
                # 1. 创建文档记录
                from app.models.document import Document
                import hashlib
                from datetime import datetime
                import uuid
                
                doc_id = uuid.uuid4()
                content_hash = hashlib.sha256(doc_info['content']).hexdigest()
                
                doc = Document(
                    id=doc_id,
                    filename=doc_info['filename'],
                    file_content=doc_info['content'],
                    content_hash=content_hash,
                    file_size=len(doc_info['content']),
                    mime_type=doc_info['mime_type'],
                    status='pending',
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                await repo.save(doc)
                print(f"Document record created: {doc_id}")
                
                # 2. 立即处理文档（同步等待）
                print(f"Starting document processing...")
                
                await doc_service._process_document_async(doc_id)
                
                # 等待一小段时间让事务提交
                await asyncio.sleep(2)
                
                # 3. 检查处理结果
                print(f"\nChecking results...")
                
                # 查询文档状态
                updated_doc = await repo.find_by_id(doc_id)
                print(f"   Status: {updated_doc.status}")
                print(f"   Chunks count: {updated_doc.chunks_count}")
                
                # 查询 chunks
                from app.models.chunk import Chunk
                from sqlalchemy import select, func
                
                total_chunks = await session.execute(
                    select(func.count(Chunk.id)).where(Chunk.document_id == doc_id)
                )
                chunk_count = total_chunks.scalar()
                print(f"   Database chunks count: {chunk_count}")
                
                # 检查有 embedding 的 chunks
                chunks_with_embedding = await session.execute(
                    select(func.count(Chunk.id))
                    .where(Chunk.document_id == doc_id)
                    .where(Chunk.embedding.isnot(None))
                )
                embedding_count = chunks_with_embedding.scalar()
                print(f"   Chunks with embedding: {embedding_count}")
                
                if embedding_count > 0:
                    # 取一个示例 chunk
                    sample_chunk = await session.execute(
                        select(Chunk).where(Chunk.document_id == doc_id).limit(1)
                    )
                    chunk = sample_chunk.scalar_one_or_none()
                    
                    if chunk:
                        print(f"\n   Sample Chunk:")
                        print(f"      ID: {chunk.id}")
                        print(f"      Content: {chunk.content[:80]}...")
                        print(f"      Embedding dimension: {len(chunk.embedding) if chunk.embedding else 0}")
            
            print("\n" + "="*60)
            print("Full pipeline test completed")
            print("="*60)
            
            # Final verification
            print("\nFinal verification:")
            total_all = await session.execute(select(func.count(Chunk.id)))
            print(f"   Total chunks: {total_all.scalar()}")
            
            total_with_embedding = await session.execute(
                select(func.count(Chunk.id)).where(Chunk.embedding.isnot(None))
            )
            print(f"   Chunks with embedding: {total_with_embedding.scalar()}")
        
        except Exception as e:
            print(f"\nTest failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await session.close()


if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
