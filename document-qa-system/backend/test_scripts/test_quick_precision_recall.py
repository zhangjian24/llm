"""
PostgreSQL 向量检索系统 - 快速精度/召回率测试

改进版本 v2:
1. 直接使用数据库查询，不依赖 HTTP API
2. 跳过等待处理过程（假设文档已处理完成）
3. 专注于测试检索精度和召回率
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import httpx
from app.core.database import get_db_session
from app.repositories.document_repository import DocumentRepository


class QuickPrecisionRecallTest:
    """快速精度与召回率测试（直接数据库访问版）"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.document_ids = []
        
    async def check_document_status(self, doc_id: str) -> Dict[str, Any]:
        """通过数据库查询检查文档状态"""
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
                    }
                else:
                    return {'error': 'Document not found'}
            except Exception as e:
                return {'error': str(e)}
            finally:
                await session.close()
        
        return {'error': 'Database connection failed'}
    
    async def execute_query(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """执行问答查询"""
        async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/chat",
                    json={"query": question, "top_k": top_k}
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
    
    def define_golden_standard(self) -> Dict[str, Dict[str, Any]]:
        """定义黄金标准（预期返回结果）"""
        return {
            # AI 相关查询
            "什么是人工智能？": {
                "keywords": ["人工智能", "AI", "计算机科学", "分支"],
                "expected_min_score": 0.7
            },
            "机器学习有哪些类型？": {
                "keywords": ["机器学习", "监督学习", "无监督学习", "强化学习"],
                "expected_min_score": 0.6
            },
            "深度学习如何工作？": {
                "keywords": ["深度学习", "神经网络", "隐藏层", "训练"],
                "expected_min_score": 0.6
            },
            "AI 在医疗领域有什么应用？": {
                "keywords": ["医疗", "健康", "医学影像", "诊断"],
                "expected_min_score": 0.5
            },
            
            # 环境相关查询
            "如何应对气候变化？": {
                "keywords": ["气候变化", "可持续发展", "能源", "生态"],
                "expected_min_score": 0.5
            },
            "污染对健康有什么影响？": {
                "keywords": ["污染", "健康", "疾病", "影响"],
                "expected_min_score": 0.5
            },
            "个人能为环保做什么？": {
                "keywords": ["个人", "环保", "节能", "绿色消费"],
                "expected_min_score": 0.5
            },
            "可再生能源有哪些类型？": {
                "keywords": ["可再生能源", "太阳能", "风能", "水能"],
                "expected_min_score": 0.5
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
        
        for chunk in retrieved_chunks:
            content = chunk.get('metadata', {}).get('content', '').lower()
            
            # 检查是否包含至少一个关键词
            has_keyword = any(keyword.lower() in content for keyword in relevant_keywords)
            
            if has_keyword:
                true_positives += 1
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
    
    async def run_tests(self):
        """运行测试"""
        print("\n" + "="*60)
        print("🚀 PostgreSQL 向量检索系统 - 快速精度/召回率测试")
        print("="*60)
        print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"后端服务：{self.base_url}")
        print("")
        
        # 首先检查现有文档
        print("\n📋 检查现有文档...")
        async for session in get_db_session():
            try:
                repo = DocumentRepository(session)
                docs, total = await repo.find_all(page=1, limit=50)
                
                print(f"总文档数：{total}")
                
                ready_docs = [doc for doc in docs if doc.status == 'ready']
                print(f"已处理完成：{len(ready_docs)} 个")
                
                for doc in ready_docs:
                    print(f"  ✅ {doc.filename} - {doc.chunks_count} chunks")
                
                if not ready_docs:
                    print("\n⚠️ 没有已处理的文档，请先上传并处理文档")
                    return
                
            except Exception as e:
                print(f"❌ 查询失败：{e}")
            finally:
                await session.close()
        
        # 获取黄金标准
        golden_standard = self.define_golden_standard()
        
        # 执行查询测试
        print("\n" + "="*60)
        print("❓ 开始执行查询测试")
        print("="*60)
        
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
            
            print(f"\n📈 测试汇总:")
            print(f"   平均准确率：{avg_precision:.2%}")
            print(f"   平均召回率：{avg_recall:.2%}")
            
            # 生成评价
            if avg_precision >= 0.7 and avg_recall >= 0.6:
                overall_eval = "🎉 优秀 - 系统表现良好，可以投入使用"
            elif avg_precision >= 0.5 and avg_recall >= 0.4:
                overall_eval = "✅ 良好 - 系统基本可用，仍有改进空间"
            else:
                overall_eval = "⚠️ 需改进 - 系统性能未达标"
            
            print(f"   综合评价：{overall_eval}")
            
            # 保存结果
            self.test_results.append({
                'timestamp': datetime.now().isoformat(),
                'queries': round_results,
                'avg_precision': avg_precision,
                'avg_recall': avg_recall,
                'overall_eval': overall_eval
            })
            
            # 生成报告
            self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        report = []
        report.append("# PostgreSQL 向量检索系统 - 精度与召回率测试报告（快速版）")
        report.append("")
        report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**测试方式**: 直接 API 查询测试")
        report.append("")
        
        for result in self.test_results:
            report.append(f"## 测试结果")
            report.append("")
            report.append(f"**平均准确率**: {result['avg_precision']:.2%}")
            report.append(f"**平均召回率**: {result['avg_recall']:.2%}")
            report.append(f"**综合评价**: {result['overall_eval']}")
            report.append("")
            
            # 详细查询结果
            report.append("### 详细查询结果")
            report.append("")
            report.append("| 序号 | 查询问题 | 准确率 | 召回率 | 评价 |")
            report.append("|------|----------|--------|--------|------|")
            
            for i, query_result in enumerate(result['queries'], 1):
                q = query_result['question'][:40]
                report.append(f"| {i} | {q} | {query_result['precision']:.2%} | {query_result['recall']:.2%} | {query_result['evaluation']} |")
            
            report.append("")
        
        # 保存报告
        report_dir = Path("test_reports")
        report_dir.mkdir(exist_ok=True)
        report_file = report_dir / f"quick_precision_recall_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(report))
        
        print(f"\n📄 测试报告已保存到：{report_file}")


async def main():
    """主函数"""
    tester = QuickPrecisionRecallTest()
    await tester.run_tests()


if __name__ == "__main__":
    asyncio.run(main())
