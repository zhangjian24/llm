"""
Pinecone 到 PostgreSQL 向量数据迁移工具
将现有 Pinecone 向量数据迁移到 PostgreSQL 数据库
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
import json
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
from uuid import UUID
import structlog

# Pinecone 服务（用于导出）
try:
    from app.services.pinecone_service import PineconeService
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

# PostgreSQL 服务（用于导入）
from app.services.postgresql_vector_service import PostgreSQLVectorService
from app.core.database import AsyncSessionLocal
from app.models.chunk import Chunk
from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class VectorDataMigration:
    """向量数据迁移工具"""
    
    def __init__(self, export_file: str = "vector_data_export.json"):
        """
        初始化迁移工具
        
        Args:
            export_file: 导出文件路径
        """
        self.export_file = Path(export_file)
        self.pinecone_service = PineconeService() if PINECONE_AVAILABLE else None
        self.postgresql_service = PostgreSQLVectorService()
        
    async def export_from_pinecone(
        self,
        batch_size: int = 1000,
        max_vectors: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        从 Pinecone 导出向量数据
        
        Args:
            batch_size: 批处理大小
            max_vectors: 最大导出向量数（None 表示全部）
            
        Returns:
            List[Dict[str, Any]]: 导出的向量数据
        """
        if not PINECONE_AVAILABLE:
            raise RuntimeError("Pinecone 服务不可用，无法导出数据")
            
        logger.info(
            "starting_pinecone_export",
            batch_size=batch_size,
            max_vectors=max_vectors
        )
        
        exported_data = []
        offset = 0
        total_exported = 0
        
        try:
            while True:
                # Pinecone 不直接支持分页查询，我们需要使用不同的策略
                # 这里假设我们可以通过某种方式获取所有向量 ID
                # 实际实现可能需要根据具体情况进行调整
                
                # 获取一批向量（这里使用相似度搜索模拟）
                dummy_vector = [0.0] * self.pinecone_service.dimension
                results = await self.pinecone_service.similarity_search(
                    query_vector=dummy_vector,
                    top_k=min(batch_size, max_vectors or batch_size) if max_vectors else batch_size,
                    include_metadata=True
                )
                
                if not results:
                    break
                    
                # 转换为导出格式
                batch_data = []
                for result in results:
                    vector_data = {
                        "id": result["id"],
                        "values": result.get("values", []),
                        "metadata": result.get("metadata", {}),
                        "export_timestamp": asyncio.get_event_loop().time()
                    }
                    batch_data.append(vector_data)
                
                exported_data.extend(batch_data)
                total_exported += len(batch_data)
                
                logger.info(
                    "export_batch_completed",
                    batch_size=len(batch_data),
                    total_exported=total_exported
                )
                
                # 检查是否达到最大导出数量
                if max_vectors and total_exported >= max_vectors:
                    break
                
                # 如果返回结果少于请求的数量，说明已经到达末尾
                if len(results) < batch_size:
                    break
                    
                offset += batch_size
            
            # 保存到文件
            self._save_export_data(exported_data)
            
            logger.info(
                "pinecone_export_completed",
                total_vectors=total_exported,
                export_file=str(self.export_file)
            )
            
            return exported_data
            
        except Exception as e:
            logger.error(
                "pinecone_export_failed",
                error=str(e),
                exc_info=True
            )
            raise
    
    async def import_to_postgresql(
        self,
        data: Optional[List[Dict[str, Any]]] = None,
        batch_size: int = 100
    ):
        """
        将向量数据导入到 PostgreSQL
        
        Args:
            data: 要导入的数据（如果为 None，则从导出文件读取）
            batch_size: 批处理大小
        """
        # 如果没有提供数据，从文件读取
        if data is None:
            data = self._load_export_data()
        
        if not data:
            logger.warning("no_data_to_import")
            return
            
        logger.info(
            "starting_postgresql_import",
            total_vectors=len(data),
            batch_size=batch_size
        )
        
        try:
            imported_count = 0
            failed_count = 0
            
            # 分批处理
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                batch_vectors = []
                
                async with AsyncSessionLocal() as session:
                    for item in batch:
                        try:
                            # 验证数据格式
                            if not all(k in item for k in ['id', 'values']):
                                logger.warning(
                                    "invalid_vector_data_format",
                                    item_id=item.get('id', 'unknown')
                                )
                                failed_count += 1
                                continue
                            
                            # 查找对应的 chunk
                            chunk_id = UUID(item['id'])
                            chunk = await session.get(Chunk, chunk_id)
                            
                            if chunk:
                                # 更新 chunk 的 embedding 字段
                                chunk.embedding = np.array(item['values'], dtype=np.float32)
                                
                                # 更新元数据（如果存在）
                                if 'metadata' in item and item['metadata']:
                                    metadata = item['metadata']
                                    if 'content' in metadata:
                                        chunk.content = metadata['content']
                                    if 'chunk_index' in metadata:
                                        chunk.chunk_index = metadata['chunk_index']
                                
                                batch_vectors.append({
                                    'id': str(chunk_id),
                                    'values': item['values'],
                                    'metadata': {
                                        'document_id': str(chunk.document_id),
                                        'chunk_index': chunk.chunk_index,
                                        'content': chunk.content
                                    }
                                })
                            else:
                                logger.warning(
                                    "chunk_not_found",
                                    chunk_id=item['id']
                                )
                                failed_count += 1
                                
                        except Exception as e:
                            logger.error(
                                "process_vector_item_failed",
                                item_id=item.get('id', 'unknown'),
                                error=str(e)
                            )
                            failed_count += 1
                    
                    # 批量提交
                    try:
                        await session.commit()
                        imported_count += len(batch_vectors)
                        
                        logger.info(
                            "import_batch_completed",
                            batch_number=(i // batch_size) + 1,
                            batch_size=len(batch_vectors),
                            cumulative_imported=imported_count
                        )
                        
                    except Exception as e:
                        await session.rollback()
                        logger.error(
                            "batch_commit_failed",
                            batch_start=i,
                            batch_end=i + len(batch),
                            error=str(e)
                        )
                        failed_count += len(batch)
            
            logger.info(
                "postgresql_import_completed",
                total_processed=len(data),
                successfully_imported=imported_count,
                failed=failed_count
            )
            
        except Exception as e:
            logger.error(
                "postgresql_import_failed",
                error=str(e),
                exc_info=True
            )
            raise
    
    def _save_export_data(self, data: List[Dict[str, Any]]):
        """保存导出数据到文件"""
        export_data = {
            "export_timestamp": asyncio.get_event_loop().time(),
            "total_vectors": len(data),
            "dimension": self.pinecone_service.dimension if self.pinecone_service else settings.VECTOR_DIMENSION,
            "vectors": data
        }
        
        with open(self.export_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        logger.info(
            "export_data_saved",
            file_path=str(self.export_file),
            size_mb=self.export_file.stat().st_size / (1024 * 1024)
        )
    
    def _load_export_data(self) -> List[Dict[str, Any]]:
        """从文件加载导出数据"""
        if not self.export_file.exists():
            raise FileNotFoundError(f"导出文件不存在: {self.export_file}")
        
        with open(self.export_file, 'r', encoding='utf-8') as f:
            export_data = json.load(f)
        
        logger.info(
            "export_data_loaded",
            file_path=str(self.export_file),
            total_vectors=export_data.get('total_vectors', 0)
        )
        
        return export_data.get('vectors', [])
    
    async def verify_migration(self) -> Dict[str, Any]:
        """
        验证迁移结果
        
        Returns:
            Dict[str, Any]: 验证结果统计
        """
        logger.info("starting_migration_verification")
        
        try:
            async with AsyncSessionLocal() as session:
                # 统计信息
                stats = await self.postgresql_service.get_index_stats(session)
                
                # 随机抽样验证
                sample_size = min(10, stats.get('total_vector_count', 0))
                if sample_size > 0:
                    # 获取一些有向量的 chunks 进行验证
                    from sqlalchemy import select
                    from sqlalchemy.orm import joinedload
                    
                    stmt = select(Chunk).where(
                        Chunk.embedding.isnot(None)
                    ).limit(sample_size)
                    
                    result = await session.execute(stmt)
                    sample_chunks = result.scalars().all()
                    
                    validation_results = []
                    for chunk in sample_chunks:
                        validation_results.append({
                            "chunk_id": str(chunk.id),
                            "document_id": str(chunk.document_id),
                            "has_embedding": chunk.embedding is not None,
                            "embedding_dimension": len(chunk.embedding) if chunk.embedding is not None else 0,
                            "content_preview": chunk.content[:50] if chunk.content else ""
                        })
                    
                    stats['validation_sample'] = validation_results
                
                logger.info(
                    "migration_verification_completed",
                    stats=stats
                )
                
                return stats
                
        except Exception as e:
            logger.error(
                "migration_verification_failed",
                error=str(e),
                exc_info=True
            )
            raise


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='向量数据迁移工具')
    parser.add_argument('--export', action='store_true', help='从 Pinecone 导出数据')
    parser.add_argument('--import-data', action='store_true', help='导入数据到 PostgreSQL')
    parser.add_argument('--verify', action='store_true', help='验证迁移结果')
    parser.add_argument('--export-file', default='vector_data_export.json', help='导出文件路径')
    parser.add_argument('--batch-size', type=int, default=100, help='批处理大小')
    parser.add_argument('--max-vectors', type=int, help='最大导出向量数')
    
    args = parser.parse_args()
    
    migration = VectorDataMigration(args.export_file)
    
    try:
        if args.export:
            if not PINECONE_AVAILABLE:
                print("❌ Pinecone 服务不可用，无法执行导出")
                return False
            await migration.export_from_pinecone(
                batch_size=args.batch_size,
                max_vectors=args.max_vectors
            )
        
        if args.import_data:
            await migration.import_to_postgresql(batch_size=args.batch_size)
        
        if args.verify:
            stats = await migration.verify_migration()
            print(f"📊 迁移验证结果：{json.dumps(stats, ensure_ascii=False, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 迁移过程出错: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)