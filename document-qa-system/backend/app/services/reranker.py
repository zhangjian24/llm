import requests
import json
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logging_config import logger
from app.core.exceptions import RerankError

class QwenReranker:
    """基于阿里巴巴云rerank-v3模型的重排序服务"""
    
    def __init__(self):
        self.api_key = settings.QWEN_API_KEY
        self.model = settings.QWEN_RERANK_MODEL
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/rerank"
        self.top_k = settings.RERANK_TOP_K
        self.score_threshold = settings.RERANK_SCORE_THRESHOLD
        
        # 请求头配置
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # 兼容旧版配置的降级机制
        self.use_legacy = not bool(self.api_key)
        if self.use_legacy:
            logger.warning("未配置QWEN_API_KEY，将使用传统排序方式")
    
    async def initialize(self):
        """初始化重排序服务"""
        try:
            if not self.use_legacy:
                # 验证API密钥有效性
                test_payload = {
                    "model": self.model,
                    "query": "测试查询",
                    "documents": ["测试文档"],
                    "top_n": 1
                }
                
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=test_payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    logger.info(f"Qwen重排序服务初始化成功: {self.model}")
                else:
                    logger.warning(f"Qwen重排序服务验证失败: {response.status_code}")
                    self.use_legacy = True
            else:
                logger.info("使用传统排序方式")
                
        except Exception as e:
            logger.error(f"重排序服务初始化失败: {str(e)}")
            self.use_legacy = True
    
    def rerank_documents(self, query: str, documents: List[Dict[str, Any]], 
                        top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """对文档进行重排序"""
        try:
            if self.use_legacy:
                return self._legacy_rerank(query, documents, top_k)
            
            # 准备文档内容列表
            doc_contents = []
            doc_metadata = []
            
            for doc in documents:
                if isinstance(doc, dict):
                    content = doc.get('content', doc.get('chunk_text', ''))
                    doc_contents.append(content)
                    doc_metadata.append({
                        'document_id': doc.get('document_id'),
                        'chunk_id': doc.get('chunk_id'),
                        'chunk_index': doc.get('chunk_index'),
                        'metadata': doc.get('metadata', {})
                    })
                elif isinstance(doc, str):
                    doc_contents.append(doc)
                    doc_metadata.append({})
                else:
                    doc_contents.append(str(doc))
                    doc_metadata.append({})
            
            if not doc_contents:
                return []
            
            # 构造API请求
            payload = {
                "model": self.model,
                "query": query,
                "documents": doc_contents,
                "top_n": top_k or self.top_k,
                "return_documents": True
            }
            
            # 发送请求
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"重排序API调用失败: {response.status_code} - {response.text}")
                return self._legacy_rerank(query, documents, top_k)
            
            result = response.json()
            
            # 解析结果
            reranked_docs = []
            if 'output' in result and 'results' in result['output']:
                for item in result['output']['results']:
                    if item.get('relevance_score', 0) >= self.score_threshold:
                        doc_idx = item.get('index', 0)
                        if doc_idx < len(doc_metadata):
                            reranked_doc = {
                                **doc_metadata[doc_idx],
                                'content': item.get('document', ''),
                                'score': item.get('relevance_score', 0),
                                'rank': len(reranked_docs) + 1
                            }
                            reranked_docs.append(reranked_doc)
            
            logger.info(f"重排序完成，返回 {len(reranked_docs)} 个文档")
            return reranked_docs
            
        except Exception as e:
            logger.error(f"重排序过程中发生错误: {str(e)}")
            return self._legacy_rerank(query, documents, top_k)
    
    def _legacy_rerank(self, query: str, documents: List[Dict[str, Any]], 
                      top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """传统的基于关键词匹配的排序方法（降级方案）"""
        try:
            # 简单的关键词匹配评分
            query_keywords = set(query.lower().split())
            
            scored_docs = []
            for doc in documents:
                content = ''
                if isinstance(doc, dict):
                    content = doc.get('content', doc.get('chunk_text', ''))
                elif isinstance(doc, str):
                    content = doc
                else:
                    content = str(doc)
                
                # 计算关键词匹配度
                content_lower = content.lower()
                matches = sum(1 for keyword in query_keywords if keyword in content_lower)
                score = matches / len(query_keywords) if query_keywords else 0
                
                if score >= 0.1:  # 最小阈值
                    scored_doc = doc.copy() if isinstance(doc, dict) else {'content': doc}
                    scored_doc['score'] = score
                    scored_docs.append(scored_doc)
            
            # 按分数排序
            scored_docs.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            # 应用top_k限制
            final_top_k = top_k or self.top_k
            return scored_docs[:final_top_k]
            
        except Exception as e:
            logger.error(f"传统排序失败: {str(e)}")
            return documents[:top_k or self.top_k]

# 创建全局实例
reranker_service = QwenReranker()