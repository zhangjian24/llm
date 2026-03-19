"""
文档状态更新修复验证脚本

测试场景：
1. 上传一个测试文档
2. 等待异步处理完成
3. 检查文档状态是否正确更新为 'ready'
"""
import httpx
import asyncio
from pathlib import Path

BASE_URL = "http://localhost:8000"

async def test_document_status_update():
    """测试文档状态更新是否正常"""
    print("\n" + "="*60)
    print("🧪 文档状态更新修复验证测试")
    print("="*60)
    
    # 1. 创建测试文档内容
    test_content = """# 测试文档
    
这是一个用于测试文档状态更新的简单文档。

## 第一章：简介

本文档用于验证文档处理完成后，状态能否正确从 'processing' 更新为 'ready'。

## 第二章：测试内容

系统应该能够：
1. 解析这个 TXT 文档
2. 对内容进行分块
3. 将分块保存到数据库
4. 更新文档状态为 'ready'
"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 2. 上传文档
            print("\n📤 步骤 1: 上传文档...")
            files = {"file": ("test_status.txt", test_content, "text/plain")}
            params = {
                "mime_type": "text/plain",
                "filename": "test_status.txt"
            }
            
            response = await client.post(
                f"{BASE_URL}/api/v1/documents/upload",
                files=files,
                params=params
            )
            
            if response.status_code != 200:
                print(f"❌ 文档上传失败：{response.status_code} - {response.text}")
                return False
            
            data = response.json()
            doc_id = data["data"]["id"]
            initial_status = data["data"]["status"]
            
            print(f"✅ 文档上传成功")
            print(f"   - 文档 ID: {doc_id}")
            print(f"   - 初始状态：{initial_status}")
            
            # 3. 等待处理完成（轮询检查）
            print("\n⏳ 步骤 2: 等待文档处理完成...")
            max_attempts = 10
            poll_interval = 2.0  # 秒
            
            for attempt in range(max_attempts):
                await asyncio.sleep(poll_interval)
                
                # 查询文档状态
                response = await client.get(
                    f"{BASE_URL}/api/v1/documents/",
                    params={"page": 1, "limit": 1}
                )
                
                if response.status_code == 200:
                    list_data = response.json()
                    docs = list_data["data"]["items"]
                    
                    # 找到我们上传的文档
                    target_doc = None
                    for doc in docs:
                        if doc["id"] == doc_id:
                            target_doc = doc
                            break
                    
                    if target_doc:
                        current_status = target_doc["status"]
                        chunks_count = target_doc.get("chunks_count", 0)
                        
                        print(f"   第 {attempt + 1} 次检查 - 状态：{current_status}, 分块数：{chunks_count}")
                        
                        if current_status == "ready":
                            print("\n✅ 成功！文档状态已正确更新为 'ready'")
                            print(f"   - 最终状态：{current_status}")
                            print(f"   - 分块数量：{chunks_count}")
                            print(f"   - 更新时间：{target_doc.get('updated_at', 'N/A')}")
                            return True
                        elif current_status == "failed":
                            print(f"\n❌ 文档处理失败！状态：{current_status}")
                            return False
            
            print(f"\n⚠️  超时：等待 {max_attempts * poll_interval} 秒后文档仍未处理完成")
            print(f"   最后状态：{current_status if 'current_status' in locals() else 'Unknown'}")
            return False
            
        except httpx.ConnectError as e:
            print(f"\n❌ 无法连接到后端服务：{e}")
            print(f"   请确保后端服务在 {BASE_URL} 运行")
            return False
        except Exception as e:
            print(f"\n❌ 测试异常：{e}")
            import traceback
            traceback.print_exc()
            return False


async def check_all_documents_status():
    """检查所有文档的状态"""
    print("\n" + "="*60)
    print("📋 检查所有文档状态")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/v1/documents/",
                params={"page": 1, "limit": 20}
            )
            
            if response.status_code == 200:
                data = response.json()
                docs = data["data"]["items"]
                total = data["data"]["total"]
                
                print(f"\n总文档数：{total}")
                print("\n文档列表:")
                print("-" * 60)
                
                status_count = {"ready": 0, "processing": 0, "failed": 0}
                
                for doc in docs:
                    status = doc["status"]
                    status_count[status] = status_count.get(status, 0) + 1
                    
                    icon = "✅" if status == "ready" else "⏳" if status == "processing" else "❌"
                    print(f"{icon} {doc['filename']} - {status} (分块：{doc.get('chunks_count', 0)})")
                
                print("\n状态统计:")
                print(f"  ✅ Ready: {status_count.get('ready', 0)}")
                print(f"  ⏳ Processing: {status_count.get('processing', 0)}")
                print(f"  ❌ Failed: {status_count.get('failed', 0)}")
                
                return True
            else:
                print(f"❌ 获取文档列表失败：{response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 异常：{e}")
            return False


async def main():
    """主函数"""
    print("\n" + "="*60)
    print("🔧 文档状态修复验证工具")
    print("="*60)
    
    # 1. 先检查所有文档状态
    await check_all_documents_status()
    
    # 2. 上传新文档测试状态更新
    success = await test_document_status_update()
    
    # 3. 再次检查所有文档状态
    await check_all_documents_status()
    
    print("\n" + "="*60)
    if success:
        print("🎉 测试通过！文档状态更新功能正常")
    else:
        print("⚠️  测试未通过，请检查后端日志")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
