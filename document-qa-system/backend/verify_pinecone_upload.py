"""
验证 Pinecone 上传和向量化状态
"""
import asyncio
from app.services.pinecone_service import PineconeService
from app.services.embedding_service import EmbeddingService

async def verify_upload():
    print("=" * 80)
    print("验证 Pinecone 上传和向量化状态")
    print("=" * 80)
    
    # 1. 初始化服务
    print("\n[1] 初始化服务...")
   pinecone_svc = PineconeService()
   embedding_svc = EmbeddingService()
    print("  ✓ 服务已初始化")
    
    # 2. 获取 Pinecone 索引统计
    print("\n[2] 获取 Pinecone 索引统计...")
   try:
      stats = await pinecone_svc.get_index_stats()
        total_count = stats.get('total_count', 0)
        print(f"  ✓ 索引中向量总数：{total_count}")
        
       if total_count> 0:
            print(f"  ✅ 成功！索引中有 {total_count} 个向量")
        else:
            print(f"  ⚠️  索引仍为空，文档可能还在处理中...")
            
    except Exception as e:
        print(f"  ❌ 获取统计失败：{e}")
       return
    
    # 3. 测试 Embedding
    print("\n[3] 测试 Embedding 服务...")
   try:
       test_text = "RAG system test"
        vector = await embedding_svc.embed_text(test_text)
        print(f"  ✓ Embedding 成功")
        print(f"  - 向量维度：{len(vector)}")
        print(f"  - 前 5 个值：{vector[:5]}")
    except Exception as e:
        print(f"  ❌ Embedding 失败：{e}")
       return
    
    # 4. 测试 Pinecone 检索
    print("\n[4] 测试 Pinecone 相似度搜索...")
   try:
      results = await pinecone_svc.similarity_search(vector, top_k=3)
        print(f"  ✓ 检索成功")
        print(f"  - 找到 {len(results)} 个结果")
        
       if results:
            print(f"\n  📊 检索结果详情:")
            for i, result in enumerate(results, 1):
               score = result.get('score', 'N/A')
                doc_id = result.get('id', 'N/A')
              metadata = result.get('metadata', {})
              content_preview = metadata.get('content', 'N/A')[:50]
                print(f"    [{i}] ID: {doc_id[:30]}..., Score: {score:.4f}")
                print(f"        Content: {content_preview}...")
        else:
            print(f"  ⚠️  未找到匹配结果（索引可能为空）")
            
    except Exception as e:
        print(f"  ❌ Pinecone 检索失败：{e}")
        import traceback
      traceback.print_exc()
       return
    
    # 5. 总结
    print("\n" + "=" * 80)
   if total_count> 0 and len(results) > 0:
        print("✅ Pinecone 向量化成功！系统已就绪！")
        print("\n下一步:")
        print("  1. 运行完整 API测试：python run_api_tests.py")
        print("  2. 测试 RAG 问答功能")
    else:
        print("⚠️  Pinecone 索引可能仍在处理中，请稍等片刻后重试")
        print("\n建议:")
        print("  1. 等待 10-30 秒")
        print("  2. 重新运行本脚本验证")
        print("  3. 或查看后端日志确认处理状态")
    print("=" * 80)

if __name__ == "__main__":
  asyncio.run(verify_upload())
