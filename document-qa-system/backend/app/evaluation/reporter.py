"""
评估报告生成器
"""
from typing import List, Dict
from .evaluator import EvaluationResult
from .metrics import THRESHOLDS


class EvaluationReport:
    """评估报告"""
    
    def __init__(self, results: List[EvaluationResult]):
        self.results = results
    
    def generate_report(self) -> str:
        """生成文本报告"""
        
        if not self.results:
            return "No evaluation results"
        
        # 计算平均指标
        avg_faithfulness = sum(r.faithfulness for r in self.results) / len(self.results)
        avg_relevancy = sum(r.answer_relevancy for r in self.results) / len(self.results)
        avg_precision = sum(r.context_precision for r in self.results) / len(self.results)
        avg_recall = sum(r.context_recall for r in self.results) / len(self.results)
        
        avg_retrieval_latency = sum(r.retrieval_latency_ms for r in self.results) / len(self.results)
        avg_generation_latency = sum(r.generation_latency_ms for r in self.results) / len(self.results)
        
        # 构建报告
        report = f"""
╔═══════════════════════════════════════════════════════════════╗
║                    RAG 评估报告                              ║
╠═══════════════════════════════════════════════════════════════╣
║ 评估样本数: {len(self.results)}                                        ║
╠═══════════════════════════════════════════════════════════════╣
║ 指标              │ 当前值   │ 阈值    │ 状态              ║
╠═══════════════════════════════════════════════════════════════╣
║ Faithfulness      │ {avg_faithfulness:.2f}    │ ≥{THRESHOLDS['faithfulness']:.2f}   │ {self._status_icon(avg_faithfulness, THRESHOLDS['faithfulness'])}             ║
║ Answer Relevance  │ {avg_relevancy:.2f}    │ ≥{THRESHOLDS['answer_relevancy']:.2f}   │ {self._status_icon(avg_relevancy, THRESHOLDS['answer_relevancy'])}             ║
║ Context Precision │ {avg_precision:.2f}    │ ≥{THRESHOLDS['context_precision']:.2f}   │ {self._status_icon(avg_precision, THRESHOLDS['context_precision'])}             ║
║ Context Recall    │ {avg_recall:.2f}    │ ≥{THRESHOLDS['context_recall']:.2f}   │ {self._status_icon(avg_recall, THRESHOLDS['context_recall'])}             ║
╠═══════════════════════════════════════════════════════════════╣
║ P95检索延迟      │ {avg_retrieval_latency:.0f}ms  │ ≤{THRESHOLDS['retrieval_latency_ms']}ms  │ {self._status_icon(avg_retrieval_latency, THRESHOLDS['retrieval_latency_ms'], inverse=True)}            ║
║ P95生成延迟      │ {avg_generation_latency:.0f}ms │ ≤{THRESHOLDS['generation_latency_ms']}ms  │ {self._status_icon(avg_generation_latency, THRESHOLDS['generation_latency_ms'], inverse=True)}            ║
╚═══════════════════════════════════════════════════════════════╝
"""
        return report
    
    def _status_icon(self, value: float, threshold: float, inverse: bool = False) -> str:
        """判断状态图标"""
        if inverse:
            return "✅" if value <= threshold else "❌"
        return "✅" if value >= threshold else "❌"
    
    def check_thresholds(self) -> Dict[str, bool]:
        """检查阈值是否通过"""
        avg_faithfulness = sum(r.faithfulness for r in self.results) / len(self.results)
        avg_relevancy = sum(r.answer_relevancy for r in self.results) / len(self.results)
        
        return {
            "faithfulness": avg_faithfulness >= THRESHOLDS["faithfulness"],
            "answer_relevancy": avg_relevancy >= THRESHOLDS["answer_relevancy"],
            "context_precision": (sum(r.context_precision for r in self.results) / len(self.results)) >= THRESHOLDS["context_precision"],
            "context_recall": (sum(r.context_recall for r in self.results) / len(self.results)) >= THRESHOLDS["context_recall"],
        }
    
    def get_summary(self) -> Dict:
        """获取汇总数据"""
        return {
            "sample_count": len(self.results),
            "avg_faithfulness": sum(r.faithfulness for r in self.results) / len(self.results),
            "avg_answer_relevancy": sum(r.answer_relevancy for r in self.results) / len(self.results),
            "avg_context_precision": sum(r.context_precision for r in self.results) / len(self.results),
            "avg_context_recall": sum(r.context_recall for r in self.results) / len(self.results),
            "avg_retrieval_latency_ms": sum(r.retrieval_latency_ms for r in self.results) / len(self.results),
            "avg_generation_latency_ms": sum(r.generation_latency_ms for r in self.results) / len(self.results),
        }
