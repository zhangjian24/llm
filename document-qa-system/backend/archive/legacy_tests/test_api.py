"""
后端 API 集成测试脚本
测试所有核心 API 端点是否符合 SRS 需求
"""
import httpx
import asyncio
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"


async def test_health_check():
    """测试健康检查接口"""
    print("\n=== 测试 1: 健康检查 ===")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        print(f"✅ 健康检查通过：{data}")
        return True


async def test_root_endpoint():
    """测试根路径"""
    print("\n=== 测试 2: 根路径 ===")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "app" in data
        assert "docs" in data
        print(f"✅ 根路径通过：{data}")
        return True


async def test_get_documents_list():
    """测试获取文档列表（空列表）"""
    print("\n=== 测试 3: 获取文档列表 ===")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/documents/")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "total" in data["data"]
        assert "items" in data["data"]
        print(f"✅ 文档列表获取成功：总计 {data['data']['total']} 个文档")
        return True


async def test_upload_document_txt():
    """测试上传 TXT 文档"""
    print("\n=== 测试 4: 上传 TXT 文档 ===")
    
    # 创建测试文件内容
    test_content = """# 测试文档
    
    这是一个用于测试 RAG 系统的简单文档。
    
    ## 第一章：简介
    
    本文档用于演示文档上传和问答功能。
    
    ## 第二章：测试内容
    
    系统应该能够解析这个文档，并回答相关问题。
    
    ### 关键信息
    
    - 测试项目 1：文档解析
    - 测试项目 2：向量化
    - 测试项目 3：语义检索
    - 测试项目 4：回答生成
    """
    
    async with httpx.AsyncClient() as client:
        files = {"file": ("test_document.txt", test_content, "text/plain")}
        params = {
            "mime_type": "text/plain",
            "filename": "test_document.txt"
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/documents/upload",
                files=files,
                params=params,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 文档上传成功：{data}")
                return data["data"]["id"] if "data" in data else None
            else:
                print(f"⚠️  文档上传失败：{response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 上传异常：{e}")
            return None


async def test_chat_non_stream():
    """测试非流式对话"""
    print("\n=== 测试 5: 非流式对话 ===")
    
    query_data = {
        "query": "你好，请介绍一下这个系统",
        "top_k": 3,
        "stream": False
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/chat/",
                json=query_data,
                timeout=60.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 对话成功：{json.dumps(data, indent=2, ensure_ascii=False)}")
                return True
            else:
                print(f"⚠️  对话失败：{response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 对话异常：{e}")
            return False


async def test_chat_stream():
    """测试流式对话"""
    print("\n=== 测试 6: 流式对话 ===")
    
    query_data = {
        "query": "什么是 RAG 技术？",
        "top_k": 3,
        "stream": True
    }
    
    async with httpx.AsyncClient() as client:
        try:
            async with client.stream(
                "POST",
                f"{BASE_URL}/api/v1/chat/",
                json=query_data,
                timeout=60.0
            ) as response:
                if response.status_code == 200:
                    print("✅ SSE 连接建立成功，接收流式数据...")
                    token_count = 0
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = json.loads(line[6:])
                            if "token" in data:
                                print(data["token"], end="", flush=True)
                                token_count += 1
                            elif "done" in data:
                                print(f"\n✅ 流式传输完成，共接收 {token_count} 个 token")
                                return True
                    return True
                else:
                    print(f"⚠️  流式对话失败：{response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ 流式对话异常：{e}")
            return False


async def test_api_docs():
    """测试 API 文档可访问"""
    print("\n=== 测试 7: API 文档 ===")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/docs")
        assert response.status_code == 200
        print("✅ Swagger 文档可访问")
        return True


async def main():
    """主测试函数"""
    print("=" * 60)
    print("RAG 文档问答系统 - 后端 API 集成测试")
    print("=" * 60)
    
    results = {
        "健康检查": await test_health_check(),
        "根路径": await test_root_endpoint(),
        "文档列表": await test_get_documents_list(),
        "文档上传": await test_upload_document_txt(),
        "非流式对话": await test_chat_non_stream(),
        "流式对话": await test_chat_stream(),
        "API 文档": await test_api_docs()
    }
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计：{passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！后端 API 运行正常，符合 SRS 需求。")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试未通过，请检查相关功能。")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
