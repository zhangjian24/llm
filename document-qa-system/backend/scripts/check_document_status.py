"""
检查数据库中文档状态
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import get_db_session
from app.repositories.document_repository import DocumentRepository


async def check_all_documents():
    """检查所有文档的状态"""
    print("="*60)
    print("📋 检查文档状态")
    print("="*60)
    
    async for session in get_db_session():
        try:
            repo = DocumentRepository(session)
            
            # 获取所有文档
            docs, total = await repo.find_all(page=1, limit=50)
            
            print(f"\n总文档数：{total}")
            print("\n文档列表:")
            print("-" * 60)
            
            for doc in docs:
                status_icon = "✅" if doc.status == 'ready' else "⏳" if doc.status == 'processing' else "❌"
                print(f"{status_icon} ID: {str(doc.id)[:8]}... | {doc.filename:30s} | {doc.status:12s} | Chunks: {doc.chunks_count or 0}")
            
            print("-" * 60)
            
            # 统计各状态文档数量
            status_count = {}
            for doc in docs:
                status = doc.status
                status_count[status] = status_count.get(status, 0) + 1
            
            print("\n状态统计:")
            for status, count in status_count.items():
                icon = "✅" if status == 'ready' else "⏳" if status == 'processing' else "❌"
                print(f"  {icon} {status}: {count} 个文档")
        
        except Exception as e:
            print(f"\n❌ 查询失败：{e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await session.close()
    
    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(check_all_documents())
