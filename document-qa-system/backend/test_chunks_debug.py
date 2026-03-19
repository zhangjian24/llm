"""
文档上传与向量化流程测试脚本
用于定位 chunks 表 metadata 和 embedding 字段为空的问题
"""
import asyncio
import sys
from pathlib import Path
from uuid import UUID
import structlog

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# 配置日志输出到控制台
structlog.configure(
    processors=[
        structlog.dev.ConsoleRenderer(colors=True),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=False,
)

logger = structlog.get_logger()


async def test_document_upload_and_vectorization():
    """测试文档上传完整流程"""
    
    print("=" * 80)
    print("🧪 开始测试文档上传与向量化流程")
    print("=" * 80)
    
    # 导入必要的模块
    from app.core.database import AsyncSessionLocal, get_db_session
    from app.services.document_service import DocumentService
    from app.repositories.document_repository import DocumentRepository
    from app.services.embedding_service import EmbeddingService
    from sqlalchemy import select, func
    from app.models.chunk import Chunk
    from app.models.document import Document
    
    test_file_path = Path("test_chunks_fix.txt")
    test_content = """
第一章：公司简介

我们公司成立于 2020 年，专注于人工智能技术的研发。
主要产品包括智能客服、文档问答系统等。
团队由来自清华、北大等知名高校的 AI 专家组成。

第二章：员工手册

1. 考勤制度
员工工作时间为周一至周五，上午 9:00 至下午 6:00。
迟到早退需要提前请假。每月允许 3 次迟到。

2. 年假制度
入职满一年后，可享受 5 天带薪年假。
每多工作一年，增加 1 天年假，最多 10 天。
年假可以分段休息，但每次至少 3 天。

第三章：财务报销

员工因公支出可以报销，需要提供发票和报销单。
报销流程：提交申请 → 部门经理审批 → 财务审核 → 打款。
报销周期为每月 15 日和 30 日。
"""
    
    try:
        # 创建测试文件
        test_file_path.write_text(test_content, encoding='utf-8')
        
        logger.info(
            "test_file_created",
            file_path=str(test_file_path),
            content_size=len(test_content)
        )
        
        async with AsyncSessionLocal() as session:
            # 创建服务实例
            doc_repo = DocumentRepository(session)
            embedding_svc = EmbeddingService()
            doc_service = DocumentService(doc_repo, embedding_svc)
            
            logger.info("services_initialized")
            
            # 读取测试文件
            file_content = test_file_path.read_bytes()
            filename = "test_chunks_fix.txt"
            mime_type = "text/plain"
            file_size = len(file_content)
            
            logger.info(
                "uploading_document",
                filename=filename,
                size_bytes=file_size,
                mime_type=mime_type
            )
            
            # 上传文档
            doc_id = await doc_service.upload_document(
                file_content=file_content,
                filename=filename,
                mime_type=mime_type,
                file_size=file_size
            )
            
            # 📝 关键：手动提交事务，让异步任务能够查询到文档
            logger.info(
                "committing_transaction",
                doc_id=str(doc_id)
            )
            await session.commit()
            logger.info(
                "transaction_committed",
                doc_id=str(doc_id)
            )
            
            # 📝 关键：事务提交后手动启动异步处理任务
            logger.info(
                "starting_async_processing_manual",
                doc_id=str(doc_id)
            )
            asyncio.create_task(doc_service._process_document_async(doc_id))
            
            logger.info(
                "document_uploaded",
                doc_id=str(doc_id),
                waiting_for_async_processing=True,
                async_task_started=True
            )
            
            # 等待异步处理完成（实际应该用事件或轮询）
            print("\n⏳ 等待异步处理完成...")
            for i in range(15):
                await asyncio.sleep(1)
                print(f"   已等待 {i+1} 秒")
                
                # 检查文档状态
                doc_result = await session.execute(
                    select(Document).where(Document.id == doc_id)
                )
                doc = doc_result.scalar_one_or_none()
                
                if doc:
                    status_info = f"状态：{doc.status}"
                    if doc.status == 'ready':
                        chunks_result = await session.execute(
                            select(func.count(Chunk.id)).where(
                                Chunk.document_id == doc_id
                            )
                        )
                        chunk_count = chunks_result.scalar()
                        
                        chunks_with_embedding = await session.execute(
                            select(func.count(Chunk.id)).where(
                                Chunk.document_id == doc_id,
                                Chunk.embedding.isnot(None)
                            )
                        )
                        embedded_count = chunks_with_embedding.scalar()
                        
                        chunks_with_metadata = await session.execute(
                            select(func.count(Chunk.id)).where(
                                Chunk.document_id == doc_id,
                                Chunk.chunk_metadata.isnot(None)
                            )
                        )
                        metadata_count = chunks_with_metadata.scalar()
                        
                        status_info += f" | Chunks: {chunk_count} | With Embedding: {embedded_count} | With Metadata: {metadata_count}"
                        
                        if embedded_count > 0 and metadata_count > 0:
                            print(f"\n✅ 处理完成！{status_info}")
                            break
                    
                if (i + 1) % 5 == 0:
                    print(f"   📊 当前状态：{status_info}")
            
            # 详细检查数据库
            print("\n" + "=" * 80)
            print("📊 数据库检查结果")
            print("=" * 80)
            
            # 1. 检查文档状态
            doc_result = await session.execute(
                select(Document).where(Document.id == doc_id)
            )
            doc = doc_result.scalar_one_or_none()
            
            if doc:
                print(f"\n📄 文档信息:")
                print(f"   ID: {doc.id}")
                print(f"   文件名：{doc.filename}")
                print(f"   状态：{doc.status}")
                print(f"   MIME 类型：{doc.mime_type}")
                print(f"   文件大小：{doc.file_size} bytes")
            else:
                print(f"\n❌ 文档未找到：{doc_id}")
            
            # 2. 检查 Chunks 统计
            total_chunks = await session.execute(
                select(func.count(Chunk.id)).where(
                    Chunk.document_id == doc_id
                )
            )
            total_count = total_chunks.scalar()
            
            with_embedding = await session.execute(
                select(func.count(Chunk.id)).where(
                    Chunk.document_id == doc_id,
                    Chunk.embedding.isnot(None)
                )
            )
            embedding_count = with_embedding.scalar()
            
            with_metadata = await session.execute(
                select(func.count(Chunk.id)).where(
                    Chunk.document_id == doc_id,
                    Chunk.chunk_metadata.isnot(None)
                )
            )
            metadata_count = with_metadata.scalar()
            
            complete_chunks = await session.execute(
                select(func.count(Chunk.id)).where(
                    Chunk.document_id == doc_id,
                    Chunk.embedding.isnot(None),
                    Chunk.chunk_metadata.isnot(None)
                )
            )
            complete_count = complete_chunks.scalar()
            
            print(f"\n📦 Chunks 统计:")
            print(f"   总数量：{total_count}")
            print(f"   有 Embedding: {embedding_count} ({embedding_count/total_count*100:.1f}%)" if total_count > 0 else "   有 Embedding: 0")
            print(f"   有 Metadata: {metadata_count} ({metadata_count/total_count*100:.1f}%)" if total_count > 0 else "   有 Metadata: 0")
            print(f"   完整数据：{complete_count} ({complete_count/total_count*100:.1f}%)" if total_count > 0 else "   完整数据：0")
            
            # 3. 抽查具体记录
            if total_count > 0:
                print(f"\n🔍 抽查前 3 条 Chunk 记录:")
                # 📝 关键：使用原生 SQL 查询，避免 SQLAlchemy 处理 pgvector 类型
                from sqlalchemy import text
                
                # 查询 chunk 基本信息（不包含 embedding）
                chunk_result = await session.execute(
                    text("""
                        SELECT id, document_id, chunk_index, content, token_count, metadata
                        FROM chunks
                        WHERE document_id = :doc_id
                        ORDER BY chunk_index
                        LIMIT 3
                    """),
                    {"doc_id": doc_id}
                )
                chunk_rows = chunk_result.all()
                
                # 单独查询 embedding 存在性和维度
                emb_result = await session.execute(
                    text("""
                        SELECT id, 
                               CASE WHEN embedding IS NOT NULL THEN vector_dims(embedding) ELSE 0 END as emb_dim,
                               embedding IS NOT NULL as has_embedding
                        FROM chunks
                        WHERE document_id = :doc_id
                        ORDER BY chunk_index
                        LIMIT 3
                    """),
                    {"doc_id": doc_id}
                )
                emb_rows = emb_result.all()
                
                for i, (chunk_row, emb_row) in enumerate(zip(chunk_rows, emb_rows), 1):
                    print(f"\n   Chunk {i}:")
                    print(f"      ID: {chunk_row.id}")
                    print(f"      Index: {chunk_row.chunk_index}")
                    print(f"      Content 长度：{len(chunk_row.content) if chunk_row.content else 0}")
                    print(f"      Token 数：{chunk_row.token_count}")
                    has_emb = emb_row.has_embedding and emb_row.emb_dim > 0
                    print(f"      Embedding: {'✅' if has_emb else '❌ NULL'}")
                    if has_emb:
                        print(f"         维度：{emb_row.emb_dim}")
                    print(f"      Metadata: {'✅' if chunk_row.metadata is not None else '❌ NULL'}")
                    if chunk_row.metadata is not None:
                        metadata_dict = chunk_row.metadata if isinstance(chunk_row.metadata, dict) else {}
                        print(f"         Keys: {list(metadata_dict.keys()) if metadata_dict else 'N/A'}")
                        print(f"         内容预览：{str(metadata_dict.get('content', ''))[:50] if metadata_dict else 'N/A'}")
            
            # 4. 问题诊断
            print("\n" + "=" * 80)
            print("🔍 问题诊断")
            print("=" * 80)
            
            if total_count == 0:
                print("\n⚠️  **问题**: 没有创建任何 Chunk 记录")
                print("💡 **建议**: 检查文档解析和分块流程")
            
            elif embedding_count == 0:
                print("\n⚠️  **问题**: 所有 Chunk 的 embedding 字段都为 NULL")
                print("💡 **建议**:")
                print("   1. 检查 Embedding API 调用是否成功")
                print("   2. 查看日志中的 embedding_* 错误")
                print("   3. 验证 DASHSCOPE_API_KEY 是否有效")
            
            elif metadata_count == 0:
                print("\n⚠️  **问题**: 所有 Chunk 的 metadata 字段都为 NULL")
                print("💡 **建议**:")
                print("   1. 检查 Chunk 对象创建时是否正确设置 metadata")
                print("   2. 查看日志中的 vector_data_validation 信息")
                print("   3. 验证 upsert_vectors 时的 metadata 参数")
            
            elif complete_count == total_count:
                print("\n✅ **成功**: 所有 Chunk 数据完整!")
            
            else:
                print(f"\n⚠️  **问题**: 部分 Chunk 数据不完整")
                print(f"   完整：{complete_count}/{total_count}")
                print(f"   缺失：{total_count - complete_count}")
            
            print("\n" + "=" * 80)
            
    except Exception as e:
        logger.error(
            "test_failed",
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True
        )
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理测试文件
        if test_file_path.exists():
            test_file_path.unlink()
            logger.info("test_file_cleaned")


if __name__ == "__main__":
    print("\n🚀 执行文档上传与向量化流程测试...\n")
    asyncio.run(test_document_upload_and_vectorization())
    print("\n✅ 测试脚本执行完成\n")
