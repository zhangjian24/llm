"""
清理测试数据
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import get_db_session
from sqlalchemy import text


async def cleanup_test_data():
    """清理所有文档和 chunks"""
    print("Cleaning up test data...")
    
    async for session in get_db_session():
        try:
            # 使用 TRUNCATE 更快更彻底
            await session.execute(text("TRUNCATE TABLE chunks, documents CASCADE"))
            await session.commit()
            print("✅ Cleanup completed (TRUNCATE)")
        except Exception as e:
            print(f"Error: {e}")
            await session.rollback()
        finally:
            await session.close()


if __name__ == "__main__":
    asyncio.run(cleanup_test_data())
