"""
验证 PINECONE_HOST 移除后的配置正确性
"""
import sys
sys.path.insert(0, '.')

print("=" * 80)
print("PINECONE_HOST 移除验证测试")
print("=" * 80)

# 1. 检查配置文件
print("\n1. 检查 config.py 中的 Settings 类:")
from app.core.config import get_settings

try:
    settings = get_settings()
    print(f"   ✅ Settings 加载成功")
    print(f"   - PINECONE_API_KEY: {'已配置' if settings.PINECONE_API_KEY else '❌ 未配置'}")
    print(f"   - PINECONE_INDEX_NAME: {settings.PINECONE_INDEX_NAME}")
    
    # 检查是否还有 PINECONE_HOST 属性
    if hasattr(settings, 'PINECONE_HOST'):
        print(f"   ⚠️  警告：Settings 仍包含 PINECONE_HOST 属性（应删除）")
    else:
        print(f"   ✅ PINECONE_HOST 已成功移除")
        
except Exception as e:
    print(f"   ❌ Settings 加载失败：{e}")

# 2. 检查 PineconeService
print("\n2. 检查 PineconeService 初始化:")
try:
    from app.services.pinecone_service import PineconeService
    
    # 创建实例（不会真正连接）
    service = PineconeService()
    
    print(f"   ✅ PineconeService 创建成功")
    print(f"   - api_key: {'已配置' if service.api_key else '❌ 未配置'}")
    print(f"   - index_name: {service.index_name}")
    print(f"   - dimension: {service.dimension}")
    
    # 检查是否有 host 属性
    if hasattr(service, 'host'):
        print(f"   ⚠️  警告：PineconeService 仍包含 host 属性（应删除）")
    else:
        print(f"   ✅ host 属性已成功移除")
        
except Exception as e:
    print(f"   ❌ PineconeService 创建失败：{e}")

# 3. 环境变量检查
print("\n3. 检查 .env.local 文件:")
import os
from pathlib import Path

# 尝试多个可能的位置
possible_paths = [
    Path('.env.local'),
    Path('backend/.env.local'),
    Path('../.env.local')
]

env_file = None
for path in possible_paths:
    if path.exists():
        env_file = path
        break

if env_file:
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    has_pinecone_host = 'PINECONE_HOST=' in content
    
    if has_pinecone_host:
        print(f"   ⚠️  警告：.env.local 仍包含 PINECONE_HOST 配置行")
    else:
        print(f"   ✅ .env.local 已移除 PINECONE_HOST")
        
    # 显示 Pinecone 相关配置
    print(f"\n   Pinecone 配置预览:")
    for line in content.split('\n'):
        if 'PINECONE_' in line and not line.strip().startswith('#'):
            print(f"     - {line.strip()}")
else:
    print(f"   ❌ .env.local 文件不存在")

# 4. 总结
print("\n" + "=" * 80)
print("验证总结")
print("=" * 80)

issues = []

# 检查 Settings
try:
    settings = get_settings()
    if hasattr(settings, 'PINECONE_HOST'):
        issues.append("Settings 类仍包含 PINECONE_HOST 属性")
except Exception as e:
    issues.append(f"Settings 加载失败：{e}")

# 检查 PineconeService
try:
    service = PineconeService()
    if hasattr(service, 'host'):
        issues.append("PineconeService 仍包含 host 属性")
except Exception as e:
    issues.append(f"PineconeService 创建失败：{e}")

# 检查 .env.local
if env_file.exists() and 'PINECONE_HOST=' in content:
    issues.append(".env.local 仍包含 PINECONE_HOST 配置")

if issues:
    print("❌ 发现问题:")
    for issue in issues:
        print(f"   - {issue}")
else:
    print("✅ 所有检查通过！PINECONE_HOST 已成功移除。")
    print("\n💡 下一步:")
    print("   1. 重启后端服务：python -m uvicorn app.main:app --reload")
    print("   2. 确保 PINECONE_API_KEY 有效")
    print("   3. 确保 Pinecone Index '{rag-documents-index}' 存在")
    print("   4. 运行 API测试验证功能")

print("=" * 80)
