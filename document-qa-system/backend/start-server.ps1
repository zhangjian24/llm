# 后端服务启动脚本
# 用于快速启动 FastAPI 后端服务

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " RAG Document QA System - Backend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 设置脚本目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "[1/5] 检查 Python 环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python 环境：$pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ 错误：未找到 Python 环境，请先安装 Python 3.9+" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/5] 检查虚拟环境..." -ForegroundColor Yellow
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "✓ 检测到虚拟环境，正在激活..." -ForegroundColor Green
    & ".\.venv\Scripts\Activate.ps1"
} else {
    Write-Host "! 未检测到虚拟环境，建议创建：" -ForegroundColor Yellow
    Write-Host "  python -m venv .venv" -ForegroundColor Gray
    Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[3/5] 检查依赖包..." -ForegroundColor Yellow
try {
    $fastapiVersion = pip show fastapi 2>&1 | Select-String "Version:" | ForEach-Object { ($_ -split ":")[1].Trim() }
    Write-Host "✓ FastAPI 版本：$fastapiVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ 警告：FastAPI 未安装，请运行：" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[4/5] 检查环境配置..." -ForegroundColor Yellow
if (Test-Path ".env.local") {
    Write-Host "✓ 检测到 .env.local 配置文件" -ForegroundColor Green
    
    # 检查关键配置
    $pineconeKey = Get-Content .env.local | Select-String "PINECONE_API_KEY" | ForEach-Object { ($_ -split "=")[1].Trim() }
    if ([string]::IsNullOrWhiteSpace($pineconeKey) -or $pineconeKey -eq "your-pinecone-api-key") {
        Write-Host "! 警告：Pinecone API Key 未配置，请在 .env.local 中设置 PINECONE_API_KEY" -ForegroundColor Yellow
    } else {
        Write-Host "✓ Pinecone API Key 已配置" -ForegroundColor Green
    }
    
    $dashscopeKey = Get-Content .env.local | Select-String "DASHSCOPE_API_KEY" | ForEach-Object { ($_ -split "=")[1].Trim() }
    if ([string]::IsNullOrWhiteSpace($dashscopeKey) -or $dashscopeKey -eq "your-dashscope-api-key") {
        Write-Host "! 警告：DashScope API Key 未配置，请在 .env.local 中设置 DASHSCOPE_API_KEY" -ForegroundColor Yellow
    } else {
        Write-Host "✓ DashScope API Key 已配置" -ForegroundColor Green
    }
} else {
    Write-Host "! 未检测到 .env.local 文件" -ForegroundColor Yellow
    Write-Host "  请复制 .env.example 为 .env.local 并配置必要的环境变量" -ForegroundColor Gray
    Write-Host "  cp .env.example .env.local" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[5/5] 启动 FastAPI服务..." -ForegroundColor Yellow
Write-Host ""

# 读取配置
$host_addr = if (Test-Path ".env.local") {
    (Get-Content .env.local | Select-String "^HOST=" | ForEach-Object { ($_ -split "=")[1].Trim() }) -replace '["'']', ''
} else {
    "0.0.0.0"
}

$port = if (Test-Path ".env.local") {
    (Get-Content .env.local | Select-String "^PORT=" | ForEach-Object { ($_ -split "=")[1].Trim() }) -replace '["'']', ''
} else {
    "8000"
}

Write-Host "  监听地址：http://$host_addr`:$port" -ForegroundColor Cyan
Write-Host "  文档地址：http://$host_addr`:$port/docs" -ForegroundColor Cyan
Write-Host "  健康检查：http://$host_addr`:$port/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 启动服务
try {
    uvicorn app.main:app --host $host_addr --port $port --reload --env-file .env.local
} catch {
    Write-Host ""
    Write-Host "✗ 服务启动失败：$_" -ForegroundColor Red
    Write-Host ""
    Write-Host "常见问题排查：" -ForegroundColor Yellow
    Write-Host "1. 检查端口 $port 是否被占用" -ForegroundColor Gray
    Write-Host "   netstat -ano | findstr :$port" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. 检查 .env.local 配置是否完整" -ForegroundColor Gray
    Write-Host "   至少需要配置：PINECONE_API_KEY, DASHSCOPE_API_KEY" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. 检查数据库连接是否正常" -ForegroundColor Gray
    Write-Host ""
    exit 1
}
