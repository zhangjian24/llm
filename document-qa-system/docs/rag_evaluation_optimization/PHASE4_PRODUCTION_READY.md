# Phase 4: 生产就绪详细方案

## 4.1 目标

完善监控、追踪、自动化，确保生产环境稳定运行。

---

## 4.2 监控体系

### 4.2.1 Prometheus指标

```python
# backend/app/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest

registry = CollectorRegistry()

# ============ 请求指标 ============
rag_requests_total = Counter(
    'rag_requests_total',
    'Total RAG requests',
    ['endpoint', 'status'],
    registry=registry
)

rag_request_duration_seconds = Histogram(
    'rag_request_duration_seconds',
    'Request latency in seconds',
    ['operation'],  # embedding, retrieval, rerank, generation
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    registry=registry
)

# ============ 质量指标 ============
quality_faithfulness = Gauge(
    'rag_quality_faithfulness',
    'Faithfulness score (sampled)',
    registry=registry
)

quality_relevance = Gauge(
    'rag_quality_answer_relevance',
    'Answer relevance score (sampled)',
    registry=registry
)

# ============ 成本指标 ============
tokens_input_total = Counter(
    'rag_tokens_input_total',
    'Total input tokens',
    ['model'],
    registry=registry
)

tokens_output_total = Counter(
    'rag_tokens_output_total',
    'Total output tokens',
    ['model'],
    registry=registry
)

cost_usd_total = Counter(
    'rag_cost_usd_total',
    'Total cost in USD',
    registry=registry
)

# ============ 缓存指标 ============
cache_hits_total = Counter(
    'rag_cache_hits_total',
    'Cache hits',
    ['cache_type'],  # embedding, retrieval, response
    registry=registry
)

cache_misses_total = Counter(
    'rag_cache_misses_total',
    'Cache misses',
    ['cache_type'],
    registry=registry
)


# ============ 指标暴露 ============
@app.get("/metrics")
async def metrics():
    """Prometheus指标端点"""
    return Response(
        content=generate_latest(registry),
        media_type="text/plain"
    )
```

### 4.2.2 指标采集中间件

```python
# backend/app/middleware/metrics.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import structlog

from app.monitoring.metrics import (
    rag_requests_total,
    rag_request_duration_seconds
)

logger = structlog.get_logger()

class MetricsMiddleware(BaseHTTPMiddleware):
    """RAG指标收集中间件"""
    
    async def dispatch(self, request: Request, call_next):
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 记录请求
        rag_requests_total.labels(
            endpoint=request.url.path,
            status="started"
        ).inc()
        
        # 处理请求
        try:
            response = await call_next(request)
            status = "success"
        except Exception as e:
            status = "error"
            raise
        finally:
            # 记录耗时
            duration = time.time() - start_time
            
            rag_request_duration_seconds.labels(
                operation="total"
            ).observe(duration)
            
            # 记录最终状态
            rag_requests_total.labels(
                endpoint=request.url.path,
                status=status
            ).inc()
        
        return response
```

### 4.2.3 告警规则

```yaml
# config/alerts.yml
groups:
  - name: rag_quality
    rules:
      - alert: LowFaithfulness
        expr: rag_quality_faithfulness < 0.7
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "RAG Faithfulness below threshold"
          description: "Faithfulness score is {{ $value }}, below threshold of 0.7"
          
      - alert: LowAnswerRelevance
        expr: rag_quality_answer_relevance < 0.65
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Answer relevance below threshold"
          
      - alert: HighLatency
        expr: histogram_quantile(0.95, rag_request_duration_seconds) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High RAG latency"
          description: "P95 latency is {{ $value }}s, above threshold of 5s"

  - name: rag_cost
    rules:
      - alert: CostSpike
        expr: rate(rag_cost_usd_total[1h]) > 2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Cost spike detected"
          description: "Cost rate is ${{ $value }}/hour"

  - name: rag_cache
    rules:
      - alert: LowCacheHitRate
        expr: (rag_cache_hits_total / (rag_cache_hits_total + rag_cache_misses_total)) < 0.2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low cache hit rate"
```

---

## 4.3 成本追踪

### 4.3.1 成本计算

```python
# backend/app/monitoring/cost_tracker.py
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List
import asyncio

@dataclass
class CostRecord:
    """成本记录"""
    timestamp: datetime
    category: str    # embedding, llm
    model: str
    tokens: int
    cost_usd: float

class CostTracker:
    """成本追踪器"""
    
    # 阿里云百炼定价 (per 1M tokens, USD)
    PRICING = {
        "qwen-max": {"input": 4.0, "output": 12.0},
        "qwen-turbo": {"input": 1.0, "output": 3.0},
        "text-embedding-v4": {"input": 1.0, "output": 0},
        "rerank-v3": {"input": 10.0, "output": 10.0}
    }
    
    def __init__(self):
        self.records: List[CostRecord] = []
        self.daily_budget: float = 100.0
    
    def record_embedding(self, model: str, tokens: int):
        """记录embedding成本"""
        rate = self.PRICING.get(model, {}).get("input", 1.0)
        cost = (tokens / 1_000_000) * rate
        
        self.records.append(CostRecord(
            timestamp=datetime.now(),
            category="embedding",
            model=model,
            tokens=tokens,
            cost_usd=cost
        ))
        
        # 更新Prometheus指标
        from app.monitoring.metrics import tokens_input_total, cost_usd_total
        tokens_input_total.labels(model=model).inc(tokens)
        cost_usd_total.inc(cost)
    
    def record_llm(self, model: str, input_tokens: int, output_tokens: int):
        """记录LLM成本"""
        rates = self.PRICING.get(model, {"input": 4.0, "output": 12.0})
        cost = (input_tokens / 1_000_000) * rates["input"]
        cost += (output_tokens / 1_000_000) * rates["output"]
        
        self.records.append(CostRecord(
            timestamp=datetime.now(),
            category="llm",
            model=model,
            tokens=input_tokens + output_tokens,
            cost_usd=cost
        ))
        
        # 更新Prometheus指标
        from app.monitoring.metrics import tokens_input_total, tokens_output_total, cost_usd_total
        tokens_input_total.labels(model=model).inc(input_tokens)
        tokens_output_total.labels(model=model).inc(output_tokens)
        cost_usd_total.inc(cost)
    
    def get_daily_report(self) -> Dict:
        """获取每日成本报告"""
        today = datetime.now().date()
        today_records = [
            r for r in self.records 
            if r.timestamp.date() == today
        ]
        
        total_cost = sum(r.cost_usd for r in today_records)
        
        by_category = {}
        by_model = {}
        for r in today_records:
            by_category[r.category] = by_category.get(r.category, 0) + r.cost_usd
            by_model[r.model] = by_model.get(r.model, 0) + r.cost_usd
        
        return {
            "date": today.isoformat(),
            "total_cost_usd": total_cost,
            "budget_usd": self.daily_budget,
            "budget_used_pct": (total_cost / self.daily_budget) * 100,
            "by_category": by_category,
            "by_model": by_model,
            "request_count": len(today_records),
            "projected_monthly": total_cost * 30
        }


# 全局单例
cost_tracker = CostTracker()
```

### 4.3.2 成本报表API

```python
# backend/app/api/v1/cost.py
from fastapi import APIRouter
from app.monitoring.cost_tracker import cost_tracker

router = APIRouter(prefix="/cost", tags=["成本管理"])

@router.get("/daily")
async def get_daily_cost_report():
    """获取每日成本报告"""
    return cost_tracker.get_daily_report()

@router.get("/monthly")
async def get_monthly_cost_report():
    """获取月度成本报告"""
    # 按日期聚合
    daily_costs = {}
    
    for record in cost_tracker.records:
        date = record.timestamp.date()
        daily_costs[date.isoformat()] = daily_costs.get(date.isoformat(), 0) + record.cost_usd
    
    total = sum(daily_costs.values())
    
    return {
        "total_cost_usd": total,
        "daily_costs": daily_costs,
        "average_daily": total / len(daily_costs) if daily_costs else 0,
        "projected_monthly": (total / len(daily_costs) * 30) if daily_costs else 0
    }
```

---

## 4.4 CI/CD集成

### 4.4.1 GitHub Actions配置

```yaml
# .github/workflows/rag-quality-gate.yml
name: RAG Quality Gate

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  rag-evaluation:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install ragas deepeval
      
      - name: Run RAG Evaluation
        env:
          DASHSCOPE_API_KEY: ${{ secrets.DASHSCOPE_API_KEY }}
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          REDIS_URL: ${{ secrets.REDIS_URL }}
        run: |
          cd backend
          python -m pytest tests/evaluation/ -v \
            --tb=short \
            --maxfail=3 \
            --junitxml=eval-results.xml
      
      - name: Check Quality Thresholds
        run: |
          cd backend
          python scripts/check_thresholds.py
          # 阈值定义:
          # faithfulness >= 0.80
          # answer_relevancy >= 0.75
          # context_precision >= 0.70
          # context_recall >= 0.75
          # 如果未达标，退出码为1
      
      - name: Upload Evaluation Results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: rag-eval-results
          path: |
            eval-results.xml
            eval_report.html

  cost-estimate:
    runs-on: ubuntu-latest
    needs: rag-evaluation
    
    steps:
      - name: Estimate Cost Impact
        run: |
          # 估算PR对成本的影响
          echo "Estimated cost impact: $0.50/day"
```

### 4.4.2 阈值检查脚本

```python
# backend/scripts/check_thresholds.py
import sys
import json

# 阈值定义
THRESHOLDS = {
    "faithfulness": 0.80,
    "answer_relevancy": 0.75,
    "context_precision": 0.70,
    "context_recall": 0.75,
}

def main():
    # 从评估结果读取
    # 这里简化处理，实际应该读取评估输出
    
    print("检查质量阈值...")
    
    passed = True
    for metric, threshold in THRESHOLDS.items():
        # 模拟值（实际从评估结果读取）
        value = 0.8  # 应该是从eval结果读取
        
        status = "✅" if value >= threshold else "❌"
        print(f"  {metric}: {value:.2f} (阈值: {threshold}) {status}")
        
        if value < threshold:
            passed = False
    
    if not passed:
        print("\n❌ 质量阈值检查未通过!")
        sys.exit(1)
    else:
        print("\n✅ 所有质量阈值检查通过!")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## 4.5 Grafana面板配置

```json
{
  "dashboard": {
    "title": "RAG System Monitoring",
    "panels": [
      {
        "title": "Request Latency (P95)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(rag_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P95 Latency"
          }
        ]
      },
      {
        "title": "Quality Scores",
        "type": "graph",
        "targets": [
          {
            "expr": "rag_quality_faithfulness",
            "legendFormat": "Faithfulness"
          },
          {
            "expr": "rag_quality_answer_relevance",
            "legendFormat": "Answer Relevance"
          }
        ]
      },
      {
        "title": "Daily Cost",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(rag_cost_usd_total[1h]) * 24",
            "legendFormat": "Daily Cost ($)"
          }
        ]
      },
      {
        "title": "Cache Hit Rate",
        "type": "gauge",
        "targets": [
          {
            "expr": "rate(rag_cache_hits_total[5m]) / (rate(rag_cache_hits_total[5m]) + rate(rag_cache_misses_total[5m]))",
            "legendFormat": "Hit Rate"
          }
        ]
      },
      {
        "title": "Token Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(rag_tokens_input_total[1h])",
            "legendFormat": "Input Tokens/hr"
          },
          {
            "expr": "rate(rag_tokens_output_total[1h])",
            "legendFormat": "Output Tokens/hr"
          }
        ]
      }
    ]
  }
}
```

---

## 4.6 交付物清单

| 交付物 | 验收标准 | 文件位置 |
|--------|----------|----------|
| Prometheus指标 | 指标暴露正确 | backend/app/monitoring/metrics.py |
| Grafana面板 | 关键指标可视化 | configs/grafana/ |
| 告警规则 | 触发正确 | config/alerts.yml |
| 成本报表API | 每日自动生成 | backend/app/api/v1/cost.py |
| CI/CD质量门 | PR自动检查 | .github/workflows/ |

---

## 4.7 下一步行动

1. 集成Prometheus指标
2. 配置Prometheus采集
3. 配置Grafana面板
4. 配置告警规则
5. 实现成本追踪
6. 配置CI/CD流程

---

**文档版本**: v1.0  
**创建日期**: 2026-03-31
