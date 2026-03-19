"""
简化版精度/召回率测试 - 直接测试向量检索功能
"""

import asyncio
import httpx
from pathlib import Path


async def test_vector_search():
    """测试向量搜索功能"""
    print("="*60)
    print("🔍 PostgreSQL 向量检索测试")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        base_url = "http://localhost:8000"
        
        # 1. 检查现有文档
        print("\n1️⃣ 检查现有文档...")
        try:
            response = await client.get(f"{base_url}/api/v1/documents?page=1&limit=10")
            if response.status_code == 200:
                docs_data = response.json()
                documents = docs_data.get('data', {}).get('items', [])
                print(f"   📄 找到 {len(documents)} 个文档")
                
                for doc in documents:
                    status = doc.get('status', 'unknown')
                    filename = doc.get('filename', 'N/A')
                    chunks_count = doc.get('chunks_count', 0)
                    print(f"      - {filename} [{status}] (Chunks: {chunks_count})")
            else:
                print(f"   ❌ 查询失败：{response.status_code}")
        except Exception as e:
            print(f"   ❌ 异常：{e}")
        
        # 2. 测试简单查询
        print("\n2️⃣ 测试问答查询...")
        test_questions = [
            "什么是人工智能？",
            "机器学习有哪些类型？",
            "如何应对气候变化？"
        ]
        
        for question in test_questions:
            print(f"\n   ❓ 问题：{question}")
            
            try:
                response = await client.post(
                    f"{base_url}/api/v1/chat",
                    json={"question": question, "top_k": 3},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # 显示回答
                    answer = result.get('data', {}).get('answer', 'N/A')
                    print(f"      💬 回答：{answer[:100]}...")
                    
                    # 显示检索到的 chunks
                    retrieved_chunks = result.get('data', {}).get('retrieved_chunks', [])
                    print(f"      📚 检索到 {len(retrieved_chunks)} 个文档块")
                    
                    for i, chunk in enumerate(retrieved_chunks[:3], 1):
                        score = chunk.get('score', 0)
                        content = chunk.get('metadata', {}).get('content', '')[:80]
                        doc_id = chunk.get('metadata', {}).get('document_id', 'N/A')
                        print(f"         [{i}] Score: {score:.3f} | Doc: {doc_id[:8]}... | {content}...")
                else:
                    print(f"      ❌ 查询失败：{response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ 异常：{e}")
        
        # 3. 上传新文档测试
        print("\n3️⃣ 上传测试文档...")
        
        # 创建简单的测试文档
        test_content = """# 测试文档：Python 编程基础

## 第一章：Python 简介

Python 是一种高级编程语言，由 Guido van Rossum 于 1989 年发明。Python 的设计哲学强调代码的可读性和简洁性，使用缩进来表示代码块的层次结构。

Python 的主要特点包括：
1. 易于学习：语法简洁清晰
2. 开源：免费使用和有庞大的社区支持
3. 可移植性：跨平台运行
4. 可扩展性：可以调用 C/C++ 库
5. 丰富的库：标准库和第三方库

## 第二章：变量和数据类型

变量是存储数据的容器。Python 中的基本数据类型包括：

### 数字类型
- int（整数）：如 42、-17
- float（浮点数）：如 3.14、-0.001
- complex（复数）：如 3+4j

### 文本类型
- str（字符串）：如 "Hello, World!"

### 布尔类型
- bool（布尔值）：True 或 False

### 序列类型
- list（列表）：有序、可变，如 [1, 2, 3]
- tuple（元组）：有序、不可变，如 (1, 2, 3)
- range（范围）：用于循环

### 映射类型
- dict（字典）：键值对，如 {"name": "Alice", "age": 25}

## 第三章：控制结构

### 条件语句
if condition:
    # 条件为真时执行
elif another_condition:
    # 另一个条件为真时执行
else:
    # 以上条件都不满足时执行

### 循环语句
# for 循环
for i in range(5):
    print(i)

# while 循环
count = 0
while count < 5:
    print(count)
    count += 1

## 第四章：函数定义

函数是一段可重复使用的代码块。定义函数的语法：

def function_name(parameters):
    # 函数文档字符串
    # 函数体
    return result

示例：
def greet(name):
    '''向用户问好'''
    return f"Hello, {name}!"

message = greet("Alice")
print(message)  # 输出：Hello, Alice!
"""
        
        test_file_path = Path("test_docs/python_basic.txt")
        test_file_path.parent.mkdir(exist_ok=True)
        
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print(f"   📝 创建测试文件：{test_file_path}")
        
        # 上传文档
        try:
            with open(test_file_path, 'rb') as f:
                files = {'file': ('python_basic.txt', f, 'text/plain')}
                params = {'mime_type': 'text/plain', 'filename': 'python_basic.txt'}
                
                response = await client.post(
                    f"{base_url}/api/v1/documents/upload",
                    files=files,
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    upload_result = response.json()
                    doc_id = upload_result['data']['id']
                    print(f"   ✅ 文档上传成功，ID: {doc_id}")
                    
                    # 等待处理
                    print(f"   ⏳ 等待文档处理完成...")
                    await asyncio.sleep(15)  # 等待 15 秒
                    
                    # 查询状态
                    for i in range(10):
                        try:
                            status_response = await client.get(
                                f"{base_url}/api/v1/documents/{doc_id}",
                                timeout=10.0
                            )
                            
                            if status_response.status_code == 200:
                                status_data = status_response.json()
                                status = status_data['data']['status']
                                chunks = status_data['data'].get('chunks_count', 0)
                                
                                print(f"      状态：{status}, Chunks: {chunks} ({i*2}s)")
                                
                                if status == 'ready':
                                    print(f"   ✅ 文档处理完成！")
                                    break
                                elif status == 'failed':
                                    print(f"   ❌ 文档处理失败")
                                    break
                            
                            await asyncio.sleep(2)
                        except Exception as e:
                            print(f"      查询失败：{e}")
                            await asyncio.sleep(2)
                    
                    # 测试针对该文档的查询
                    print(f"\n4️⃣ 测试针对新文档的查询...")
                    python_questions = [
                        "Python 是什么？",
                        "Python 有哪些数据类型？",
                        "如何定义函数？",
                        "for 循环怎么写？"
                    ]
                    
                    for q in python_questions:
                        print(f"\n      ❓ 问题：{q}")
                        
                        try:
                            resp = await client.post(
                                f"{base_url}/api/v1/chat",
                                json={"question": q, "top_k": 3},
                                timeout=30.0
                            )
                            
                            if resp.status_code == 200:
                                res = resp.json()
                                ans = res.get('data', {}).get('answer', 'N/A')
                                chunks_count = len(res.get('data', {}).get('retrieved_chunks', []))
                                
                                print(f"         💬 回答：{ans[:80]}...")
                                print(f"         📚 检索到 {chunks_count} 个相关块")
                                
                                # 简单评估：如果检索到结果且回答不为空，算成功
                                if chunks_count > 0 and ans and len(ans) > 10:
                                    print(f"         ✅ 检索成功")
                                else:
                                    print(f"         ⚠️ 检索效果不佳")
                                    
                        except Exception as ex:
                            print(f"         ❌ 查询异常：{ex}")
                    
                else:
                    print(f"   ❌ 上传失败：{response.status_code} - {response.text}")
                    
        except Exception as e:
            print(f"   ❌ 上传异常：{e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*60)
        print("✅ 测试完成")
        print("="*60)


if __name__ == "__main__":
    asyncio.run(test_vector_search())
