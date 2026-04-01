"""
评估指标配置
"""
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

THRESHOLDS = {
    "faithfulness": 0.8,
    "answer_relevancy": 0.75,
    "context_precision": 0.7,
    "context_recall": 0.75,
    "retrieval_latency_ms": 500,
    "generation_latency_ms": 5000,
}
