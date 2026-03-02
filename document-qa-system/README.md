# 企业级RAG文档问答系统

一个基于FastAPI和React的现代化文档问答系统，采用RAG（检索增强生成）技术架构，支持文档上传、语义检索、智能问答等功能。

## 🏗️ 技术架构

### 后端技术栈
- **框架**: FastAPI (Async支持)
- **RAG引擎**: LangChain (v1.x+)  
- **向量数据库**: Pinecone (Serverless)
- **AI模型**: 
  - 嵌入模型: `text-embedding-v4`
  - 重排序模型: `rerank-v3`
  - 聊天模型: `qwen-max`
- **依赖管理**: uv/pip
- **类型检查**: Pydantic v2+

### 前端技术栈
- **框架**: React 19 + TypeScript
- **构建工具**: Vite
- **样式**: TailwindCSS
- **状态管理**: Zustand + TanStack Query
- **包管理**: pnpm

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- pnpm (推荐) 或 npm

### 后端部署

1. **进入后端目录**
```bash
cd backend
```

2. **创建虚拟环境**
```bash
# 使用uv (推荐)
uv venv
uv sync

# 或使用传统方式
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入实际的API密钥
```

4. **启动后端服务**
```bash
# 开发模式
uvicorn app.main:app --reload

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 前端部署

1. **进入前端目录**
```bash
cd frontend
```

2. **安装依赖**
```bash
pnpm install
# 或
npm install
```

3. **启动开发服务器**
```bash
pnpm dev
# 或
npm run dev
```

4. **构建生产版本**
```bash
pnpm build
# 或
npm run build
```

## 📁 项目结构

```
document-qa-system/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API路由
│   │   │   └── routes/
│   │   │       ├── chat.py    # 聊天相关API
│   │   │       ├── documents.py # 文档管理API
│   │   │       └── health.py  # 健康检查API
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 应用配置
│   │   │   └── logging.py     # 日志配置
│   │   ├── models/            # 数据模型
│   │   │   └── schemas.py     # Pydantic模型
│   │   ├── services/          # 业务服务
│   │   │   ├── pinecone_service.py # Pinecone服务
│   │   │   ├── llm_service.py      # LLM服务
│   │   │   └── rag_service.py      # RAG核心服务
│   │   └── main.py            # 应用入口
│   ├── requirements.txt       # Python依赖
│   └── .env.example           # 环境变量模板
│
└── frontend/                   # 前端应用
    ├── src/
    │   ├── components/        # React组件
    │   │   ├── chat/          # 聊天组件
    │   │   └── upload/        # 上传组件
    │   ├── services/          # API服务
    │   │   └── api.ts         # API客户端
    │   ├── stores/            # 状态管理
    │   │   └── chatStore.ts   # 聊天状态
    │   ├── types/             # TypeScript类型
    │   │   └── index.ts       # 类型定义
    │   ├── App.tsx            # 主应用组件
    │   └── main.tsx           # 入口文件
    ├── package.json           # Node依赖
    └── vite.config.ts         # Vite配置
```

## 🔧 环境变量配置

### 后端配置 (.env)
```bash
# OpenAI兼容接口配置
OPENAI_BASE_URL=your_openai_compatible_gateway_url
OPENAI_API_KEY=your_api_key_here

# Pinecone配置
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=document_qa_index

# 应用配置
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO
HOST=localhost
PORT=8000

# RAG参数配置
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RETRIEVAL=20
TOP_N_RERANK=5
```

## 🎯 核心功能

### 1. 文档管理
- ✅ 支持多种文档格式上传 (PDF, DOC, DOCX, TXT, MD)
- ✅ 自动文档分块和向量化
- ✅ 文档列表查看和管理
- ✅ 文档删除功能

### 2. 智能问答
- ✅ 基于RAG的语义检索
- ✅ 文档重排序优化
- ✅ 流式响应支持
- ✅ 对话历史管理
- ✅ 引用来源展示

### 3. 系统特性
- ✅ 完整的类型安全保障
- ✅ 异步非阻塞架构
- ✅ 实时日志监控
- ✅ 健康检查和监控
- ✅ CORS跨域支持

## 🔄 RAG工作流程

1. **文档处理**: 文档上传 → 文本提取 → 递归分块
2. **向量化**: 使用 `text-embedding-v4` 生成向量表示
3. **存储检索**: 向量存储到 Pinecone → 语义相似度搜索
4. **重排序**: 使用 `rerank-v3` 优化检索结果
5. **生成回答**: 基于上下文调用 `qwen-max` 生成答案

## 📊 API接口

### 聊天接口
- `POST /api/chat/query` - 同步问答
- `POST /api/chat/stream` - 流式问答
- `GET /api/chat/history/{id}` - 获取对话历史
- `DELETE /api/chat/history/{id}` - 清除对话历史

### 文档接口
- `POST /api/documents/upload` - 上传文档
- `GET /api/documents` - 获取文档列表
- `DELETE /api/documents/{id}` - 删除文档
- `GET /api/documents/{id}/info` - 获取文档详情

### 健康检查
- `GET /api/health` - 健康检查
- `GET /api/health/ready` - 就绪检查
- `GET /api/health/live` - 存活检查

## 🐳 Docker部署

### 后端Docker化
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 前端Docker化
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
```

## 🔒 安全考虑

- [ ] API密钥安全存储
- [ ] 输入验证和清理
- [ ] 速率限制实现
- [ ] 访问权限控制
- [ ] SSL/TLS加密传输

## 📈 性能优化

- [ ] 连接池配置
- [ ] 缓存策略实现
- [ ] 异步批量处理
- [ ] 负载均衡部署
- [ ] 监控告警机制

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 支持

如有问题或建议，请提交 Issue 或联系项目维护者。

---
*构建于 2026年，采用最新技术栈*