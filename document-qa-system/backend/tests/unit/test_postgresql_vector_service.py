"""
PostgreSQL 向量服务测试
验证 PostgreSQLVectorService 的功能实现
"""

import asyncio
import numpy as np
from app.services.postgresql_vector_service import PostgreSQLVectorService
from app.core.database import AsyncSessionLocal
from app.core.config import get_settings

settings = get_settings()


async def test_postgresql_vector_service():
    """测试 PostgreSQL 向量服务功能"""
    print("🧪 PostgreSQL 向量服务测试")
    print("=" * 50)
    
    service = PostgreSQLVectorService()
    print(f"服务配置：维度={service.dimension}, 索引类型={service.index_type}")
    
    try:
        # 1. 测试向量相似度计算
        print("\n1. 测试向量相似度计算...")
        query_vector = [1.0, 2.0, 3.0, 4.0] + [0.0] * (service.dimension - 4)
        candidate_vectors = [
            [1.1, 2.1, 3.1, 4.1] + [0.0] * (service.dimension - 4),  # 相似
            [4.0, 3.0, 2.0, 1.0] + [0.0] * (service.dimension - 4),  # 不相似
            [1.0, 2.0, 3.0, 4.0] + [0.0] * (service.dimension - 4),  # 完全相同
        ]
        
        similarities = service.calculate_similarity(query_vector, candidate_vectors)
        print("   相似度计算结果：")
        for i, (idx, score) in enumerate(similarities):
            print(f"   [{i+1}] 候选{idx+1}: {score:.4f}")
        
        # 2. 测试数据库连接和统计
        print("\n2. 测试数据库连接和统计...")
        async with AsyncSessionLocal() as session:
            stats = await service.get_index_stats(session)
            print(f"   数据库统计：{stats}")
        
        # 3. 测试空向量搜索
        print("\n3. 测试空向量搜索...")
        async with AsyncSessionLocal() as session:
            empty_results = await service.similarity_search(
                session=session,
                query_vector=query_vector,
                top_k=5
            )
            print(f"   空搜索返回结果数：{len(empty_results)}")
        
        print("\n" + "=" * 50)
        print("🎉 PostgreSQL 向量服务测试通过!")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_vector_service_adapter():
    """测试向量服务适配器"""
    print("\n🔌 向量服务适配器测试")
    print("=" * 50)
    
    try:
        from app.services.vector_service_adapter import create_vector_service
        
        # 测试创建 PostgreSQL 服务
        config = {'vector_store_type': 'postgresql'}
        adapter = create_vector_service(config)
        print(f"   ✅ 成功创建 {adapter.service_type}")
        
        # 测试统计功能（通过适配器）
        stats = await adapter.get_index_stats()
        print(f"   统计信息：{stats}")
        
        print("\n" + "=" * 50)
        print("🎉 向量服务适配器测试通过!")
        return True
        
    except Exception as e:
        print(f"\n❌ 适配器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("🚀 开始 PostgreSQL 向量服务测试")
    
    # 测试核心服务
    service_success = await test_postgresql_vector_service()
    
    # 测试适配器
    adapter_success = await test_vector_service_adapter()
    
    if service_success and adapter_success:
        print("\n🎊 所有测试通过! PostgreSQL 向量服务正常工作")
        return True
    else:
        print("\n💥 部分测试失败，请检查错误信息")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)