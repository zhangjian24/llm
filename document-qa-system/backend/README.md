# 快速启动指南

## 首次启动

### 1. 配置环境变量

```powershell
# Windows (PowerShell)
cp .env.example .env.local
```

编辑 `.env.local` 文件，填入必要的配置：

```bash
# 必需配置
PINECONE_API_KEY=your-pinecone-api-key
DASHSCOPE_API_KEY=your-dashscope-api-key

# 可选配置（使用默认值即可）
PORT=8000
LOG_LEVEL=INFO
```

### 2. 安装依赖

```powershell
# 创建虚拟环境（推荐）
python -m venv .venv

# 激活虚拟环境
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 启动服务

#### Windows (PowerShell)

```powershell
.\start-server.ps1
```

#### Linux/Mac (Bash)

```bash
chmod +x start-server.sh
./start-server.sh
```

#### 直接启动（不使用脚本）

```powershell
# 开发模式（支持热重载）
uvicorn app.main:app --reload --env-file .env.local

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 验证服务

服务启动后，访问以下地址：

- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **ReDoc 文档**: http://localhost:8000/redoc

---

## 常见问题

### 1. 端口被占用

**错误**: `OSError: [Errno 48] Address already in use`

**解决方案**:

```powershell
# Windows - 查找占用端口的进程
netstat -ano | findstr :8000

# 终止进程（替换 PID）
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

或在 `.env.local` 中修改端口：
```bash
PORT=8001
```

### 2. API Key 未配置

**警告**: `Pinecone API Key 未配置`

**解决方案**: 
确保 `.env.local` 文件中配置了正确的 API Key：
```bash
PINECONE_API_KEY=pc_xxxxxxxxxxxx
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxx
```

### 3. 数据库连接失败

**错误**: `sqlalchemy.exc.OperationalError`

**解决方案**:

- **PostgreSQL**: 确保数据库服务已启动，连接字符串正确
- **SQLite**: 使用简化配置，在 `.env.local` 中设置：
  ```bash
  DATABASE_URL=sqlite+aiosqlite:///./rag_qa.db
  ```

### 4. 虚拟环境问题

**错误**: `ModuleNotFoundError: No module named 'fastapi'`

**解决方案**:
```powershell
# 重新创建虚拟环境
rm -r .venv
python -m venv .venv

# 激活并安装
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 开发模式

### 热重载开发

```powershell
.\start-server.ps1
```

脚本会自动检测代码变化并重启服务。

### 查看日志

日志输出格式（JSON）：
```json
{
  "level": "info",
  "event": "server_started",
  "host": "0.0.0.0",
  "port": 8000,
  "timestamp": "2026-03-05T14:30:00.000Z"
}
```

### 调试模式

在 `.env.local` 中设置：
```bash
DEBUG=True
LOG_LEVEL=DEBUG
```

---

## 生产部署

### Docker 部署

```bash
# 构建镜像
docker build -t rag-backend .

# 运行容器
docker run -d \
  -p 8000:8000 \
  -e PINECONE_API_KEY=your-key \
  -e DASHSCOPE_API_KEY=your-key \
  --name rag-backend \
  rag-backend
```

### 多进程部署

```bash
# 使用 gunicorn 管理多个 worker
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

---

## 环境变量说明

| 变量名 | 必填 | 说明 | 默认值 |
|--------|------|------|--------|
| `PINECONE_API_KEY` | ✅ | Pinecone 向量数据库 API Key | - |
| `DASHSCOPE_API_KEY` | ✅ | 阿里云百炼 API Key | - |
| `DATABASE_URL` | ⚠️ | 数据库连接 URL | SQLite（开发） |
| `PORT` | ❌ | 服务监听端口 | 8000 |
| `HOST` | ❌ | 服务监听地址 | 0.0.0.0 |
| `DEBUG` | ❌ | 调试模式 | False |
| `LOG_LEVEL` | ❌ | 日志级别 | INFO |
| `CHUNK_SIZE` | ❌ | 文本分块大小 | 800 |
| `MAX_FILE_SIZE` | ❌ | 最大上传文件大小 | 50MB |

---

## 相关文档

- [API 使用指南](../docs/api_guide.md)
- [数据库初始化](../scripts/init_db.sql)
- [部署文档](../docs/deployment.md)
