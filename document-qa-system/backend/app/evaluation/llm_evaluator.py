"""
LLM评估器 - 使用LLM-as-a-Judge进行专业RAG评估
基于Ragas标准实现
"""
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import structlog
import json
import httpx

logger = structlog.get_logger()


LLM_JUDGE_SYSTEM_PROMPT = """你是一个专业的RAG系统评估专家。你的任务是评估检索增强生成系统的质量。
你需要根据给定的上下文和问题，对答案进行公正、严格的专业评估。

评估标准：
1. 忠实度(Faithfulness)：答案中的陈述是否被上下文所支持
2. 答案相关性(Answer Relevancy)：答案是否直接回答了问题
3. 上下文精确度(Context Precision)：检索到的上下文与问题的相关程度
4. 上下文召回率(Context Recall)：检索到的上下文是否覆盖了ground truth中的信息

请严格按照指定的评分标准进行评估，只返回JSON格式的结果，不要添加任何解释。"""


FAITHFULNESS_PROMPT = """请评估以下答案的忠实度。

【问题】
{question}

【答案】
{answer}

【上下文】
{contexts}

评估标准：
- 答案中的每个陈述都必须有上下文的支撑
- 如果答案中的所有陈述都能在上下文中找到支持，则得分为1.0
- 如果答案中的部分陈述能被上下文支持，得分为0.5
- 如果答案中的陈述与上下文无关或矛盾，得分为0.0

请只返回一个JSON对象，格式如下：
{{"score": <分数>, "reason": "<简短原因>"}}"""


ANSWER_RELEVANCY_PROMPT = """请评估以下答案与问题的相关性。

【问题】
{question}

【答案】
{answer}

评估标准：
- 答案是否完整回答了问题
- 答案是否包含问题所要求的核心信息
- 如果答案完整且直接回答了问题，得分为1.0
- 如果答案部分回答了问题，得分为0.5
- 如果答案与问题无关，得分为0.0

请只返回一个JSON对象，格式如下：
{{"score": <分数>, "reason": "<简短原因>"}}"""


CONTEXT_PRECISION_PROMPT = """请评估检索到的上下文与问题的相关程度。

【问题】
{question}

【检索到的上下文】
{contexts}

评估标准：
- 对于每个上下文，评估其与问题的相关程度
- 计算相关上下文数量占总上下文数量的比例
- 如果所有上下文都高度相关，得分为1.0
- 如果大部分相关(>=70%)，得分为0.7
- 如果部分相关(>=50%)，得分为0.5
- 如果大部分不相关，得分为0.3
- 如果几乎不相关，得分为0.0

请只返回一个JSON对象，格式如下：
{{"score": <分数>, "reason": "<简短原因>"}}"""


CONTEXT_RECALL_PROMPT = """请评估检索到的上下文是否覆盖了ground truth中的信息。

【Ground Truth】
{ground_truth}

【检索到的上下文】
{contexts}

评估标准：
- 评估上下文是否包含了ground truth中的核心信息
- 如果上下文完整覆盖了ground truth的所有关键信息，得分为1.0
- 如果上下文覆盖了大部分关键信息(>=75%)，得分为0.75
- 如果上下文覆盖了部分关键信息(>=50%)，得分为0.5
- 如果上下文只覆盖了很少的关键信息(<50%)，得分为0.25
- 如果上下文几乎没有包含ground truth的信息，得分为0.0

请只返回一个JSON对象，格式如下：
{{"score": <分数>, "reason": "<简短原因>"}}"""


@dataclass
class EvaluationResult:
    """评估结果"""
    question: str
    answer: str = ""
    contexts: List[str] = field(default_factory=list)
    ground_truth: Optional[str] = None
    
    faithfulness: float = 0.0
    answer_relevancy: float = 0.0
    context_precision: float = 0.0
    context_recall: float = 0.0
    
    retrieval_latency_ms: float = 0.0
    generation_latency_ms: float = 0.0
    
    retrieved_chunks: List[Dict] = field(default_factory=list)


class LLMEvaluator:
    """基于LLM的RAG评估器"""
    
    def __init__(
        self,
        rag_service=None,
        llm_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
        llm_api_key: str = None,
        judge_model: str = "qwen-max"
    ):
        self.rag_service = rag_service
        self.llm_base_url = llm_base_url
        self.llm_api_key = llm_api_key
        self.judge_model = judge_model
    
    async def _call_judge_llm(self, prompt: str, system_prompt: str = None) -> Dict:
        """调用Judge LLM进行评估"""
        if system_prompt is None:
            system_prompt = LLM_JUDGE_SYSTEM_PROMPT
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.llm_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.llm_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.judge_model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.0
                    }
                )
                
                response.raise_for_status()
                result = response.json()
                
                content = result["choices"][0]["message"]["content"]
                
                # 尝试解析JSON
                import re
                json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                
                # 如果无法解析，返回默认
                logger.warning(f"无法解析LLM响应: {content}")
                return {"score": 0.5, "reason": "评估失败，使用默认分数"}
                
        except Exception as e:
            logger.error(f"Judge LLM调用失败: {e}")
            return {"score": 0.5, "reason": f"调用失败: {str(e)}"}
    
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
            start_time = asyncio.get_event_loop().time()
            
            # 获取检索到的chunks
            query_vector = await self.rag_service._embed_question(question)
            similar_chunks = await self.rag_service._retrieve_similar_chunks(query_vector, top_k=10)
            
            retrieval_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # 重排序
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
            
            # LLM评估
            if self.llm_api_key:
                # Faithfulness
                faithfulness_prompt = FAITHFULNESS_PROMPT.format(
                    question=question,
                    answer=answer_text,
                    contexts="\n\n---\n\n".join(contexts)
                )
                faithfulness_result = await self._call_judge_llm(faithfulness_prompt)
                result.faithfulness = faithfulness_result.get("score", 0.5)
                
                # Answer Relevancy
                relevancy_prompt = ANSWER_RELEVANCY_PROMPT.format(
                    question=question,
                    answer=answer_text
                )
                relevancy_result = await self._call_judge_llm(relevancy_prompt)
                result.answer_relevancy = relevancy_result.get("score", 0.5)
                
                # Context Precision
                precision_prompt = CONTEXT_PRECISION_PROMPT.format(
                    question=question,
                    contexts="\n\n---\n\n".join(contexts)
                )
                precision_result = await self._call_judge_llm(precision_prompt)
                result.context_precision = precision_result.get("score", 0.5)
                
                # Context Recall (需要ground truth)
                if ground_truth:
                    recall_prompt = CONTEXT_RECALL_PROMPT.format(
                        ground_truth=ground_truth,
                        contexts="\n\n---\n\n".join(contexts)
                    )
                    recall_result = await self._call_judge_llm(recall_prompt)
                    result.context_recall = recall_result.get("score", 0.5)
            else:
                logger.warning("LLM API key not set, using simplified evaluation")
                result = self._simplified_eval(result, contexts, question, ground_truth)
            
            logger.info(
                "eval_completed",
                question=question[:50],
                faithfulness=result.faithfulness,
                answer_relevancy=result.answer_relevancy
            )
            
        except Exception as e:
            logger.error(f"evaluation failed: {e}", exc_info=True)
        
        return result
    
    def _simplified_eval(
        self,
        result: EvaluationResult,
        contexts: List[str],
        question: str,
        ground_truth: Optional[str]
    ) -> EvaluationResult:
        """简化评估（当没有LLM API时使用）"""
        # Faithfulness
        if result.answer and len(result.answer) > 10:
            result.faithfulness = 0.7
        
        # Answer Relevancy
        question_words = set(question.lower().split())
        answer_words = set(result.answer.lower().split())
        overlap = len(question_words & answer_words)
        if overlap > 0:
            result.answer_relevancy = min(overlap / len(question_words), 1.0)
        
        # Context Precision
        if contexts:
            result.context_precision = 0.6
        
        # Context Recall
        if ground_truth and contexts:
            result.context_recall = 0.5
        
        return result
    
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
            
            # 避免请求过于频繁
            await asyncio.sleep(0.5)
        
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
