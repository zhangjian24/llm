"""
数据库迁移脚本：移除 documents 表的 file_path 列

背景:
- 旧版本使用 file_path 存储文件系统路径
- 新版本直接在数据库中存储 file_content (LargeBinary)
- 需要移除了 file_path 列以匹配当前的数据模型

使用方法:
    python scripts/remove_file_path_column.py
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_settings

settings = get_settings()


async def migrate():
    """执行数据库迁移"""
    print("=" * 60)
    print("数据库迁移：移除 file_path 列")
    print("=" * 60)
    print()
    
    engine = create_async_engine(settings.DATABASE_URL)
    
    try:
        async with engine.connect() as conn:
            # Step 1: 检查 file_path 列是否存在
            print("📋 检查数据库表结构...")
            result = await conn.execute(text("""
                SELECT column_name, is_nullable, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'documents' 
                AND column_name = 'file_path'
            """))
            
            column_info = result.first()
            
            if not column_info:
                print("✅ file_path 列不存在，无需迁移")
                print()
                # 检查是否有其他相关约束
                result = await conn.execute(text("""
                    SELECT constraint_name, constraint_type 
                    FROM information_schema.table_constraints 
                    WHERE table_name = 'documents'
                """))
                constraints = result.fetchall()
                if constraints:
                    print("📊 当前 documents 表的约束:")
                    for c in constraints:
                        print(f"   - {c[0]}: {c[1]}")
                return
            
            print(f"✅ 找到 file_path 列")
            print(f"   - 是否允许 NULL: {column_info[1]}")
            print(f"   - 数据类型：{column_info[2]}")
            print()
            
            # Step 2: 如果列为 NOT NULL，先移除约束
            if column_info[1] == 'NO':
                print("🔧 步骤 1/2: 移除 NOT NULL 约束...")
                await conn.execute(text("""
                    ALTER TABLE documents 
                    ALTER COLUMN file_path DROP NOT NULL
                """))
                print("✅ 已移除 NOT NULL 约束")
                print()
            else:
                print("ℹ️  列已经允许 NULL，跳过此步骤")
                print()
            
            # Step 3: 删除列
            print("🔧 步骤 2/2: 删除 file_path 列...")
            await conn.execute(text("""
                ALTER TABLE documents 
                DROP COLUMN file_path
            """))
            print("✅ 已成功删除 file_path 列")
            print()
            
            # Step 4: 验证删除结果
            print("📋 验证迁移结果...")
            result = await conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'documents'
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            print("✅ 当前 documents 表的列:")
            for col in columns:
                print(f"   - {col[0]}: {col[1]}")
            print()
            
            # 提交事务
            await conn.commit()
            
            print("=" * 60)
            print("✅ 数据库迁移完成！")
            print("=" * 60)
            print()
            print("下一步:")
            print("1. 重启后端服务")
            print("2. 重新测试文档上传功能")
            print("3. 检查日志确认无错误")
            
    except Exception as e:
        print(f"❌ 迁移失败：{e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(migrate())
    except KeyboardInterrupt:
        print("\n⚠️  用户中断")
        sys.exit(1)
