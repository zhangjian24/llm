#!/usr/bin/env python3
"""
大文件分块存储表创建脚本
"""

import asyncio
import sys
from pathlib import Path
from sqlalchemy import text
from app.core.database import get_db_session

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

async def create_document_chunks_table():
    """创建document_chunks表"""
    print("正在创建document_chunks表...")
    
    async for session in get_db_session():
        try:
            # 创建document_chunks表
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    chunk_index INTEGER NOT NULL,
                    chunk_data BYTEA NOT NULL,
                    chunk_size INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    
                    -- 确保同一文档的分块索引唯一
                    UNIQUE(document_id, chunk_index)
                )
            """))
            
            # 创建索引
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id 
                ON document_chunks (document_id)
            """))
            
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_document_chunks_created_at 
                ON document_chunks (created_at)
            """))
            
            await session.commit()
            print("✓ document_chunks表创建完成")
            
        except Exception as e:
            await session.rollback()
            print(f"✗ 创建表失败: {e}")
            raise

async def main():
    """主函数"""
    print("=" * 50)
    print("大文件分块存储表创建工具")
    print("=" * 50)
    
    try:
        await create_document_chunks_table()
        print("\n✓ 表创建完成!")
        
    except Exception as e:
        print(f"\n✗ 创建失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())