"""
测试修复后的向量搜索功能
验证 SQL 语法是否正确
"""

import asyncio
import sys
from pathlib import Path

# 修复导入路径
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(script_dir))

from app.services.vector_service_adapter import create_vector_service
from app.services.embedding_service import EmbeddingService


async def test_fixed_vector_search():
    """测试修复后的向量搜索功能"""
    print("🔍 测试修复后的向量搜索功能")
    print("=" * 50)
    
    try:
        # 创建服务实例
        vector_svc = create_vector_service({'vector_store_type': 'postgresql'})
        embedding_svc = EmbeddingService()
        
        print(f"✅ 服务创建成功: {vector_svc.service_type}")
        
        # 生成测试向量
        print("\n1. 生成测试向量...")
        test_text = "人工智能是计算机科学的一个重要分支"
        query_vector = await embedding_svc.embed_text(test_text)
        print(f"   ✅ 向量维度: {len(query_vector)}")
        
        # 执行相似度搜索
        print("\n2. 执行相似度搜索...")
        results = await vector_svc.similarity_search(
            query_vector=query_vector,
            top_k=3,
            include_metadata=True
        )
        
        print(f"   ✅ 搜索完成，返回 {len(results)} 个结果")
        
        # 显示结果
        if results:
            print("\n3. 搜索结果:")
            for i, result in enumerate(results):
                print(f"   [{i+1}] ID: {result.get('id', 'N/A')}")
                print(f"       相似度: {result.get('score', 0):.4f}")
                metadata = result.get('metadata', {})
                if metadata:
                    print(f"       文档ID: {metadata.get('document_id', 'N/A')}")
                    print(f"       内容预览: {metadata.get('content', 'N/A')[:50]}...")
        else:
            print("   ⚠️  未找到相关结果")
        
        print("\n" + "=" * 50)
        print("🎉 向量搜索测试通过!")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    success = await test_fixed_vector_search()
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)