"""
测试 Pydantic Settings 加载 - 显式指定.env 文件路径
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings

# 获取当前脚本所在目录
current_dir = Path(__file__).parent
env_file = current_dir / '.env.local'

print("=" * 80)
print("Pydantic Settings 加载测试")
print("=" * 80)
print(f"\n当前目录：{current_dir}")
print(f".env.local 路径：{env_file}")
print(f"文件存在：{env_file.exists()}")

if env_file.exists():
    print("\n✅ .env.local 文件存在，尝试加载...")
    
    # 方法 1: 使用 Config 类指定 env_file
    class Settings(BaseSettings):
        PINECONE_API_KEY: str = ""
        PINECONE_INDEX_NAME: str = "rag-documents"
        
        class Config:
            env_file = str(env_file)
            case_sensitive = True
    
    try:
        settings = Settings()
        print(f"\n✅ Settings 加载成功！")
        print(f"   PINECONE_API_KEY: {settings.PINECONE_API_KEY[:20]}...")
        print(f"   PINECONE_INDEX_NAME: {settings.PINECONE_INDEX_NAME}")
    except Exception as e:
        print(f"\n❌ Settings 加载失败：{e}")
        
    # 方法 2: 直接通过环境变量
    print("\n\n方法 2: 从.env.local 手动读取")
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            if 'PINECONE_' in line and not line.strip().startswith('#'):
                print(f"   {line.strip()}")
else:
    print("\n❌ .env.local 文件不存在")
