"""
手动触发文档处理脚本

用于处理那些上传后一直处于 processing 状态的文档
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import get_db_session
from app.repositories.document_repository import DocumentRepository
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService


async def process_all_pending_documents():
    """处理所有 pending 状态的文档"""
    print("="*60)
    print("🔧 手动触发文档处理")
    print("="*60)
    
    async for session in get_db_session():
        try:
            # 创建服务实例
            repo = DocumentRepository(session)
            embedding_svc = EmbeddingService()
            service = DocumentService(repo, embedding_svc)
            
            # 获取所有 processing 状态的文档
            print("\n📋 查询 processing 状态的文档...")
            docs, total = await repo.find_all(status='processing')
            
            if not docs:
                print("✅ 没有需要处理的文档")
                return
            
            print(f"找到 {len(docs)} 个待处理文档")
            
            # 逐个处理
            for doc in docs:
                print(f"\n处理文档：{doc.filename} (ID: {doc.id})")
                print(f"  状态：{doc.status}")
                print(f"  大小：{doc.file_size} bytes")
                
                try:
                    # 触发异步处理
                    print(f"  🚀 开始处理...")
                    await service._process_document_async(doc.id)
                    await session.commit()
                    print(f"  ✅ 处理成功！")
                    
                except Exception as e:
                    print(f"  ❌ 处理失败：{e}")
                    await session.rollback()
                    
                    # 更新状态为 failed
                    try:
                        await repo.update_status(doc.id, 'failed')
                        await session.commit()
                        print(f"  ⚠️ 已标记为失败")
                    except Exception as update_error:
                        print(f"  ❌ 更新状态失败：{update_error}")
        
        except Exception as e:
            print(f"\n❌ 发生错误：{e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await session.close()
    
    print("\n" + "="*60)
    print("✅ 所有文档处理完成")
    print("="*60)


async def check_document_status(doc_id: str):
    """检查特定文档的状态"""
    print(f"\n🔍 检查文档状态：{doc_id}")
    
    async for session in get_db_session():
        try:
            repo = DocumentRepository(session)
            doc = await repo.find_by_id(doc_id)
            
            if doc:
                print(f"  文件名：{doc.filename}")
                print(f"  状态：{doc.status}")
                print(f"  Chunks: {doc.chunks_count}")
                print(f"  创建时间：{doc.created_at}")
                print(f"  更新时间：{doc.updated_at}")
            else:
                print(f"  ❌ 文档不存在")
        
        except Exception as e:
            print(f"  ❌ 查询失败：{e}")
        
        finally:
            await session.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 检查特定文档
        doc_id = sys.argv[1]
        asyncio.run(check_document_status(doc_id))
    else:
        # 处理所有 pending 文档
        asyncio.run(process_all_pending_documents())
