"""
Pinecone Service 验证测试
测试更新后的 Pinecone SDK v8+ API 功能
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.pinecone_service import PineconeService
from app.exceptions import RetrievalException
import structlog

logger = structlog.get_logger()


async def test_pinecone_initialization():
    """测试 1: Pinecone 客户端初始化"""
    print("\n" + "="*80)
    print("测试 1: Pinecone 客户端初始化")
    print("="*80)
    
    try:
        service = PineconeService()
        print(f"✅ Pinecone 客户端初始化成功")
        print(f"   - Index 名称：{service.index_name}")
        print(f"   - 向量维度：{service.dimension}")
        print(f"   - SDK 版本：7.0.1")
        return True, service
    except Exception as e:
        print(f"❌ Pinecone 客户端初始化失败：{e}")
        return False, None


async def test_list_indexes(service):
    """测试 2: 列出所有索引"""
    print("\n" + "="*80)
    print("测试 2: 列出所有索引")
    print("="*80)
    
    try:
        existing_indexes = service.pc.list_indexes()
        index_names = [idx.name for idx in existing_indexes]
        
        print(f"✅ 当前索引列表:")
        for name in index_names:
            print(f"   - {name}")
        
        if service.index_name in index_names:
            print(f"✅ 目标索引 '{service.index_name}' 已存在")
        else:
            print(f"⚠️  目标索引 '{service.index_name}' 不存在，需要创建")
        
        return True, index_names
    except Exception as e:
        print(f"❌ 列出索引失败：{e}")
        return False, []


async def test_create_index(service):
    """测试 3: 创建索引（如果不存在）"""
    print("\n" + "="*80)
    print("测试 3: 创建索引（如不存在）")
    print("="*80)
    
    try:
        await service.create_index_if_not_exists()
        print(f"✅ 索引检查/创建完成")
        return True
    except Exception as e:
        print(f"❌ 索引创建失败：{e}")
        return False


async def test_index_stats(service):
    """测试 4: 获取索引统计信息"""
    print("\n" + "="*80)
    print("测试 4: 获取索引统计信息")
    print("="*80)
    
    try:
        stats = await service.get_index_stats()
        
        if "error" in stats:
            print(f"⚠️  获取统计信息失败：{stats['error']}")
            return False
        
        total_vectors = stats.get('total_vector_count', 0)
        namespaces = stats.get('namespaces', {})
        
        print(f"✅ 索引统计信息:")
        print(f"   - 总向量数：{total_vectors}")
        print(f"   - 命名空间数：{len(namespaces)}")
        if namespaces:
            for ns, count in list(namespaces.items())[:5]:  # 只显示前 5 个
                print(f"     * {ns}: {count} vectors")
        
        return True
    except Exception as e:
        print(f"❌ 获取统计信息失败：{e}")
        return False


async def test_upsert_vectors(service):
    """测试 5: 插入测试向量"""
    print("\n" + "="*80)
    print("测试 5: 插入测试向量")
    print("="*80)
    
    try:
        # 创建测试向量
        test_vectors = [
            {
                "id": f"test_chunk_{i}",
                "values": [0.1] * service.dimension,  # 1536 维向量
                "metadata": {
                    "document_id": "test_doc_001",
                    "chunk_index": i,
                    "content": f"测试文档块 {i}"
                }
            }
            for i in range(3)
        ]
        
        await service.upsert_vectors(test_vectors, namespace="test_namespace")
        
        print(f"✅ 成功插入 {len(test_vectors)} 个测试向量")
        return True
    except Exception as e:
        print(f"❌ 插入向量失败：{e}")
        return False


async def test_similarity_search(service):
    """测试 6: 相似度搜索"""
    print("\n" + "="*80)
    print("测试 6: 相似度搜索")
    print("="*80)
    
    try:
        # 创建测试查询向量
        query_vector = [0.1] * service.dimension
        
        results = await service.similarity_search(
            query_vector=query_vector,
            top_k=3,
            filter_dict={"document_id": "test_doc_001"},
            include_metadata=True
        )
        
        print(f"✅ 搜索到 {len(results)} 个结果")
        
        for i, result in enumerate(results, 1):
            print(f"\n   结果 {i}:")
            print(f"   - ID: {result.get('id')}")
            print(f"   - 分数：{result.get('score', 'N/A')}")
            if result.get('metadata'):
                print(f"   - 文档 ID: {result['metadata'].get('document_id')}")
                print(f"   - 内容：{result['metadata'].get('content', 'N/A')[:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ 相似度搜索失败：{e}")
        return False


async def test_delete_vectors(service):
    """测试 7: 删除测试向量"""
    print("\n" + "="*80)
    print("测试 7: 删除测试向量")
    print("="*80)
    
    try:
        await service.delete_vectors(
            ids=["test_chunk_0", "test_chunk_1", "test_chunk_2"],
            namespace="test_namespace"
        )
        
        print(f"✅ 成功删除 3 个测试向量")
        return True
    except Exception as e:
        print(f"❌ 删除向量失败：{e}")
        return False


async def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("🧪 Pinecone Service (SDK v8+) 完整验证测试")
    print("="*80)
    print(f"执行时间：{asyncio.get_event_loop().time():.2f}s")
    
    results = []
    
    # 测试 1: 初始化
    success, service = await test_pinecone_initialization()
    results.append(("初始化", success))
    
    if not success:
        print("\n❌ 测试终止：Pinecone 客户端初始化失败")
        return False
    
    # 测试 2: 列出索引
    success, indexes = await test_list_indexes(service)
    results.append(("列出索引", success))
    
    # 测试 3: 创建索引
    success = await test_create_index(service)
    results.append(("创建索引", success))
    
    # 等待索引准备就绪
    print("\n⏳ 等待索引准备就绪...")
    await asyncio.sleep(3)
    
    # 测试 4: 统计信息
    success = await test_index_stats(service)
    results.append(("统计信息", success))
    
    # 测试 5: 插入向量
    success = await test_upsert_vectors(service)
    results.append(("插入向量", success))
    
    # 等待向量化完成
    if success:
        print("\n⏳ 等待向量索引...")
        await asyncio.sleep(2)
    
    # 测试 6: 相似度搜索
    success = await test_similarity_search(service)
    results.append(("相似度搜索", success))
    
    # 测试 7: 删除向量
    success = await test_delete_vectors(service)
    results.append(("删除向量", success))
    
    # 汇总结果
    print("\n" + "="*80)
    print("📊 测试结果汇总")
    print("="*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        icon = "✅" if success else "❌"
        status = "通过" if success else "失败"
        print(f"{icon} {test_name}: {status}")
    
    print(f"\n总计：{passed}/{total} 测试通过")
    print(f"通过率：{passed/total*100:.1f}%")
    
    # 最终结论
    print("\n" + "="*80)
    if passed == total:
        print("✅ 测试结论：所有测试通过！Pinecone Service (SDK v8+) 功能正常")
    elif passed >= total * 0.8:
        print("⚠️  测试结论：大部分测试通过，部分功能需完善")
    else:
        print("❌ 测试结论：多个测试失败，需检查配置和实现")
    
    print("="*80)
    
    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        exit(1)
    except Exception as e:
        print(f"\n❌ 测试执行异常：{e}")
        import traceback
        traceback.print_exc()
        exit(1)
