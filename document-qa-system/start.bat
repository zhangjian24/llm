@echo off
title 文档问答系统启动器

echo 🚀 启动文档问答系统

REM 检查环境变量文件
if not exist "backend\.env" (
    echo ❌ 请先创建 backend\.env 文件并配置必要参数
    echo 📋 参考 backend\.env.example 文件
    pause
    exit /b 1
)

REM 构建并启动服务
echo 🏗️  构建Docker镜像...
docker-compose up --build -d

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo 🔍 检查服务状态...
docker-compose ps

echo ✅ 系统启动完成！
echo 🌐 前端访问地址: http://localhost:3000
echo 🔧 后端API地址: http://localhost:8000
echo 📚 API文档地址: http://localhost:8000/docs

pause