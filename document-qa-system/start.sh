#!/bin/bash

# 文档问答系统一键启动脚本

echo "🚀 启动文档问答系统..."

# 检查是否在正确的目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 启动后端服务
echo "🔧 启动后端服务..."
cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📥 安装后端依赖..."
pip install -r requirements.txt

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "⚠️  请先配置 .env 文件"
    cp .env.example .env
    echo "📝 已创建 .env 文件，请编辑填入实际的API密钥"
    exit 1
fi

# 在后台启动后端
echo "🏃 后端服务启动中..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd ..

# 启动前端服务
echo "🎨 启动前端服务..."
cd frontend

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

# 在后台启动前端
echo "🏃 前端服务启动中..."
npm run dev &
FRONTEND_PID=$!

cd ..

echo "✅ 服务启动完成!"
echo "🌐 前端地址: http://localhost:3000"
echo "🔌 后端地址: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo ""
echo "📌 按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# 保持脚本运行
while true; do
    sleep 1
done