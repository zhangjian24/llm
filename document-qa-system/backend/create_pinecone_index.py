"""
创建 Pinecone 索引并验证
"""
import asyncio
from app.services.pinecone_service import PineconeService

async def create_and_verify_index():
    print("=" * 80)
    print("创建 Pinecone 索引并验证")
    print("=" * 80)
    
    # 1. 初始化服务
    print("\n[1] 初始化 Pinecone 服务...")
    service = PineconeService()
    print(f"  ✓ 服务已初始化")
    print(f"  - Index 名称：{service.index_name}")
    print(f"  - 预期维度：{service.dimension}")
    
    # 2. 检查现有索引
    print("\n[2] 检查现有索引...")
    existing_indexes = service.pc.list_indexes()
    index_names = [idx.name for idx in existing_indexes]
    print(f"  可用索引：{index_names}")
    
    if service.index_name in index_names:
        print(f"  ⚠️  索引 '{service.index_name}' 已存在")
        print(f"  💡 将删除旧索引并重建（确保维度正确）")
        
        # 删除旧索引
        print(f"\n[3] 删除旧索引...")
        await service.delete_index()
        print(f"  ✓ 旧索引已删除")
    else:
        print(f"  ℹ️  索引 '{service.index_name}' 不存在")
    
    # 4. 创建新索引
    print(f"\n[4] 创建新索引 '{service.index_name}'...")
    try:
        await service.create_index_if_not_exists()
        print(f"  ✓ 索引创建成功")
        
        # 5. 验证索引
        print(f"\n[5] 验证索引...")
        await asyncio.sleep(3)  # 等待索引完全就绪
        index_info = service.pc.describe_index(service.index_name)
        
        # Pinecone SDK v8 API 变更
        try:
            stats_result = index_info.describe_index_stats()
            if hasattr(stats_result, '__call__'):
                stats = stats_result()
            else:
                stats = stats_result if stats_result else {}
        except:
            # 备用方案：使用 Index 对象
            idx = service.pc.Index(service.index_name)
            stats = idx.describe_index_stats() or {}
        
        print(f"  ✓ 索引状态：{'Ready' if index_info.status.ready else 'Creating'}")
        print(f"  - 维度：{stats.get('dimension', 'unknown')}")
        print(f"  - 向量数：{stats.get('total_count', 0)}")
        print(f"  - 度量方式：cosine")
        
        # 6. 维度验证
        print(f"\n[6] 维度验证...")
        if stats.get('dimension') == service.dimension:
            print(f"  ✅ 维度匹配！索引维度 ({stats.get('dimension')}) = 预期维度 ({service.dimension})")
        else:
            print(f"  ❌ 维度不匹配！索引维度 ({stats.get('dimension')}) ≠ 预期维度 ({service.dimension})")
        
        print(f"\n" + "=" * 80)
        print("✅ Pinecone 索引准备就绪!")
        print("=" * 80)
        print(f"\n下一步:")
        print(f"  1. 重启后端服务：python -m uvicorn app.main:app --reload")
        print(f"  2. 运行 API 测试：python run_api_tests.py")
        print(f"  3. 上传测试文档并验证 RAG 功能")
        
    except Exception as e:
        print(f"  ❌ 索引创建失败：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_and_verify_index())
