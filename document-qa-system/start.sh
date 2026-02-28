#!/bin/bash

echo "正在启动文档问答系统..."

# 检查Docker是否运行
if ! docker info >/dev/null 2>&1; then
    echo "错误: Docker未运行，请先启动Docker"
    exit 1
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "警告: .env文件不存在，正在复制示例文件..."
    cp backend/.env.example .env
    echo "请编辑.env文件并填入正确的配置信息"
    exit 1
fi

# 构建并启动服务
echo "正在构建Docker镜像..."
docker-compose build

echo "正在启动服务..."
docker-compose up -d

echo ""
echo "系统启动中..."
sleep 10

echo ""
echo "服务状态:"
docker-compose ps

echo ""
echo "访问地址:"
echo "前端界面: http://localhost:3000"
echo "后端API: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"

echo ""
echo "日志查看命令:"
echo "docker-compose logs -f"