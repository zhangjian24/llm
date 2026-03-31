# Phase 1: 评估体系建设详细方案

## 1.1 目标

建立系统化的RAG评估体系，获取当前系统基线指标，为后续优化提供量化依据。

---

## 1.2 评估框架搭建

### 1.2.1 依赖安装

```bash
pip install ragas deepeval datasets
```

### 1.2.2 目录结构

```
backend/app/evaluation/
├── __init__.py
├── metrics.py          # 指标定义
├── evaluator.py        # 评估器
├── dataset.py         # 数据集管理
├── reporter.py        # 报告生成
└── scripts/
    ├── __init__.py
    ├── run_eval.py    # 执行评估
    └── check_baseline.py # 基线检查
```

### 1.2.3 核心代码

#### 指标配置

```python
# backend/app/evaluation/metrics.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class EvaluationConfig:
    """评估配置"""
    # 生成指标阈值
    faithfulness_threshold: float = 0.8
    answer_relevancy_threshold: float = 0.75
    
    # 检索指标阈值
    context_precision_threshold: float = 0.7
    context_recall_threshold: float = 0.75
    
    # 性能指标阈值
    max_retrieval_latency_ms: int = 500
    max_generation_latency_ms: int = 5000
    
    # Judge配置
    judge_model: str = "qwen-turbo"
    judge_temperature: float = 0.0

# 指标阈值常量
THRESHOLDS = {
    "faithfulness": 0.8,
    "answer_relevancy": 0.75,
    "context_precision": 0.7,
    "context_recall": 0.75,
    "retrieval_latency_ms": 500,
    "generation_latency_ms": 5000,
}
```

#### 评估器实现

```python
# backend/app/evaluation/evaluator.py
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import structlog

from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)
from datasets import Dataset

from app.services.rag_service import RAGService

logger = structlog.get_logger()

@dataclass
class EvaluationResult:
    """评估结果"""
    question: str
    answer: str
    contexts: List[str]
    ground_truth: Optional[str]
    
    # 指标分数
    faithfulness: float = 0.0
    answer_relevancy: float = 0.0
    context_precision: float = 0.0
    context_recall: float = 0.0
    
    # 性能指标
    retrieval_latency_ms: float = 0.0
    generation_latency_ms: float = 0.0

class RAGEvaluator:
    """RAG评估器"""
    
    def __init__(self, rag_service: RAGService):
        self.rag_service = rag_service
    
    async def evaluate_single(
        self,
        question: str,
        ground_truth: Optional[str] = None
    ) -> EvaluationResult:
        """评估单个问题"""
        
        # 执行RAG查询（需要修改RAGService以返回检索结果）
        start_time = asyncio.get_event_loop().time()
        
        answer_chunks = []
        answer_text = ""
        
        async for chunk in self.rag_service.query(question):
            answer_text += chunk
        
        # 获取检索到的chunks（需要RAGService暴露此方法）
        retrieved_chunks = await self.rag_service.get_retrieved_chunks(question)
        
        retrieval_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        # 构建评估数据
        eval_data = {
            "question": [question],
            "answer": [answer_text],
            "contexts": [[c["content"] for c in retrieved_chunks]],
        }
        
        if ground_truth:
            eval_data["ground_truth"] = [ground_truth]
        
        # 执行评估
        dataset = Dataset.from_dict(eval_data)
        
        metrics = [faithfulness, answer_relevancy, context_precision]
        if ground_truth:
            metrics.append(context_recall)
        
        result = evaluate(dataset=dataset, metrics=metrics)
        
        # 转换为结果对象
        eval_result = EvaluationResult(
            question=question,
            answer=answer_text,
            contexts=[c["content"] for c in retrieved_chunks],
            ground_truth=ground_truth,
            retrieval_latency_ms=retrieval_time
        )
        
        # 提取分数
        result_df = result.to_pandas()
        if len(result_df) > 0:
            eval_result.faithfulness = result_df.iloc[0].get("faithfulness", 0.0)
            eval_result.answer_relevancy = result_df.iloc[0].get("answer_relevancy", 0.0)
            eval_result.context_precision = result_df.iloc[0].get("context_precision", 0.0)
            if ground_truth:
                eval_result.context_recall = result_df.iloc[0].get("context_recall", 0.0)
        
        return eval_result
    
    async def evaluate_dataset(
        self,
        dataset_path: str
    ) -> List[EvaluationResult]:
        """评估整个数据集"""
        
        # 加载测试数据
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
        import json
        
        with open(dataset_path, "r", encoding="utf-8") as f:
            return json.load(f)
```

#### 报告生成器

```python
# backend/app/evaluation/reporter.py
from typing import List, Dict, Any
from dataclasses import dataclass
from .evaluator import EvaluationResult
from .metrics import THRESHOLDS

@dataclass
class EvaluationReport:
    """评估报告"""
    results: List[EvaluationResult]
    
    def generate_report(self) -> str:
        """生成文本报告"""
        
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
```

---

## 1.3 测试数据集构建

### 1.3.1 数据集规格

| 类型 | 数量 | 来源 | 用途 |
|------|------|------|------|
| Golden | 50条 | 人工标注 | 核心指标追踪 |
| 合成 | 200条 | Ragas生成 | 回归测试 |
| 生产回填 | 持续 | 用户query | 真实验证 |

### 1.3.2 Golden数据集格式

```json
[
  {
    "id": "golden_001",
    "question": "什么是人工智能？",
    "ground_truth": "人工智能是计算机科学的一个重要分支...",
    "expected_sources": ["chunk_id_1", "chunk_id_2"],
    "complexity": "simple",
    "category": "概念解释"
  },
  {
    "id": "golden_002",
    "question": "机器学习和深度学习有什么区别？",
    "ground_truth": "机器学习是AI的一个子集，深度学习是机器学习的一个分支...",
    "expected_sources": ["chunk_id_3", "chunk_id_4"],
    "complexity": "medium",
    "category": "对比分析"
  },
  {
    "id": "golden_003",
    "question": "根据文档内容，分析人工智能对未来就业市场的影响，并提出应对建议",
    "ground_truth": "人工智能对未来就业市场的影响是多方面的...",
    "expected_sources": ["chunk_id_5", "chunk_id_6", "chunk_id_7"],
    "complexity": "complex",
    "category": "分析建议"
  }
]
```

### 1.3.3 字段说明

| 字段 | 说明 |
|------|------|
| question | 测试问题 |
| ground_truth | 标准答案（用于Context Recall计算） |
| expected_sources | 期望被检索到的chunk ID |
| complexity | 复杂度(simple/medium/complex) |
| category | 问题类型 |

### 1.3.4 数据集存储位置

```
backend/
├── data/
│   └── evaluation/
│       ├── golden_dataset.json    # 50条
│       ├── synthetic_dataset.json  # 200条
│       └── production_samples.json # 生产样本
```

---

## 1.4 执行脚本

### 1.4.1 运行评估

```python
# backend/app/evaluation/scripts/run_eval.py
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.evaluation.evaluator import RAGEvaluator
from app.evaluation.reporter import EvaluationReport
from app.services.rag_service import RAGService
from app.services.embedding_service import EmbeddingService
from app.services.vector_service_adapter import VectorServiceAdapter
from app.services.rerank_service import RerankService

async def main():
    # 初始化服务
    print("初始化服务...")
    embedding_svc = EmbeddingService()
    vector_svc = VectorServiceAdapter()
    rerank_svc = RerankService()
    rag_svc = RAGService(embedding_svc, vector_svc, rerank_svc)
    
    # 创建评估器
    evaluator = RAGEvaluator(rag_svc)
    
    # 加载Golden数据集
    dataset_path = "data/evaluation/golden_dataset.json"
    print(f"加载数据集: {dataset_path}")
    
    # 执行评估
    print("开始评估...")
    results = await evaluator.evaluate_dataset(dataset_path)
    
    # 生成报告
    reporter = EvaluationReport(results)
    report = reporter.generate_report()
    print(report)
    
    # 检查阈值
    passed = reporter.check_thresholds()
    print("\n阈值检查:")
    for metric, result in passed.items():
        status = "✅ 通过" if result else "❌ 未通过"
        print(f"  {metric}: {status}")
    
    return passed

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 1.5 RAGService改造

为了让评估器能够获取检索结果，需要修改RAGService：

```python
# backend/app/services/rag_service.py 新增方法

class RAGService:
    # ... 现有代码 ...
    
    async def get_retrieved_chunks(self, question: str, top_k: int = None) -> List[Dict]:
        """
        获取检索到的chunks（用于评估）
        
        Args:
            question: 用户问题
            top_k: 检索数量
            
        Returns:
            检索到的chunks列表
        """
        top_k = top_k or settings.RAG_TOP_K
        
        # 转换为向量
        query_vector = await self._embed_question(question)
        
        # 检索
        similar_chunks = await self._retrieve_similar_chunks(
            query_vector, 
            top_k=top_k
        )
        
        # 重排序
        try:
            reranked_chunks = await self._rerank_results(
                similar_chunks,
                question,
                keep_top_k=top_k
            )
        except Exception:
            reranked_chunks = similar_chunks[:top_k]
        
        # 过滤
        filtered_chunks = [
            chunk for chunk in reranked_chunks
            if chunk.get('relevance_score', 0) >= settings.RELEVANCE_THRESHOLD
        ]
        
        return filtered_chunks
```

---

## 1.6 交付物清单

| 交付物 | 验收标准 | 文件位置 |
|--------|----------|----------|
| 评估框架代码 | 可执行，指标计算正确 | backend/app/evaluation/ |
| Golden数据集 | 50条，含标注 | backend/data/evaluation/golden_dataset.json |
| 基线报告 | 含各项指标当前值 | 运行run_eval.py输出 |

---

## 1.7 下一步行动

1. 安装评估依赖
2. 创建评估模块目录结构
3. 实现评估器代码
4. 构建Golden数据集（50条）
5. 运行基线评估

---

**文档版本**: v1.0  
**创建日期**: 2026-03-31
