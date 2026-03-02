@echo off
title 文档问答系统启动器

echo 🚀 启动文档问答系统...

REM 检查目录结构
if not exist "backend" (
    echo ❌ 错误: 请在项目根目录运行此脚本
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ❌ 错误: 请在项目根目录运行此脚本
    pause
    exit /b 1
)

REM 启动后端服务
echo 🔧 启动后端服务...
cd backend

REM 检查虚拟环境
if not exist "venv" (
    echo 📦 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo 📥 安装后端依赖...
pip install -r requirements.txt

REM 检查环境变量文件
if not exist ".env" (
    echo ⚠️  请先配置 .env 文件
    copy .env.example .env
    echo 📝 已创建 .env 文件，请编辑填入实际的API密钥
    pause
    exit /b 1
)

REM 启动后端服务
echo 🏃 后端服务启动中...
start "后端服务" /min cmd /c "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 & pause"

cd ..

REM 启动前端服务
echo 🎨 启动前端服务...
cd frontend

REM 检查依赖
if not exist "node_modules" (
    echo 📦 安装前端依赖...
    npm install
)

REM 启动前端服务
echo 🏃 前端服务启动中...
start "前端服务" /min cmd /c "npm run dev & pause"

cd ..

echo ✅ 服务启动完成!
echo 🌐 前端地址: http://localhost:3000
echo 🔌 后端地址: http://localhost:8000
echo 📚 API文档: http://localhost:8000/docs
echo.
echo 📌 请手动关闭两个命令窗口来停止服务
echo 📌 或者按任意键退出此脚本（服务将继续运行）

pause