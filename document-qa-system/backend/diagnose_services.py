"""
诊断测试 - 检查各个服务的连接性
"""
import asyncio
import httpx
from dotenv import load_dotenv
import os

load_dotenv('.env.local')

async def test_services():
    print("=" * 80)
    print("服务连接性诊断测试")
    print("=" * 80)
    
    # 1. 测试阿里云百炼 Embedding API
    print("\n[1] 测试阿里云百炼 Embedding API...")
    api_key = os.getenv('DASHSCOPE_API_KEY')
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    model = "text-embedding-v4"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "input": "Hello world"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                embedding = data['data'][0]['embedding']
                print(f"  ✅ API 调用成功!")
                print(f"  返回维度：{len(embedding)}")
                print(f"  模型：{model}")
            else:
                print(f"  ❌ API 调用失败：HTTP {response.status_code}")
                print(f"  响应：{response.text[:200]}")
    except Exception as e:
        print(f"  ❌ 异常：{e}")
    
    # 2. 测试 Pinecone 连接
    print("\n[2] 测试 Pinecone 连接...")
    from pinecone import Pinecone, ServerlessSpec
    
    pinecone_api_key = os.getenv('PINECONE_API_KEY')
    pinecone_index_name = os.getenv('PINECONE_INDEX_NAME')
    
    try:
        pc = Pinecone(api_key=pinecone_api_key)
        
        # 列出所有索引
        indexes = pc.list_indexes()
        print(f"  ✅ Pinecone 连接成功")
        print(f"  可用索引：{[idx.name for idx in indexes]}")
        
        # 检查目标索引
        if pinecone_index_name in [idx.name for idx in indexes]:
            print(f"  ✓ 目标索引 '{pinecone_index_name}' 存在")
            
            # 获取索引详情
            index_info = pc.Index(pinecone_index_name)
            stats = index_info.describe_index_stats()
            print(f"  索引维度：{stats.get('dimension', 'unknown')}")
            print(f"  向量总数：{stats.get('total_count', 0)}")
            print(f"  度量方式：{stats.get('metric', 'unknown')}")
        else:
            print(f"  ⚠️  目标索引 '{pinecone_index_name}' 不存在")
            print(f"  💡 建议创建新索引")
            
    except Exception as e:
        print(f"  ❌ Pinecone 连接失败：{e}")
    
    # 3. 总结
    print("\n" + "=" * 80)
    print("诊断结论:")
    print("  - 如果 Embedding API 失败：检查 API Key 和网络连接")
    print("  - 如果 Pinecone 索引维度不匹配：需要重建索引")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_services())
