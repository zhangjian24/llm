"""
批量导入测试文档到向量数据库
"""
import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.chunkers.semantic_chunker import TextChunker
from app.services.embedding_service import EmbeddingService
from app.services.postgresql_vector_service import PostgreSQLVectorService
from app.services.vector_service_adapter import VectorServiceAdapter
from app.core.database import AsyncSessionLocal, Base
from sqlalchemy import text
from uuid import uuid4
import structlog

logger = structlog.get_logger()

ML_KNOWLEDGE = """
机器学习是人工智能的核心技术，主要分为监督学习、无监督学习和强化学习三种类型。

监督学习使用带标签的训练数据进行学习，常见算法包括线性回归、决策树、支持向量机等。监督学习适用于分类和回归任务。

无监督学习不需要标签数据，通过发现数据中的模式和结构进行学习。常见算法包括聚类、降维、关联规则等。

强化学习通过与环境交互，学习采取行动以最大化奖励。典型应用包括游戏AI、机器人控制等。

深度学习是机器学习的一个分支，使用多层神经网络进行特征学习和表示学习。

卷积神经网络(CNN)主要用于图像处理和计算机视觉任务，如图像分类、目标检测、语义分割等。

循环神经网络(RNN)主要用于序列数据处理，如自然语言处理和时间序列预测。长短期记忆网络(LSTM)是其重要变体。

Transformer模型改变了自然语言处理的格局，被广泛应用于机器翻译、文本生成、问答系统等任务。

注意力机制是Transformer的核心组件，允许模型在处理序列时关注最相关的部分。

大型语言模型(LLM)是在大规模文本数据上训练的深度学习模型，具有强大的语言理解和生成能力。

预训练和微调是训练大型语言模型的常用范式，可以在大量通用数据上预训练，然后在特定任务上微调。

提示工程(Prompt Engineering)是通过设计输入提示来引导语言模型产生期望输出的技术。

检索增强生成(RAG)结合了信息检索和文本生成，可以利用外部知识库来增强语言模型的回答质量。

向量数据库用于存储和检索高维向量表示，在RAG系统中用于高效的知识检索。

Embedding将文本转换为稠密向量表示，使得语义相似的内容在向量空间中接近。

HNSW是一种高效的向量索引算法，可以在大规模数据集上进行近实时检索。

混合搜索结合向量搜索和关键词搜索，可以同时捕获语义相关性和关键词匹配。

模型路由根据查询复杂度选择合适的模型，可以在质量和成本之间取得平衡。

缓存可以显著降低RAG系统的延迟和成本，特别是对于重复查询。

评估RAG系统需要考虑多个维度，包括准确性、延迟、成本和用户体验。
"""


async def main():
    print("=" * 60)
    print("批量导入测试文档")
    print("=" * 60)
    
    # 初始化服务
    chunker = TextChunker(chunk_size=600, overlap=200)
    embedding_svc = EmbeddingService()
    pg_svc = PostgreSQLVectorService()
    vector_svc = VectorServiceAdapter(pg_svc)
    
    # 分块
    print("\n[1/4] 分块中...")
    chunks = chunker.chunk_by_semantic(ML_KNOWLEDGE)
    print(f"  生成 {len(chunks)} 个chunks")
    
    # 生成向量
    print("\n[2/4] 生成向量中...")
    doc_id = str(uuid4())
    vectors = []
    for i, chunk in enumerate(chunks):
        print(f"  chunk {i+1}/{len(chunks)}: {chunk.content[:30]}...")
        vec = await embedding_svc.embed_text(chunk.content)
        vectors.append({
            "id": str(uuid4()),  # 新UUID确保插入新记录
            "values": vec,
            "metadata": {
                "document_id": doc_id,
                "chunk_index": i,
                "content": chunk.content,
                "token_count": chunk.token_count
            }
        })
    
    # 写入数据库
    print("\n[3/4] 写入向量数据库...")
    async with AsyncSessionLocal() as session:
        # 先创建document记录
        doc_id = str(uuid4())
        await session.execute(text("""
            INSERT INTO documents (id, filename, mime_type, file_size, status, created_at, updated_at)
            VALUES (:id, :filename, :mime_type, :file_size, :status, NOW(), NOW())
        """), {
            "id": doc_id,
            "filename": "ml_knowledge.txt",
            "mime_type": "text/plain",
            "file_size": 5000,
            "status": "completed"
        })
        
        # 再插入chunks
        for vec in vectors:
            await session.execute(text("""
                INSERT INTO chunks (id, document_id, chunk_index, content, token_count, embedding, metadata)
                VALUES (:id, :doc_id, :idx, :content, :token_count, :emb, :meta)
            """), {
                "id": vec["id"],
                "doc_id": doc_id,
                "idx": vec["metadata"]["chunk_index"],
                "content": vec["metadata"]["content"],
                "token_count": vec["metadata"]["token_count"],
                "emb": "[" + ",".join([str(x) for x in vec["values"]]) + "]",
                "meta": json.dumps(vec["metadata"])
            })
        await session.commit()
    
    print(f"  成功写入 {len(vectors)} 个向量")
    
    # 验证
    print("\n[4/4] 验证...")
    async with AsyncSessionLocal() as session:
        results = await vector_svc.similarity_search(
            await embedding_svc.embed_text("什么是机器学习"),
            top_k=5
        )
        print(f"  检索到 {len(results)} 个结果")
        for r in results:
            print(f"    - score: {r['score']:.3f}, content: {r.get('metadata', {}).get('content', '')[:40]}...")
    
    print("\n导入完成!")


if __name__ == "__main__":
    asyncio.run(main())
