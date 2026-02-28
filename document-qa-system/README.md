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
- Ollama Cloud 账户（推荐）或本地 Ollama 服务

> **推荐使用 Ollama Cloud**：提供更好的性能和稳定性，支持更大的模型

### Ollama Cloud 配置（推荐）

1. **注册 Ollama Cloud 账户**：访问 [ollama.com](https://ollama.com) 注册账户
2. **创建 API 密钥**：在 [设置页面](https://ollama.com/settings/keys) 创建 API 密钥
3. **配置环境变量**：
   ```bash
   # 在 .env.local 文件中配置
   OLLAMA_API_KEY=your_actual_ollama_api_key_here
   OLLAMA_BASE_URL=https://ollama.com/api
   ```

### 本地 Ollama 服务（推荐用于嵌入功能）
由于 Ollama Cloud 主要提供大型语言模型，建议使用本地 Ollama 服务来获得更好的嵌入模型支持：
```bash
# 下载专用嵌入模型
ollama pull bge-m3
ollama pull nomic-embed-text

# 下载语言模型
ollama pull gpt-oss:20b

# 启动本地服务
ollama serve

# 更新配置使用本地服务
# OLLAMA_BASE_URL=http://localhost:11434
# EMBEDDING_MODEL=bge-m3
```

### 启动方式

> **重要提醒**: 首次启动前请确保已配置有效的 Pinecone API 密钥和 Ollama Cloud API 密钥

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

# Ollama配置 (Ollama Cloud - 推荐)
OLLAMA_BASE_URL=https://ollama.com/api
OLLAMA_API_KEY=your_actual_ollama_api_key_here
EMBEDDING_MODEL=bge-m3
LLM_MODEL=gpt-oss:20b

# 或使用本地 Ollama 服务
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_API_KEY=
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
   - **Ollama Cloud 用户**：检查 API 密钥是否正确配置，确认账户有足够额度
   - **本地 Ollama 用户**：确保服务已启动并在正确端口运行（默认 11434）
   - 验证网络连接和防火墙设置

3. **配置加载失败**
   - 检查 `.env` 文件是否存在且格式正确
   - 确保 `OLLAMA_API_KEY` 已正确配置（Ollama Cloud 用户）
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

### Ollama Cloud 集成

根据 Ollama 官方 Cloud 文档，系统已集成 Ollama Cloud 服务：

#### 主要特性
- **官方认证支持**: 使用 Bearer Token 认证方式
- **统一 API 端点**: `https://ollama.com/api`
- **模型兼容性**: 支持 gpt-oss 系列等 Cloud 模型
- **灵活部署**: 可选择 Cloud 服务或本地部署

#### 配置变更
- 新增 `OLLAMA_API_KEY` 环境变量
- 更新默认端点为官方 Cloud API
- 保持向后兼容本地 Ollama 部署

#### 使用优势
- 无需本地 GPU 资源
- 自动扩缩容支持
- 更好的模型性能
- 简化的部署流程

---

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