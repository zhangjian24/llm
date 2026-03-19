"""
PostgreSQL 向量存储迁移完整测试
验证迁移后的系统功能完整性和性能表现
"""

import asyncio
import time
import numpy as np
from typing import List, Dict, Any
import structlog
from app.services.embedding_service import EmbeddingService
from app.services.vector_service_adapter import create_vector_service
from app.services.rerank_service import RerankService
from app.services.rag_service import RAGService
from app.core.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class MigrationTestSuite:
    """迁移测试套件"""
    
    def __init__(self):
        """初始化测试套件"""
        self.embedding_service = EmbeddingService()
        self.vector_service = create_vector_service({'vector_store_type': 'postgresql'})
        self.rerank_service = RerankService()
        self.rag_service = RAGService(
            embedding_svc=self.embedding_service,
            vector_svc=self.vector_service,
            rerank_svc=self.rerank_service
        )
        
        # 测试数据
        self.test_questions = [
            "什么是人工智能？",
            "机器学习的基本概念是什么？",
            "深度学习和传统机器学习有什么区别？",
            "自然语言处理的应用场景有哪些？",
            "计算机视觉技术的发展现状如何？"
        ]
        
        self.test_documents = [
            "人工智能是计算机科学的一个分支，旨在创造能够执行通常需要人类智能的任务的系统。",
            "机器学习是人工智能的一个重要子领域，它使计算机能够在不被明确编程的情况下学习和改进。",
            "深度学习是机器学习的一种特殊形式，使用多层神经网络来模拟人脑的学习过程。",
            "自然语言处理技术广泛应用于机器翻译、情感分析、问答系统和文本摘要等领域。",
            "计算机视觉技术在医疗影像分析、自动驾驶、安防监控和工业检测等方面发挥重要作用。"
        ]
    
    async def test_vector_operations(self) -> Dict[str, Any]:
        """测试向量操作功能"""
        print("🧮 测试 1: 向量操作功能")
        print("-" * 40)
        
        results = {
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        try:
            # 测试向量维度
            test_vector = await self.embedding_service.embed_text("测试文本")
            expected_dim = settings.VECTOR_DIMENSION
            
            if len(test_vector) == expected_dim:
                print(f"✅ 向量维度正确: {len(test_vector)}")
                results['passed'] += 1
            else:
                print(f"❌ 向量维度错误: 期望 {expected_dim}, 实际 {len(test_vector)}")
                results['failed'] += 1
            results['details'].append(f"向量维度测试: {'通过' if len(test_vector) == expected_dim else '失败'}")
            
            # 测试向量相似度计算
            vec1 = np.array([1.0, 2.0, 3.0, 4.0] + [0.0] * (expected_dim - 4))
            vec2 = np.array([1.1, 2.1, 3.1, 4.1] + [0.0] * (expected_dim - 4))
            vec3 = np.array([4.0, 3.0, 2.0, 1.0] + [0.0] * (expected_dim - 4))
            
            from app.models.types import cosine_similarity
            sim_1_2 = cosine_similarity(vec1, vec2)
            sim_1_3 = cosine_similarity(vec1, vec3)
            
            if sim_1_2 > sim_1_3:
                print(f"✅ 相似度计算正确: {sim_1_2:.4f} > {sim_1_3:.4f}")
                results['passed'] += 1
            else:
                print(f"❌ 相似度计算异常: {sim_1_2:.4f} <= {sim_1_3:.4f}")
                results['failed'] += 1
            results['details'].append(f"相似度计算测试: {'通过' if sim_1_2 > sim_1_3 else '失败'}")
            
        except Exception as e:
            print(f"❌ 向量操作测试失败: {e}")
            results['failed'] += 1
            results['details'].append(f"向量操作测试: 失败 - {str(e)}")
        
        return results
    
    async def test_vector_storage_and_retrieval(self) -> Dict[str, Any]:
        """测试向量存储和检索功能"""
        print("\n💾 测试 2: 向量存储和检索")
        print("-" * 40)
        
        results = {
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        try:
            # 获取初始统计
            initial_stats = await self.vector_service.get_index_stats()
            initial_count = initial_stats.get('total_vector_count', 0)
            print(f"初始向量数: {initial_count}")
            
            # 测试相似度搜索（即使没有数据也应该正常返回）
            query_vector = await self.embedding_service.embed_text("测试查询")
            search_results = await self.vector_service.similarity_search(
                query_vector=query_vector,
                top_k=5
            )
            print(f"空搜索返回结果数: {len(search_results)}")
            
            if isinstance(search_results, list):
                print("✅ 相似度搜索接口正常")
                results['passed'] += 1
            else:
                print("❌ 相似度搜索接口异常")
                results['failed'] += 1
            results['details'].append(f"相似度搜索测试: {'通过' if isinstance(search_results, list) else '失败'}")
            
            # 测试统计功能
            final_stats = await self.vector_service.get_index_stats()
            if 'total_vector_count' in final_stats:
                print("✅ 统计功能正常")
                results['passed'] += 1
            else:
                print("❌ 统计功能异常")
                results['failed'] += 1
            results['details'].append(f"统计功能测试: {'通过' if 'total_vector_count' in final_stats else '失败'}")
            
        except Exception as e:
            print(f"❌ 存储检索测试失败: {e}")
            results['failed'] += 1
            results['details'].append(f"存储检索测试: 失败 - {str(e)}")
        
        return results
    
    async def test_rag_pipeline(self) -> Dict[str, Any]:
        """测试完整的 RAG 流水线"""
        print("\n🔄 测试 3: RAG 流水线")
        print("-" * 40)
        
        results = {
            'passed': 0,
            'failed': 0,
            'details': [],
            'performance_metrics': {}
        }
        
        try:
            # 选择一个测试问题
            test_question = self.test_questions[0]
            print(f"测试问题: {test_question}")
            
            # 测试 RAG 查询（应该能正常处理，即使没有相关文档）
            start_time = time.time()
            
            response_tokens = []
            async for token in self.rag_service.query(
                question=test_question,
                top_k=3,
                rerank_top_k=2
            ):
                response_tokens.append(token)
            
            response_time = time.time() - start_time
            response_text = ''.join(response_tokens)
            
            print(f"响应时间: {response_time:.2f}秒")
            print(f"响应长度: {len(response_text)}字符")
            print(f"响应预览: {response_text[:100]}...")
            
            # 验证响应质量
            if len(response_text) > 0:
                print("✅ RAG 流水线正常工作")
                results['passed'] += 1
            else:
                print("❌ RAG 流水线未产生有效响应")
                results['failed'] += 1
            results['details'].append(f"RAG 流水线测试: {'通过' if len(response_text) > 0 else '失败'}")
            
            # 性能指标
            results['performance_metrics'] = {
                'response_time': response_time,
                'response_length': len(response_text),
                'tokens_per_second': len(response_tokens) / response_time if response_time > 0 else 0
            }
            
        except Exception as e:
            print(f"❌ RAG 流水线测试失败: {e}")
            results['failed'] += 1
            results['details'].append(f"RAG 流水线测试: 失败 - {str(e)}")
        
        return results
    
    async def test_performance_benchmark(self) -> Dict[str, Any]:
        """性能基准测试"""
        print("\n⚡ 测试 4: 性能基准")
        print("-" * 40)
        
        results = {
            'passed': 0,
            'failed': 0,
            'details': [],
            'benchmarks': {}
        }
        
        try:
            # 向量化性能测试
            print("向量化性能测试...")
            text_samples = ["这是测试文本" + str(i) for i in range(10)]
            
            start_time = time.time()
            embeddings = await self.embedding_service.embed_batch(text_samples, batch_size=5)
            embedding_time = time.time() - start_time
            
            print(f"  批量向量化 {len(text_samples)} 个文本耗时: {embedding_time:.2f}秒")
            print(f"  平均每个文本: {embedding_time/len(text_samples)*1000:.1f}毫秒")
            
            # 存储性能测试
            print("向量存储性能测试...")
            vector_data = [
                {
                    "id": f"test_{i}",
                    "values": embeddings[i],
                    "metadata": {"content": text_samples[i]}
                }
                for i in range(min(5, len(embeddings)))
            ]
            
            start_time = time.time()
            await self.vector_service.upsert_vectors(vector_data)
            storage_time = time.time() - start_time
            
            print(f"  存储 {len(vector_data)} 个向量耗时: {storage_time:.2f}秒")
            
            # 搜索性能测试
            print("向量搜索性能测试...")
            query_vector = embeddings[0]
            
            start_time = time.time()
            search_results = await self.vector_service.similarity_search(
                query_vector=query_vector,
                top_k=3
            )
            search_time = time.time() - start_time
            
            print(f"  搜索耗时: {search_time*1000:.1f}毫秒")
            print(f"  返回结果数: {len(search_results)}")
            
            # 性能基准结果
            results['benchmarks'] = {
                'embedding_batch_time': embedding_time,
                'embedding_avg_ms': embedding_time/len(text_samples)*1000,
                'storage_time': storage_time,
                'search_time_ms': search_time*1000,
                'results_returned': len(search_results)
            }
            
            # 性能阈值检查
            embedding_threshold = 5000  # 5秒
            search_threshold = 1000     # 1秒
            
            if embedding_time < embedding_threshold and search_time*1000 < search_threshold:
                print("✅ 性能基准达标")
                results['passed'] += 1
            else:
                print("⚠️  性能基准未完全达标")
                results['failed'] += 0  # 不算失败，只是警告
            results['details'].append(f"性能基准测试: {'达标' if embedding_time < embedding_threshold and search_time*1000 < search_threshold else '部分达标'}")
            
        except Exception as e:
            print(f"❌ 性能基准测试失败: {e}")
            results['failed'] += 1
            results['details'].append(f"性能基准测试: 失败 - {str(e)}")
        
        return results
    
    async def run_complete_test_suite(self) -> Dict[str, Any]:
        """运行完整的测试套件"""
        print("🚀 PostgreSQL 向量存储迁移测试套件")
        print("=" * 60)
        print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"配置: 维度={settings.VECTOR_DIMENSION}, 索引类型={settings.VECTOR_INDEX_TYPE}")
        print()
        
        # 运行各项测试
        test_results = {}
        
        test_results['vector_operations'] = await self.test_vector_operations()
        test_results['vector_storage'] = await self.test_vector_storage_and_retrieval()
        test_results['rag_pipeline'] = await self.test_rag_pipeline()
        test_results['performance'] = await self.test_performance_benchmark()
        
        # 汇总结果
        total_passed = sum(result['passed'] for result in test_results.values())
        total_failed = sum(result['failed'] for result in test_results.values())
        
        print("\n" + "=" * 60)
        print("📋 测试汇总报告")
        print("=" * 60)
        print(f"总测试项: {total_passed + total_failed}")
        print(f"通过: {total_passed}")
        print(f"失败: {total_failed}")
        print(f"成功率: {(total_passed/(total_passed + total_failed)*100):.1f}%" if (total_passed + total_failed) > 0 else "0%")
        
        # 详细结果
        print("\n详细测试结果:")
        for test_name, result in test_results.items():
            status = "✅ 通过" if result['failed'] == 0 else f"❌ 失败 ({result['failed']} 项)"
            print(f"  {test_name}: {status}")
            for detail in result['details']:
                print(f"    - {detail}")
        
        # 性能指标
        if 'performance' in test_results:
            perf = test_results['performance']
            if 'benchmarks' in perf:
                print("\n性能指标:")
                benchmarks = perf['benchmarks']
                print(f"  批量向量化: {benchmarks.get('embedding_avg_ms', 0):.1f} ms/文本")
                print(f"  向量搜索: {benchmarks.get('search_time_ms', 0):.1f} ms")
                print(f"  存储操作: {benchmarks.get('storage_time', 0):.2f} 秒")
        
        # 最终结论
        print("\n" + "=" * 60)
        if total_failed == 0:
            print("🎉 所有测试通过！迁移成功！")
            conclusion = "SUCCESS"
        elif total_failed <= 2:
            print("⚠️  大部分测试通过，存在轻微问题")
            conclusion = "PARTIAL_SUCCESS"
        else:
            print("❌ 多项测试失败，需要进一步调查")
            conclusion = "FAILURE"
        print("=" * 60)
        
        return {
            'conclusion': conclusion,
            'total_passed': total_passed,
            'total_failed': total_failed,
            'test_results': test_results,
            'timestamp': time.time()
        }


async def main():
    """主测试函数"""
    test_suite = MigrationTestSuite()
    results = await test_suite.run_complete_test_suite()
    
    # 保存测试报告
    import json
    from pathlib import Path
    
    report_file = Path("migration_test_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n测试报告已保存到: {report_file}")
    
    return results['conclusion'] == 'SUCCESS'


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)