"""
文档重新向量化脚本
对现有文档的 chunks 进行向量化并存储到 PostgreSQL
"""

import sys
import os
from pathlib import Path

# 修复导入路径问题
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(script_dir))

import asyncio
import numpy as np
from typing import List
from sqlalchemy import select
from app.models.chunk import Chunk
from app.models.document import Document
from app.services.embedding_service import EmbeddingService
from app.services.postgresql_vector_service import PostgreSQLVectorService
from app.core.database import AsyncSessionLocal
from app.core.config import get_settings
import structlog

logger = structlog.get_logger()
settings = get_settings()


async def revectorize_documents(
    batch_size: int = 50,
    max_documents: int = None
):
    """
    对现有文档重新向量化
    
    Args:
        batch_size: 批处理大小
        max_documents: 最大处理文档数（None 表示全部）
    """
    print("🔄 开始文档重新向量化")
    print("=" * 50)
    
    embedding_service = EmbeddingService()
    vector_service = PostgreSQLVectorService()
    
    try:
        async with AsyncSessionLocal() as session:
            # 获取需要向量化的文档
            stmt = select(Document).where(
                Document.status == 'ready'
            ).order_by(Document.created_at.desc())
            
            if max_documents:
                stmt = stmt.limit(max_documents)
            
            result = await session.execute(stmt)
            documents = result.scalars().all()
            
            print(f"找到 {len(documents)} 个已就绪的文档")
            
            if not documents:
                print("⚠️  没有找到需要向量化的文档")
                return
            
            total_chunks_processed = 0
            total_chunks_vectorized = 0
            
            # 按文档处理
            for doc_idx, document in enumerate(documents):
                print(f"\n处理文档 [{doc_idx + 1}/{len(documents)}]: {document.filename}")
                
                # 获取该文档的所有 chunks
                stmt = select(Chunk).where(
                    Chunk.document_id == document.id
                ).order_by(Chunk.chunk_index)
                
                result = await session.execute(stmt)
                chunks = result.scalars().all()
                
                print(f"  - 找到 {len(chunks)} 个文档块")
                
                if not chunks:
                    continue
                
                # 分批向量化
                for i in range(0, len(chunks), batch_size):
                    batch_chunks = chunks[i:i + batch_size]
                    batch_vectors = []
                    
                    print(f"  - 处理批次 [{i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}]")
                    
                    # 批量生成向量
                    chunk_contents = [chunk.content for chunk in batch_chunks]
                    try:
                        embeddings = await embedding_service.embed_batch(
                            chunk_contents, 
                            batch_size=min(len(chunk_contents), 10)
                        )
                        
                        # 准备向量数据
                        for j, (chunk, embedding) in enumerate(zip(batch_chunks, embeddings)):
                            if len(embedding) != settings.VECTOR_DIMENSION:
                                logger.warning(
                                    "embedding_dimension_mismatch",
                                    expected=settings.VECTOR_DIMENSION,
                                    actual=len(embedding),
                                    chunk_id=str(chunk.id)
                                )
                                continue
                            
                            batch_vectors.append({
                                'id': str(chunk.id),
                                'values': embedding,
                                'metadata': {
                                    'document_id': str(chunk.document_id),
                                    'chunk_index': chunk.chunk_index,
                                    'content': chunk.content[:200]  # 截断长内容
                                }
                            })
                            
                            # 直接更新 chunk 的 embedding 字段
                            chunk.embedding = np.array(embedding, dtype=np.float32)
                    
                    except Exception as e:
                        logger.error(
                            "batch_embedding_failed",
                            document_id=str(document.id),
                            batch_start=i,
                            error=str(e)
                        )
                        continue
                    
                    # 批量更新数据库
                    if batch_vectors:
                        try:
                            await session.commit()
                            total_chunks_vectorized += len(batch_vectors)
                            print(f"    ✅ 成功向量化 {len(batch_vectors)} 个块")
                        except Exception as e:
                            await session.rollback()
                            logger.error(
                                "batch_database_update_failed",
                                document_id=str(document.id),
                                batch_start=i,
                                error=str(e)
                            )
                    
                    total_chunks_processed += len(batch_chunks)
                
                # 显示进度
                progress = (doc_idx + 1) / len(documents) * 100
                print(f"  进度: {progress:.1f}% ({doc_idx + 1}/{len(documents)})")
            
            # 最终统计
            print("\n" + "=" * 50)
            print("📊 重新向量化完成统计:")
            print(f"  - 处理文档数: {len(documents)}")
            print(f"  - 处理块总数: {total_chunks_processed}")
            print(f"  - 成功向量化: {total_chunks_vectorized}")
            print(f"  - 成功率: {(total_chunks_vectorized/total_chunks_processed)*100:.1f}%" if total_chunks_processed > 0 else "0%")
            
            # 显示数据库统计
            stats = await vector_service.get_index_stats(session)
            print(f"  - 数据库向量总数: {stats.get('total_vector_count', 0)}")
            
            print("\n🎉 文档重新向量化完成!")
            
    except Exception as e:
        logger.error(
            "revectorization_failed",
            error=str(e),
            exc_info=True
        )
        raise


async def verify_vectorization():
    """验证向量化结果"""
    print("\n🔍 验证向量化结果")
    print("=" * 50)
    
    vector_service = PostgreSQLVectorService()
    
    try:
        async with AsyncSessionLocal() as session:
            # 获取统计信息
            stats = await vector_service.get_index_stats(session)
            
            print(f"数据库统计:")
            print(f"  - 总向量数: {stats.get('total_vector_count', 0)}")
            print(f"  - 向量维度: {stats.get('dimension', 0)}")
            print(f"  - 索引类型: {stats.get('index_type', 'unknown')}")
            
            # 显示文档分布
            documents = stats.get('documents', [])
            if documents:
                print(f"\n按文档分布:")
                for doc_stat in documents[:10]:  # 只显示前10个
                    print(f"  - 文档 {doc_stat['document_id'][:8]}: {doc_stat['vector_count']} 个向量")
                if len(documents) > 10:
                    print(f"  ... 还有 {len(documents) - 10} 个文档")
            
            # 测试相似度搜索
            print(f"\n测试相似度搜索:")
            test_vector = [0.1] * settings.VECTOR_DIMENSION
            results = await vector_service.similarity_search(
                session=session,
                query_vector=test_vector,
                top_k=3
            )
            
            print(f"  - 搜索返回 {len(results)} 个结果")
            for i, result in enumerate(results):
                print(f"    [{i+1}] ID: {result['id'][:8]}..., 相似度: {result['score']:.4f}")
            
            return stats
            
    except Exception as e:
        logger.error(
            "verification_failed",
            error=str(e),
            exc_info=True
        )
        raise


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='文档重新向量化工具')
    parser.add_argument('--batch-size', type=int, default=50, help='批处理大小')
    parser.add_argument('--max-documents', type=int, help='最大处理文档数')
    parser.add_argument('--verify-only', action='store_true', help='仅验证现有向量化')
    
    args = parser.parse_args()
    
    try:
        if args.verify_only:
            await verify_vectorization()
        else:
            await revectorize_documents(
                batch_size=args.batch_size,
                max_documents=args.max_documents
            )
            await verify_vectorization()
            
        return True
        
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)