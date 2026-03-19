"""
PostgreSQL vs Pinecone 性能对比测试
比较两种向量存储方案的性能表现
"""

import asyncio
import time
import numpy as np
from typing import List, Dict, Any
import structlog

logger = structlog.get_logger()


class PerformanceComparisonTest:
    """性能对比测试"""
    
    def __init__(self):
        """初始化测试"""
        self.test_vectors_count = 1000
        self.query_count = 100
        self.vector_dimension = 1024
        
    async def setup_test_data(self) -> List[List[float]]:
        """准备测试数据"""
        print("准备测试数据...")
        
        # 生成测试向量
        test_vectors = []
        for i in range(self.test_vectors_count):
            # 生成具有一定结构的向量（模拟真实场景）
            base_vector = np.random.rand(self.vector_dimension) * 0.5
            # 添加一些模式
            pattern_strength = 0.3
            if i % 10 == 0:  # 每10个向量有一个共同模式
                base_vector[:10] += pattern_strength
            elif i % 7 == 0:
                base_vector[10:20] += pattern_strength
            test_vectors.append(base_vector.tolist())
        
        return test_vectors
    
    async def test_postgresql_performance(self, test_vectors: List[List[float]]) -> Dict[str, Any]:
        """测试 PostgreSQL 向量性能"""
        print("\n🧪 测试 PostgreSQL 向量性能")
        print("-" * 40)
        
        try:
            from app.services.postgresql_vector_service import PostgreSQLVectorService
            from app.core.database import AsyncSessionLocal
            
            service = PostgreSQLVectorService()
            results = {}
            
            # 1. 测试插入性能
            print("1. 测试向量插入性能...")
            insert_data = [
                {
                    "id": f"perf_test_{i}",
                    "values": test_vectors[i],
                    "metadata": {"test": f"data_{i}"}
                }
                for i in range(len(test_vectors))
            ]
            
            start_time = time.time()
            async with AsyncSessionLocal() as session:
                await service.upsert_vectors(session, insert_data[:100])  # 先测试100个
            insert_time = time.time() - start_time
            
            results['insert_time_100'] = insert_time
            results['insert_rate'] = 100 / insert_time if insert_time > 0 else 0
            print(f"   插入100个向量耗时: {insert_time:.3f}秒 ({results['insert_rate']:.1f} 向量/秒)")
            
            # 2. 测试搜索性能
            print("2. 测试向量搜索性能...")
            query_vectors = test_vectors[:self.query_count]
            search_times = []
            
            async with AsyncSessionLocal() as session:
                for query_vector in query_vectors:
                    start_time = time.time()
                    await service.similarity_search(
                        session=session,
                        query_vector=query_vector,
                        top_k=10
                    )
                    search_time = time.time() - start_time
                    search_times.append(search_time)
            
            avg_search_time = np.mean(search_times)
            p95_search_time = np.percentile(search_times, 95)
            
            results['avg_search_time'] = avg_search_time
            results['p95_search_time'] = p95_search_time
            results['search_throughput'] = 1 / avg_search_time if avg_search_time > 0 else 0
            
            print(f"   平均搜索时间: {avg_search_time*1000:.2f}毫秒")
            print(f"   95%分位搜索时间: {p95_search_time*1000:.2f}毫秒")
            print(f"   搜索吞吐量: {results['search_throughput']:.1f} 查询/秒")
            
            # 3. 测试内存使用（简单估计）
            print("3. 测试资源使用...")
            vector_memory_mb = (len(test_vectors) * self.vector_dimension * 4) / (1024 * 1024)
            results['estimated_memory_mb'] = vector_memory_mb
            print(f"   估计内存使用: {vector_memory_mb:.1f} MB")
            
            return results
            
        except Exception as e:
            print(f"❌ PostgreSQL 性能测试失败: {e}")
            return {'error': str(e)}
    
    async def test_pinecone_performance(self, test_vectors: List[List[float]]) -> Dict[str, Any]:
        """测试 Pinecone 性能（如果可用）"""
        print("\n🌲 测试 Pinecone 性能")
        print("-" * 40)
        
        try:
            from app.services.pinecone_service import PineconeService
            
            service = PineconeService()
            results = {}
            
            # 1. 测试插入性能
            print("1. 测试向量插入性能...")
            insert_data = [
                {
                    "id": f"perf_test_{i}",
                    "values": test_vectors[i],
                    "metadata": {"test": f"data_{i}"}
                }
                for i in range(min(100, len(test_vectors)))  # Pinecone 测试100个
            ]
            
            start_time = time.time()
            await service.upsert_vectors(insert_data, namespace="perf_test")
            insert_time = time.time() - start_time
            
            results['insert_time_100'] = insert_time
            results['insert_rate'] = 100 / insert_time if insert_time > 0 else 0
            print(f"   插入100个向量耗时: {insert_time:.3f}秒 ({results['insert_rate']:.1f} 向量/秒)")
            
            # 等待索引完成
            await asyncio.sleep(2)
            
            # 2. 测试搜索性能
            print("2. 测试向量搜索性能...")
            query_vectors = test_vectors[:min(50, len(test_vectors))]  # Pinecone 测试50个查询
            search_times = []
            
            for query_vector in query_vectors:
                start_time = time.time()
                await service.similarity_search(
                    query_vector=query_vector,
                    top_k=10,
                    include_metadata=True
                )
                search_time = time.time() - start_time
                search_times.append(search_time)
            
            avg_search_time = np.mean(search_times)
            p95_search_time = np.percentile(search_times, 95)
            
            results['avg_search_time'] = avg_search_time
            results['p95_search_time'] = p95_search_time
            results['search_throughput'] = 1 / avg_search_time if avg_search_time > 0 else 0
            
            print(f"   平均搜索时间: {avg_search_time*1000:.2f}毫秒")
            print(f"   95%分位搜索时间: {p95_search_time*1000:.2f}毫秒")
            print(f"   搜索吞吐量: {results['search_throughput']:.1f} 查询/秒")
            
            # 3. 清理测试数据
            print("3. 清理测试数据...")
            await service.delete_vectors(
                ids=[f"perf_test_{i}" for i in range(100)],
                namespace="perf_test"
            )
            
            return results
            
        except Exception as e:
            print(f"⚠️  Pinecone 性能测试不可用: {e}")
            return {'unavailable': True, 'reason': str(e)}
    
    async def run_comparison(self):
        """运行性能对比"""
        print("⚡ PostgreSQL vs Pinecone 性能对比测试")
        print("=" * 60)
        
        # 准备测试数据
        test_vectors = await self.setup_test_data()
        print(f"准备了 {len(test_vectors)} 个 {self.vector_dimension}维测试向量")
        
        # 测试 PostgreSQL
        pg_results = await self.test_postgresql_performance(test_vectors)
        
        # 测试 Pinecone（如果可用）
        pinecone_results = await self.test_pinecone_performance(test_vectors)
        
        # 生成对比报告
        print("\n" + "=" * 60)
        print("📊 性能对比报告")
        print("=" * 60)
        
        # 插入性能对比
        print("\n📥 向量插入性能:")
        if 'insert_time_100' in pg_results:
            print(f"  PostgreSQL: {pg_results['insert_time_100']:.3f}秒 ({pg_results['insert_rate']:.1f} 向量/秒)")
        if 'insert_time_100' in pinecone_results:
            print(f"  Pinecone:   {pinecone_results['insert_time_100']:.3f}秒 ({pinecone_results['insert_rate']:.1f} 向量/秒)")
        elif 'unavailable' in pinecone_results:
            print("  Pinecone:   不可用")
        
        # 搜索性能对比
        print("\n🔍 向量搜索性能:")
        if 'avg_search_time' in pg_results:
            print(f"  PostgreSQL: 平均 {pg_results['avg_search_time']*1000:.2f}ms, 95%分位 {pg_results['p95_search_time']*1000:.2f}ms")
        if 'avg_search_time' in pinecone_results:
            print(f"  Pinecone:   平均 {pinecone_results['avg_search_time']*1000:.2f}ms, 95%分位 {pinecone_results['p95_search_time']*1000:.2f}ms")
        elif 'unavailable' in pinecone_results:
            print("  Pinecone:   不可用")
        
        # 资源使用
        print("\n💾 资源使用:")
        if 'estimated_memory_mb' in pg_results:
            print(f"  PostgreSQL: ~{pg_results['estimated_memory_mb']:.1f} MB 内存")
        print("  Pinecone:   托管服务，资源使用不可见")
        
        # 总体评估
        print("\n🎯 总体评估:")
        
        pg_available = 'error' not in pg_results
        pinecone_available = 'unavailable' not in pinecone_results and 'error' not in pinecone_results
        
        if pg_available and pinecone_available:
            # 都可用时进行对比
            pg_search_time = pg_results.get('avg_search_time', float('inf'))
            pinecone_search_time = pinecone_results.get('avg_search_time', float('inf'))
            
            if pg_search_time < pinecone_search_time:
                print("  🥇 PostgreSQL 搜索性能更优")
            elif pinecone_search_time < pg_search_time:
                print("  🥇 Pinecone 搜索性能更优")
            else:
                print("  🤝 两者搜索性能相当")
                
        elif pg_available:
            print("  ✅ PostgreSQL 正常工作")
        elif pinecone_available:
            print("  ✅ Pinecone 正常工作")
        else:
            print("  ❌ 两种方案都存在问题")
        
        # 保存报告
        import json
        from pathlib import Path
        
        report = {
            'postgresql': pg_results,
            'pinecone': pinecone_results,
            'test_config': {
                'vector_count': self.test_vectors_count,
                'query_count': self.query_count,
                'dimension': self.vector_dimension
            },
            'timestamp': time.time()
        }
        
        report_file = Path("performance_comparison_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细报告已保存到: {report_file}")
        
        return report


async def main():
    """主函数"""
    tester = PerformanceComparisonTest()
    await tester.run_comparison()


if __name__ == "__main__":
    asyncio.run(main())