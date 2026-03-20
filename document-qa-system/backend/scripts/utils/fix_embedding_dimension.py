"""
修复 chunks 表的 embedding 维度
从 1536 改为 1024（匹配 text-embedding-v4）
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import get_db_session
from sqlalchemy import text


async def fix_embedding_dimension():
    """修复 embedding 维度"""
    print("="*60)
    print("Fixing Embedding Dimension")
    print("="*60)
    
    async for session in get_db_session():
        try:
            # Step 1: 检查当前维度
            result = await session.execute(text("""
                SELECT atttypmod
                FROM pg_attribute a
                JOIN pg_class c ON a.attrelid = c.oid
                WHERE c.relname = 'chunks' AND attname = 'embedding'
            """))
            
            current_dim = result.scalar()
            print(f"\nCurrent embedding dimension: {current_dim}")
            
            if current_dim == 1024:
                print("✅ Already correct dimension (1024)")
                return
            
            # Step 2: 删除旧的 chunks 表（因为里面有旧数据）
            print("\nDropping old chunks table...")
            await session.execute(text("DROP TABLE IF EXISTS chunks CASCADE"))
            print("✅ Table dropped")
            
            # Step 3: 重新创建 chunks 表（使用正确的维度）
            print("\nCreating new chunks table with dimension 1024...")
            
            await session.execute(text("""
                CREATE TABLE chunks (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    token_count INTEGER NOT NULL,
                    embedding VECTOR(1024),
                    metadata JSONB,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
                    UNIQUE(document_id, chunk_index)
                )
            """))
            
            print("✅ Table created")
            
            # Step 4: 创建索引
            print("\nCreating indexes...")
            
            await session.execute(text("""
                CREATE INDEX idx_chunks_document_id ON chunks(document_id)
            """))
            
            await session.execute(text("""
                CREATE INDEX idx_chunks_embedding ON chunks USING hnsw (embedding vector_cosine_ops)
            """))
            
            print("✅ Indexes created")
            
            # Step 5: 提交
            await session.commit()
            print("\n✅ Changes committed")
            
            print("\n" + "="*60)
            print("Embedding dimension fixed successfully!")
            print("New dimension: 1024")
            print("="*60)
            
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
        
        finally:
            await session.close()


if __name__ == "__main__":
    asyncio.run(fix_embedding_dimension())
