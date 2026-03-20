"""
简单测试：验证事务统一管理的修复效果
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.core.database import AsyncSessionLocal
from app.services.document_service import DocumentService
from app.repositories.document_repository import DocumentRepository
from sqlalchemy import text


async def test_transaction():
    """测试文档上传完整流程"""
    
    print("=" * 80)
    print("🧪 测试事务统一管理修复")
    print("=" * 80)
    
    test_content = """第一章：公司简介

我们公司成立于 2020 年，专注于人工智能技术的研发。
"""
    
    try:
        # 创建测试文件
        test_file_path = Path("test_transaction.txt")
        test_file_path.write_text(test_content, encoding='utf-8')
        
        async with AsyncSessionLocal() as session:
            # 创建服务实例
            doc_repo = DocumentRepository(session)
            from app.services.embedding_service import EmbeddingService
            embedding_svc = EmbeddingService()
            doc_service = DocumentService(doc_repo, embedding_svc)
            
            # 读取测试文件
            file_content = test_file_path.read_bytes()
            filename = "test_transaction.txt"
            mime_type = "text/plain"
            file_size = len(file_content)
            
            print(f"\n📄 上传文档：{filename}")
            
            # 上传文档
            doc_id = await doc_service.upload_document(
                file_content=file_content,
                filename=filename,
                mime_type=mime_type,
                file_size=file_size
            )
            
            print(f"✅ 文档已上传，ID: {doc_id}")
            print(f"⏳ 等待异步处理完成...")
            
            # 提交事务并启动异步任务
            await session.commit()
            asyncio.create_task(doc_service._process_document_async(doc_id))
            
            # 等待处理完成
            for i in range(20):
                await asyncio.sleep(1)
                
                # 检查文档状态
                result = await session.execute(
                    text("""
                        SELECT status, 
                               (SELECT COUNT(*) FROM chunks WHERE document_id = :doc_id) as total_chunks,
                               (SELECT COUNT(*) FROM chunks WHERE document_id = :doc_id AND embedding IS NOT NULL) as with_embedding,
                               (SELECT COUNT(*) FROM chunks WHERE document_id = :doc_id AND metadata IS NOT NULL) as with_metadata
                        FROM documents 
                        WHERE id = :doc_id
                    """),
                    {"doc_id": doc_id}
                )
                row = result.first()
                
                if row and row[0] == 'ready':
                    print(f"\n✅ 处理完成！")
                    print(f"   状态：{row[0]}")
                    print(f"   总 Chunks: {row[1]}")
                    print(f"   有 Embedding: {row[2]}")
                    print(f"   有 Metadata: {row[3]}")
                    
                    if row[2] == row[1] and row[3] == row[1]:
                        print(f"\n🎉 成功！所有 Chunk 都有 Embedding 和 Metadata!")
                    else:
                        print(f"\n⚠️  部分 Chunk 缺失数据")
                    break
                
                if (i + 1) % 5 == 0:
                    print(f"   已等待 {i+1} 秒...")
            
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理测试文件
        if test_file_path.exists():
            test_file_path.unlink()


if __name__ == "__main__":
    asyncio.run(test_transaction())
