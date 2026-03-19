#!/usr/bin/env python3
"""
使用 PostgreSQL MCP 工具初始化项目数据表结构

执行步骤:
1. 启用 uuid-ossp 扩展
2. 创建 documents 表（文档元数据）
3. 创建 chunks 表（文档块）
4. 创建 document_chunks 表（大文件分块存储）
5. 创建 conversations 表（对话历史）
6. 创建索引
7. 创建触发器（自动更新 updated_at）

使用方法:
    python scripts/init_database_with_mcp.py
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import get_db_session


async def init_database():
    """初始化数据库的所有表结构"""
    
    print("=" * 60)
    print("RAG 文档问答系统 - 数据库表结构初始化")
    print("=" * 60)
    print()
    
    async for session in get_db_session():
        try:
            # Step 1: 启用扩展
            print("Step 1: 启用 PostgreSQL 扩展...")
            await session.execute(text("""
                CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
            """))
            print("✓ uuid-ossp 扩展已启用")
            print()
            
            # Step 2: 创建 documents 表
            print("Step 2: 创建 documents 表（文档元数据）...")
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS documents (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    filename VARCHAR(255) NOT NULL,
                    file_content BYTEA,
                    content_hash VARCHAR(64) UNIQUE,
                    file_size INTEGER NOT NULL,
                    mime_type VARCHAR(50) NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'processing',
                    chunks_count INTEGER,
                    chunk_count INTEGER,
                    metadata JSONB,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """))
            print("✓ documents 表创建完成")
            print()
            
            # Step 3: 创建 chunks 表
            print("Step 3: 创建 chunks 表（文档块）...")
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    token_count INTEGER NOT NULL,
                    embedding vector(1536),
                    metadata JSONB
                );
            """))
            print("✓ chunks 表创建完成")
            print()
            
            # Step 4: 创建 document_chunks 表（大文件分块存储）
            print("Step 4: 创建 document_chunks 表（大文件分块存储）...")
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    chunk_index INTEGER NOT NULL,
                    chunk_data BYTEA NOT NULL,
                    chunk_size INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    
                    UNIQUE(document_id, chunk_index)
                );
            """))
            print("✓ document_chunks 表创建完成")
            print()
            
            # Step 5: 创建 conversations 表
            print("Step 5: 创建 conversations 表（对话历史）...")
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID,
                    title VARCHAR(200),
                    messages JSONB,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """))
            print("✓ conversations 表创建完成")
            print()
            
            # Step 6: 创建索引
            print("Step 6: 创建索引...")
            
            # documents 表的索引
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
            """))
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at DESC);
            """))
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_documents_status_created ON documents(status, created_at DESC);
            """))
            
            # chunks 表的索引
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
            """))
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_chunks_doc_idx ON chunks(document_id, chunk_index);
            """))
            
            # document_chunks 表的索引
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);
            """))
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_document_chunks_created_at ON document_chunks(created_at);
            """))
            
            # conversations 表的索引
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
            """))
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at DESC);
            """))
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_conversations_user_updated ON conversations(user_id, updated_at DESC);
            """))
            
            print("✓ 所有索引创建完成")
            print()
            
            # Step 7: 创建触发器函数（自动更新 updated_at）
            print("Step 7: 创建触发器函数...")
            await session.execute(text("""
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """))
            print("✓ 触发器函数创建完成")
            print()
            
            # Step 8: 创建触发器
            print("Step 8: 创建触发器...")
            
            # documents 表的触发器
            await session.execute(text("""
                DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;
            """))
            await session.execute(text("""
                CREATE TRIGGER update_documents_updated_at
                    BEFORE UPDATE ON documents
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column();
            """))
            
            # conversations 表的触发器
            await session.execute(text("""
                DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;
            """))
            await session.execute(text("""
                CREATE TRIGGER update_conversations_updated_at
                    BEFORE UPDATE ON conversations
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column();
            """))
            
            print("✓ 所有触发器创建完成")
            print()
            
            await session.commit()
            
            # 完成
            print("=" * 60)
            print("✓ 数据库表结构初始化完成！")
            print("=" * 60)
            print()
            print("已创建的表:")
            print("  1. documents - 文档元数据表")
            print("  2. chunks - 文档块表（含向量字段）")
            print("  3. document_chunks - 大文件分块存储表")
            print("  4. conversations - 对话历史表")
            print()
            print("已创建的索引:")
            print("  - documents: status, created_at, status+created_at 复合索引")
            print("  - chunks: document_id, document_id+chunk_index 复合索引")
            print("  - document_chunks: document_id, created_at 索引")
            print("  - conversations: user_id, updated_at, user_id+updated_at 复合索引")
            print()
            print("已创建的触发器:")
            print("  - update_documents_updated_at - 自动更新 documents.updated_at")
            print("  - update_conversations_updated_at - 自动更新 conversations.updated_at")
            print()
            
        except Exception as e:
            await session.rollback()
            print(f"✗ 初始化失败：{e}")
            import traceback
            traceback.print_exc()
            raise


def main():
    """主函数"""
    try:
        asyncio.run(init_database())
        print("\n✓ 初始化成功完成!")
        return 0
    except Exception as e:
        print(f"\n✗ 初始化失败：{e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
