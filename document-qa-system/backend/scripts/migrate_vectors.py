"""
数据库迁移脚本：添加向量字段和索引
用于将现有 chunks 表迁移到支持向量存储的新结构
"""

import sys
import os
from pathlib import Path

# 修复导入路径问题
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(script_dir))

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import get_settings

settings = get_settings()


async def migrate_database_for_vectors(database_url: str):
    """执行数据库迁移以支持向量存储"""
    print("🚀 开始数据库向量迁移")
    print("=" * 50)
    
    try:
        engine = create_async_engine(database_url)
        
        async with engine.connect() as conn:
            # 开始事务
            trans = await conn.begin()
            
            try:
                # 1. 检查 chunks 表是否存在
                print("1. 检查 chunks 表...")
                result = await conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'chunks'
                    )
                """))
                table_exists = result.scalar()
                
                if not table_exists:
                    print("   ❌ chunks 表不存在，请先初始化数据库")
                    return False
                
                # 2. 检查 embedding 字段是否已存在
                print("2. 检查 embedding 字段...")
                result = await conn.execute(text("""
                    SELECT EXISTS (
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'chunks' AND column_name = 'embedding'
                    )
                """))
                column_exists = result.scalar()
                
                if column_exists:
                    print("   ✅ embedding 字段已存在")
                else:
                    print("   ➕ 添加 embedding 字段...")
                    # 添加向量字段
                    await conn.execute(text(f"""
                        ALTER TABLE chunks 
                        ADD COLUMN embedding VECTOR({settings.VECTOR_DIMENSION})
                    """))
                    print("   ✅ embedding 字段添加成功")
                
                # 3. 检查向量索引是否存在
                print("3. 检查向量索引...")
                result = await conn.execute(text("""
                    SELECT EXISTS (
                        SELECT indexname 
                        FROM pg_indexes 
                        WHERE tablename = 'chunks' AND indexname LIKE '%embedding%'
                    )
                """))
                index_exists = result.scalar()
                
                if index_exists:
                    print("   ✅ 向量索引已存在")
                else:
                    print("   ➕ 创建向量索引...")
                    # 根据配置选择索引类型
                    if settings.VECTOR_INDEX_TYPE.lower() == 'hnsw':
                        # 尝试创建 HNSW 索引
                        try:
                            await conn.execute(text(f"""
                                CREATE INDEX idx_chunks_embedding_hnsw 
                                ON chunks 
                                USING hnsw (embedding vector_cosine_ops)
                                WITH (m = {settings.HNSW_M}, ef_construction = {settings.HNSW_EF_CONSTRUCTION})
                            """))
                            print("   ✅ HNSW 向量索引创建成功")
                        except Exception as e:
                            print(f"   ⚠️  HNSW 索引创建失败: {e}")
                            print("   ➕ 创建 IVFFlat 索引作为替代...")
                            await conn.execute(text("""
                                CREATE INDEX idx_chunks_embedding_ivfflat 
                                ON chunks 
                                USING ivfflat (embedding vector_cosine_ops)
                                WITH (lists = 100)
                            """))
                            print("   ✅ IVFFlat 向量索引创建成功")
                    else:
                        # 创建 IVFFlat 索引
                        await conn.execute(text("""
                            CREATE INDEX idx_chunks_embedding_ivfflat 
                            ON chunks 
                            USING ivfflat (embedding vector_cosine_ops)
                            WITH (lists = 100)
                        """))
                        print("   ✅ IVFFlat 向量索引创建成功")
                
                # 4. 验证迁移结果
                print("4. 验证迁移结果...")
                result = await conn.execute(text("""
                    SELECT 
                        COUNT(*) as total_chunks,
                        COUNT(embedding) as chunks_with_embedding
                    FROM chunks
                """))
                stats = result.fetchone()
                print(f"   总块数: {stats.total_chunks}")
                print(f"   已向量化块数: {stats.chunks_with_embedding}")
                
                # 提交事务
                await trans.commit()
                print("\n" + "=" * 50)
                print("🎉 数据库向量迁移完成!")
                print("✅ 可以继续进行服务层重构")
                
                return True
                
            except Exception as e:
                # 回滚事务
                await trans.rollback()
                print(f"❌ 迁移过程中发生错误: {e}")
                raise
                
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    finally:
        if 'engine' in locals():
            await engine.dispose()


async def rollback_migration(database_url: str):
    """回滚数据库迁移"""
    print("🔄 开始回滚数据库向量迁移")
    print("=" * 50)
    
    try:
        engine = create_async_engine(database_url)
        
        async with engine.connect() as conn:
            # 开始事务
            trans = await conn.begin()
            
            try:
                # 删除向量索引
                print("1. 删除向量索引...")
                await conn.execute(text("DROP INDEX IF EXISTS idx_chunks_embedding_hnsw"))
                await conn.execute(text("DROP INDEX IF EXISTS idx_chunks_embedding_ivfflat"))
                print("   ✅ 向量索引已删除")
                
                # 删除 embedding 字段
                print("2. 删除 embedding 字段...")
                await conn.execute(text("ALTER TABLE chunks DROP COLUMN IF EXISTS embedding"))
                print("   ✅ embedding 字段已删除")
                
                # 提交事务
                await trans.commit()
                print("\n" + "=" * 50)
                print("✅ 数据库向量迁移已回滚!")
                
            except Exception as e:
                # 回滚事务
                await trans.rollback()
                print(f"❌ 回滚过程中发生错误: {e}")
                raise
                
    except Exception as e:
        print(f"❌ 回滚失败: {e}")
    finally:
        if 'engine' in locals():
            await engine.dispose()


async def main():
    """主函数"""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description='数据库向量迁移工具')
    parser.add_argument('--rollback', action='store_true', help='执行回滚操作')
    parser.add_argument('--database-url', help='数据库连接URL')
    
    args = parser.parse_args()
    
    # 获取数据库URL
    database_url = args.database_url or os.getenv('DATABASE_URL')
    if not database_url:
        database_url = 'postgresql+asyncpg://postgresql:mM6hbJXelbGd@localhost:5432/postgresql'
    
    print(f"使用数据库URL: {database_url}")
    print()
    
    if args.rollback:
        success = await rollback_migration(database_url)
    else:
        success = await migrate_database_for_vectors(database_url)
    
    if not success:
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())