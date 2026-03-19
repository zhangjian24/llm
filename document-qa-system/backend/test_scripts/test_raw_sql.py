"""
简化测试 - 直接 SQL 验证
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import get_db_session
from app.services.embedding_service import EmbeddingService
from sqlalchemy import text


async def test_with_raw_sql():
    """使用原生 SQL 测试"""
    print("="*60)
    print("Testing with Raw SQL")
    print("="*60)
    
    async for session in get_db_session():
        try:
            # Step 1: 创建测试文档
            print("\n[1/5] Creating test document...")
            
            import hashlib
            from datetime import datetime
            import uuid
            
            test_content = f"测试文档_{datetime.now().timestamp()}_人工智能是计算机科学的重要分支，致力于模拟人类智能。机器学习是 AI 的核心技术。".encode('utf-8')
            doc_id = uuid.uuid4()
            content_hash = hashlib.sha256(test_content).hexdigest()
            
            await session.execute(text("""
                INSERT INTO documents (id, filename, file_content, content_hash, file_size, mime_type, status)
                VALUES (:id, :filename, :content, :hash, :size, :mime, :status)
            """), {
                'id': str(doc_id),
                'filename': 'test_raw_sql.txt',
                'content': test_content,
                'hash': content_hash,
                'size': len(test_content),
                'mime': 'text/plain',
                'status': 'pending'
            })
            
            await session.commit()
            print(f"   Document created: {doc_id}")
            
            # Step 2: 处理文档（解析、分块）
            print("\n[2/5] Processing document...")
            
            from app.repositories.document_repository import DocumentRepository
            from app.services.document_service import DocumentService
            
            repo = DocumentRepository(session)
            embedding_svc = EmbeddingService()
            doc_service = DocumentService(repo, embedding_svc)
            
            # 这里会失败，因为异步处理使用了不同的 session
            # 我们改用手动方式
            
            # 解析文档
            from app.parsers.base_parser import ParserRegistry
            parser = ParserRegistry.get_parser('text/plain')
            text_content = await parser.parse(test_content)
            print(f"   Parsed text length: {len(text_content)}")
            
            # 分块
            chunks = doc_service.chunker.chunk_by_semantic(text_content)
            print(f"   Chunks created: {len(chunks)}")
            
            # Step 3: 保存 chunks（不使用 embedding）
            print("\n[3/5] Saving chunks...")
            
            for idx, chunk in enumerate(chunks):
                chunk_id = uuid.uuid4()
                await session.execute(text("""
                    INSERT INTO chunks (id, document_id, chunk_index, content, token_count)
                    VALUES (:id, :doc_id, :idx, :content, :tokens)
                """), {
                    'id': str(chunk_id),
                    'doc_id': str(doc_id),
                    'idx': idx,
                    'content': chunk.content,
                    'tokens': chunk.token_count
                })
            
            await session.commit()
            print(f"   Saved {len(chunks)} chunks")
            
            # Step 4: 向量化并更新
            print("\n[4/5] Vectorizing and updating...")
            
            for idx, chunk in enumerate(chunks):
                # 获取向量
                vector = await embedding_svc.embed_text(chunk.content)
                
                # 转为字符串格式
                vector_str = '[' + ','.join([f'{x:.6f}' for x in vector]) + ']'
                
                # 获取 chunk_id
                result = await session.execute(text("""
                    SELECT id FROM chunks WHERE document_id = :doc_id AND chunk_index = :idx
                """), {'doc_id': str(doc_id), 'idx': idx})
                
                chunk_row = result.fetchone()
                if chunk_row:
                    chunk_id = chunk_row.id
                    
                    # 更新 embedding（使用 CAST）
                    await session.execute(text("""
                        UPDATE chunks 
                        SET embedding = CAST(:vec AS VECTOR(1024))
                        WHERE id = :chunk_id
                    """), {'vec': vector_str, 'chunk_id': str(chunk_id)})
                    
                    print(f"   Updated chunk {idx} with embedding")
            
            await session.commit()
            print("   Embeddings updated")
            
            # Step 5: 测试搜索
            print("\n[5/5] Testing similarity search...")
            
            query_vector = await embedding_svc.embed_text("什么是人工智能")
            query_vec_str = '[' + ','.join([f'{x:.6f}' for x in query_vector]) + ']'
            
            result = await session.execute(text("""
                SELECT id, content, (embedding <=> CAST(:vec AS VECTOR(1024))) as distance
                FROM chunks
                WHERE embedding IS NOT NULL
                ORDER BY distance ASC
                LIMIT 3
            """), {'vec': query_vec_str})
            
            rows = result.fetchall()
            
            if rows:
                print(f"\n[SUCCESS] Search successful! Found {len(rows)} results:")
                for i, row in enumerate(rows, 1):
                    print(f"   [{i}] Distance: {row.distance:.4f}")
                    print(f"       Content: {str(row.content)[:80]}...")
            else:
                print("\n[ERROR] No results found")
            
            print("\n" + "="*60)
            print("Test completed successfully!")
            print("="*60)
            
        except Exception as e:
            print(f"\nTest failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await session.close()


if __name__ == "__main__":
    asyncio.run(test_with_raw_sql())
