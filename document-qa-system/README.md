# 文档问答系统 (Document QA System)

基于向量检索和上下文注入的智能文档问答系统。

## 核心特性

- 📄 多格式文档支持 (PDF, TXT, DOCX, HTML)
- 🧠 向量检索 (BGE嵌入模型 + Pinecone向量数据库)
- 💬 智能问答 (Ollama gpt-oss:20b大语言模型)
- 🔧 模块化架构 (LangChain框架)
- ⚡ FastAPI后端 + React前端
- 🐳 Docker容器化部署

## 技术栈

### 后端
- **框架**: FastAPI
- **向量处理**: LangChain
- **向量数据库**: Pinecone
- **嵌入模型**: BGE (基于Ollama)
- **大语言模型**: Ollama gpt-oss:20b

### 前端
- **框架**: React 18
- **样式**: TailwindCSS
- **构建工具**: Vite

## 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+
- pnpm (推荐) 或 npm
- Docker (可选)
- Ollama (用于本地BGE模型)

Ollama 下载模型（可选，也可使用远程Ollama服务）
```bash
ollama pull gpt-oss:20b
ollama pull bge-m3
```

### 启动方式

> **重要提醒**: 首次启动前请确保已配置有效的 Pinecone API 密钥

#### 方式一：一键启动脚本
```bash
# Windows
./start.bat

# Linux/Mac
./start.sh
```

#### 方式二：手动启动
```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端 (推荐使用 pnpm)
cd frontend
pnpm install
pnpm run dev

# 或使用 npm
cd frontend
npm install
npm run dev
```

#### 方式三：Docker部署
```bash
docker-compose up --build
```

## 配置说明

复制 `.env.example` 到 `.env` 并填写相应配置：

> **注意**: 系统已简化配置结构，移除了未使用的配置项，当前只需配置核心必需项。

```bash
# Pinecone配置 (需要有效的API密钥)
PINECONE_API_KEY=your_actual_pinecone_api_key_here
PINECONE_INDEX_NAME=document-qa-index

# Ollama配置 (已配置远程服务)
OLLAMA_BASE_URL=https://occurrence-pressure-implementing-rose.trycloudflare.com/
EMBEDDING_MODEL=bge-m3
LLM_MODEL=gpt-oss:20b
```

## 项目结构

```
document-qa-system/
├── backend/              # 后端服务
│   ├── app/
│   │   ├── api/         # API路由
│   │   ├── core/        # 核心配置
│   │   ├── models/      # 数据模型
│   │   ├── services/    # 业务服务
│   │   └── utils/       # 工具函数
│   └── requirements.txt
├── frontend/            # 前端应用
│   ├── src/
│   │   ├── components/  # React组件
│   │   ├── services/    # API服务
│   │   └── types/       # TypeScript类型
│   └── package.json
├── docker-compose.yml   # Docker编排
└── README.md
```

## API文档

启动后访问: http://localhost:8000/docs

主要接口：
- `POST /api/documents/upload` - 上传文档
- `POST /api/chat/query` - 问答查询
- `GET /api/documents/list` - 文档列表
- `DELETE /api/documents/{doc_id}` - 删除文档

## 开发指南

### 后端开发
```bash
cd backend
# 安装依赖
pip install -r requirements.txt

# 验证配置
python -c "from app.core.config import settings; print('配置加载成功')"

# 启动开发服务器
uvicorn app.main:app --reload --port 8000
```

### 前端开发
```bash
cd frontend
# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 故障排除

常见问题及解决方案：

1. **Pinecone API密钥错误**
   - 确保在 `.env` 文件中配置了有效的 Pinecone API 密钥
   - 检查密钥是否有足够的权限访问向量数据库

2. **Ollama连接失败**
   - 确认远程 Ollama 服务地址可访问
   - 如果使用本地 Ollama，确保服务已启动并在正确端口运行

3. **配置加载失败**
   - 检查 `.env` 文件是否存在且格式正确
   - 运行 `python -c "from app.core.config import settings; print('配置OK')"` 验证配置

## 部署

### 生产环境部署
```bash
# 使用生产环境docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

### 云部署
支持部署到各种云平台：
- AWS ECS
- Google Cloud Run
- Azure Container Instances
- 阿里云容器服务

## 技术更新记录

### Pinecone SDK 更新 (v5.3.0)

根据 Pinecone 官方最新 Python SDK 文档，系统已完成重要更新：

#### 主要变更
- **依赖包更新**: `pinecone-client==3.0.0` → `pinecone==5.3.0`
- **初始化方式**: 采用面向对象的 `Pinecone()` 初始化
- **索引管理**: 使用 `ServerlessSpec` 配置，支持自动扩缩容
- **配置简化**: 移除了不再需要的 `PINECONE_ENVIRONMENT` 参数

#### 新增优势
- Serverless 索引支持（按使用付费）
- 改进的 API 设计和错误处理
- 更快的初始化速度和并发处理能力

以上为主要更新内容，具体技术细节已在上方说明。

### PNPM 依赖管理

前端项目已迁移到 PNPM 包管理器，带来显著性能提升：

#### 性能优势
- 🚀 安装速度提升 30-50%
- 💾 磁盘空间节省约 60%
- 🔒 更严格的依赖管理和安全性

#### 使用方式
```bash
# 推荐使用 PNPM
cd frontend
pnpm install
pnpm run dev

# 或继续使用 npm
cd frontend
npm install
npm run dev
```

以上为使用说明，更多 PNPM 相关命令请参考官方文档。

## 许可证

MIT License