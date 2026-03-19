"""
重新处理文档 - 修复缺失的 embeddings
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
from app.models.chunk import Chunk
from sqlalchemy import select


async def fix_missing_embeddings():
    """修复缺失的 embeddings"""
    print("="*60)
    print("🔧 修复缺失的 Embeddings")
    print("="*60)
    
    async for session in get_db_session():
        try:
            repo = DocumentRepository(session)
            
            # 查找 chunks_count > 0 但实际没有 embedding 的文档
            docs, total = await repo.find_all(page=1, limit=50)
            
            docs_to_fix = []
            
            for doc in docs:
                if doc.status == 'ready':
                    # 检查该文档的 chunks 是否有 embedding
                    chunks_result = await session.execute(
                        select(Chunk).where(Chunk.document_id == doc.id)
                    )
                    chunks = chunks_result.scalars().all()
                    
                    chunks_with_embedding = sum(1 for c in chunks if c.embedding is not None)
                    
                    print(f"\n📄 {doc.filename}:")
                    print(f"   总 chunks: {len(chunks)}")
                    print(f"   有 embedding: {chunks_with_embedding}")
                    
                    if len(chunks) > 0 and chunks_with_embedding == 0:
                        docs_to_fix.append(doc)
                        print(f"   ❌ 需要修复")
                    elif chunks_with_embedding > 0:
                        print(f"   ✅ 已有 embedding")
            
            if not docs_to_fix:
                print("\n✅ 所有文档都有有效的 embeddings")
                return
            
            print(f"\n📋 需要修复的文档数：{len(docs_to_fix)}")
            
            # 重新处理每个文档
            for doc in docs_to_fix:
                print(f"\n🔄 开始修复：{doc.filename} ({doc.id})")
                
                try:
                    # 删除旧的 chunks（没有 embedding 的）
                    await session.execute(
                        Chunk.__table__.delete().where(Chunk.__table__.c.document_id == doc.id)
                    )
                    print(f"   ✅ 已删除旧 chunks")
                    
                    # 重置文档状态为 processing
                    await repo.update_status(doc.id, 'processing', 0)
                    await session.commit()
                    print(f"   ✅ 状态重置为 processing")
                    
                    # 重新处理文档
                    embedding_svc = EmbeddingService()
                    service = DocumentService(repo, embedding_svc)
                    
                    # 获取文件内容并重新处理
                    file_content = await repo.get_document_content(doc.id)
                    
                    if file_content:
                        # 解析文档
                        from app.parsers.base_parser import ParserRegistry
                        parser = ParserRegistry.get_parser(doc.mime_type)
                        text_content = await parser.parse(file_content)
                        print(f"   ✅ 文档解析完成，文本长度：{len(text_content)}")
                        
                        # 分块
                        chunks = service.chunker.chunk_by_semantic(text_content)
                        print(f"   ✅ 文本分块完成，共 {len(chunks)} 个块")
                        
                        # 向量化并存储
                        await service._vectorize_chunks(repo, chunks, doc.id, doc.filename, session)
                        print(f"   ✅ 向量化完成")
                        
                        # 更新状态为 ready
                        await repo.update_status(doc.id, 'ready', len(chunks))
                        await session.commit()
                        print(f"   ✅ 状态更新为 ready")
                        
                    else:
                        print(f"   ❌ 无法获取文件内容")
                        await repo.update_status(doc.id, 'failed')
                        await session.commit()
                        
                except Exception as e:
                    print(f"   ❌ 修复失败：{e}")
                    import traceback
                    traceback.print_exc()
                    await session.rollback()
        
        except Exception as e:
            print(f"\n❌ 修复过程失败：{e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await session.close()
    
    print("\n" + "="*60)
    print("✅ 修复流程完成")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(fix_missing_embeddings())
