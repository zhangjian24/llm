"""
Pinecone 维度验证测试
检查 Embedding 维度和 Pinecone 索引维度是否匹配
"""
import asyncio
from app.services.pinecone_service import PineconeService
from app.services.embedding_service import EmbeddingService

async def test_dimension_match():
    print("=" * 80)
    print("Pinecone 维度验证测试")
    print("=" * 80)
    
    # 1. 初始化服务
    print("\n[1] 初始化服务...")
    pinecone_svc = PineconeService()
    embedding_svc = EmbeddingService()
    print("  ✓ 服务初始化成功")
    
    # 2. 获取 Embedding 维度
    print("\n[2] 测试 Embedding 维度...")
    test_text = "This is a test sentence for dimension check."
    embedding = await embedding_svc.embed_text(test_text)
    embedding_dim = len(embedding)
    print(f"  ✓ Embedding 维度：{embedding_dim}")
    
    # 3. 获取 Pinecone 索引信息
    print("\n[3] 获取 Pinecone 索引统计...")
    try:
        stats = await pinecone_svc.get_index_stats()
        total_count = stats.get('total_count', 0)
        print(f"  ✓ 索引中向量总数：{total_count}")
        
        # 尝试查询索引元数据
        index_info = pinecone_svc.pc.Index(pinecone_svc.index_name)
        describe_result = index_info.describe_index_stats()
        index_dim = describe_result.get('dimension', 'unknown')
        print(f"  ✓ 索引维度：{index_dim}")
        
        # 4. 维度对比
        print("\n[4] 维度对比...")
        if index_dim == 'unknown':
            print("  ⚠️  无法获取索引维度")
        elif index_dim == embedding_dim:
            print(f"  ✅ 维度匹配！索引维度 ({index_dim}) = Embedding 维度 ({embedding_dim})")
        else:
            print(f"  ❌ 维度不匹配！索引维度 ({index_dim}) ≠ Embedding 维度 ({embedding_dim})")
            print(f"  💡 建议：删除旧索引并重建，或使用正确的维度配置")
        
        # 5. 测试相似度搜索
        print("\n[5] 测试相似度搜索...")
        try:
            results = await pinecone_svc.similarity_search(embedding, top_k=3)
            print(f"  ✅ 搜索成功！找到 {len(results)} 个结果")
            if results:
                for i, result in enumerate(results[:3], 1):
                    score = result.get('score', 'N/A')
                    doc_id = result.get('id', 'N/A')
                    print(f"    [{i}] ID: {doc_id[:20]}..., Score: {score}")
        except Exception as e:
            print(f"  ❌ 搜索失败：{e}")
            if 'dimension' in str(e).lower():
                print(f"  💡 错误原因：维度不匹配")
        
    except Exception as e:
        print(f"  ❌ 获取统计信息失败：{e}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(test_dimension_match())
