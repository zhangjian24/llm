"""
Pinecone Service 验证测试（简化版 - 无 emoji）
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.pinecone_service import PineconeService
from app.exceptions import RetrievalException


async def test_pinecone_service():
    """完整的 Pinecone 服务测试"""
    
    print("="*80)
    print("Pinecone Service (SDK v8+) Verification Test")
    print("="*80)
    
    results = []
    
    # Test 1: Initialization
    print("\n[TEST 1] Pinecone Client Initialization")
    try:
        service = PineconeService()
        print(f"[PASS] Initialized successfully")
        print(f"  - Index Name: {service.index_name}")
        print(f"  - Dimension: {service.dimension}")
        results.append(("Initialization", True))
    except Exception as e:
        print(f"[FAIL] {e}")
        return False
    
    # Test 2: List Indexes
    print("\n[TEST 2] List All Indexes")
    try:
        indexes = service.pc.list_indexes()
        index_names = [idx.name for idx in indexes]
        print(f"[PASS] Found {len(index_names)} index(es): {', '.join(index_names)}")
        results.append(("List Indexes", True))
    except Exception as e:
        print(f"[FAIL] {e}")
        results.append(("List Indexes", False))
    
    # Test 3: Create Index
    print("\n[TEST 3] Create Index (if not exists)")
    try:
        await service.create_index_if_not_exists()
        print(f"[PASS] Index ready")
        results.append(("Create Index", True))
    except Exception as e:
        print(f"[FAIL] {e}")
        results.append(("Create Index", False))
    
    # Wait for index to be ready
    print("\nWaiting for index to be ready...")
    await asyncio.sleep(3)
    
    # Test 4: Get Stats
    print("\n[TEST 4] Get Index Statistics")
    try:
        stats = await service.get_index_stats()
        if "error" in stats:
            print(f"[WARN] Error: {stats['error']}")
            results.append(("Get Stats", False))
        else:
            total_vectors = stats.get('total_vector_count', 0)
            print(f"[PASS] Total vectors: {total_vectors}")
            results.append(("Get Stats", True))
    except Exception as e:
        print(f"[FAIL] {e}")
        results.append(("Get Stats", False))
    
    # Test 5: Upsert Vectors
    print("\n[TEST 5] Insert Test Vectors")
    try:
        test_vectors = [
            {
                "id": f"test_{i}",
                "values": [0.1] * service.dimension,
                "metadata": {"content": f"Test chunk {i}"}
            }
            for i in range(3)
        ]
        await service.upsert_vectors(test_vectors, namespace="test")
        print(f"[PASS] Inserted {len(test_vectors)} vectors")
        results.append(("Upsert Vectors", True))
    except Exception as e:
        print(f"[FAIL] {e}")
        results.append(("Upsert Vectors", False))
    
    # Wait for indexing
    await asyncio.sleep(2)
    
    # Test 6: Similarity Search
    print("\n[TEST 6] Similarity Search")
    try:
        query_vector = [0.1] * service.dimension
        results_search = await service.similarity_search(
            query_vector=query_vector,
            top_k=3,
            include_metadata=True
        )
        print(f"[PASS] Found {len(results_search)} matches")
        results.append(("Similarity Search", True))
    except Exception as e:
        print(f"[FAIL] {e}")
        results.append(("Similarity Search", False))
    
    # Test 7: Delete Vectors
    print("\n[TEST 7] Delete Test Vectors")
    try:
        await service.delete_vectors(ids=["test_0", "test_1", "test_2"], namespace="test")
        print(f"[PASS] Deleted 3 vectors")
        results.append(("Delete Vectors", True))
    except Exception as e:
        print(f"[FAIL] {e}")
        results.append(("Delete Vectors", False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"  [{status}] {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print(f"Pass Rate: {passed/total*100:.1f}%")
    
    print("\n" + "="*80)
    if passed == total:
        print("CONCLUSION: ALL TESTS PASSED!")
    elif passed >= total * 0.8:
        print("CONCLUSION: MOST TESTS PASSED")
    else:
        print("CONCLUSION: MULTIPLE FAILURES DETECTED")
    print("="*80)
    
    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(test_pinecone_service())
        exit(0 if success else 1)
    except Exception as e:
        print(f"\nTest execution error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
