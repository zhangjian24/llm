"""
使用原生 SQL 为 chunks 生成向量嵌入
避免 SQLAlchemy ORM 的类型处理问题
"""

import asyncio
import sys
from pathlib import Path
from tqdm import tqdm

# 修复导入路径
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(script_dir))

from app.core.database import AsyncSessionLocal
from app.services.embedding_service import EmbeddingService
from sqlalchemy import text


async def generate_embeddings_sql():
    """使用原生 SQL 生成向量嵌入"""
    print("🔄 使用原生 SQL 为 chunks 生成向量嵌入")
    print("=" * 50)
    
    try:
        # 初始化嵌入服务
        embedding_svc = EmbeddingService()
        print("✅ 嵌入服务初始化成功")
        
        async with AsyncSessionLocal() as session:
            # 查找所有没有向量的 chunks
            stmt = text("""
                SELECT id, content 
                FROM chunks 
                WHERE embedding IS NULL 
                ORDER BY id
            """)
            result = await session.execute(stmt)
            chunks_without_embedding = result.fetchall()
            
            total_chunks = len(chunks_without_embedding)
            print(f"📊 发现 {total_chunks} 个需要生成向量的 chunks")
            
            if total_chunks == 0:
                print("✅ 所有 chunks 都已有向量数据")
                return True
            
            # 分批处理
            batch_size = 1
            processed_count = 0
            
            with tqdm(total=total_chunks, desc="生成向量") as pbar:
                for i in range(0, total_chunks, batch_size):
                    batch = chunks_without_embedding[i:i + batch_size]
                    
                    # 为批次中的每个 chunk 生成向量
                    for row in batch:
                        try:
                            chunk_id = row.id
                            content = row.content
                            
                            # 生成嵌入向量
                            embedding = await embedding_svc.embed_text(content)
                            
                            # 将向量转换为 PostgreSQL 数组格式（限制长度）
                            # 只取前 1024 维度（假设这是设置的维度）
                            embedding_truncated = embedding[:1024] if len(embedding) > 1024 else embedding
                            embedding_array = '[' + ','.join([f'{x:.6f}' for x in embedding_truncated]) + ']'
                            
                            # 更新数据库记录
                            update_stmt = text("""
                                UPDATE chunks 
                                SET embedding = CAST(:embedding AS VECTOR(1024))
                                WHERE id = :chunk_id
                            """)
                            await session.execute(update_stmt, {
                                "embedding": embedding_array,
                                "chunk_id": chunk_id
                            })
                            
                            # 立即提交，避免事务累积错误
                            await session.commit()
                            
                            processed_count += 1
                            pbar.update(1)
                            
                        except Exception as e:
                            print(f"\n⚠️  处理 chunk {row.id} 时出错: {e}")
                            # 回滚当前事务
                            await session.rollback()
                            continue
            
            print(f"\n✅ 成功为 {processed_count} 个 chunks 生成向量嵌入")
            
            # 验证结果
            stmt = text("SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL")
            result = await session.execute(stmt)
            chunks_with_embedding = result.scalar()
            print(f"📊 当前总共有 {chunks_with_embedding} 个 chunks 包含向量数据")
            
            return True
            
    except Exception as e:
        print(f"\n❌ 向量生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    success = await generate_embeddings_sql()
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)