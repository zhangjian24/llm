"""
检查数据库表结构
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import get_db_session
from sqlalchemy import text


async def check_table_structure():
    """检查 chunks 表结构"""
    print("="*60)
    print("Checking Database Table Structure")
    print("="*60)
    
    async for session in get_db_session():
        try:
            # 检查 chunks 表的 embedding 列定义
            result = await session.execute(text("""
                SELECT column_name, data_type, udt_name, character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = 'chunks' AND column_name = 'embedding'
            """))
            
            rows = result.fetchall()
            
            if rows:
                print("\nChunks table 'embedding' column:")
                for row in rows:
                    print(f"   Column: {row.column_name}")
                    print(f"   Data Type: {row.data_type}")
                    print(f"   UDT Name: {row.udt_name}")
                    print(f"   Max Length: {row.character_maximum_length}")
            
            # 检查 pgvector 扩展
            result = await session.execute(text("""
                SELECT * FROM pg_extension WHERE extname = 'vector'
            """))
            
            ext_rows = result.fetchall()
            if ext_rows:
                print("\n✅ pgvector extension installed")
                for row in ext_rows:
                    print(f"   Extension: {row.extname}, Version: {row.extversion}")
            else:
                print("\n❌ pgvector extension NOT found")
            
            # 尝试查询 vector 维度
            result = await session.execute(text("""
                SELECT attname, atttypmod
                FROM pg_attribute a
                JOIN pg_class c ON a.attrelid = c.oid
                WHERE c.relname = 'chunks' AND attname = 'embedding'
            """))
            
            attr_rows = result.fetchall()
            if attr_rows:
                print("\nEmbedding attribute details:")
                for row in attr_rows:
                    print(f"   Attribute: {row.attname}")
                    print(f"   Type Modifier: {row.atttypmod}")
                    # atttypmod for vector includes dimension info
            
            # 检查当前有多少数据
            result = await session.execute(text("SELECT COUNT(*) FROM chunks"))
            count = result.scalar()
            print(f"\nTotal chunks in database: {count}")
            
            result = await session.execute(text("SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL"))
            emb_count = result.scalar()
            print(f"Chunks with embedding: {emb_count}")
            
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await session.close()
    
    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(check_table_structure())
