#!/usr/bin/env python3
"""
测试问答功能
"""

import asyncio
import httpx
import json

async def test_chat_api():
    """测试聊天API"""
    print("💬 测试问答功能...")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # 测试1: 基本问答
            print("\n1. 测试基本问答...")
            payload = {
                "query": "这份Humech白皮书主要讲什么内容？",
                "top_k": 5,
                "stream": False
            }
            
            response = await client.post(
                "http://localhost:8000/api/v1/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 问答成功!")
                print(f"回答: {data.get('data', {}).get('answer', '无回答')}")
                print(f"对话ID: {data.get('data', {}).get('conversation_id', '无ID')}")
            elif response.status_code == 500:
                error_data = response.json()
                print(f"❌ 服务器错误: {error_data.get('detail', '未知错误')}")
            else:
                print(f"❌ 其他错误: {response.text}")
                
            # 测试2: 简单问题
            print("\n2. 测试简单问题...")
            payload2 = {
                "query": "你好",
                "top_k": 3,
                "stream": False
            }
            
            response2 = await client.post(
                "http://localhost:8000/api/v1/chat",
                json=payload2,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"状态码: {response2.status_code}")
            
            if response2.status_code == 200:
                data2 = response2.json()
                print("✅ 简单问答成功!")
                print(f"回答: {data2.get('data', {}).get('answer', '无回答')}")
            elif response2.status_code == 500:
                error_data2 = response2.json()
                print(f"❌ 服务器错误: {error_data2.get('detail', '未知错误')}")
            else:
                print(f"❌ 其他错误: {response2.text}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat_api())