"""
RAG 系统精度/召回率测试

测试不同查询下的检索质量，计算：
- Precision@K: 前 K 个结果中相关的比例
- Recall@K: 检索到的相关文档占所有相关文档的比例
- NDCG@K: 归一化折损累计增益（考虑排序质量）
"""
import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Set
from dataclasses import dataclass

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import get_db_session
from app.services.embedding_service import EmbeddingService
from sqlalchemy import text


@dataclass
class QueryGroundTruth:
    """查询的真实标签"""
    query: str
    relevant_keywords: Set[str]  # 相关 chunk 的关键词集合


@dataclass
class SearchResult:
    """搜索结果"""
    chunk_id: str
    content: str
    distance: float


async def create_test_dataset():
    """创建测试数据集"""
    print("="*60)
    print("Step 1: 创建测试数据集")
    print("="*60)
    
    async for session in get_db_session():
        try:
            # 清理旧数据
            await session.execute(text("TRUNCATE TABLE chunks, documents CASCADE"))
            await session.commit()
            
            # 创建多个主题的测试文档
            test_docs = [
                {
                    "filename": "ai_basics.txt",
                    "content": """人工智能是计算机科学的重要分支。机器学习是 AI 的核心技术，包括监督学习、无监督学习和强化学习。深度学习使用神经网络，如 CNN 和 RNN。Transformer 架构是现代大语言模型的基础。""".encode('utf-8'),
                    "chunks": [
                        "人工智能是计算机科学的重要分支，致力于模拟人类智能。",
                        "机器学习包括监督学习、无监督学习和强化学习三种主要类型。",
                        "深度学习使用多层神经网络，包括 CNN、RNN 和 Transformer。"
                    ]
                },
                {
                    "filename": "environment.txt",
                    "content": """环境保护非常重要。气候变化是全球性挑战。减少碳排放、发展可再生能源是关键措施。垃圾分类和资源回收有助于可持续发展。""".encode('utf-8'),
                    "chunks": [
                        "环境保护对地球生态系统的健康至关重要。",
                        "气候变化导致全球气温上升，需要减少碳排放。",
                        "可再生能源如太阳能和风能是未来的发展方向。"
                    ]
                },
                {
                    "filename": "history.txt",
                    "content": """中国有五千年的文明历史。唐朝是中国古代最繁荣的朝代之一。丝绸之路促进了东西方文化交流。四大发明对世界文明产生深远影响。""".encode('utf-8'),
                    "chunks": [
                        "中国文明历史源远流长，有五千年的历史。",
                        "唐朝时期经济文化繁荣，是古代中国的黄金时代。",
                        "丝绸之路连接东西方，促进了贸易和文化交流。"
                    ]
                }
            ]
            
            import hashlib
            import uuid
            from datetime import datetime
            
            all_chunks = []
            
            for doc in test_docs:
                doc_id = uuid.uuid4()
                content_hash = hashlib.sha256(doc["content"]).hexdigest()
                
                # 插入文档
                await session.execute(text("""
                    INSERT INTO documents (id, filename, file_content, content_hash, file_size, mime_type, status)
                    VALUES (:id, :filename, :content, :hash, :size, :mime, :status)
                """), {
                    'id': str(doc_id),
                    'filename': doc['filename'],
                    'content': doc['content'],
                    'hash': content_hash,
                    'size': len(doc['content']),
                    'mime': 'text/plain',
                    'status': 'ready'
                })
                
                # 插入分块
                for idx, chunk_content in enumerate(doc["chunks"]):
                    chunk_id = uuid.uuid4()
                    all_chunks.append({
                        'id': str(chunk_id),
                        'document_id': str(doc_id),
                        'chunk_index': idx,
                        'content': chunk_content,
                        'token_count': len(chunk_content) // 4  # 粗略估算
                    })
                    
                    await session.execute(text("""
                        INSERT INTO chunks (id, document_id, chunk_index, content, token_count)
                        VALUES (:id, :doc_id, :idx, :content, :tokens)
                    """), {
                        'id': str(chunk_id),
                        'doc_id': str(doc_id),
                        'idx': idx,
                        'content': chunk_content,
                        'tokens': len(chunk_content) // 4
                    })
            
            await session.commit()
            print(f"[OK] 创建了 {len(test_docs)} 个文档，共 {len(all_chunks)} 个分块\n")
            
            return all_chunks
            
        except Exception as e:
            print(f"[ERROR] 错误：{e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
            return []
        finally:
            await session.close()


async def vectorize_all_chunks():
    """向量化所有分块"""
    print("="*60)
    print("Step 2: 向量化所有分块")
    print("="*60)
    
    embedding_svc = EmbeddingService()
    
    async for session in get_db_session():
        try:
            # 获取所有未向量化的分块
            result = await session.execute(text("""
                SELECT id, content FROM chunks WHERE embedding IS NULL
            """))
            
            chunks = result.fetchall()
            print(f"需要向量化 {len(chunks)} 个分块...")
            
            for chunk in chunks:
                # 获取向量
                vector = await embedding_svc.embed_text(chunk.content)
                vector_str = '[' + ','.join([f'{x:.6f}' for x in vector]) + ']'
                
                # 更新数据库
                await session.execute(text("""
                    UPDATE chunks 
                    SET embedding = CAST(:vec AS VECTOR(1024))
                    WHERE id = :chunk_id
                """), {
                    'vec': vector_str,
                    'chunk_id': str(chunk.id)
                })
            
            await session.commit()
            print(f"[OK] 完成 {len(chunks)} 个分块的向量化\n")
            
        except Exception as e:
            print(f"[ERROR] 错误：{e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
        finally:
            await session.close()


def get_ground_truth_queries() -> List[QueryGroundTruth]:
    """定义测试查询和真实标签"""
    return [
        QueryGroundTruth(
            query="什么是人工智能？",
            relevant_keywords={"人工智能", "计算机科学", "模拟人类智能"}
        ),
        QueryGroundTruth(
            query="机器学习有哪些类型？",
            relevant_keywords={"机器学习", "监督学习", "无监督学习", "强化学习"}
        ),
        QueryGroundTruth(
            query="深度学习用什么技术？",
            relevant_keywords={"深度学习", "神经网络", "CNN", "RNN", "Transformer"}
        ),
        QueryGroundTruth(
            query="环境保护为什么重要？",
            relevant_keywords={"环境保护", "生态系统", "健康"}
        ),
        QueryGroundTruth(
            query="如何应对气候变化？",
            relevant_keywords={"气候变化", "减少碳排放", "气温上升"}
        ),
        QueryGroundTruth(
            query="中国历史有多久？",
            relevant_keywords={"中国历史", "五千年", "文明"}
        ),
        QueryGroundTruth(
            query="唐朝是什么样的朝代？",
            relevant_keywords={"唐朝", "经济文化繁荣", "黄金时代"}
        ),
        QueryGroundTruth(
            query="丝绸之路的作用？",
            relevant_keywords={"丝绸之路", "贸易", "文化交流", "东西方"}
        )
    ]


def is_relevant_result(result: SearchResult, relevant_keywords: Set[str]) -> bool:
    """判断结果是否相关（通过关键词匹配）"""
    content_lower = result.content.lower()
    return any(keyword.lower() in content_lower for keyword in relevant_keywords)


async def search_similar_documents(query: str, top_k: int = 3) -> List[SearchResult]:
    """搜索相似文档"""
    embedding_svc = EmbeddingService()
    
    async for session in get_db_session():
        try:
            # 获取查询向量
            query_vector = await embedding_svc.embed_text(query)
            query_vec_str = '[' + ','.join([f'{x:.6f}' for x in query_vector]) + ']'
            
            # 搜索
            result = await session.execute(text("""
                SELECT id, content, (embedding <=> CAST(:vec AS VECTOR(1024))) as distance
                FROM chunks
                WHERE embedding IS NOT NULL
                ORDER BY distance ASC
                LIMIT :limit
            """), {
                'vec': query_vec_str,
                'limit': top_k
            })
            
            rows = result.fetchall()
            return [
                SearchResult(
                    chunk_id=str(row.id),
                    content=str(row.content),
                    distance=float(row.distance)
                )
                for row in rows
            ]
            
        except Exception as e:
            print(f"❌ 搜索错误：{e}")
            return []
        finally:
            await session.close()


def calculate_precision_at_k(results: List[SearchResult], relevant_keywords: Set[str], k: int) -> float:
    """计算 Precision@K"""
    if not results or k <= 0:
        return 0.0
    
    top_k = results[:k]
    relevant_retrieved = sum(1 for r in top_k if is_relevant_result(r, relevant_keywords))
    return relevant_retrieved / len(top_k)


def calculate_recall_at_k(results: List[SearchResult], relevant_keywords: Set[str], total_relevant: int) -> float:
    """计算 Recall@K"""
    if not relevant_keywords or total_relevant == 0:
        return 0.0
    
    relevant_retrieved = sum(1 for r in results if is_relevant_result(r, relevant_keywords))
    return relevant_retrieved / total_relevant


def calculate_dcg_at_k(results: List[SearchResult], relevant_keywords: Set[str], k: int) -> float:
    """计算 DCG@K (Discounted Cumulative Gain)"""
    dcg = 0.0
    for i, result in enumerate(results[:k]):
        rel = 1.0 if is_relevant_result(result, relevant_keywords) else 0.0
        dcg += rel / (i + 1)  # 对数折损
    return dcg


def calculate_ndcg_at_k(results: List[SearchResult], relevant_keywords: Set[str], k: int, total_relevant: int) -> float:
    """计算 NDCG@K (Normalized DCG)"""
    dcg = calculate_dcg_at_k(results, relevant_keywords, k)
    
    # 理想情况下的 DCG (所有相关结果都排在前面)
    ideal_dcg = sum(1.0 / (i + 1) for i in range(min(k, total_relevant)))
    
    return dcg / ideal_dcg if ideal_dcg > 0 else 0.0


async def run_evaluation():
    """运行完整评估"""
    print("\n" + "="*60)
    print("Step 3: 运行精度/召回率评估")
    print("="*60 + "\n")
    
    queries = get_ground_truth_queries()
    metrics = {'precision': [], 'recall': [], 'ndcg': []}
    
    # 获取所有 chunks 用于计算 recall
    async for session in get_db_session():
        try:
            result = await session.execute(text("SELECT content FROM chunks"))
            all_chunks = [str(row.content) for row in result.fetchall()]
        finally:
            await session.close()
    
    for i, qgt in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] 查询：{qgt.query}")
        
        # 搜索
        results = await search_similar_documents(qgt.query, top_k=3)
        
        if not results:
            print(f"   [WARN] 未找到结果\n")
            continue
        
        # 计算这个查询的相关文档总数
        total_relevant = sum(1 for chunk in all_chunks if is_relevant_result(
            SearchResult(chunk_id="", content=chunk, distance=0.0), 
            qgt.relevant_keywords
        ))
        
        # 计算指标
        p1 = calculate_precision_at_k(results, qgt.relevant_keywords, k=1)
        p3 = calculate_precision_at_k(results, qgt.relevant_keywords, k=3)
        r3 = calculate_recall_at_k(results, qgt.relevant_keywords, total_relevant)
        ndcg3 = calculate_ndcg_at_k(results, qgt.relevant_keywords, k=3, total_relevant=total_relevant)
        
        metrics['precision'].append(p3)
        metrics['recall'].append(r3)
        metrics['ndcg'].append(ndcg3)
        
        # 显示结果
        print(f"   Top-1 结果：{results[0].content[:50]}... (距离：{results[0].distance:.4f})")
        print(f"   Precision@1: {p1:.2f}, Precision@3: {p3:.2f}")
        print(f"   Recall@3: {r3:.2f}, NDCG@3: {ndcg3:.2f}")
        
        is_relevant = is_relevant_result(results[0], qgt.relevant_keywords)
        print(f"   {'[OK] 相关' if is_relevant else '[FAIL] 不相关'}\n")
    
    # 汇总统计
    print("="*60)
    print("评估结果汇总")
    print("="*60)
    
    avg_precision = sum(metrics['precision']) / len(metrics['precision']) if metrics['precision'] else 0
    avg_recall = sum(metrics['recall']) / len(metrics['recall']) if metrics['recall'] else 0
    avg_ndcg = sum(metrics['ndcg']) / len(metrics['ndcg']) if metrics['ndcg'] else 0
    
    print(f"\n平均指标 (n={len(queries)}):")
    print(f"  Precision@3: {avg_precision:.4f} ({avg_precision*100:.1f}%)")
    print(f"  Recall@3:    {avg_recall:.4f} ({avg_recall*100:.1f}%)")
    print(f"  NDCG@3:      {avg_ndcg:.4f} ({avg_ndcg*100:.1f}%)")
    
    # 质量评级
    if avg_ndcg >= 0.8:
        quality = "优秀 (5星)"
    elif avg_ndcg >= 0.6:
        quality = "良好 (4 星)"
    elif avg_ndcg >= 0.4:
        quality = "中等 (3 星)"
    else:
        quality = "需改进 (2 星)"
    
    print(f"\n检索质量评级：{quality}")
    print("="*60)
    
    # 详细报告
    print("\n详细测试报告:")
    print("-"*60)
    print(f"测试查询数：{len(queries)}")
    print(f"平均 Precision@3: {avg_precision:.4f} ({avg_precision*100:.1f}%)")
    print(f"平均 Recall@3: {avg_recall:.4f} ({avg_recall*100:.1f}%)")
    print(f"平均 NDCG@3: {avg_ndcg:.4f} ({avg_ndcg*100:.1f}%)")
    
    if avg_ndcg >= 0.8:
        conclusion = "优秀 - 系统检索质量很高"
    elif avg_ndcg >= 0.6:
        conclusion = "良好 - 系统基本满足需求"
    elif avg_ndcg >= 0.4:
        conclusion = "中等 - 需要进一步优化"
    else:
        conclusion = "需改进 - 建议调整 embedding 或检索策略"
    
    print(f"\n结论：{conclusion}")
    print("="*60)


async def main():
    """主函数"""
    print("\n" + "="*60)
    print("RAG 系统精度/召回率测试")
    print("="*60 + "\n")
    
    # Step 1: 创建测试数据集
    await create_test_dataset()
    
    # Step 2: 向量化
    await vectorize_all_chunks()
    
    # Step 3: 评估
    await run_evaluation()
    
    print("\n[OK] 测试完成！\n")


if __name__ == "__main__":
    asyncio.run(main())
