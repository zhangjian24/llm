#!/usr/bin/env python3
"""
文档存储迁移脚本
将文档从文件系统存储迁移到数据库存储

注意：此脚本应在生产环境执行前进行充分测试
建议先在测试环境中运行并验证结果
"""

import os
import sys
import hashlib
import asyncio
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import get_settings
from app.core.database import get_db_session

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

settings = get_settings()

async def create_migration_tables():
    """创建迁移所需的表结构"""
    print("正在创建迁移表结构...")
    
    async for session in get_db_session():
        try:
            # 添加新的字段
            await session.execute(text("""
                ALTER TABLE documents 
                ADD COLUMN IF NOT EXISTS file_content BYTEA,
                ADD COLUMN IF NOT EXISTS content_hash VARCHAR(64) UNIQUE,
                ADD COLUMN IF NOT EXISTS chunk_count INTEGER
            """))
            
            # 创建索引
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_documents_content_hash 
                ON documents (content_hash)
            """))
            
            await session.commit()
            print("✓ 表结构更新完成")
        except Exception as e:
            await session.rollback()
            print(f"✗ 表结构更新失败: {e}")
            raise

async def calculate_file_hash(file_path: str) -> str:
    """计算文件内容的SHA256哈希"""
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except FileNotFoundError:
        return None

async def migrate_existing_documents():
    """迁移现有的文档文件到数据库"""
    print("正在迁移现有文档...")
    
    async for session in get_db_session():
        try:
            # 查询所有文档
            result = await session.execute(text("""
                SELECT id, file_path, file_size 
                FROM documents 
                WHERE file_path IS NOT NULL
            """))
            
            documents = result.fetchall()
            total_docs = len(documents)
            migrated_count = 0
            
            print(f"找到 {total_docs} 个需要迁移的文档")
            
            for doc in documents:
                doc_id, file_path, file_size = doc
                
                if not file_path or not os.path.exists(file_path):
                    print(f"警告: 文档 {doc_id} 的文件路径不存在: {file_path}")
                    continue
                
                try:
                    # 计算文件哈希
                    content_hash = await calculate_file_hash(file_path)
                    if not content_hash:
                        print(f"警告: 无法计算文档 {doc_id} 的哈希值")
                        continue
                    
                    # 读取文件内容
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                    
                    # 检查是否已有相同内容的文档
                    existing_doc = await session.execute(text("""
                        SELECT id FROM documents 
                        WHERE content_hash = :content_hash AND id != :doc_id
                    """), {"content_hash": content_hash, "doc_id": doc_id})
                    
                    if existing_doc.fetchone():
                        print(f"跳过重复文档 {doc_id}: 已存在相同内容")
                        continue
                    
                    # 更新文档记录
                    await session.execute(text("""
                        UPDATE documents 
                        SET file_content = :file_content,
                            content_hash = :content_hash
                        WHERE id = :doc_id
                    """), {
                        "file_content": file_content,
                        "content_hash": content_hash,
                        "doc_id": doc_id
                    })
                    
                    migrated_count += 1
                    print(f"✓ 迁移文档 {doc_id} ({migrated_count}/{total_docs})")
                    
                except Exception as e:
                    print(f"✗ 迁移文档 {doc_id} 失败: {e}")
                    continue
            
            await session.commit()
            print(f"迁移完成: {migrated_count}/{total_docs} 个文档")
            
        except Exception as e:
            await session.rollback()
            print(f"✗ 迁移过程失败: {e}")
            raise

async def verify_migration():
    """验证迁移结果"""
    print("正在验证迁移结果...")
    
    async for session in get_db_session():
        try:
            # 检查迁移统计
            result = await session.execute(text("""
                SELECT 
                    COUNT(*) as total_docs,
                    COUNT(file_content) as docs_with_content,
                    COUNT(content_hash) as docs_with_hash
                FROM documents
            """))
            
            stats = result.fetchone()
            total, with_content, with_hash = stats
            
            print(f"迁移统计:")
            print(f"  总文档数: {total}")
            print(f"  已迁移文档数: {with_content}")
            print(f"  有哈希值文档数: {with_hash}")
            
            # 检查是否有未迁移的文档
            result = await session.execute(text("""
                SELECT COUNT(*) 
                FROM documents 
                WHERE file_path IS NOT NULL AND file_content IS NULL
            """))
            
            unprocessed = result.scalar()
            if unprocessed > 0:
                print(f"⚠ 警告: 仍有 {unprocessed} 个文档未迁移")
            else:
                print("✓ 所有文档均已成功迁移")
                
        except Exception as e:
            print(f"✗ 验证失败: {e}")
            raise

async def cleanup_old_files():
    """清理旧的文件系统文件（可选）"""
    print("清理旧文件...")
    
    # 这里可以根据需要实现文件清理逻辑
    # 建议在确认迁移完全成功后再执行
    print("文件清理功能待实现")

async def main():
    """主迁移函数"""
    print("=" * 50)
    print("文档存储迁移工具")
    print("=" * 50)
    
    try:
        # 1. 创建表结构
        await create_migration_tables()
        
        # 2. 迁移现有文档
        await migrate_existing_documents()
        
        # 3. 验证迁移结果
        await verify_migration()
        
        # 4. 清理旧文件（可选）
        # await cleanup_old_files()
        
        print("\n✓ 迁移完成!")
        print("请测试系统功能确保一切正常工作")
        
    except Exception as e:
        print(f"\n✗ 迁移失败: {e}")
        print("请检查错误信息并重新尝试")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())