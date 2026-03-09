"""
直接测试 Pinecone 连接 - 手动加载.env.local
"""
import sys
from pathlib import Path

# 手动加载 .env.local
env_file = Path(__file__).parent / '.env.local'

print("=" * 80)
print("Pinecone 直接连接测试")
print("=" * 80)

if env_file.exists():
    print(f"\n✅ 找到 .env.local: {env_file}")
    
    # 手动解析环境变量
    env_vars = {}
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    api_key = env_vars.get('PINECONE_API_KEY', '')
    index_name = env_vars.get('PINECONE_INDEX_NAME', '')
    
    print(f"\n📋 配置信息:")
    print(f"   API Key: {api_key[:20]}... (长度：{len(api_key)})")
    print(f"   Index Name: {index_name}")
    
    if not api_key or api_key == 'your-pinecone-api-key':
        print(f"\n❌ API Key 无效或未配置")
        print(f"💡 请在 .env.local 中填写真实的 PINECONE_API_KEY")
        sys.exit(1)
    
    # 测试 Pinecone 连接
    print(f"\n🔗 测试 Pinecone 连接...")
    try:
        from pinecone import Pinecone
        
        pc = Pinecone(api_key=api_key)
        print(f"✅ Pinecone 客户端初始化成功")
        
        # 列出所有索引
        print(f"\n📂 查询现有索引...")
        indexes = pc.list_indexes()
        index_names = [idx.name for idx in indexes]
        
        print(f"   找到 {len(index_names)} 个索引:")
        for name in index_names:
            print(f"     - {name}")
        
        # 检查目标索引
        print(f"\n🔍 检查目标索引 '{index_name}'...")
        if index_name in index_names:
            print(f"   ✅ 索引 '{index_name}' 存在")
            
            # 获取索引详情
            print(f"\n📊 获取索引详情...")
            index_info = pc.describe_index(index_name)
            
            print(f"   ✅ 索引信息:")
            print(f"      - Name: {index_info.name}")
            print(f"      - Dimension: {index_info.dimension}")
            print(f"      - Metric: {index_info.metric}")
            print(f"      - Host: {index_info.host}")
            
            # 验证配置
            print(f"\n✓ 验证配置:")
            if index_info.dimension == 1536:
                print(f"   ✅ Dimension: 1536 ✓")
            else:
                print(f"   ⚠️  Dimension: {index_info.dimension} (期望 1536)")
            
            if index_info.metric == 'cosine':
                print(f"   ✅ Metric: cosine ✓")
            else:
                print(f"   ⚠️  Metric: {index_info.metric} (期望 cosine)")
            
            # 测试连接
            print(f"\n🧪 测试索引连接...")
            index = pc.Index(index_name)
            stats = index.describe_index_stats()
            
            print(f"   ✅ 连接成功")
            print(f"      - 总向量数：{stats.get('total_vector_count', 0)}")
            print(f"      - 命名空间数：{len(stats.get('namespaces', {}))}")
            
            if stats.get('total_vector_count', 0) == 0:
                print(f"\n💡 提示：索引为空，这是正常的。上传文档后会自动填充向量。")
            
            # 总结
            print("\n" + "=" * 80)
            print("✅ 验证总结")
            print("=" * 80)
            print("✅ Pinecone Index 配置正确且可连接！")
            print("\n下一步操作:")
            print("  1. 重启后端服务（如果正在运行）")
            print("  2. 运行完整 API测试：python test_api_complete.py")
            print("  3. 上传测试文档并验证问答功能")
            print("=" * 80)
            
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
            print(f"\n⏸️  等待您创建索引后再继续测试...")
            
    except Exception as e:
        print(f"\n❌ Pinecone 连接失败：{e}")
        print(f"💡 请检查:")
        print(f"   1. API Key 是否正确")
        print(f"   2. 网络连接是否正常")
        print(f"   3. Pinecone 账号状态是否正常")
        import traceback
        traceback.print_exc()
else:
    print(f"\n❌ .env.local 文件不存在")
    print(f"💡 请复制 .env.example 并修改")
