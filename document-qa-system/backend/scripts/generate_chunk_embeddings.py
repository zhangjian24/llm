"""
为现有 chunks 生成向量嵌入
将文本内容转换为向量存储到 PostgreSQL 中
"""

import asyncio
import sys
from pathlib import Path
from tqdm import tqdm

# 修复导入路径
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(script_dir))

from app.core.database import AsyncSessionLocal
from app.models.chunk import Chunk
from app.services.embedding_service import EmbeddingService
from sqlalchemy import select, update


async def generate_embeddings():
    """为现有 chunks 生成向量嵌入"""
    print("🔄 为现有 chunks 生成向量嵌入")
    print("=" * 50)
    
    try:
        # 初始化嵌入服务
        embedding_svc = EmbeddingService()
        print("✅ 嵌入服务初始化成功")
        
        async with AsyncSessionLocal() as session:
            # 查找所有没有向量的 chunks
            stmt = select(Chunk).where(Chunk.embedding.is_(None))
            result = await session.execute(stmt)
            chunks_without_embedding = result.scalars().all()
            
            total_chunks = len(chunks_without_embedding)
            print(f"📊 发现 {total_chunks} 个需要生成向量的 chunks")
            
            if total_chunks == 0:
                print("✅ 所有 chunks 都已有向量数据")
                return True
            
            # 分批处理，避免内存问题
            batch_size = 10
            processed_count = 0
            
            with tqdm(total=total_chunks, desc="生成向量") as pbar:
                for i in range(0, total_chunks, batch_size):
                    batch = chunks_without_embedding[i:i + batch_size]
                    
                    # 为批次中的每个 chunk 生成向量
                    for chunk in batch:
                        try:
                            # 生成嵌入向量
                            embedding = await embedding_svc.embed_text(chunk.content)
                            
                            # 更新数据库记录
                            stmt = update(Chunk).where(Chunk.id == chunk.id).values(
                                embedding=embedding
                            )
                            await session.execute(stmt)
                            
                            processed_count += 1
                            pbar.update(1)
                            
                        except Exception as e:
                            print(f"\n⚠️  处理 chunk {chunk.id} 时出错: {e}")
                            continue
                    
                    # 提交当前批次的更改
                    await session.commit()
            
            print(f"\n✅ 成功为 {processed_count} 个 chunks 生成向量嵌入")
            
            # 验证结果
            stmt = select(Chunk).where(Chunk.embedding.isnot(None))
            result = await session.execute(stmt)
            chunks_with_embedding = len(result.scalars().all())
            print(f"📊 当前总共有 {chunks_with_embedding} 个 chunks 包含向量数据")
            
            return True
            
    except Exception as e:
        print(f"\n❌ 向量生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    success = await generate_embeddings()
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)