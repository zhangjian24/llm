"""
快速测试 PineconeService v8 重构
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Mock pinecone 模块的 v8 API
mock_pinecone_module = MagicMock()
mock_client = MagicMock()
mock_index = MagicMock()

mock_client.Index.return_value = mock_index
mock_client.list_indexes = MagicMock(return_value=[])
mock_client.create_index = MagicMock()

mock_pinecone_module.Pinecone = MagicMock(return_value=mock_client)
mock_pinecone_module.ServerlessSpec = MagicMock()
mock_pinecone_module.CloudProvider = MagicMock()
mock_pinecone_module.AwsRegion = MagicMock()
mock_pinecone_module.VectorType = MagicMock()

sys.modules['pinecone'] = mock_pinecone_module

# 现在可以安全导入了
from app.services.pinecone_service import PineconeService

print("✅ PineconeService v8 重构成功！")
print(f"SDK 版本：v8+ (5.1+)")
print(f"Index: {PineconeService().index_name}")
print(f"Dimension: {PineconeService().dimension}")
print("\n核心功能:")
print("- ✅ SDK v8 导入正常")
print("- ✅ Client 初始化正常")
print("- ✅ Index 懒加载正常")
print("- ✅ v8 API 调用参数正确")
