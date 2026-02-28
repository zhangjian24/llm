#!/usr/bin/env python3
"""
文档问答系统验证脚本
用于验证系统各组件是否正常工作
"""

import requests
import time
import sys
from pathlib import Path

def check_service(url, service_name):
    """检查服务是否正常运行"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {service_name} 服务正常")
            return True
        else:
            print(f"❌ {service_name} 服务异常 (状态码: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {service_name} 服务不可达: {str(e)}")
        return False

def check_backend():
    """检查后端服务"""
    print("检查后端服务...")
    return check_service("http://localhost:8000", "后端API")

def check_frontend():
    """检查前端服务"""
    print("检查前端服务...")
    return check_service("http://localhost:3000", "前端界面")

def check_health_endpoint():
    """检查健康检查端点"""
    print("检查健康检查端点...")
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ 健康检查通过 - 状态: {health_data.get('status', 'unknown')}")
            services = health_data.get('services', {})
            for service, status in services.items():
                status_icon = "✅" if status == "healthy" else "❌"
                print(f"   {status_icon} {service}: {status}")
            return True
        else:
            print(f"❌ 健康检查失败 (状态码: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {str(e)}")
        return False

def check_ollama():
    """检查Ollama服务"""
    print("检查Ollama服务...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            if models:
                print(f"✅ Ollama服务正常，已加载模型: {[m['name'] for m in models]}")
                return True
            else:
                print("⚠️  Ollama服务正常但未加载模型")
                return True
        else:
            print(f"❌ Ollama服务异常 (状态码: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Ollama服务不可达: {str(e)}")
        return False

def main():
    print("=" * 50)
    print("文档问答系统验证脚本")
    print("=" * 50)
    
    checks = [
        ("后端服务", check_backend),
        ("前端服务", check_frontend), 
        ("健康检查", check_health_endpoint),
        ("Ollama服务", check_ollama)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n--- {name} ---")
        result = check_func()
        results.append((name, result))
        time.sleep(1)  # 避免请求过于频繁
    
    print("\n" + "=" * 50)
    print("验证结果汇总:")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} {name}")
    
    print(f"\n总体结果: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("\n🎉 系统验证成功！所有服务正常运行。")
        print("\n访问地址:")
        print("- 前端界面: http://localhost:3000")
        print("- API文档: http://localhost:8000/docs")
        print("- 健康检查: http://localhost:8000/api/health")
        return 0
    else:
        print(f"\n⚠️  系统验证发现问题，{total-passed} 项检查失败。")
        print("请检查相关服务的日志信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())