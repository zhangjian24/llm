"""
快速检查 Pinecone 配置 - 直接读取 .env.local 文件
"""
from pathlib import Path

print("=" * 80)
print("Pinecone 配置快速检查")
print("=" * 80)

# 1. 读取 .env.local 文件
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

if not env_file:
    print(f"\n❌ .env.local 文件不存在")
    print(f"💡 请复制 .env.example 并修改")
else:
    print(f"\n✅ .env.local 文件存在")
    
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 2. 提取 Pinecone 配置
    print("\n📋 Pinecone 配置:")
    
    pinecone_lines = []
    for line in content.split('\n'):
        if 'PINECONE_' in line and not line.strip().startswith('#'):
            pinecone_lines.append(line)
    
    if pinecone_lines:
        for line in pinecone_lines:
            print(f"   {line}")
    else:
        print(f"   ⚠️  未找到 PINECONE_ 相关配置")
    
    # 3. 检查关键字段
    has_api_key = 'PINECONE_API_KEY=' in content and len([l for l in content.split('\n') if 'PINECONE_API_KEY=' in l and '=' in l and l.split('=')[1].strip()]) > 0
    has_index_name = 'PINECONE_INDEX_NAME=' in content
    
    print(f"\n✅ 配置检查:")
    print(f"   - PINECONE_API_KEY: {'✅ 已配置' if has_api_key else '❌ 未配置'}")
    print(f"   - PINECONE_INDEX_NAME: {'✅ 已配置' if has_index_name else '❌ 未配置'}")
    
    # 4. 提取实际值（去除等号后的内容）
    api_key_line = [l for l in content.split('\n') if 'PINECONE_API_KEY=' in l and not l.startswith('#')]
    if api_key_line:
        api_key_value = api_key_line[0].split('=', 1)[1].strip()
        if api_key_value:
            print(f"\n✅ API Key 格式正确：{api_key_value[:15]}... (长度：{len(api_key_value)})")
        else:
            print(f"\n❌ API Key 值为空，请填写")

print("\n" + "=" * 80)
