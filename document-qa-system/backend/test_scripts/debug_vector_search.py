"""
调试 PostgreSQL 向量搜索
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import get_db_session
from app.services.embedding_service import EmbeddingService
from app.services.postgresql_vector_service import PostgreSQLVectorService


async def debug_vector_search():
    """调试向量搜索"""
    print("="*60)
    print("🔍 调试 PostgreSQL 向量搜索")
    print("="*60)
    
    async for session in get_db_session():
        try:
            # Step 1: 检查数据库中有多少 chunks
            from sqlalchemy import select, func
            from app.models.chunk import Chunk
            
            total_chunks = await session.execute(select(func.count(Chunk.id)))
            total_count = total_chunks.scalar()
            
            print(f"\n📊 总 chunks 数：{total_count}")
            
            # 检查有 embedding 的 chunks
            chunks_with_embedding = await session.execute(
                select(func.count(Chunk.id)).where(Chunk.embedding.isnot(None))
            )
            embedding_count = chunks_with_embedding.scalar()
            
            print(f"✅ 有 embedding 的 chunks 数：{embedding_count}")
            
            if embedding_count == 0:
                print("\n❌ 数据库中没有带 embedding 的 chunks！")
                print("💡 请先运行文档处理流程，确保文档已向量化")
                return
            
            # Step 2: 随机取一个 chunk 查看
            sample_chunk = await session.execute(
                select(Chunk).where(Chunk.embedding.isnot(None)).limit(1)
            )
            chunk = sample_chunk.scalar_one_or_none()
            
            if chunk:
                print(f"\n📄 示例 Chunk:")
                print(f"   ID: {chunk.id}")
                print(f"   Document ID: {chunk.document_id}")
                print(f"   Content: {chunk.content[:100]}...")
                print(f"   Embedding 维度：{len(chunk.embedding) if chunk.embedding else 0}")
            
            # Step 3: 测试问题向量化
            test_question = "什么是人工智能"
            print(f"\n❓ 测试问题：{test_question}")
            
            embedding_svc = EmbeddingService()
            query_vector = await embedding_svc.embed_text(test_question)
            
            print(f"✅ 问题向量维度：{len(query_vector)}")
            print(f"   前 5 个值：{query_vector[:5]}")
            
            # Step 4: 执行向量搜索
            print(f"\n🔍 执行向量搜索 (top_k=5)...")
            
            vector_svc = PostgreSQLVectorService()
            results = await vector_svc.similarity_search(
                session=session,
                query_vector=query_vector,
                top_k=5
            )
            
            print(f"✅ 检索到 {len(results)} 个结果")
            
            if results:
                print("\n📊 检索结果详情:")
                for i, result in enumerate(results, 1):
                    print(f"\n[{i}] Chunk ID: {result['id']}")
                    print(f"    相似度：{result['score']:.4f}")
                    print(f"    内容预览：{result['metadata'].get('content', '')[:80]}...")
                    print(f"    Document ID: {result['metadata'].get('document_id')}")
                    print(f"    Chunk Index: {result['metadata'].get('chunk_index')}")
            else:
                print("\n❌ 未检索到任何结果")
                print("\n💡 可能原因:")
                print("   1. 向量维度不匹配")
                print("   2. 数据库中没有有效的 embeddings")
                print("   3. SQL 查询有问题")
                
                # 尝试直接执行原生 SQL
                from sqlalchemy import text
                query_vector_str = '[' + ','.join([f'{x:.6f}' for x in query_vector]) + ']'
                
                sql = text("""
                    SELECT id, document_id, content,
                           (embedding <=> CAST(:qv AS VECTOR(1024))) as distance
                    FROM chunks 
                    WHERE embedding IS NOT NULL
                    ORDER BY distance ASC 
                    LIMIT 5
                """)
                
                result = await session.execute(sql, {"qv": query_vector_str})
                rows = result.fetchall()
                
                print(f"\n🔧 直接 SQL 查询结果：{len(rows)} 条")
                for row in rows:
                    print(f"   ID: {row.id}, Distance: {row.distance:.4f}, Content: {str(row.content)[:50]}...")
        
        except Exception as e:
            print(f"\n❌ 调试失败：{e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await session.close()
    
    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(debug_vector_search())
