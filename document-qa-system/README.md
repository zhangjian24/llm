# 文档问答系统 (Document QA System)

基于阿里巴巴云通义千问系列模型(text-embedding-v4、rerank-v3、qwen-max)和Pinecone向量数据库的智能文档问答系统。

## 核心特性

- 📄 多格式文档支持 (PDF, TXT, DOCX, HTML)
- 🧠 向量检索 (text-embedding-v4嵌入模型 + Pinecone v5.3.0向量数据库)
- 💬 智能问答 (通义千问qwen-max大语言模型)
- 🔍 结果重排序 (rerank-v3相关性排序)
- 🔧 模块化架构 (LangChain框架)
- ⚡ FastAPI后端 + React 18.3.1前端
- 🐳 Docker容器化部署
- 🔐 Bearer Token标准认证
- 📊 实时进度显示和系统监控

## 技术栈

### 后端
- **框架**: FastAPI 0.104.1
- **向量处理**: LangChain 0.1.0
- **向量数据库**: Pinecone 5.3.0
- **嵌入模型**: Alibaba Cloud text-embedding-v4
- **重排序模型**: Alibaba Cloud rerank-v3
- **大语言模型**: Alibaba Cloud qwen-max
- **认证**: Bearer Token标准认证

### 前端
- **框架**: React 18.3.1
- **样式**: TailwindCSS 3.4.19
- **构建工具**: Vite 5.4.21
- **包管理**: pnpm (推荐)

## 快速开始

### 环境要求
- Python 3.9+
- Node.js 18+
- pnpm (推荐) 或 npm
- Docker (可选)
- 阿里巴巴云账户（推荐）

> **推荐使用阿里巴巴云通义千问服务**：提供企业级的模型服务，更好的性能和稳定性

### 阿里巴巴云通义千问配置（推荐）

1. **注册阿里巴巴云账户**：访问 [阿里云官网](https://www.aliyun.com/) 注册账户
2. **开通DashScope服务**：在[DashScope控制台](https://dashscope.console.aliyun.com/)开通服务
3. **创建API密钥**：在控制台创建API密钥
4. **配置环境变量**：
   ```bash
   # 在 .env.local 文件中配置
   QWEN_API_KEY=your_actual_alibaba_cloud_api_key_here
   QWEN_EMBEDDING_MODEL=text-embedding-v4
   QWEN_RERANK_MODEL=rerank-v3
   QWEN_LLM_MODEL=qwen-max
   ```

### 降级配置（无API密钥时）
系统支持降级运行模式，当未配置阿里巴巴云API密钥时，将使用本地Ollama服务作为后备：
```bash
# 下载Ollama服务
# 访问 https://ollama.com 下载并安装

# 下载模型
ollama pull bge-m3
ollama pull nomic-embed-text
ollama pull gpt-oss:20b

# 启动本地服务
ollama serve

# 系统将自动检测并使用本地服务
```

### 启动方式

> **重要提醒**: 首次启动前请确保已配置有效的 Pinecone API 密钥和阿里巴巴云API密钥（或启用降级模式）

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
# Pinecone配置 (v5.3.0 - 必需)
PINECONE_API_KEY=your_actual_pinecone_api_key_here
PINECONE_INDEX_NAME=document-qa-index

# 阿里巴巴云通义千问配置 (推荐)
QWEN_API_KEY=your_actual_alibaba_cloud_api_key_here
QWEN_EMBEDDING_MODEL=text-embedding-v4
QWEN_RERANK_MODEL=rerank-v3
QWEN_LLM_MODEL=qwen-max

# 降级配置 (无API密钥时使用)
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_API_KEY=
# EMBEDDING_MODEL=bge-m3
# LLM_MODEL=gpt-oss:20b
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

### 核心接口：
- `POST /api/documents/upload` - 上传文档
- `POST /api/chat/query` - 问答查询
- `GET /api/documents/list` - 文档列表
- `DELETE /api/documents/{doc_id}` - 删除文档

### 新增标准化接口：
- `POST /api/embeddings` - 文本嵌入生成 (OpenAI兼容)
- `POST /api/rerank` - 文档相关性重排序
- `GET /api/embeddings/models` - 嵌入模型列表
- `GET /api/rerank/models` - 重排序模型列表

### 认证方式：
所有API接口均支持Bearer Token认证：
```bash
Authorization: Bearer YOUR_API_KEY
```

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

2. **阿里巴巴云API密钥错误**
   - 检查 `QWEN_API_KEY` 是否正确配置
   - 确认DashScope服务已开通且有足够额度
   - 系统将自动降级到本地Ollama服务

3. **配置加载失败**
   - 检查 `.env` 文件是否存在且格式正确
   - 运行 `python -c "from app.core.config import settings; print('配置OK')"` 验证配置
   - 系统支持无API密钥的降级运行模式

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

### 技术架构升级

#### 后端重大升级
- **模型服务迁移**: 从Ollama迁移到阿里巴巴云通义千问系列模型
- **向量数据库**: 升级到Pinecone v5.3.0，支持Serverless索引
- **API标准化**: 实现OpenAI兼容的RESTful API接口
- **认证机制**: 添加Bearer Token标准认证支持

#### 前端现代化升级
- **框架版本**: React 18.2.0 → 18.3.1
- **样式框架**: TailwindCSS 3.3.6 → 3.4.19
- **构建工具**: Vite 5.0.8 → 5.4.21
- **用户体验**: 添加实时进度显示和系统状态监控

以上为主要更新内容，具体技术细节已在上方说明。

### 阿里巴巴云通义千问集成

系统现已全面集成阿里巴巴云通义千问系列模型服务：

#### 核心模型组件
- **text-embedding-v4**: 768维文本嵌入模型
- **rerank-v3**: 文档相关性重排序模型
- **qwen-max**: 企业级大语言模型

#### 技术优势
- **企业级稳定性**: 阿里巴巴云提供的高可用服务
- **标准化API**: OpenAI兼容的RESTful接口设计
- **智能降级**: 无API密钥时自动切换到本地Ollama服务
- **按需付费**: 灵活的计费模式，成本可控

---

### 系统测试验证

项目包含完整的自动化测试套件：

#### 测试覆盖范围
- ✅ 健康检查接口
- ✅ 嵌入API接口
- ✅ 重排序API接口
- ✅ 文档管理接口
- ✅ 聊天问答接口

#### 运行测试
```bash
# 运行系统集成测试
python system_test.py

# 查看详细测试结果
cat test_results.json
```

#### 测试结果示例
```json
{
  "overall_status": "SUCCESS",
  "statistics": {
    "total_tests": 5,
    "passed_tests": 4,
    "success_rate": 80.0,
    "total_time": 10.06
  }
}
```

---

以上为完整的使用说明和技术文档。

## 许可证

MIT License