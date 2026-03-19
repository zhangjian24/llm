import asyncio
from app.core.database import get_db_session
from sqlalchemy import text

async def alter_table():
    async for session in get_db_session():
        try:
            await session.execute(text('ALTER TABLE documents ALTER COLUMN file_path DROP NOT NULL'))
            await session.commit()
            print('✓ file_path列已修改为允许NULL值')
        except Exception as e:
            await session.rollback()
            print(f'✗ 修改失败: {e}')

if __name__ == "__main__":
    asyncio.run(alter_table())