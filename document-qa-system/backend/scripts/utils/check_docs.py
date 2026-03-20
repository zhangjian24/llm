#!/usr/bin/env python3
"""
检查数据库中的文档状态
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import get_db_session
from app.repositories.document_repository import DocumentRepository
from app.models.document import Document

async def check_documents():
    """检查文档状态"""
    print("=" * 60)
    print("检查数据库中的文档")
    print("=" * 60)
    
    try:
        # 获取数据库会话
        db_gen = get_db_session()
        session = await db_gen.__anext__()  # 获取第一个（也是唯一一个）yield的值
        
        try:
            repo = DocumentRepository(session)
            
            # 查询所有文档
            documents, total = await repo.find_all(page=1, limit=100)
            
            print(f"📊 数据库中共有 {total} 个文档")
            print()
            
            if documents:
                print("📄 文档列表:")
                print("-" * 60)
                for i, doc in enumerate(documents, 1):
                    status_icon = "✅" if doc.status == "ready" else "⏳" if doc.status == "processing" else "❌"
                    print(f"{i:2d}. {status_icon} {doc.filename}")
                    print(f"     ID: {doc.id}")
                    print(f"     状态: {doc.status}")
                    print(f"     大小: {doc.file_size:,} bytes")
                    print(f"     时间: {doc.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    print()
            else:
                print("⚠️  数据库中没有文档")
                print("💡 请先上传一些文档到系统中")
                
            # 检查就绪文档数量
            ready_docs = [doc for doc in documents if doc.status == "ready"]
            processing_docs = [doc for doc in documents if doc.status == "processing"]
            failed_docs = [doc for doc in documents if doc.status == "failed"]
            
            print("=" * 60)
            print("📈 统计信息:")
            print(f"   就绪文档: {len(ready_docs)} 个")
            print(f"   处理中: {len(processing_docs)} 个")
            print(f"   失败文档: {len(failed_docs)} 个")
            print("=" * 60)
            
        finally:
            await session.close()
            await db_gen.aclose()  # 关闭生成器
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_documents())