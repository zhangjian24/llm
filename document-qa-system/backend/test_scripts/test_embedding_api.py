"""
测试 Embedding API
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.embedding_service import EmbeddingService


async def test_embedding_api():
    """测试 Embedding API 是否正常工作"""
    print("="*60)
    print("Testing Embedding API")
    print("="*60)
    
    embedding_svc = EmbeddingService()
    
    # 测试文本
    test_texts = [
        "什么是人工智能？",
        "机器学习有哪些类型？",
        "环境保护很重要"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n[{i}/{len(test_texts)}] Testing: {text}")
        
        try:
            vector = await embedding_svc.embed_text(text)
            
            print(f"   Status: SUCCESS")
            print(f"   Vector dimension: {len(vector)}")
            print(f"   Vector sample (first 5 values): {vector[:5]}")
            print(f"   Vector type: {type(vector)}")
            
            # 验证向量质量
            magnitude = sum(x**2 for x in vector) ** 0.5
            print(f"   Vector magnitude: {magnitude:.4f}")
            
        except Exception as e:
            print(f"   Status: FAILED")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("Embedding API Test Completed")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_embedding_api())
