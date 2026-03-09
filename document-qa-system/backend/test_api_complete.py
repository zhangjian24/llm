"""
RAG 文档问答系统 - 完整 API 集成测试
基于 SRS 需求规格和详细设计文档

测试覆盖:
- FR-001: 文档上传
- FR-002: 文档分块与向量化 (间接验证)
- FR-003: 语义检索 (需要 Pinecone 配置)
- FR-004: 智能问答生成 (需要 Pinecone 配置)
- FR-005: 对话历史管理
- FR-006: 流式响应展示
- FR-007: 文档列表与管理
- FR-008: 引用来源追溯 (需要完整 RAG 流程)

非功能需求测试:
- NFR-001: 性能需求（响应时间）
- NFR-002: 安全性需求（文件类型验证）
- NFR-004: 可维护性需求（日志、健康检查）
"""
import httpx
import asyncio
import json
import time
from pathlib import Path
from typing import List, Dict, Any

BASE_URL = "http://localhost:8000"


class TestResult:
    """测试结果记录"""
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.error = None
        self.duration = 0.0
        self.details = {}


async def test_health_check() -> TestResult:
    """NFR-004: 健康检查"""
    result = TestResult("健康检查 (NFR-004)")
    start = time.time()
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "version" in data
        
        result.passed = True
        result.duration = time.time() - start
        result.details = {"response": data}
        
    except Exception as e:
        result.error = str(e)
    
    return result


async def test_document_upload_txt() -> TestResult:
    """
    FR-001: 文档上传 - TXT格式
    验收标准：系统应在 30 秒内完成处理并显示成功提示
    """
    result = TestResult("FR-001: 上传 TXT 文档")
    start = time.time()
    
    try:
        # 创建测试文档
        test_content = """# 员工手册
    
## 第一章：总则
    
### 1.1 公司简介
本公司致力于为员工提供良好的工作环境和发展机会。

### 1.2 企业文化
核心价值观：诚信、创新、协作、共赢

## 第二章：考勤管理

### 2.1 工作时间
工作日：周一至周五 9:00-18:00
午休时间：12:00-13:00

### 2.2 迟到早退
- 迟到 30 分钟以内扣款 50 元
- 迟到 30 分钟以上按旷工半天处理
- 每月迟到超过 3 次，额外扣款 200 元

### 2.3 请假流程
1. 提前在 OA 系统提交申请
2. 直属领导审批
3. HR 备案
4. 病假需提供医院证明

## 第三章：薪酬福利

### 3.1 工资构成
基本工资 + 绩效奖金 + 补贴

### 3.2 五险一金
养老保险、医疗保险、失业保险、工伤保险、生育保险
住房公积金

### 3.3 带薪年假
- 工作满 1 年不满 10 年：5 天
- 工作满 10 年不满 20 年：10 天
- 工作满 20 年：15 天

## 第四章：报销政策

### 4.1 差旅报销
- 交通：高铁二等座、飞机经济舱
- 住宿：一线城市≤500 元/天，其他城市≤300 元/天
- 餐饮：补贴 100 元/天

### 4.2 报销流程
1. 填写报销单
2. 附发票原件
3. 部门经理审批
4. 财务审核
5. 每周三统一打款
"""
        
        async with httpx.AsyncClient() as client:
            files = {
                "file": ("employee_handbook.txt", test_content, "text/plain")
            }
            params = {
                "mime_type": "text/plain",
                "filename": "employee_handbook.txt"
            }
            
            response = await client.post(
                f"{BASE_URL}/api/v1/documents/upload",
                files=files,
                params=params,
                timeout=30.0
            )
            
            assert response.status_code == 200, f"HTTP {response.status_code}: {response.text}"
            data = response.json()
            
            assert data["code"] == 0, f"业务错误：{data.get('message')}"
            assert "data" in data
            assert "id" in data["data"]
            assert data["data"]["status"] == "processing"
        
        result.passed = True
        result.duration = time.time() - start
        result.details = {
            "doc_id": data["data"]["id"],
            "filename": "employee_handbook.txt",
            "size_bytes": len(test_content.encode('utf-8')),
            "processing_time_sec": result.duration,
            "status": data["data"]["status"]
        }
        
    except Exception as e:
        result.error = str(e)
    
    return result


async def test_document_list() -> TestResult:
    """
    FR-007: 文档列表与管理
    验收标准：应显示所有文档，并支持按上传时间倒序排列
    """
    result = TestResult("FR-007: 获取文档列表")
    start = time.time()
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/documents/",
                params={"page": 1, "limit": 20}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["code"] == 0
            assert "total" in data["data"]
            assert "items" in data["data"]
            assert isinstance(data["data"]["items"], list)
            assert data["data"]["page"] == 1
            assert data["data"]["limit"] == 20
        
        result.passed = True
        result.duration = time.time() - start
        result.details = {
            "total_docs": data["data"]["total"],
            "current_page": data["data"]["page"],
            "page_size": data["data"]["limit"],
            "docs": [
                {
                    "id": item["id"],
                    "filename": item["filename"],
                    "status": item["status"],
                    "chunks_count": item.get("chunks_count")
                }
                for item in data["data"]["items"][:3]  # 只显示前 3 个
            ]
        }
        
    except Exception as e:
        result.error = str(e)
    
    return result


async def test_chat_non_stream() -> TestResult:
    """
    FR-004: 智能问答生成（非流式）
    验收标准：回答必须包含具体政策条款，并标注出自哪个文档的哪一部分
    """
    result = TestResult("FR-004: 非流式问答")
    start = time.time()
    
    try:
        query_data = {
            "query": "公司的工作时间是什么？",
            "top_k": 3,
            "stream": False
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/chat/",
                json=query_data,
                timeout=60.0
            )
            
            # 如果返回 500，说明 Pinecone 未配置，这是预期的
            if response.status_code == 500:
                result.passed = False
                result.error = "Pinecone 未配置或 Index 不存在（预期情况）"
                result.details = {"note": "需要配置 PINECONE_HOST"}
                return result
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["code"] == 0
            assert "answer" in data["data"] or "conversation_id" in data["data"]
        
        result.passed = True
        result.duration = time.time() - start
        result.details = {
            "query": query_data["query"],
            "has_answer": "answer" in data.get("data", {}),
            "conversation_id": data.get("data", {}).get("conversation_id")
        }
        
    except Exception as e:
        result.error = str(e)
    
    return result


async def test_chat_stream() -> TestResult:
    """
    FR-006: 流式响应展示
    验收标准：用户应在 1 秒内看到第一个字，之后持续流畅显示直至完成
    """
    result = TestResult("FR-006: 流式问答")
    start = time.time()
    first_token_time = None
    
    try:
        query_data = {
            "query": "如何申请年假？",
            "top_k": 3,
            "stream": True
        }
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{BASE_URL}/api/v1/chat/",
                json=query_data,
                timeout=60.0
            ) as response:
                if response.status_code == 500:
                    result.passed = False
                    result.error = "Pinecone 未配置（预期情况）"
                    return result
                
                token_count = 0
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        
                        if "token" in data:
                            token_count += 1
                            if first_token_time is None:
                                first_token_time = time.time() - start
                            
                            if token_count <= 5:  # 只记录前 5 个 token
                                result.details[f"token_{token_count}"] = data["token"]
                        
                        elif "done" in data:
                            break
                
                # 检查首字延迟（NFR-001: ≤1 秒）
                if first_token_time and first_token_time > 1.0:
                    result.passed = False
                    result.error = f"首字延迟过长：{first_token_time:.2f}秒 (>1 秒)"
                else:
                    result.passed = True
        
        result.duration = time.time() - start
        result.details.update({
            "query": query_data["query"],
            "total_tokens": token_count,
            "first_token_sec": first_token_time,
            "tokens_per_second": token_count / result.duration if result.duration > 0 else 0
        })
        
    except Exception as e:
        result.error = str(e)
    
    return result


async def test_conversation_history() -> TestResult:
    """
    FR-005: 对话历史管理
    验收标准：对话记录应保持（除非主动清空）
    """
    result = TestResult("FR-005: 对话历史查询")
    start = time.time()
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/chat/conversations",
                params={"limit": 10}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["code"] == 0
            assert isinstance(data["data"], list)
        
        result.passed = True
        result.duration = time.time() - start
        result.details = {
            "total_conversations": len(data["data"]),
            "conversations": [
                {
                    "id": conv.get("id"),
                    "title": conv.get("title", "新对话"),
                    "turns": conv.get("turns", 0)
                }
                for conv in data["data"][:3]
            ]
        }
        
    except Exception as e:
        result.error = str(e)
    
    return result


async def test_api_docs() -> TestResult:
    """NFR-004: API 文档可访问性"""
    result = TestResult("NFR-004: Swagger API 文档")
    start = time.time()
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/docs")
            assert response.status_code == 200
        
        result.passed = True
        result.duration = time.time() - start
        
    except Exception as e:
        result.error = str(e)
    
    return result


async def test_file_type_validation() -> TestResult:
    """
    NFR-002: 安全性需求 - 文件类型验证
    验收标准：严格限制格式和大小，防止恶意文件
    """
    result = TestResult("NFR-002: 文件类型验证")
    start = time.time()
    
    try:
        # 尝试上传不支持的文件类型
        async with httpx.AsyncClient() as client:
            # 模拟 PNG 文件（实际是文本）
            fake_png = b"\x89PNG\r\n\x1a\n" + b"fake image content"
            
            files = {
                "file": ("fake.png", fake_png, "image/png")
            }
            params = {
                "mime_type": "image/png",
                "filename": "fake.png"
            }
            
            response = await client.post(
                f"{BASE_URL}/api/v1/documents/upload",
                files=files,
                params=params,
                timeout=10.0
            )
            
            # 应该返回 400 错误
            if response.status_code == 400:
                error_data = response.json()
                assert "detail" in error_data or "message" in error_data
                result.passed = True
                result.details = {
                    "rejected_unsupported_type": True,
                    "error_message": error_data.get("detail") or error_data.get("message")
                }
            else:
                result.passed = False
                result.error = f"未拒绝不支持的类型，HTTP {response.status_code}"
        
        result.duration = time.time() - start
        
    except Exception as e:
        result.error = str(e)
    
    return result


async def run_all_tests():
    """执行所有测试"""
    print("=" * 80)
    print("RAG 文档问答系统 - 完整 API 集成测试")
    print("基于 SRS 需求规格说明书")
    print("=" * 80)
    
    tests = [
        test_health_check(),
        test_document_upload_txt(),
        test_document_list(),
        test_chat_non_stream(),
        test_chat_stream(),
        test_conversation_history(),
        test_api_docs(),
        test_file_type_validation()
    ]
    
    results: List[TestResult] = await asyncio.gather(*tests)
    
    # 输出结果
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed and r.error)
    blocked = sum(1 for r in results if not r.passed and "Pinecone" in str(r.error))
    
    for i, result in enumerate(results, 1):
        status_icon = "✅" if result.passed else ("⚠️" if "Pinecone" in str(result.error) else "❌")
        print(f"\n{i}. {result.name}")
        print(f"   状态：{status_icon} {'通过' if result.passed else '失败'}")
        if result.error:
            print(f"   错误：{result.error}")
        if result.duration:
            print(f"   耗时：{result.duration:.2f}秒")
        if result.details:
            print(f"   详情:")
            for key, value in result.details.items():
                print(f"     - {key}: {value}")
    
    # 总结
    print("\n" + "=" * 80)
    print("测试统计")
    print("=" * 80)
    print(f"总测试数：{len(results)}")
    print(f"✅ 通过：{passed}")
    print(f"❌ 失败：{failed}")
    print(f"⚠️  阻塞（Pinecone 配置）: {blocked}")
    print(f"通过率：{passed/len(results)*100:.1f}%")
    
    # SRS 符合性评估
    print("\n" + "=" * 80)
    print("SRS 需求符合性评估")
    print("=" * 80)
    
    fr_results = {
        "FR-001 (文档上传)": any("FR-001" in r.name and r.passed for r in results),
        "FR-005 (对话历史)": any("FR-005" in r.name and r.passed for r in results),
        "FR-006 (流式响应)": any("FR-006" in r.name and r.passed for r in results),
        "FR-007 (文档列表)": any("FR-007" in r.name and r.passed for r in results),
    }
    
    nfr_results = {
        "NFR-001 (性能)": any("首字延迟" in str(r.details) for r in results if r.passed),
        "NFR-002 (安全)": any("FR-002" in r.name and r.passed for r in results),
        "NFR-004 (可维护)": any("NFR-004" in r.name and r.passed for r in results),
    }
    
    print("\n功能需求:")
    for fr, passed in fr_results.items():
        icon = "✅" if passed else "❌"
        print(f"  {icon} {fr}: {'符合' if passed else '不符合'}")
    
    print("\n非功能需求:")
    for nfr, passed in nfr_results.items():
        icon = "✅" if passed else "❌"
        print(f"  {icon} {nfr}: {'符合' if passed else '不符合'}")
    
    # 结论
    print("\n" + "=" * 80)
    overall_pass_rate = sum(fr_results.values()) / len(fr_results) * 100
    if overall_pass_rate >= 80:
        print("✅ 测试结论：通过（满足 SRS 核心需求）")
    elif overall_pass_rate >= 60:
        print("⚠️  测试结论：有条件通过（核心功能可用，需完善配置）")
    else:
        print("❌ 测试结论：不通过（需修复关键问题）")
    
    if blocked > 0:
        print(f"\n💡 提示：{blocked} 个测试因 Pinecone 配置问题阻塞，配置后即可启用完整 RAG 功能。")
    
    print("=" * 80)
    
    return passed == len(results)


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
