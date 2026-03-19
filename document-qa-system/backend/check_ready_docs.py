#!/usr/bin/env python3
"""
检查就绪文档
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import get_db_session
from app.repositories.document_repository import DocumentRepository

async def check_ready_documents():
    """检查就绪文档"""
    print("🔍 检查就绪文档...")
    
    try:
        # 获取数据库会话
        db_gen = get_db_session()
        session = await db_gen.__anext__()
        
        try:
            repo = DocumentRepository(session)
            
            # 查询就绪文档
            docs, total = await repo.find_all(page=1, limit=10, status='ready')
            
            print(f"✅ 就绪文档数量: {len(docs)}")
            print()
            
            if docs:
                print("📄 就绪文档列表:")
                for i, doc in enumerate(docs, 1):
                    print(f"{i}. {doc.filename}")
                    print(f"   ID: {doc.id}")
                    print(f"   大小: {doc.file_size:,} bytes")
                    print()
            else:
                print("⚠️  没有就绪文档")
                
        finally:
            await session.close()
            await db_gen.aclose()
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_ready_documents())