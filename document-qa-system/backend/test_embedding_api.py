#!/usr/bin/env python3
"""
测试Embedding API
"""

import asyncio
import httpx

async def test_embedding_api():
    """测试Embedding API"""
    print("🔍 测试Embedding API...")
    print("=" * 50)
    
    api_key = "sk-f0804f51d9284e41a406e6bceecc00a7"
    base_url = "https://dashscope.aliyuncs.com/api/v1"
    
    async with httpx.AsyncClient() as client:
        try:
            # 测试1: 基本Embedding请求
            print("\n1. 测试基本Embedding请求...")
            payload = {
                "model": "text-embedding-v4",
                "input": "hello world"
            }
            
            response = await client.post(
                f"{base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30.0
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                embedding = data['data'][0]['embedding']
                print(f"✅ Embedding成功!")
                print(f"向量维度: {len(embedding)}")
                print(f"前5个值: {embedding[:5]}")
            else:
                print(f"❌ API错误: {response.status_code}")
                print(f"响应内容: {response.text}")
                
            # 测试2: 错误的API密钥
            print("\n2. 测试错误API密钥...")
            response2 = await client.post(
                f"{base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer invalid_key",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30.0
            )
            
            print(f"状态码: {response2.status_code}")
            if response2.status_code != 200:
                print("✅ 正确识别了无效密钥")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    asyncio.run(test_embedding_api())