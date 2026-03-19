#!/usr/bin/env python3
"""
PostgreSQL pgvector 环境检查脚本
用于验证 PostgreSQL 版本和 pgvector 扩展安装状态
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
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text


async def check_postgresql_environment(database_url: str):
    """检查 PostgreSQL 环境配置"""
    print("🔍 PostgreSQL 环境检查")
    print("=" * 50)
    
    try:
        # 创建数据库连接
        engine = create_async_engine(database_url)
        
        async with engine.connect() as conn:
            # 1. 检查 PostgreSQL 版本
            print("1. 检查 PostgreSQL 版本...")
            result = await conn.execute(text("SELECT version()"))
            version_info = result.scalar()
            print(f"   ✅ {version_info.split(',')[0]}")
            
            # 提取版本号
            version_line = version_info.split('\n')[0]
            version_parts = version_line.split()[1].split('.')
            major_version = int(version_parts[0])
            minor_version = int(version_parts[1]) if len(version_parts) > 1 else 0
            
            print(f"   版本: {major_version}.{minor_version}")
            
            if major_version < 12:
                print("   ⚠️  警告: 建议使用 PostgreSQL 12+ 版本")
                return False
            elif major_version < 14:
                print("   ℹ️  注意: HNSW 索引需要 PostgreSQL 14+")
            else:
                print("   ✅ 支持 HNSW 索引")
            
            # 2. 检查 pgvector 扩展
            print("\n2. 检查 pgvector 扩展...")
            try:
                result = await conn.execute(text(
                    "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'"
                ))
                extension = result.fetchone()
                
                if extension:
                    print(f"   ✅ pgvector 扩展已安装 (版本: {extension.extversion})")
                else:
                    print("   ❌ pgvector 扩展未安装")
                    print("   💡 请运行以下命令安装:")
                    print("      CREATE EXTENSION IF NOT EXISTS vector;")
                    return False
                    
            except Exception as e:
                print(f"   ❌ 扩展检查失败: {e}")
                return False
            
            # 3. 检查向量操作符
            print("\n3. 检查向量操作符支持...")
            try:
                result = await conn.execute(text("""
                    SELECT oprname, oprleft::regtype, oprright::regtype, oprresult::regtype
                    FROM pg_operator 
                    WHERE oprname IN ('<->', '<#>', '<=>')
                    ORDER BY oprname
                """))
                operators = result.fetchall()
                
                if operators:
                    print("   ✅ 支持的向量操作符:")
                    for op in operators:
                        print(f"      {op.oprname} ({op.oprleft} x {op.oprright} → {op.oprresult})")
                else:
                    print("   ⚠️  未找到向量操作符")
                    
            except Exception as e:
                print(f"   ⚠️  操作符检查失败: {e}")
            
            # 4. 测试基本向量功能
            print("\n4. 测试基本向量功能...")
            try:
                # 创建临时测试表
                await conn.execute(text("""
                    CREATE TEMP TABLE test_vectors (
                        id SERIAL PRIMARY KEY,
                        content TEXT,
                        embedding VECTOR(3)
                    )
                """))
                
                # 插入测试数据
                await conn.execute(text("""
                    INSERT INTO test_vectors (content, embedding) 
                    VALUES 
                        ('测试1', '[0.1, 0.2, 0.3]'),
                        ('测试2', '[0.4, 0.5, 0.6]')
                """))
                
                # 执行相似度查询
                result = await conn.execute(text("""
                    SELECT id, content, embedding <-> '[0.2, 0.3, 0.4]' as distance
                    FROM test_vectors 
                    ORDER BY embedding <-> '[0.2, 0.3, 0.4]'
                    LIMIT 2
                """))
                
                rows = result.fetchall()
                print("   ✅ 向量查询功能正常")
                for row in rows:
                    print(f"      ID: {row.id}, 内容: {row.content}, 距离: {row.distance:.4f}")
                    
                # 清理临时表
                await conn.execute(text("DROP TABLE test_vectors"))
                
            except Exception as e:
                print(f"   ❌ 向量功能测试失败: {e}")
                return False
            
            print("\n" + "=" * 50)
            print("🎉 PostgreSQL 向量环境检查通过!")
            print("✅ 可以继续进行迁移步骤")
            
            return True
            
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("💡 请检查:")
        print("   1. PostgreSQL 服务是否运行")
        print("   2. 数据库连接字符串是否正确")
        print("   3. 数据库用户是否有足够权限")
        return False
    finally:
        if 'engine' in locals():
            await engine.dispose()


async def main():
    """主函数"""
    # 从环境变量获取数据库URL，或者使用默认值
    import os
    database_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgresql:mM6hbJXelbGd@localhost:5432/postgresql')
    
    print(f"使用数据库URL: {database_url}")
    print()
    
    success = await check_postgresql_environment(database_url)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())