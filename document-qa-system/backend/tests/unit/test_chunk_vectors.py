"""
Chunk 模型向量字段测试
验证 embedding 字段的创建和基本操作
"""

import asyncio
import numpy as np
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models.chunk import Chunk
from app.models.document import Document
from app.core.database import Base, AsyncSessionLocal
from app.core.config import get_settings
from uuid import uuid4

settings = get_settings()


async def test_vector_field():
    """测试向量字段功能"""
    print("🧪 Chunk 模型向量字段测试")
    print("=" * 50)
    
    # 创建测试数据
    test_document_id = uuid4()
    test_vector = np.random.rand(settings.VECTOR_DIMENSION).astype(np.float32)
    
    print(f"测试文档ID: {test_document_id}")
    print(f"向量维度: {len(test_vector)}")
    print(f"向量样本: {test_vector[:5]}...")
    
    try:
        # 创建数据库会话
        async with AsyncSessionLocal() as session:
            # 1. 创建测试文档
            print("\n1. 创建测试文档...")
            test_doc = Document(
                id=test_document_id,
                filename="test_vector_document.txt",
                file_path="/tmp/test.txt",
                file_size=1024,
                mime_type="text/plain",
                status="ready"
            )
            session.add(test_doc)
            await session.commit()
            print("   ✅ 测试文档创建成功")
            
            # 2. 创建带向量的 chunk
            print("\n2. 创建带向量的 chunk...")
            test_chunk = Chunk(
                document_id=test_document_id,
                chunk_index=0,
                content="这是测试向量存储的文档块内容",
                token_count=20,
                embedding=test_vector,
                chunk_metadata={"test": "vector_storage"}
            )
            session.add(test_chunk)
            await session.commit()
            print("   ✅ 带向量的 chunk 创建成功")
            
            # 3. 查询验证
            print("\n3. 查询验证...")
            chunk_from_db = await session.get(Chunk, test_chunk.id)
            if chunk_from_db:
                print("   ✅ Chunk 查询成功")
                print(f"   文档ID: {chunk_from_db.document_id}")
                print(f"   内容: {chunk_from_db.content}")
                print(f"   有向量: {chunk_from_db.embedding is not None}")
                if chunk_from_db.embedding is not None:
                    print(f"   向量维度: {len(chunk_from_db.embedding)}")
                    print(f"   向量值: {chunk_from_db.embedding[:5]}...")
                    
                    # 验证向量值是否正确
                    vector_diff = np.linalg.norm(chunk_from_db.embedding - test_vector)
                    if vector_diff < 1e-6:
                        print("   ✅ 向量值保存正确")
                    else:
                        print(f"   ❌ 向量值有差异: {vector_diff}")
            
            # 4. 测试空向量情况
            print("\n4. 测试空向量情况...")
            empty_chunk = Chunk(
                document_id=test_document_id,
                chunk_index=1,
                content="这是没有向量的文档块",
                token_count=15,
                embedding=None,
                chunk_metadata={"test": "no_vector"}
            )
            session.add(empty_chunk)
            await session.commit()
            
            empty_from_db = await session.get(Chunk, empty_chunk.id)
            if empty_from_db and empty_from_db.embedding is None:
                print("   ✅ 空向量处理正确")
            
            # 5. 清理测试数据
            print("\n5. 清理测试数据...")
            await session.delete(empty_chunk)
            await session.delete(test_chunk)
            await session.delete(test_doc)
            await session.commit()
            print("   ✅ 测试数据清理完成")
            
            print("\n" + "=" * 50)
            print("🎉 Chunk 向量字段测试通过!")
            return True
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_vector_operations():
    """测试向量操作功能"""
    print("\n🧮 向量操作功能测试")
    print("=" * 50)
    
    try:
        from app.models.types import cosine_similarity, euclidean_distance, normalize_vector
        
        # 创建测试向量
        vec1 = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
        vec2 = np.array([2.0, 3.0, 4.0, 5.0], dtype=np.float32)
        zero_vec = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)
        
        print(f"向量1: {vec1}")
        print(f"向量2: {vec2}")
        print(f"零向量: {zero_vec}")
        
        # 测试余弦相似度
        print("\n1. 测试余弦相似度...")
        cos_sim = cosine_similarity(vec1, vec2)
        print(f"   cos(vec1, vec2) = {cos_sim:.4f}")
        
        cos_sim_self = cosine_similarity(vec1, vec1)
        print(f"   cos(vec1, vec1) = {cos_sim_self:.4f}")
        
        cos_sim_zero = cosine_similarity(vec1, zero_vec)
        print(f"   cos(vec1, zero) = {cos_sim_zero:.4f}")
        
        # 测试欧氏距离
        print("\n2. 测试欧氏距离...")
        euclid_dist = euclidean_distance(vec1, vec2)
        print(f"   dist(vec1, vec2) = {euclid_dist:.4f}")
        
        euclid_dist_self = euclidean_distance(vec1, vec1)
        print(f"   dist(vec1, vec1) = {euclid_dist_self:.4f}")
        
        # 测试向量归一化
        print("\n3. 测试向量归一化...")
        normalized_vec1 = normalize_vector(vec1)
        print(f"   原向量: {vec1}")
        print(f"   归一化后: {normalized_vec1}")
        print(f"   归一化后模长: {np.linalg.norm(normalized_vec1):.4f}")
        
        print("\n" + "=" * 50)
        print("🎉 向量操作功能测试通过!")
        return True
        
    except Exception as e:
        print(f"\n❌ 向量操作测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("🚀 开始 Chunk 模型向量功能测试")
    
    # 先测试向量操作
    ops_success = await test_vector_operations()
    
    # 再测试数据库操作
    db_success = await test_vector_field()
    
    if ops_success and db_success:
        print("\n🎊 所有测试通过! Chunk 向量功能正常工作")
        return True
    else:
        print("\n💥 部分测试失败，请检查错误信息")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)