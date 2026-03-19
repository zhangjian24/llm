import httpx
import asyncio
import json

async def test_chat():
    async with httpx.AsyncClient() as client:
        # 测试聊天API
        payload = {
            "query": "人工智能的发展历程是什么？",
            "stream": False
        }
        
        try:
            resp = await client.post(
                'http://localhost:8000/api/v1/chat/',
                json=payload,
                timeout=30.0
            )
            print(f"Chat Status: {resp.status_code}")
            print(f"Chat Response: {resp.text}")
            
            if resp.status_code == 200:
                data = resp.json()
                print("\n--- 答案分析 ---")
                if 'data' in data and 'answer' in data['data']:
                    answer = data['data']['answer']
                    print(f"答案长度: {len(answer)} 字符")
                    print(f"答案预览: {answer[:200]}...")
                    
                    # 检查是否包含相关文档内容
                    if 'sources' in data['data'] and data['data']['sources']:
                        print(f"\n引用文档数: {len(data['data']['sources'])}")
                        for i, source in enumerate(data['data']['sources'][:3]):
                            print(f"  来源 {i+1}: {source.get('filename', 'Unknown')} "
                                  f"(相似度: {source.get('similarity', 0):.3f})")
                    else:
                        print("\n未找到相关文档引用")
                else:
                    print("响应格式不符合预期")
                    
        except Exception as e:
            print(f"Chat API Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat())