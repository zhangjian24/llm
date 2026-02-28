@echo off
echo 正在启动文档问答系统...

REM 检查Docker是否运行
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Docker未运行，请先启动Docker Desktop
    pause
    exit /b 1
)

REM 检查.env文件
if not exist ".env" (
    echo 警告: .env文件不存在，正在复制示例文件...
    copy backend\.env.example .env
    echo 请编辑.env文件并填入正确的配置信息
    pause
    exit /b 1
)

REM 构建并启动服务
echo 正在构建Docker镜像...
docker-compose build

echo 正在启动服务...
docker-compose up -d

echo.
echo 系统启动中...
timeout /t 10 /nobreak >nul

echo.
echo 服务状态:
docker-compose ps

echo.
echo 访问地址:
echo 前端界面: http://localhost:3000
echo 后端API: http://localhost:8000
echo API文档: http://localhost:8000/docs

echo.
echo 日志查看命令:
echo docker-compose logs -f

pause