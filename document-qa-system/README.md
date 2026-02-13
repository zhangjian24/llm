# 文档问答系统

基于向量检索和上下文注入的智能文档问答系统。

## 技术栈

### 后端
- **FastAPI**: 高性能Python Web框架
- **LangChain**: LLM应用开发框架
- **Pinecone**: 向量数据库服务
- **BGE**: 中文向量嵌入模型
- **千问API**: 大语言模型服务

### 前端
- **React 18**: 现代前端框架
- **TailwindCSS**: 实用优先的CSS框架
- **TypeScript**: 类型安全的JavaScript超集

## 功能特性

- 📄 文档上传与管理（支持PDF、TXT、DOCX等格式）
- 🔍 智能向量检索
- 💬 上下文感知问答
- 🎯 相关文档引用
- 📱 响应式用户界面

## 快速开始

### 环境准备

1. 复制环境变量配置文件：
```bash
cd backend
cp .env.example .env
```

2. 在 `.env` 文件中配置以下环境变量：
```env
# Pinecone配置
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=document-qa-index

# 千问API配置
DASHSCOPE_API_KEY=your_dashscope_api_key
```

### 使用Docker运行（推荐）

```bash
# 构建并启动所有服务
docker-compose up --build

# 后台运行
docker-compose up -d
```

### 本地开发运行

#### 后端服务

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### 前端服务

```bash
cd frontend
npm install
npm run dev
```

## 项目结构

```
document-qa-system/
├── backend/                    # FastAPI后端服务
│   ├── app/
│   │   ├── api/               # API路由
│   │   ├── core/              # 核心配置
│   │   ├── models/            # 数据模型
│   │   ├── services/          # 业务服务
│   │   ├── utils/             # 工具函数
│   │   └── main.py            # 应用入口
│   ├── requirements.txt       # Python依赖
│   └── .env                   # 环境变量
├── frontend/                  # React前端应用
│   ├── src/
│   │   ├── components/        # React组件
│   │   ├── hooks/             # 自定义Hook
│   │   ├── services/          # API服务
│   │   └── App.tsx            # 主应用组件
│   ├── package.json           # Node依赖
│   └── tailwind.config.js     # Tailwind配置
├── docker-compose.yml         # 容器编排
└── README.md                  # 项目文档
```

## API文档

启动后端服务后，访问 `http://localhost:8000/docs` 查看自动生成的API文档。

## 开发指南

### 添加新的文档格式支持

在 `backend/app/services/document_processor.py` 中扩展文档解析器。

### 自定义提示词模板

修改 `backend/app/services/qa_engine.py` 中的提示词模板。

### 前端组件开发

在 `frontend/src/components/` 目录下创建新的React组件。

## 部署

### 生产环境部署

1. 更新环境变量为生产配置
2. 构建前端静态文件：
```bash
cd frontend
npm run build
```

3. 使用Docker部署：
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 许可证

MIT License