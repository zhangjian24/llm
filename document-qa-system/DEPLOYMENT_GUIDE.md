# 文档问答系统 - 部署和使用指南

## 系统架构

本系统采用现代化的微服务架构设计：

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   前端应用   │───▶│   后端API    │───▶│  向量数据库  │
│  (React)    │    │ (FastAPI)   │    │ (Pinecone)  │
└─────────────┘    └─────────────┘    └─────────────┘
                         │
                   ┌─────▼─────┐
                   │ 嵌入模型   │
                   │ (Ollama)  │
                   └───────────┘
                         │
                   ┌─────▼─────┐
                   │ 大语言模型 │
                   │  (千问)   │
                   └───────────┘
```

## 核心功能模块

### 1. 文档处理服务
- **支持格式**: PDF, TXT, DOCX, DOC, HTML
- **文本提取**: 自动识别和提取文档内容
- **智能分块**: 将长文档分割为适当大小的文本块
- **元数据管理**: 记录文档基本信息和处理状态

### 2. 向量嵌入服务
- **模型**: BGE-M3 (基于Ollama本地部署)
- **维度**: 768维向量空间
- **批处理**: 支持批量文档嵌入
- **缓存机制**: 优化重复内容的处理效率

### 3. 向量检索服务
- **数据库**: Pinecone向量数据库
- **相似度算法**: 余弦相似度
- **检索策略**: Top-K最近邻搜索
- **过滤机制**: 支持按文档范围筛选

### 4. 智能问答引擎
- **语言模型**: 通义千问API
- **Prompt工程**: 上下文感知的提示词设计
- **置信度评估**: 自动计算回答可信度
- **来源追踪**: 显示答案引用的具体文档段落

## 部署方式

### 方式一：Docker一键部署（推荐）

```bash
# 1. 克隆项目
git clone <repository-url>
cd document-qa-system

# 2. 配置环境变量
cp backend/.env.example .env
# 编辑.env文件，填入必要配置

# 3. 启动服务
# Windows:
./start.bat
# Linux/Mac:
./start.sh
```

### 方式二：手动部署

#### 后端服务
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 前端服务
```bash
cd frontend
npm install
npm run dev
```

#### Ollama服务
```bash
# 下载并安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 拉取BGE模型
ollama pull bge-m3
ollama serve
```

## 环境配置

### 必需配置项

在 `.env` 文件中设置以下参数：

```bash
# Pinecone向量数据库配置
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_environment
PINECONE_INDEX_NAME=document_qa_index

# 千问API配置
QWEN_API_KEY=your_qwen_api_key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/api/v1

# Ollama配置
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=bge-m3
```

### 可选配置项

```bash
# 应用设置
APP_ENV=production
DEBUG=False
LOG_LEVEL=INFO

# 上传设置
MAX_FILE_SIZE=10485760
UPLOAD_FOLDER=./uploads

# 向量设置
VECTOR_DIMENSION=768
TOP_K_RESULTS=5
SCORE_THRESHOLD=0.7
```

## API接口文档

### 文档管理接口

**上传文档**
```
POST /api/documents/upload
Content-Type: multipart/form-data

Response:
{
  "document_id": "uuid",
  "filename": "example.pdf",
  "status": "success",
  "message": "文档上传并处理成功"
}
```

**文档列表**
```
GET /api/documents/list

Response:
{
  "documents": [...],
  "total": 10
}
```

### 问答接口

**文档问答**
```
POST /api/chat/query
Content-Type: application/json

{
  "query": "文档的主要内容是什么？",
  "document_ids": ["doc1", "doc2"],
  "top_k": 5
}

Response:
{
  "query": "文档的主要内容是什么？",
  "answer": "根据文档内容...",
  "sources": [...],
  "confidence": 0.85
}
```

**健康检查**
```
GET /api/health

Response:
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "services": {
    "vector_store": "healthy",
    "embedding_service": "healthy",
    "llm_service": "healthy"
  }
}
```

## 性能优化建议

### 硬件要求
- **CPU**: 4核以上
- **内存**: 8GB以上（推荐16GB）
- **存储**: SSD硬盘，至少50GB可用空间
- **GPU**: 可选（用于加速嵌入计算）

### 软件优化
1. **Ollama配置**: 为BGE模型分配足够内存
2. **Pinecone索引**: 选择合适的Pod类型
3. **缓存策略**: 合理设置Redis缓存
4. **并发控制**: 调整API并发限制

### 监控指标
- 文档处理成功率
- 查询响应时间
- 向量检索准确率
- 系统资源使用率

## 故障排除

### 常见问题

**1. 文档上传失败**
- 检查文件格式是否支持
- 确认文件大小未超出限制
- 验证Ollama服务是否正常运行

**2. 问答质量不佳**
- 检查文档内容质量和完整性
- 调整相似度阈值参数
- 优化Prompt模板设计

**3. 系统响应缓慢**
- 检查网络连接状态
- 监控系统资源使用情况
- 优化向量数据库索引

### 日志查看

```bash
# Docker环境下查看日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 手动部署查看日志
tail -f backend/logs/app.log
```

## 安全考虑

### 数据安全
- 文档加密存储
- API访问控制
- 敏感信息脱敏处理

### 系统安全
- 定期更新依赖包
- 配置防火墙规则
- 启用HTTPS加密传输

## 扩展功能

### 计划中的功能
- [ ] 用户认证和权限管理
- [ ] 多语言支持
- [ ] 文档版本控制
- [ ] 高级搜索功能
- [ ] 数据可视化仪表板

### 自定义开发
系统采用模块化设计，便于：
- 添加新的文档格式支持
- 集成不同的嵌入模型
- 替换向量数据库
- 扩展问答功能

## 技术支持

如有问题，请联系：
- 项目维护者: [maintainer@example.com]
- GitHub Issues: [项目链接]
- 文档地址: [文档链接]

---
*文档版本: v1.0.0*
*最后更新: 2024年2月*