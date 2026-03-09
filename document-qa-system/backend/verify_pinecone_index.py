"""
验证 Pinecone Index 是否已正确创建和配置
"""
import sys
sys.path.insert(0, '.')

print("=" * 80)
print("Pinecone Index 验证工具")
print("=" * 80)

try:
    # 1. 导入 Pinecone SDK
    print("\n1. 加载 Pinecone SDK...")
    from pinecone import Pinecone
    print("   ✅ SDK 加载成功")
    
    # 2. 从配置文件读取 API Key
    print("\n2. 读取配置...")
    from app.core.config import get_settings
    settings = get_settings()
    
    api_key = settings.PINECONE_API_KEY
    index_name = settings.PINECONE_INDEX_NAME
    
    if not api_key:
        print("   ❌ PINECONE_API_KEY 未配置")
        print("   💡 请在 .env.local 中配置 PINECONE_API_KEY")
        sys.exit(1)
    
    if not index_name:
        print("   ❌ PINECONE_INDEX_NAME 未配置")
        print("   💡 请在 .env.local 中配置 PINECONE_INDEX_NAME")
        sys.exit(1)
    
    print(f"   ✅ API Key: {api_key[:20]}... (已脱敏)")
    print(f"   ✅ Index Name: {index_name}")
    
    # 3. 初始化客户端
    print("\n3. 初始化 Pinecone 客户端...")
    pc = Pinecone(api_key=api_key)
    print("   ✅ 客户端初始化成功")
    
    # 4. 列出所有索引
    print("\n4. 查询现有索引...")
    indexes = pc.list_indexes()
    index_names = [idx.name for idx in indexes]
    
    print(f"   找到 {len(index_names)} 个索引:")
    for name in index_names:
        print(f"     - {name}")
    
    # 5. 检查目标索引是否存在
    print(f"\n5. 检查目标索引 '{index_name}'...")
    if index_name in index_names:
        print(f"   ✅ 索引 '{index_name}' 已存在")
        
        # 6. 获取索引详情
        print(f"\n6. 获取索引详细信息...")
        try:
            index_info = pc.describe_index(index_name)
            print(f"   ✅ 索引详情:")
            print(f"      - Name: {index_info.name}")
            print(f"      - Dimension: {index_info.dimension}")
            print(f"      - Metric: {index_info.metric}")
            print(f"      - Host: {index_info.host}")
            
            # 7. 验证配置匹配
            print(f"\n7. 验证配置匹配性...")
            
            dimension_match = index_info.dimension == 1536
            metric_match = index_info.metric == 'cosine'
            
            if dimension_match:
                print(f"   ✅ Dimension 匹配 (1536)")
            else:
                print(f"   ⚠️  Dimension 不匹配 (期望 1536, 实际 {index_info.dimension})")
            
            if metric_match:
                print(f"   ✅ Metric 匹配 (cosine)")
            else:
                print(f"   ⚠️  Metric 不匹配 (期望 cosine, 实际 {index_info.metric})")
            
            # 8. 测试连接
            print(f"\n8. 测试索引连接...")
            index = pc.Index(index_name)
            stats = index.describe_index_stats()
            print(f"   ✅ 连接成功")
            print(f"      - 总向量数：{stats.get('total_vector_count', 0)}")
            print(f"      - 命名空间数：{len(stats.get('namespaces', {}))}")
            
            if stats.get('total_vector_count', 0) == 0:
                print(f"\n💡 提示：索引为空，这是正常的。上传文档后会自动填充向量。")
            
            # 9. 总结
            print("\n" + "=" * 80)
            print("验证总结")
            print("=" * 80)
            
            if dimension_match and metric_match:
                print("✅ 所有检查通过！Pinecone Index 配置正确。")
                print("\n下一步:")
                print("  1. 重启后端服务：uvicorn 会自动重载")
                print("  2. 运行 API测试：python test_api_complete.py")
                print("  3. 上传测试文档并验证问答功能")
            else:
                print("⚠️  部分配置不匹配，建议重新创建索引。")
                print("\n正确的配置:")
                print("  - Dimension: 1536")
                print("  - Metric: cosine")
                print("  - Cloud: AWS")
                print("  - Region: us-east-1 或 ap-southeast-1")
            
            print("=" * 80)
            
        except Exception as e:
            print(f"   ❌ 获取索引详情失败：{e}")
            print(f"   💡 请检查 API Key 是否有效")
            
    else:
        print(f"   ❌ 索引 '{index_name}' 不存在")
        print(f"\n💡 请在 Pinecone 控制台创建该索引:")
        print(f"   1. 访问 https://app.pinecone.io/")
        print(f"   2. 点击 'Create Index'")
        print(f"   3. 填写配置:")
        print(f"      - Name: {index_name}")
        print(f"      - Dimension: 1536")
        print(f"      - Metric: cosine")
        print(f"      - Cloud: AWS")
        print(f"      - Region: us-east-1 或 ap-southeast-1")
        
except ImportError as e:
    print(f"\n❌ Pinecone SDK 导入失败：{e}")
    print(f"💡 请安装依赖：pip install pinecone-client")
    
except Exception as e:
    print(f"\n❌ 验证过程出错：{e}")
    print(f"💡 请检查网络和配置")
    import traceback
    traceback.print_exc()
