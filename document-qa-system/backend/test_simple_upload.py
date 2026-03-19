"""
简单文档上传测试 - 检查异步处理
"""
import httpx
import asyncio

async def test_simple_upload():
    """简单测试文档上传"""
    print("\n=== 简单文档上传测试 ===\n")
    
    test_content = "这是一个测试文档，用于验证状态更新。\n" * 10
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 上传
            print("1. 上传文档...")
            files = {"file": ("simple_test.txt", test_content, "text/plain")}
            params = {"mime_type": "text/plain", "filename": "simple_test.txt"}
            
            response = await client.post(
                "http://localhost:8000/api/v1/documents/upload",
                files=files,
                params=params
            )
            
            print(f"   响应状态码：{response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 上传成功")
                print(f"   文档 ID: {data['data']['id']}")
                print(f"   初始状态：{data['data']['status']}")
                
                # 立即查询
                print("\n2. 立即查询文档状态...")
                list_response = await client.get(
                    "http://localhost:8000/api/v1/documents/",
                    params={"page": 1, "limit": 5}
                )
                
                if list_response.status_code == 200:
                    list_data = list_response.json()
                    docs = list_data["data"]["items"]
                    
                    target = None
                    for doc in docs:
                        if doc["id"] == data["data"]["id"]:
                            target = doc
                            break
                    
                    if target:
                        print(f"   查询到的状态：{target['status']}")
                        print(f"   分块数：{target.get('chunks_count')}")
                        print(f"   更新时间：{target.get('updated_at')}")
                    else:
                        print("   ❌ 未找到文档")
                else:
                    print(f"   ❌ 查询失败：{list_response.status_code}")
                    
            else:
                print(f"   ❌ 上传失败：{response.status_code}")
                print(f"   响应：{response.text}")
                
        except Exception as e:
            print(f"❌ 异常：{e}")

if __name__ == "__main__":
    asyncio.run(test_simple_upload())
