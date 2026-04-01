"""
运行RAG评估脚本
"""
import asyncio
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.evaluation.llm_evaluator import LLMEvaluator
from app.services.embedding_service import EmbeddingService
from app.services.postgresql_vector_service import PostgreSQLVectorService
from app.services.vector_service_adapter import VectorServiceAdapter
from app.services.rerank_service import RerankService
from app.core.config import get_settings
import structlog

logger = structlog.get_logger()


async def main():
    settings = get_settings()
    
    if not settings.DASHSCOPE_API_KEY:
        print("错误: DASHSCOPE_API_KEY 未设置")
        return
    
    print("初始化服务...")
    
    # 初始化服务
    embedding_svc = EmbeddingService()
    pg_svc = PostgreSQLVectorService()
    vector_svc = VectorServiceAdapter(pg_svc)
    
    rerank_svc = RerankService()
    
    from app.services.rag_service import RAGService
    rag_svc = RAGService(embedding_svc, vector_svc, rerank_svc)
    
    # 创建LLM评估器
    evaluator = LLMEvaluator(
        rag_service=rag_svc,
        llm_base_url=settings.DASHSCOPE_BASE_URL,
        llm_api_key=settings.DASHSCOPE_API_KEY,
        judge_model="qwen-turbo"  # 使用turbo作为judge加速评估
    )
    
    # 加载测试数据
    dataset_path = "data/evaluation/test_dataset.json"
    
    if not os.path.exists(dataset_path):
        print(f"错误: 测试数据集不存在: {dataset_path}")
        return
    
    print(f"加载测试数据集: {dataset_path}")
    test_data = json.load(open(dataset_path, "r", encoding="utf-8"))
    print(f"共 {len(test_data)} 个测试问题")
    
    # 运行评估
    print("\n开始评估...")
    results = await evaluator.evaluate_dataset(dataset_path)
    
    # 计算平均分数
    total = len(results)
    avg_faithfulness = sum(r.faithfulness for r in results) / total
    avg_relevancy = sum(r.answer_relevancy for r in results) / total
    avg_precision = sum(r.context_precision for r in results) / total
    avg_recall = sum(r.context_recall for r in results) / total
    avg_retrieval_latency = sum(r.retrieval_latency_ms for r in results) / total
    avg_generation_latency = sum(r.generation_latency_ms for r in results) / total
    
    print("\n" + "="*60)
    print("评估结果汇总")
    print("="*60)
    print(f"Faithfulness:       {avg_faithfulness:.2f} (阈值: ≥0.80)")
    print(f"Answer Relevancy:   {avg_relevancy:.2f} (阈值: ≥0.75)")
    print(f"Context Precision:  {avg_precision:.2f} (阈值: ≥0.70)")
    print(f"Context Recall:     {avg_recall:.2f} (阈值: ≥0.75)")
    print(f"检索延迟(P95):      {avg_retrieval_latency:.0f}ms (阈值: ≤500ms)")
    print(f"生成延迟(P95):      {avg_generation_latency:.0f}ms (阈值: ≤5000ms)")
    print("="*60)
    
    # 保存结果
    output_path = "data/evaluation/results.json"
    evaluator.save_results(results, output_path)
    print(f"\n详细结果已保存到: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
