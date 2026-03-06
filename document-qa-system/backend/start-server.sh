#!/bin/bash
# 后端服务启动脚本 (Linux/Mac)

echo "========================================"
echo " RAG Document QA System - Backend"
echo "========================================"
echo ""

# 设置脚本目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "[1/5] 检查 Python 环境..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Python 环境：$PYTHON_VERSION"
else
    echo "✗ 错误：未找到 Python 环境，请先安装 Python 3.9+"
    exit 1
fi

echo ""
echo "[2/5] 检查虚拟环境..."
if [ -d ".venv" ]; then
    echo "✓ 检测到虚拟环境，正在激活..."
    source .venv/bin/activate
else
    echo "! 未检测到虚拟环境，建议创建："
    echo "  python3 -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  pip install -r requirements.txt"
fi

echo ""
echo "[3/5] 检查依赖包..."
if pip show fastapi &> /dev/null; then
    FASTAPI_VERSION=$(pip show fastapi | grep Version | cut -d' ' -f2)
    echo "✓ FastAPI 版本：$FASTAPI_VERSION"
else
    echo "✗ 警告：FastAPI 未安装，请运行：pip install -r requirements.txt"
fi

echo ""
echo "[4/5] 检查环境配置..."
if [ -f ".env.local" ]; then
    echo "✓ 检测到 .env.local 配置文件"
    
    # 检查关键配置
    if grep -q "PINECONE_API_KEY=your-pinecone-api-key" .env.local || ! grep -q "PINECONE_API_KEY=" .env.local; then
        echo "! 警告：Pinecone API Key 未配置，请在 .env.local 中设置 PINECONE_API_KEY"
    else
        echo "✓ Pinecone API Key 已配置"
    fi
    
    if grep -q "DASHSCOPE_API_KEY=your-dashscope-api-key" .env.local || ! grep -q "DASHSCOPE_API_KEY=" .env.local; then
        echo "! 警告：DashScope API Key 未配置，请在 .env.local 中设置 DASHSCOPE_API_KEY"
    else
        echo "✓ DashScope API Key 已配置"
    fi
else
    echo "! 未检测到 .env.local 文件"
    echo "  请复制 .env.example 为 .env.local 并配置必要的环境变量"
    echo "  cp .env.example .env.local"
fi

echo ""
echo "[5/5] 启动 FastAPI服务..."
echo ""

# 读取配置
HOST_ADDR="0.0.0.0"
PORT="8000"

if [ -f ".env.local" ]; then
    HOST_ADDR=$(grep "^HOST=" .env.local | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    PORT=$(grep "^PORT=" .env.local | cut -d'=' -f2 | tr -d '"' | tr -d "'")
fi

echo "  监听地址：http://$HOST_ADDR:$PORT"
echo "  文档地址：http://$HOST_ADDR:$PORT/docs"
echo "  健康检查：http://$HOST_ADDR:$PORT/health"
echo ""
echo "按 Ctrl+C 停止服务"
echo "========================================"
echo ""

# 启动服务
uvicorn app.main:app --host "$HOST_ADDR" --port "$PORT" --reload --env-file .env.local
