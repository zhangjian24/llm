"""
调试 PostgreSQL 向量搜索
逐步排查问题所在
"""

import asyncio
import sys
from pathlib import Path

# 修复导入路径
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(script_dir))

from app.core.database import AsyncSessionLocal
from app.models.chunk import Chunk
from sqlalchemy import text


async def debug_vector_search():
    """调试向量搜索"""
    print("🔬 调试 PostgreSQL 向量搜索")
    print("=" * 50)
    
    try:
        async with AsyncSessionLocal() as session:
            # 1. 检查是否有向量数据
            print("1. 检查向量数据...")
            stmt = text("SELECT COUNT(*) as total, COUNT(embedding) as with_embedding FROM chunks")
            result = await session.execute(stmt)
            row = result.fetchone()
            total_chunks = row[0]
            chunks_with_embedding = row[1]
            print(f"   总 chunks: {total_chunks}")
            print(f"   有向量的 chunks: {chunks_with_embedding}")
            
            # 2. 检查 pgvector 扩展
            print("\n2. 检查 pgvector 扩展...")
            stmt = text("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'")
            result = await session.execute(stmt)
            extensions = result.fetchall()
            if extensions:
                print(f"   ✅ pgvector 版本: {extensions[0].extversion}")
            else:
                print("   ❌ pgvector 扩展未安装")
                return False
            
            # 3. 测试基本向量操作
            print("\n3. 测试基本向量操作...")
            try:
                stmt = text("SELECT '[1,2,3]'::vector <-> '[4,5,6]'::vector as distance")
                result = await session.execute(stmt)
                row = result.fetchone()
                print(f"   ✅ 基本向量运算正常: {row.distance}")
            except Exception as e:
                print(f"   ❌ 基本向量运算失败: {e}")
                return False
            
            # 4. 检查 chunks 表结构
            print("\n4. 检查 chunks 表结构...")
            stmt = text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'chunks' AND column_name = 'embedding'
            """)
            result = await session.execute(stmt)
            columns = result.fetchall()
            if columns:
                print(f"   ✅ embedding 列存在: {columns[0].data_type}")
            else:
                print("   ❌ embedding 列不存在")
                return False
            
            # 5. 测试实际查询
            print("\n5. 测试实际查询...")
            if chunks_with_embedding > 0:
                try:
                    # 获取一个测试向量
                    stmt = text("SELECT embedding FROM chunks WHERE embedding IS NOT NULL LIMIT 1")
                    result = await session.execute(stmt)
                    test_embedding = result.fetchone().embedding
                    print(f"   ✅ 获取测试向量成功，维度: {len(test_embedding)}")
                    
                    # 测试相似度搜索
                    query_vector_str = '{' + ','.join(map(str, test_embedding[:10])) + ',0' * (1024-10) + '}'
                    stmt = text("""
                        SELECT id, (embedding <=> :query_vector::vector) as distance
                        FROM chunks 
                        WHERE embedding IS NOT NULL
                        ORDER BY distance ASC 
                        LIMIT 3
                    """)
                    result = await session.execute(stmt, {"query_vector": query_vector_str})
                    rows = result.fetchall()
                    print(f"   ✅ 相似度搜索成功，返回 {len(rows)} 个结果")
                    for i, row in enumerate(rows):
                        print(f"     [{i+1}] ID: {row.id}, 距离: {row.distance}")
                        
                except Exception as e:
                    print(f"   ❌ 实际查询失败: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            else:
                print("   ⚠️  没有向量数据可供测试")
            
            print("\n" + "=" * 50)
            print("🎉 调试完成，基础功能正常!")
            return True
            
    except Exception as e:
        print(f"\n❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    success = await debug_vector_search()
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)