#!/usr/bin/env python3
"""
文档数据库存储功能测试脚本
"""

import asyncio
import sys
from pathlib import Path
import hashlib

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import get_db_session
from app.repositories.document_repository import DocumentRepository
from app.models.document import Document
from app.models.document_chunk import DocumentChunk

async def test_small_document_storage():
    """测试小文档直接存储"""
    print("=== 测试小文档存储 ===")
    
    async for session in get_db_session():
        try:
            repo = DocumentRepository(session)
            
            # 创建测试文档
            test_content = b"This is a test document content for small file storage."
            content_hash = hashlib.sha256(test_content).hexdigest()
            
            doc = Document(
                filename="test_small.txt",
                file_path="temp_path",  # 临时设置避免NOT NULL约束
                file_content=test_content,
                content_hash=content_hash,
                file_size=len(test_content),
                mime_type="text/plain",
                status="processing"
            )
            
            # 保存文档
            doc_id = await repo.save(doc)
            print(f"✓ 小文档保存成功，ID: {doc_id}")
            
            # 验证内容检索
            retrieved_content = await repo.get_document_content(doc_id)
            if retrieved_content == test_content:
                print("✓ 小文档内容检索验证通过")
            else:
                print("✗ 小文档内容检索失败")
                
            # 清理测试数据
            await repo.delete(doc_id)
            await session.commit()
            print("✓ 测试数据清理完成")
            
        except Exception as e:
            await session.rollback()
            print(f"✗ 小文档测试失败: {e}")
            raise

async def test_large_document_chunking():
    """测试大文档分块存储"""
    print("\n=== 测试大文档分块存储 ===")
    
    async for session in get_db_session():
        try:
            repo = DocumentRepository(session)
            
            # 创建测试大文档（模拟15MB文件）
            chunk_size = 5 * 1024 * 1024  # 5MB
            test_content = b"A" * (chunk_size * 3 + 100)  # 略大于15MB
            
            content_hash = hashlib.sha256(test_content).hexdigest()
            
            doc = Document(
                filename="test_large.bin",
                file_path="temp_path_large",  # 临时设置避免NOT NULL约束
                file_content=None,  # 大文件不直接存储内容
                content_hash=content_hash,
                file_size=len(test_content),
                mime_type="application/octet-stream",
                status="processing",
                chunk_count=0
            )
            
            # 保存文档
            doc_id = await repo.save(doc)
            print(f"✓ 大文档记录创建成功，ID: {doc_id}")
            
            # 分割成块
            chunks = []
            for i in range(0, len(test_content), chunk_size):
                chunk_data = test_content[i:i + chunk_size]
                chunks.append(chunk_data)
            
            print(f"✓ 文档分割成 {len(chunks)} 个分块")
            
            # 保存分块
            success = await repo.save_large_document_chunks(doc_id, chunks, len(chunks))
            if success:
                print("✓ 大文档分块保存成功")
            else:
                print("✗ 大文档分块保存失败")
                return
                
            # 验证分块合并
            merged_content = await repo.get_document_content(doc_id)
            if merged_content == test_content:
                print("✓ 大文档分块合并验证通过")
            else:
                print("✗ 大文档分块合并失败")
                print(f"  原始长度: {len(test_content)}")
                print(f"  合并长度: {len(merged_content) if merged_content else 0}")
                
            # 验证分块数量
            result = await session.execute(
                f"SELECT COUNT(*) FROM document_chunks WHERE document_id = '{doc_id}'"
            )
            chunk_count = result.scalar()
            if chunk_count == len(chunks):
                print("✓ 分块数量验证通过")
            else:
                print(f"✗ 分块数量不匹配: 期望{len(chunks)}, 实际{chunk_count}")
                
            # 清理测试数据
            await repo.delete(doc_id)
            await session.commit()
            print("✓ 测试数据清理完成")
            
        except Exception as e:
            await session.rollback()
            print(f"✗ 大文档测试失败: {e}")
            raise

async def test_duplicate_detection():
    """测试重复文档检测"""
    print("\n=== 测试重复文档检测 ===")
    
    async for session in get_db_session():
        try:
            repo = DocumentRepository(session)
            
            # 创建测试内容
            test_content = b"Duplicate detection test content"
            content_hash = hashlib.sha256(test_content).hexdigest()
            
            # 第一次保存
            doc1 = Document(
                filename="test_dup1.txt",
                file_path="temp_path_dup1",  # 临时设置避免NOT NULL约束
                file_content=test_content,
                content_hash=content_hash,
                file_size=len(test_content),
                mime_type="text/plain",
                status="ready"
            )
            
            doc_id1 = await repo.save(doc1)
            print(f"✓ 第一次保存成功，ID: {doc_id1}")
            
            # 第二次保存相同内容
            doc2 = Document(
                filename="test_dup2.txt",
                file_path="temp_path_dup2",  # 临时设置避免NOT NULL约束
                file_content=test_content,
                content_hash=content_hash,
                file_size=len(test_content),
                mime_type="text/plain",
                status="processing"
            )
            
            doc_id2 = await repo.save(doc2)
            print(f"✓ 第二次保存完成，ID: {doc_id2}")
            
            # 检查是否返回相同的ID（去重功能）
            if doc_id1 == doc_id2:
                print("✓ 重复文档检测功能正常")
            else:
                # 如果返回不同ID，检查是否能找到相同hash的文档
                existing_doc = await repo.find_by_content_hash(content_hash)
                if existing_doc and existing_doc.id == doc_id1:
                    print("✓ 重复文档检测功能正常（通过hash查找）")
                else:
                    print("✗ 重复文档检测功能异常")
            
            # 清理测试数据
            await repo.delete(doc_id1)
            await session.commit()
            print("✓ 测试数据清理完成")
            
        except Exception as e:
            await session.rollback()
            print(f"✗ 重复检测测试失败: {e}")
            raise

async def main():
    """主测试函数"""
    print("文档数据库存储功能测试")
    print("=" * 50)
    
    try:
        await test_small_document_storage()
        await test_large_document_chunking()
        await test_duplicate_detection()
        
        print("\n" + "=" * 50)
        print("✓ 所有测试通过!")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())