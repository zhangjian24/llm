"""
修复脚本导入路径问题
在 Windows 环境下正确设置 Python 模块搜索路径
"""

import sys
import os
from pathlib import Path

# 获取当前脚本所在目录
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent

# 将项目根目录和 backend 目录添加到 Python 路径
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(script_dir))

print(f"脚本目录: {script_dir}")
print(f"项目根目录: {project_root}")
print(f"Python 路径已更新")

# 现在可以安全导入模块
try:
    from app.core.config import get_settings
    print("✅ 模块导入成功")
    
    # 测试配置加载
    settings = get_settings()
    print(f"数据库URL: {settings.DATABASE_URL}")
    print(f"向量维度: {settings.VECTOR_DIMENSION}")
    
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请检查:")
    print("1. 是否在正确的项目目录下运行")
    print("2. backend 目录结构是否完整")
    print("3. 是否安装了所需依赖")
    
except Exception as e:
    print(f"❌ 配置加载失败: {e}")