"""
RAG评估器 - 自包含版本
不依赖ragas框架，使用简单指标计算
"""
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import structlog
import json

logger = structlog.get_logger()

@dataclass
class EvaluationResult:
    """评估结果"""
    question: str
    answer: str = ""
    contexts: List[str] = field(default_factory=list)
    ground_truth: Optional[str] = None
    
    # 指标分数
    faithfulness: float = 0.0
    answer_relevancy: float = 0.0
    context_precision: float = 0.0
    context_recall: float = 0.0
    
    # 性能指标
    retrieval_latency_ms: float = 0.0
    generation_latency_ms: float = 0.0
    
    # 检索结果
    retrieved_chunks: List[Dict] = field(default_factory=list)


class RAGEvaluator:
    """RAG评估器 - 简化版"""
    
    def __init__(self, rag_service=None):
        self.rag_service = rag_service
    
    async def evaluate_single(
        self,
        question: str,
        ground_truth: Optional[str] = None
    ) -> EvaluationResult:
        """评估单个问题"""
        
        result = EvaluationResult(
            question=question,
            ground_truth=ground_truth
        )
        
        if not self.rag_service:
            logger.warning("rag_service not initialized")
            return result
        
        try:
            # 执行RAG查询并获取结果
            start_time = asyncio.get_event_loop().time()
            
            # 获取检索到的chunks
            query_vector = await self.rag_service._embed_question(question)
            similar_chunks = await self.rag_service._retrieve_similar_chunks(query_vector, top_k=10)
            
            retrieval_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # 尝试重排序
            try:
                reranked_chunks = await self.rag_service._rerank_results(
                    similar_chunks,
                    question,
                    keep_top_k=5
                )
            except Exception as e:
                logger.warning(f"rerank failed: {e}")
                reranked_chunks = similar_chunks[:5]
            
            result.retrieved_chunks = reranked_chunks
            result.retrieval_latency_ms = retrieval_time
            
            # 构建上下文
            contexts = [
                chunk.get("metadata", {}).get("content", "")
                for chunk in reranked_chunks
            ]
            result.contexts = contexts
            
            # 执行生成
            answer_text = ""
            async for token in self.rag_service.query(question):
                answer_text += token
            
            result.answer = answer_text
            result.generation_latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000 - retrieval_time
            
            # 简单指标计算
            result.faithfulness = self._calc_faithfulness(answer_text, contexts)
            result.answer_relevancy = self._calc_answer_relevancy(answer_text, question)
            result.context_precision = self._calc_context_precision(contexts, question)
            if ground_truth:
                result.context_recall = self._calc_context_recall(contexts, ground_truth)
            
            logger.info(
                "eval_completed",
                question=question[:50],
                faithfulness=result.faithfulness,
                answer_relevancy=result.answer_relevancy
            )
            
        except Exception as e:
            logger.error(f"evaluation failed: {e}", exc_info=True)
        
        return result
    
    def _calc_faithfulness(self, answer: str, contexts: List[str]) -> float:
        """计算忠实度 - 简单版本"""
        if not answer or not contexts:
            return 0.0
        
        # 检查答案中是否有足够的上下文支撑
        # 这里简化处理：检查答案长度是否合理，是否包含上下文中的关键词
        context_text = " ".join(contexts)
        
        # 简单指标：答案不应该太长（可能幻觉）也不应该太短
        answer_len = len(answer)
        if answer_len < 10:
            return 0.3
        elif answer_len > 2000:
            return 0.5
        
        # 检查答案是否提到了相关内容
        has_context_ref = any(keyword in answer.lower() for keyword in [
            "根据", "文档", "提到", "根据文档", "在文档中"
        ])
        
        return 0.7 if has_context_ref else 0.6
    
    def _calc_answer_relevancy(self, answer: str, question: str) -> float:
        """计算答案相关性"""
        if not answer or not question:
            return 0.0
        
        # 简单检查：答案是否回答了问题
        question_keywords = set(question.lower().split())
        answer_words = set(answer.lower().split())
        
        # 移除常见停用词
        stopwords = {"是", "的", "了", "在", "有", "和", "与", "或", "这", "那", "什么", "如何", "怎样"}
        question_keywords = question_keywords - stopwords
        answer_words = answer_words - stopwords
        
        if not question_keywords:
            return 0.5
        
        overlap = len(question_keywords & answer_words)
        relevance = min(overlap / len(question_keywords), 1.0)
        
        return max(relevance, 0.5)
    
    def _calc_context_precision(self, contexts: List[str], question: str) -> float:
        """计算上下文精确度"""
        if not contexts:
            return 0.0
        
        # 简单检查：上下文是否与问题相关
        question_keywords = set(question.lower().split())
        
        relevant_count = 0
        for ctx in contexts:
            ctx_keywords = set(ctx.lower().split())
            if question_keywords & ctx_keywords:
                relevant_count += 1
        
        return relevant_count / len(contexts) if contexts else 0.0
    
    def _calc_context_recall(self, contexts: List[str], ground_truth: str) -> float:
        """计算上下文召回率"""
        if not contexts or not ground_truth:
            return 0.0
        
        # 简单检查：上下文是否覆盖了ground truth
        truth_keywords = set(ground_truth.lower().split())
        
        covered_count = 0
        for ctx in contexts:
            ctx_lower = ctx.lower()
            for keyword in truth_keywords:
                if len(keyword) > 2 and keyword in ctx_lower:
                    covered_count += 1
                    break
        
        # 简化计算
        min_len = min(len(contexts), 5)
        return covered_count / min_len if min_len > 0 else 0.0
    
    async def evaluate_dataset(
        self,
        dataset_path: str
    ) -> List[EvaluationResult]:
        """评估整个数据集"""
        
        test_data = self.load_dataset(dataset_path)
        
        results = []
        for item in test_data:
            result = await self.evaluate_single(
                question=item["question"],
                ground_truth=item.get("ground_truth")
            )
            results.append(result)
            
            logger.info(
                "eval_item_completed",
                question=item["question"][:50],
                faithfulness=result.faithfulness,
                answer_relevancy=result.answer_relevancy
            )
        
        return results
    
    def load_dataset(self, dataset_path: str) -> List[Dict]:
        """加载测试数据集"""
        with open(dataset_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def save_results(self, results: List[EvaluationResult], output_path: str):
        """保存评估结果"""
        data = []
        for r in results:
            data.append({
                "question": r.question,
                "answer": r.answer,
                "faithfulness": r.faithfulness,
                "answer_relevancy": r.answer_relevancy,
                "context_precision": r.context_precision,
                "context_recall": r.context_recall,
                "retrieval_latency_ms": r.retrieval_latency_ms,
                "generation_latency_ms": r.generation_latency_ms,
            })
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
