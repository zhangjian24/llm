"""
PostgreSQL 向量检索系统 - 快速精度/召回率测试

改进点:
1. 修复 httpx 客户端跟随重定向
2. 增加等待时间到 120 秒
3. 显示更多调试信息（chunks 数量）
4. 增强错误处理
5. 添加手动触发处理的选项
"""

import asyncio
import time
import json
import httpx
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime


class PrecisionRecallTest:
    """精度与召回率测试类（改进版）"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.document_ids = []
        
    async def upload_document(self, file_path: str, filename: str, mime_type: str) -> str:
        """上传测试文档"""
        print(f"\n📤 上传文档：{filename}")
        
        # ✅ 关键修复：使用 follow_redirects=True
        async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
            with open(file_path, 'rb') as f:
                files = {'file': (filename, f, mime_type)}
                params = {'mime_type': mime_type, 'filename': filename}
                
                try:
                    response = await client.post(
                        f"{self.base_url}/api/v1/documents/upload",
                        files=files,
                        params=params
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        doc_id = data['data']['id']
                        print(f"✅ 文档上传成功，ID: {doc_id}")
                        return doc_id
                    else:
                        print(f"❌ 文档上传失败：{response.status_code}")
                        print(f"   响应：{response.text[:200]}")
                        return None
                        
                except Exception as e:
                    print(f"❌ 上传异常：{e}")
                    import traceback
                    traceback.print_exc()
                    return None
    
    async def check_document_status(self, doc_id: str) -> Dict[str, Any]:
        """检查文档状态 - 通过查询数据库"""
        # 直接查询数据库而不是调用 API
        import sys
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        from app.core.database import get_db_session
        from app.repositories.document_repository import DocumentRepository
        
        async for session in get_db_session():
            try:
                repo = DocumentRepository(session)
                doc = await repo.find_by_id(doc_id)
                
                if doc:
                    return {
                        'id': str(doc.id),
                        'filename': doc.filename,
                        'status': doc.status,
                        'chunks_count': doc.chunks_count,
                        'created_at': str(doc.created_at) if doc.created_at else None,
                        'updated_at': str(doc.updated_at) if doc.updated_at else None
                    }
                else:
                    return {'error': 'Document not found'}
            except Exception as e:
                return {'error': str(e)}
            finally:
                await session.close()
        
        return {'error': 'Database connection failed'}
    
    async def wait_for_processing(self, doc_id: str, max_wait: int = 120, auto_trigger: bool = False) -> bool:
        """
        等待文档处理完成
        
        Args:
            doc_id: 文档 ID
            max_wait: 最大等待时间（秒）
            auto_trigger: 是否自动触发处理（如果卡住）
            
        Returns:
            bool: 是否处理完成
        """
        print(f"\n⏳ 等待文档处理完成 (最多 {max_wait} 秒)...")
        
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            for i in range(max_wait // 2):
                try:
                    response = await client.get(
                        f"{self.base_url}/api/v1/documents/{doc_id}"
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        status = data['data']['status']
                        chunks = data['data'].get('chunks_count', 0)
                        
                        if status == 'ready':
                            print(f"✅ 文档处理完成！Chunks: {chunks}")
                            return True
                        elif status == 'failed':
                            print(f"❌ 文档处理失败")
                            return False
                        else:
                            # 显示详细进度
                            if i % 10 == 0:  # 每 20 秒显示一次
                                print(f"   当前状态：{status}, Chunks: {chunks} ({i*2}s)")
                    else:
                        print(f"   查询失败：{response.status_code}")
                    
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    print(f"   查询状态失败：{e}")
                    await asyncio.sleep(2)
        
        print(f"⚠️ 等待超时 ({max_wait}秒)")
        
        # 如果超时且启用了自动触发，尝试手动触发
        if auto_trigger:
            print(f"\n🔧 尝试手动触发处理...")
            return await self.manually_trigger_processing(doc_id)
        
        return False
    
    async def manually_trigger_processing(self, doc_id: str) -> bool:
        """手动触发文档处理"""
        print(f"   🔧 手动触发处理流程...")
        
        # 这里可以调用一个特殊的 API 端点来手动触发
        # 或者运行一个脚本来处理
        print(f"   ⚠️ 需要运行 manual_process_docs.py 脚本")
        return False
    
    async def execute_query(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """执行问答查询"""
        async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/chat",
                    json={"question": question, "top_k": top_k}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # 提取关键信息
                    answer = result.get('data', {}).get('answer', '')
                    retrieved_chunks = result.get('data', {}).get('retrieved_chunks', [])
                    
                    return {
                        'success': True,
                        'answer': answer,
                        'retrieved_chunks': retrieved_chunks,
                        'chunks_count': len(retrieved_chunks)
                    }
                else:
                    return {
                        'success': False,
                        'error': f"Status {response.status_code}: {response.text[:200]}"
                    }
                    
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e)
                }
    
    def create_test_documents(self) -> List[Tuple[str, str, str]]:
        """创建测试文档"""
        print("\n📝 创建测试文档...")
        
        test_docs_dir = Path("test_docs")
        test_docs_dir.mkdir(exist_ok=True)
        
        # 文档 1: 人工智能基础（精简版）
        ai_doc_content = """# 人工智能基础教程

## 第一章：什么是人工智能

人工智能（Artificial Intelligence，简称 AI）是计算机科学的一个重要分支，旨在创造能够执行通常需要人类智能的任务的系统。这些任务包括学习、推理、问题解决、感知和理解语言等。

人工智能的发展经历了几个重要阶段：
1. 符号主义 AI（1950s-1980s）：基于逻辑推理和符号操作
2. 连接主义 AI（1980s-至今）：基于神经网络和深度学习
3. 现代 AI（2010s-至今）：结合深度学习和强化学习

## 第二章：机器学习基础

机器学习是人工智能的一个核心子领域，它使计算机能够在不被明确编程的情况下从数据中学习和改进。机器学习的主要类型包括：

### 监督学习
通过标记好的训练数据来学习输入到输出的映射关系。常见算法有：
- 线性回归：用于预测连续值
- 逻辑回归：用于分类问题
- 决策树和随机森林：用于分类和回归
- 支持向量机：用于分类和回归
- 神经网络：用于复杂的非线性问题

### 无监督学习
从无标记数据中发现隐藏的模式和结构。常见算法有：
- K-means 聚类：将数据分成 K 个簇
- 层次聚类：构建聚类的层次结构
- 主成分分析（PCA）：用于降维和可视化

### 强化学习
通过与环境交互，根据奖励信号学习最优策略。应用包括：
- 游戏 AI（如 AlphaGo）
- 机器人控制
- 自动驾驶

## 第三章：深度学习原理

深度学习是机器学习的一种特殊形式，使用多层神经网络来模拟人脑的学习过程。深度学习的核心概念包括：

### 神经网络结构
1. 输入层：接收原始数据
2. 隐藏层：进行特征提取和转换
3. 输出层：产生最终预测结果

### 常见网络架构
- 卷积神经网络（CNN）：主要用于图像处理
- 循环神经网络（RNN）：适合序列数据处理
- Transformer：在自然语言处理中取得突破性进展

## 第四章：应用场景案例

人工智能技术已广泛应用于各个领域：

### 医疗健康
- 医学影像分析：辅助诊断癌症等疾病
- 药物发现：加速新药研发过程
- 个性化治疗：基于基因组学的精准医疗

### 金融服务
- 欺诈检测：识别异常交易模式
- 风险评估：信用评分和贷款审批
- 量化交易：算法交易和投资组合优化

### 交通运输
- 自动驾驶汽车：感知环境和自主导航
- 交通流量预测：优化城市交通管理
- 物流路径规划：提高配送效率
"""
        
        # 文档 2: 环境保护（精简版）
        env_doc_content = """# 环境保护与可持续发展

## 第一章：气候变化现状

全球气候变化是当今世界面临的最严峻挑战之一。主要表现包括：

### 温度上升
- 过去 100 年全球平均气温上升了约 1.1°C
- 北极地区升温速度是全球平均水平的两倍
- 极端高温事件频率显著增加

### 冰川融化
- 格陵兰冰盖每年损失约 2800 亿吨冰
- 南极冰盖不稳定，可能导致海平面大幅上升
- 山地冰川退缩影响数十亿人的水资源供应

### 海平面上升
- 20 世纪全球海平面上升了约 15-20 厘米
- 威胁沿海城市和岛屿国家
- 盐水入侵影响淡水资源和农业

## 第二章：污染类型与影响

环境污染对人类健康和生态系统造成严重危害：

### 空气污染
主要来源：
- 工业排放：工厂烟囱释放的有害气体
- 交通尾气：汽车、飞机等交通工具排放
- 燃煤发电：二氧化硫、氮氧化物排放

健康影响：
- 呼吸系统疾病：哮喘、支气管炎
- 心血管疾病：心脏病、中风
- 肺癌风险增加

### 水污染
污染源：
- 工业废水：含有重金属和有毒化学物质
- 农业径流：化肥、农药流入水体
- 生活污水：未经处理的生活废水

生态影响：
- 水生生物死亡
- 富营养化导致藻华
- 饮用水源受污染

## 第三章：可持续发展策略

实现可持续发展需要多管齐下：

### 能源转型
可再生能源发展：
- 太阳能：光伏发电成本持续下降
- 风能：陆上和海上风电装机容量增长
- 水能：水力发电技术成熟

节能措施：
- 建筑节能：绿色建筑设计
- 工业节能：提高能源利用效率
- 交通节能：推广电动汽车

### 循环经济
3R 原则：
- 减量化（Reduce）：减少资源消耗
- 再利用（Reuse）：延长产品使用寿命
- 资源化（Recycle）：废弃物回收再利用

实践案例：
- 垃圾分类：提高回收效率
- 共享经济：提高资源利用率
- 产业共生：企业间废物交换利用

## 第四章：个人行动建议

每个人都可以为环保贡献力量：

### 日常生活方式
节能减排：
- 选择公共交通或骑行出行
- 使用节能电器和 LED 灯
- 合理设置空调温度
- 减少一次性用品使用

绿色消费：
- 购买环保认证产品
- 选择本地当季食品
- 减少肉类摄入
- 自带购物袋和水杯

### 社区参与
志愿活动：
- 参加环保组织
- 参与清洁行动
- 植树造林活动
- 环保宣传教育
"""
        
        # 保存文档
        ai_doc_path = test_docs_dir / "ai_basics.txt"
        env_doc_path = test_docs_dir / "environment.txt"
        
        with open(ai_doc_path, 'w', encoding='utf-8') as f:
            f.write(ai_doc_content)
        
        with open(env_doc_path, 'w', encoding='utf-8') as f:
            f.write(env_doc_content)
        
        print(f"✅ 创建 2 个测试文档")
        print(f"   - {ai_doc_path} (~1500 字)")
        print(f"   - {env_doc_path} (~1300 字)")
        
        return [
            (str(ai_doc_path), "ai_basics.txt", "text/plain"),
            (str(env_doc_path), "environment.txt", "text/plain")
        ]
    
    def define_golden_standard(self) -> Dict[str, Dict[str, Any]]:
        """定义黄金标准（预期返回结果）"""
        return {
            # Round 1: 单文档测试（仅 AI 文档）
            "什么是人工智能？": {
                "relevant_topics": ["AI 定义", "人工智能概述"],
                "keywords": ["人工智能", "AI", "计算机科学", "分支"],
                "expected_min_score": 0.7
            },
            "机器学习有哪些类型？": {
                "relevant_topics": ["机器学习类型", "监督学习", "无监督学习"],
                "keywords": ["机器学习", "监督学习", "无监督学习", "强化学习"],
                "expected_min_score": 0.6
            },
            "深度学习如何工作？": {
                "relevant_topics": ["深度学习原理", "神经网络结构"],
                "keywords": ["深度学习", "神经网络", "隐藏层", "训练"],
                "expected_min_score": 0.6
            },
            "AI 在医疗领域有什么应用？": {
                "relevant_topics": ["医疗应用", "健康医疗"],
                "keywords": ["医疗", "健康", "医学影像", "诊断"],
                "expected_min_score": 0.5
            },
            "什么是卷积神经网络？": {
                "relevant_topics": ["网络架构", "CNN"],
                "keywords": ["卷积神经网络", "CNN", "图像处理"],
                "expected_min_score": 0.6
            },
            
            # Round 2: 多文档测试（AI + 环境）
            "如何应对气候变化？": {
                "relevant_topics": ["可持续发展", "能源转型", "生态保护"],
                "keywords": ["气候变化", "可持续发展", "能源", "生态"],
                "expected_min_score": 0.5,
                "should_retrieve_from": "environment.txt"
            },
            "污染对健康有什么影响？": {
                "relevant_topics": ["空气污染", "水污染", "健康影响"],
                "keywords": ["污染", "健康", "疾病", "影响"],
                "expected_min_score": 0.5,
                "should_retrieve_from": "environment.txt"
            },
            "个人能为环保做什么？": {
                "relevant_topics": ["个人行动", "日常生活", "绿色消费"],
                "keywords": ["个人", "环保", "节能", "绿色消费"],
                "expected_min_score": 0.5,
                "should_retrieve_from": "environment.txt"
            },
            "机器学习和深度学习有什么区别？": {
                "relevant_topics": ["机器学习基础", "深度学习原理"],
                "keywords": ["机器学习", "深度学习", "区别", "神经网络"],
                "expected_min_score": 0.5,
                "should_retrieve_from": "ai_basics.txt"
            },
            "可再生能源有哪些类型？": {
                "relevant_topics": ["能源转型", "可再生能源"],
                "keywords": ["可再生能源", "太阳能", "风能", "水能"],
                "expected_min_score": 0.5,
                "should_retrieve_from": "environment.txt"
            }
        }
    
    def calculate_metrics(self, retrieved_chunks: List[Dict], ground_truth: Dict) -> Tuple[float, float, str]:
        """
        计算准确率和召回率
        
        Returns:
            Tuple[float, float, str]: (准确率，召回率，评价)
        """
        if not retrieved_chunks:
            return 0.0, 0.0, "无结果"
        
        # 基于关键词匹配判断相关性
        relevant_keywords = set(ground_truth.get('keywords', []))
        
        if not relevant_keywords:
            return 0.0, 0.0, "无关键词"
        
        true_positives = 0
        false_positives = 0
        relevant_contents = []
        
        for chunk in retrieved_chunks:
            content = chunk.get('metadata', {}).get('content', '').lower()
            
            # 检查是否包含至少一个关键词
            has_keyword = any(keyword.lower() in content for keyword in relevant_keywords)
            
            if has_keyword:
                true_positives += 1
                relevant_contents.append(content[:50])
            else:
                false_positives += 1
        
        # 召回率计算（假设应该有 3 个相关结果）
        expected_relevant = 3
        actual_relevant = true_positives
        
        precision = true_positives / len(retrieved_chunks) if retrieved_chunks else 0.0
        recall = actual_relevant / expected_relevant if expected_relevant > 0 else 0.0
        
        # 生成评价
        if precision >= 0.8 and recall >= 0.7:
            evaluation = "优秀"
        elif precision >= 0.6 and recall >= 0.5:
            evaluation = "良好"
        elif precision >= 0.4:
            evaluation = "及格"
        else:
            evaluation = "需改进"
        
        return precision, recall, evaluation
    
    async def run_round_1_single_document(self):
        """Round 1: 单文档测试"""
        print("\n" + "="*60)
        print("🔵 Round 1: 单文档基础测试")
        print("="*60)
        
        # 仅上传 AI 文档
        test_docs = self.create_test_documents()
        doc_path, doc_name, mime_type = test_docs[0]
        
        doc_id = await self.upload_document(doc_path, doc_name, mime_type)
        if not doc_id:
            print("❌ 文档上传失败，跳过此轮测试")
            return
        
        self.document_ids.append(doc_id)
        
        # 等待处理完成（启用自动触发）
        if not await self.wait_for_processing(doc_id, auto_trigger=True):
            print("⚠️ 文档处理未完成，跳过此轮测试")
            print("💡 提示：检查 Embedding API 配置是否正确")
            return
        
        # 获取黄金标准（仅 AI 相关查询）
        golden_standard = {
            k: v for k, v in self.define_golden_standard().items()
            if 'environment' not in str(v.get('should_retrieve_from', ''))
        }
        
        # 执行查询
        round_results = []
        for question, gt in golden_standard.items():
            print(f"\n❓ 查询：{question}")
            
            result = await self.execute_query(question, top_k=5)
            
            if not result.get('success'):
                print(f"   ❌ 查询失败：{result.get('error', 'Unknown')}")
                continue
            
            retrieved_chunks = result.get('retrieved_chunks', [])
            answer = result.get('answer', '')
            
            # 计算指标
            precision, recall, evaluation = self.calculate_metrics(retrieved_chunks, gt)
            
            print(f"   📊 准确率：{precision:.2%}, 召回率：{recall:.2%} - {evaluation}")
            print(f"   📄 返回 {len(retrieved_chunks)} 个结果")
            print(f"   💬 回答预览：{answer[:80]}...")
            
            # 显示前 3 个结果
            for i, chunk in enumerate(retrieved_chunks[:3]):
                score = chunk.get('score', 0)
                content = chunk.get('metadata', {}).get('content', '')[:80]
                print(f"   [{i+1}] Score: {score:.3f} - {content}...")
            
            round_results.append({
                'question': question,
                'precision': precision,
                'recall': recall,
                'evaluation': evaluation,
                'results_count': len(retrieved_chunks),
                'retrieved_chunks': retrieved_chunks,
                'ground_truth': gt
            })
        
        # 计算平均指标
        if round_results:
            avg_precision = sum(r['precision'] for r in round_results) / len(round_results)
            avg_recall = sum(r['recall'] for r in round_results) / len(round_results)
            
            print(f"\n📈 Round 1 汇总:")
            print(f"   平均准确率：{avg_precision:.2%}")
            print(f"   平均召回率：{avg_recall:.2%}")
            
            self.test_results.append({
                'round': 1,
                'type': 'single_document',
                'document': doc_name,
                'queries': round_results,
                'avg_precision': avg_precision,
                'avg_recall': avg_recall,
                'timestamp': datetime.now().isoformat()
            })
    
    async def run_round_2_multi_documents(self):
        """Round 2: 多文档干扰测试"""
        print("\n" + "="*60)
        print("🟢 Round 2: 多文档干扰测试")
        print("="*60)
        
        # 上传环境文档
        test_docs = self.create_test_documents()
        doc_path, doc_name, mime_type = test_docs[1]
        
        doc_id = await self.upload_document(doc_path, doc_name, mime_type)
        if not doc_id:
            print("❌ 文档上传失败，跳过此轮测试")
            return
        
        self.document_ids.append(doc_id)
        
        # 等待处理完成
        if not await self.wait_for_processing(doc_id, auto_trigger=True):
            print("⚠️ 文档处理未完成，跳过此轮测试")
            return
        
        # 获取完整的黄金标准
        golden_standard = self.define_golden_standard()
        
        # 执行查询
        round_results = []
        for question, gt in golden_standard.items():
            print(f"\n❓ 查询：{question}")
            
            result = await self.execute_query(question, top_k=5)
            
            if not result.get('success'):
                print(f"   ❌ 查询失败：{result.get('error', 'Unknown')}")
                continue
            
            retrieved_chunks = result.get('retrieved_chunks', [])
            answer = result.get('answer', '')
            
            # 计算指标
            precision, recall, evaluation = self.calculate_metrics(retrieved_chunks, gt)
            
            print(f"   📊 准确率：{precision:.2%}, 召回率：{recall:.2%} - {evaluation}")
            print(f"   📄 返回 {len(retrieved_chunks)} 个结果")
            print(f"   💬 回答预览：{answer[:80]}...")
            
            # 显示前 3 个结果
            for i, chunk in enumerate(retrieved_chunks[:3]):
                score = chunk.get('score', 0)
                content = chunk.get('metadata', {}).get('content', '')[:80]
                print(f"   [{i+1}] Score: {score:.3f} - {content}...")
            
            round_results.append({
                'question': question,
                'precision': precision,
                'recall': recall,
                'evaluation': evaluation,
                'results_count': len(retrieved_chunks),
                'retrieved_chunks': retrieved_chunks,
                'ground_truth': gt
            })
        
        # 计算平均指标
        if round_results:
            avg_precision = sum(r['precision'] for r in round_results) / len(round_results)
            avg_recall = sum(r['recall'] for r in round_results) / len(round_results)
            
            print(f"\n📈 Round 2 汇总:")
            print(f"   平均准确率：{avg_precision:.2%}")
            print(f"   平均召回率：{avg_recall:.2%}")
            
            self.test_results.append({
                'round': 2,
                'type': 'multi_documents',
                'documents': ['ai_basics.txt', 'environment.txt'],
                'queries': round_results,
                'avg_precision': avg_precision,
                'avg_recall': avg_recall,
                'timestamp': datetime.now().isoformat()
            })
    
    def generate_report(self) -> str:
        """生成测试报告"""
        report = []
        report.append("# PostgreSQL 向量检索系统 - 精度与召回率测试报告（改进版）")
        report.append("")
        report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**测试 API**: {self.base_url}")
        report.append("")
        
        for round_result in self.test_results:
            report.append(f"## Round {round_result['round']}: {round_result['type']}")
            report.append("")
            
            if 'document' in round_result:
                report.append(f"**测试文档**: {round_result['document']}")
            elif 'documents' in round_result:
                report.append(f"**测试文档**: {', '.join(round_result['documents'])}")
            
            report.append("")
            report.append(f"**平均准确率**: {round_result['avg_precision']:.2%}")
            report.append(f"**平均召回率**: {round_result['avg_recall']:.2%}")
            report.append("")
            
            # 详细查询结果
            report.append("### 详细查询结果")
            report.append("")
            report.append("| 序号 | 查询问题 | 准确率 | 召回率 | 评价 |")
            report.append("|------|----------|--------|--------|------|")
            
            for i, query_result in enumerate(round_result['queries'], 1):
                q = query_result['question'][:30] + "..." if len(query_result['question']) > 30 else query_result['question']
                report.append(f"| {i} | {q} | {query_result['precision']:.2%} | {query_result['recall']:.2%} | {query_result['evaluation']} |")
            
            report.append("")
        
        # 总体结论
        report.append("## 总体结论")
        report.append("")
        
        if self.test_results:
            overall_precision = sum(r['avg_precision'] for r in self.test_results) / len(self.test_results)
            overall_recall = sum(r['avg_recall'] for r in self.test_results) / len(self.test_results)
            
            report.append(f"- **总体平均准确率**: {overall_precision:.2%}")
            report.append(f"- **总体平均召回率**: {overall_recall:.2%}")
            report.append("")
            
            if overall_precision >= 0.7 and overall_recall >= 0.6:
                report.append("🎉 **系统整体表现优秀，可以投入使用！**")
            elif overall_precision >= 0.5 and overall_recall >= 0.4:
                report.append("✅ **系统基本满足要求，建议优化后使用。**")
            else:
                report.append("⚠️ **系统需要进一步优化才能达到实用标准。**")
        
        return "\n".join(report)
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*60)
        print("🚀 PostgreSQL 向量检索系统 - 精度/召回率全面测试（改进版）")
        print("="*60)
        print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"后端服务：{self.base_url}")
        print("")
        
        try:
            # Round 1: 单文档测试
            await self.run_round_1_single_document()
            
            # Round 2: 多文档测试
            await self.run_round_2_multi_documents()
            
            # 生成报告
            report = self.generate_report()
            
            # 保存报告
            report_dir = Path("test_reports")
            report_dir.mkdir(exist_ok=True)
            report_file = report_dir / f"precision_recall_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"\n📄 测试报告已保存到：{report_file}")
            
            # 打印摘要
            print("\n" + "="*60)
            print("📊 测试摘要")
            print("="*60)
            
            for round_result in self.test_results:
                print(f"\nRound {round_result['round']}:")
                print(f"  平均准确率：{round_result['avg_precision']:.2%}")
                print(f"  平均召回率：{round_result['avg_recall']:.2%}")
            
            print("\n" + "="*60)
            print("✅ 测试完成！")
            print("="*60)
            
        except Exception as e:
            print(f"\n❌ 测试过程中发生错误：{e}")
            import traceback
            traceback.print_exc()


async def main():
    """主函数"""
    tester = PrecisionRecallTest()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
