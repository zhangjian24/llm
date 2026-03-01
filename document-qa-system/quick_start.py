#!/usr/bin/env python3
"""
快速启动脚本
检查环境配置并启动文档问答系统
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 9):
        print("❌ Python版本过低，需要Python 3.9或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    print(f"✅ Python版本检查通过: {sys.version.split()[0]}")
    return True

def check_environment_variables():
    """检查必要的环境变量"""
    required_vars = ['PINECONE_API_KEY', 'PINECONE_INDEX_NAME']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ 缺少必要的环境变量:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n请在 .env.local 文件中配置这些变量")
        return False
    
    print("✅ 环境变量检查通过")
    return True

def check_dependencies():
    """检查Python依赖"""
    try:
        import fastapi
        import pinecone
        import langchain
        print("✅ Python依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少Python依赖: {e}")
        print("请运行: pip install -r backend/requirements.txt")
        return False

def start_backend():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    try:
        # 切换到后端目录
        backend_dir = Path("backend")
        if not backend_dir.exists():
            print("❌ 找不到backend目录")
            return False
            
        os.chdir(backend_dir)
        
        # 启动FastAPI应用
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", "--host", "0.0.0.0", "--port", "8000"
        ])
        
        print("✅ 后端服务启动成功")
        print("🌐 API文档: http://localhost:8000/docs")
        return process
        
    except Exception as e:
        print(f"❌ 后端服务启动失败: {e}")
        return None

def start_frontend():
    """启动前端服务"""
    print("🎨 启动前端服务...")
    try:
        # 切换到前端目录
        frontend_dir = Path("frontend")
        if not frontend_dir.exists():
            print("❌ 找不到frontend目录")
            return False
            
        os.chdir(frontend_dir)
        
        # 检查pnpm是否可用
        try:
            subprocess.run(["pnpm", "--version"], check=True, capture_output=True)
            cmd = ["pnpm", "run", "dev"]
        except (subprocess.CalledProcessError, FileNotFoundError):
            # 使用npm作为备选
            cmd = ["npm", "run", "dev"]
        
        process = subprocess.Popen(cmd)
        
        print("✅ 前端服务启动成功")
        print("🌐 前端地址: http://localhost:3000")
        return process
        
    except Exception as e:
        print(f"❌ 前端服务启动失败: {e}")
        return None

def main():
    """主函数"""
    print("=" * 60)
    print("📚 文档问答系统快速启动脚本")
    print("=" * 60)
    
    # 加载环境变量
    env_file = Path(".env.local")
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print("✅ 环境变量加载成功")
    else:
        print("⚠️  未找到 .env.local 文件，请确保已正确配置环境变量")
    
    # 执行检查
    checks = [
        check_python_version(),
        check_environment_variables(),
        check_dependencies()
    ]
    
    if not all(checks):
        print("\n❌ 环境检查未通过，请解决上述问题后重试")
        return
    
    print("\n✅ 所有检查通过，准备启动服务...")
    print("-" * 60)
    
    # 启动服务
    backend_process = start_backend()
    time.sleep(3)  # 等待后端启动
    
    frontend_process = start_frontend()
    
    if backend_process and frontend_process:
        print("\n" + "=" * 60)
        print("🎉 系统启动成功！")
        print("=" * 60)
        print("📋 访问地址:")
        print("   前端界面: http://localhost:3000")
        print("   API文档:  http://localhost:8000/docs")
        print("   健康检查: http://localhost:8000/api/health")
        print("\n💡 提示:")
        print("   - 按 Ctrl+C 停止所有服务")
        print("   - 首次使用请先上传文档")
        print("   - 确保已配置有效的API密钥以获得最佳体验")
        print("=" * 60)
        
        try:
            # 等待用户中断
            backend_process.wait()
            frontend_process.wait()
        except KeyboardInterrupt:
            print("\n\n🛑 正在停止服务...")
            backend_process.terminate()
            frontend_process.terminate()
            print("✅ 服务已停止")
    else:
        print("\n❌ 服务启动失败")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()

if __name__ == "__main__":
    main()