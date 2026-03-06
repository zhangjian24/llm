# RAG 文档问答系统 - 系统架构说明书 (SAD)

## 1. 架构概述

### 设计原则
- **高内聚低耦合**: 各模块职责单一，通过明确定义的接口通信
- **异步优先**: I/O 操作全部异步化，提升吞吐量
- **配置驱动**: 所有魔法数字通过环境变量配置，支持多环境部署
- **可观测性**: 内置日志、指标追踪，便于问题诊断
- **渐进式演进**: MVP 采用单体架构，预留微服务拆分能力

### 架构风格
**分层架构 (Layered Architecture)** + **事件驱动 (Event-Driven)**

```
┌─────────────────────────────────────┐
│         Presentation Layer          │
│    (React SPA + TypeScript)         │
└─────────────────────────────────────┘
                  ↕ HTTP/REST + SSE
┌─────────────────────────────────────┐
│         Application Layer           │
│    (FastAPI API Endpoints)          │
└─────────────────────────────────────┘
                  ↕ Service Interface
┌─────────────────────────────────────┐
│         Business Logic Layer        │
│  (RAG Service, Document Service)    │
└─────────────────────────────────────┘
                  ↕ Repository Pattern
┌─────────────────────────────────────┐
│         Data Access Layer           │
│   (Pinecone, Local FS, Memory)      │
└─────────────────────────────────────┘
```

### 技术栈全景图

| 层级 | 技术选型 | 版本 | 选型理由 |
|------|----------|------|----------|
| **前端框架** | React | 19+ | 生态成熟，组件丰富，性能优秀 |
| **构建工具** | Vite | 5+ | 极速冷启动，HMR 体验好 |
| **类型系统** | TypeScript | 5+ | 类型安全，IDE 友好 |
| **样式方案** | TailwindCSS | 3+ | 原子化 CSS，开发效率高 |
| **状态管理** | Zustand | 4+ | 轻量简洁，替代 Redux |
| **数据请求** | TanStack Query | 5+ | 强大的服务端状态管理 |
| **后端框架** | FastAPI | 0.100+ | 原生异步，自动 OpenAPI 文档 |
| **AI 框架** | LangChain | v1.x+ | RAG 工具链完善，抽象优雅 |
| **LLM SDK** | langchain_openai | Latest | OpenAI 兼容，无缝切换模型 |
| **向量数据库** | Pinecone | Serverless | 免运维，自动扩展，性价比高 |
| **文档解析** | PyMuPDF, python-docx | Latest | 解析效果好，社区活跃 |
| **部署容器** | Docker | Latest | 环境一致性，便于 CI/CD |

---

## 2. 系统逻辑视图

### 模块划分

#### 2.1 前端子系统 (Frontend Subsystem)
**职责**: 用户界面展示、交互处理、状态管理

**核心模块**:
- `ChatModule`: 对话界面、流式响应渲染、历史管理
- `DocumentModule`: 文档上传、列表展示、进度跟踪
- `SharedModule`: 通用组件、工具函数、API 客户端

#### 2.2 后端 API 层 (API Gateway Layer)
**职责**: HTTP 请求路由、参数验证、认证鉴权、响应格式化

**端点分组**:
- `/api/documents/*`: 文档管理相关
- `/api/chat/*`: 对话相关
- `/api/conversations/*`: 会话历史相关

#### 2.3 业务逻辑层 (Business Logic Layer)
**职责**: 核心 RAG 流程编排、业务规则实现

**核心服务**:
- `DocumentService`: 文档解析、分块、向量化编排
- `RAGService`: 检索、重排序、回答生成
- `ChatService`: 对话上下文管理、消息持久化
- `EmbeddingService`: 文本向量化（调用外部 API）
- `RerankService`: 检索结果重排序

#### 2.4 数据访问层 (Data Access Layer)
**职责**: 数据持久化、缓存管理、外部服务集成

**存储策略**:
- **Pinecone**: 向量数据存储（主存储）
- **本地文件系统**: 原始文档存储
- **内存存储**: 对话历史（Session）、临时缓存

### 模块交互图

```mermaid
graph TB
    subgraph Frontend["前端子系统"]
        UI[React 界面]
        State[Zustand 状态]
        Query[TanStack Query]
    end
    
    subgraph API["后端 API 层"]
        DocAPI[Documents Router]
        ChatAPI[Chat Router]
        ConvAPI[Conversations Router]
    end
    
    subgraph Business["业务逻辑层"]
        DocSvc[DocumentService]
        RAGSvc[RAGService]
        ChatSvc[ChatService]
        EmbSvc[EmbeddingService]
        RerankSvc[RerankService]
    end
    
    subgraph Data["数据访问层"]
        Pinecone[(Pinecone<br/>Vector DB)]
        FileSystem[(本地文件系统)]
        Memory[(内存存储)]
    end
    
    subgraph External["外部服务"]
        Bailian[阿里云百炼<br/>qwen-max/embedding/rerank]
    end
    
    UI --> State
    UI --> Query
    Query --> DocAPI
    Query --> ChatAPI
    Query --> ConvAPI
    
    DocAPI --> DocSvc
    ChatAPI --> RAGSvc
    ChatAPI --> ChatSvc
    ConvAPI --> ChatSvc
    
    DocSvc --> EmbSvc
    DocSvc --> Pinecone
    DocSvc --> FileSystem
    
    RAGSvc --> EmbSvc
    RAGSvc --> RerankSvc
    RAGSvc --> Pinecone
    RAGSvc --> Bailian
    
    EmbSvc --> Bailian
    RerankSvc --> Bailian
    
    ChatSvc --> Memory
```

### 关键业务流程架构

#### 2.5 文档上传与向量化流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant FE as 前端
    participant API as API 层
    participant DocSvc as DocumentService
    participant Parser as 文档解析器
    participant EmbSvc as EmbeddingService
    participant Pinecone as Pinecone DB
    
    User->>FE: 选择文件并上传
    FE->>API: POST /api/documents/upload
    API->>DocSvc: upload_document(file)
    
    DocSvc->>Parser: parse_to_text(file)
    Parser-->>DocSvc: 纯文本内容
    
    DocSvc->>DocSvc: chunk_by_semantic(text)
    loop 每个文档块
        DocSvc->>EmbSvc: embed(chunk_text)
        EmbSvc->>Bailian: text-embedding-v4 API
        Bailian-->>EmbSvc: 向量 [1536]
        DocSvc->>Pinecone: upsert(id, vector, metadata)
    end
    
    DocSvc-->>API: {id, status: "ready", chunks_count}
    API-->>FE: 200 OK
    FE-->>User: 显示上传成功
```

#### 2.6 RAG 问答流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant FE as 前端
    participant ChatAPI as Chat API
    participant RAGSvc as RAGService
    participant EmbSvc as EmbeddingService
    participant Pinecone as Pinecone DB
    participant RerankSvc as RerankService
    participant LLM as qwen-max
    
    User->>FE: 输入问题
    FE->>ChatAPI: POST /api/chat (stream=true)
    ChatAPI->>RAGSvc: query(question, history)
    
    RAGSvc->>EmbSvc: embed(question)
    EmbSvc->>Bailian: embedding API
    Bailian-->>EmbSvc: query_vector
    
    RAGSvc->>Pinecone: similarity_search(query_vector, top_k=10)
    Pinecone-->>RAGSvc: 10 个相似块
    
    RAGSvc->>RerankSvc: rerank(results, question)
    RerankSvc->>Bailian: rerank-v3 API
    Bailian-->>RerankSvc: 重排序后的 5 个块
    
    RAGSvc->>RAGSvc: build_prompt(question, context, history)
    RAGSvc->>LLM: generate_stream(prompt)
    LLM-->>RAGSvc: token stream
    
    loop 每个 token
        RAGSvc-->>ChatAPI: SSE data: {"token": "..."}
        ChatAPI-->>FE: Server-Sent Event
        FE-->>User: 逐字显示
    end
```

---

## 3. 系统物理视图 (部署架构)

### 网络拓扑

```
                    ┌──────────────────┐
                    │   Cloudflare     │
                    │     CDN/WAF      │
                    └────────┬─────────┘
                             │ HTTPS
                    ┌────────▼─────────┐
                    │  Load Balancer   │
                    │   (可选/Nginx)   │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌───────▼────────┐  ┌───────▼────────┐
│  Frontend Pod  │  │  Backend Pod 1 │  │  Backend Pod 2 │
│  (Static Files)│  │  (FastAPI)     │  │  (FastAPI)     │
│  :80/:443      │  │  :8000         │  │  :8000         │
└────────────────┘  └────────────────┘  └────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
    ┌─────────▼──────────┐      ┌──────────▼──────────┐
    │   Pinecone Cloud   │      │  阿里云百炼 API     │
    │   (Serverless)     │      │  (Public Internet)  │
    └────────────────────┘      └─────────────────────┘
```

### 节点规划

#### MVP 阶段 (单实例部署)
| 节点类型 | 配置 | 数量 | 用途 |
|----------|------|------|------|
| 应用服务器 | 4 核 8GB, 100GB SSD | 1 | 运行 FastAPI + 静态文件服务 |
| 对象存储 | OSS/S3 | 1 | 存储原始文档（可选） |

#### 生产阶段 (高可用部署)
| 节点类型 | 配置 | 数量 | 用途 |
|----------|------|------|------|
| 负载均衡器 | Nginx/ALB | 1 | 流量分发、SSL 终止 |
| 应用节点 | 4 核 8GB | 2-4 | 无状态 FastAPI 实例 |
| 静态资源 | CDN | 1 | 前端文件加速 |

### 高可用设计

**故障转移策略**:
1. **健康检查**: 每 5 秒检测后端实例健康状态 (`GET /health`)
2. **自动剔除**: 连续 3 次失败则从负载均衡池移除
3. **优雅降级**: 
   - Pinecone 不可用 → 切换至关键词检索 (BM25)
   - 百炼 API 超时 → 重试 3 次后返回友好错误

**数据备份策略**:
- Pinecone 自动备份（托管服务特性）
- 文档元数据每日凌晨 2 点导出至 JSON 备份文件
- RPO (恢复点目标): ≤24 小时
- RTO (恢复时间目标): ≤1 小时

---

## 4. 非功能性架构设计

### 安全性架构

#### 4.1 传输层安全
```yaml
TLS 配置:
  版本：TLS 1.3
  加密套件: TLS_AES_256_GCM_SHA384
  证书：Let's Encrypt 或云厂商 SSL 证书
  强制 HTTPS: HSTS header (max-age=31536000)
```

#### 4.2 输入验证
```python
# 文件上传验证示例
class DocumentUploadValidator:
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/markdown',
        'text/plain'
    }
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    async def validate(self, file: UploadFile):
        # 1. MIME 类型白名单
        if file.content_type not in self.ALLOWED_MIME_TYPES:
            raise HTTPException(400, "不支持的文件格式")
        
        # 2. 文件大小限制
        content = await file.read()
        if len(content) > self.MAX_FILE_SIZE:
            raise HTTPException(413, "文件超过 50MB")
        
        # 3. 文件签名验证 (防止 MIME 伪造)
        if not self._verify_magic_number(content):
            raise HTTPException(400, "文件损坏或格式不匹配")
```

#### 4.3 速率限制
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/chat")
@limiter.limit("60/minute")  # 单 IP 每分钟最多 60 次请求
async def chat(request: Request, ...):
    ...
```

#### 4.4 审计日志
```python
import structlog

logger = structlog.get_logger()

async def audit_log_middleware(request: Request, call_next):
    response = await call_next(request)
    
    # 记录关键操作
    if request.method == "POST" and "/documents" in request.url.path:
        logger.info(
            "document_uploaded",
            ip=request.client.host,
            user_agent=request.headers.get("user-agent"),
            filename=request.form.get("filename"),
            status=response.status_code
        )
    
    return response
```

### 性能架构

#### 4.5 缓存策略
```python
from functools import lru_cache
from cachetools import TTLCache

# 1. 嵌入向量缓存 (避免重复计算相同文本)
embedding_cache = TTLCache(maxsize=1000, ttl=3600)  # 1 小时过期

@lru_cache(maxsize=100)
def get_document_metadata(doc_id: str):
    """文档元数据缓存"""
    return db.query(Document).filter(Document.id == doc_id).first()
```

#### 4.6 异步 I/O
```python
# 所有 I/O 操作使用异步
import aiofiles
import httpx

async def process_document(file_path: str):
    # 异步文件读取
    async with aiofiles.open(file_path, 'rb') as f:
        content = await f.read()
    
    # 异步 API 调用
    async with httpx.AsyncClient() as client:
        response = await client.post(embedding_api, json={...})
```

#### 4.7 批量处理优化
```python
# 批量向量化（减少 API 调用次数）
async def batch_embed_documents(texts: List[str], batch_size: int = 32):
    batches = [texts[i:i+batch_size] for i in range(0, len(texts), batch_size)]
    
    tasks = [embed_batch(batch) for batch in batches]
    results = await asyncio.gather(*tasks)
    
    return [vec for batch_result in results for vec in batch_result]
```

### 可扩展性设计

#### 4.8 水平扩展预留
- **无状态设计**: 后端实例不保存会话状态，可任意扩缩容
- **会话外置**: 对话历史存储在独立内存/RDB，与具体实例解耦
- **数据库分离**: Pinecone 天然支持自动扩展，无需分库分表

#### 4.9 模块化插件机制
```python
# 文档解析器注册表
parser_registry = {}

def register_parser(file_type: str):
    def decorator(cls):
        parser_registry[file_type] = cls
        return cls
    return decorator

@register_parser("pdf")
class PDFParser:
    async def parse(self, file: bytes) -> str:
        ...

# 新增格式只需添加新解析器，无需修改核心逻辑
```

---

## 5. 关键技术决策记录 (ADR)

### ADR-001: 为什么选择 FastAPI 而不是 Flask/Django?

**背景**: 需要选择一个 Python Web 框架作为后端 API 基础

**选项对比**:

| 维度 | FastAPI | Flask | Django REST Framework |
|------|---------|-------|----------------------|
| 异步支持 | ✅ 原生异步 | ❌ 同步 (需额外扩展) | ⚠️ 部分异步 |
| 性能 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 自动文档 | ✅ OpenAPI 自动生成 | ❌ 需手动 | ⚠️ 需配置 |
| 类型检查 | ✅ Pydantic 强类型 | ❌ 弱类型 | ⚠️ 中等 |
| 学习曲线 | 平缓 | 平缓 | 陡峭 |
| 生态成熟度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**最终决定**: **FastAPI**

**理由**:
1. 原生异步支持，契合 RAG 流程中大量 I/O 操作
2. 自动 OpenAPI 文档，减少维护成本
3. Pydantic 提供优秀的类型验证和序列化
4. 性能优于 Flask/Django，符合 NFR-001 性能需求

---

### ADR-002: 为什么选择 Pinecone 而不是 Milvus/Weaviate?

**背景**: 需要选择向量数据库存储文档嵌入

**选项对比**:

| 维度 | Pinecone | Milvus | Weaviate |
|------|----------|--------|----------|
| 部署方式 | 全托管 SaaS | 自建/托管 | 自建/托管 |
| 运维成本 | ⭐⭐⭐⭐⭐ (零运维) | ⭐⭐ (需运维) | ⭐⭐⭐ |
| 扩展性 | 自动扩展 | 手动分片 | 手动扩展 |
| 查询性能 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 成本 (MVP) | $0 起步 | 服务器成本 | 服务器成本 |
| 功能丰富度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**最终决定**: **Pinecone Serverless**

**理由**:
1. **零运维**: 团队规模小，避免分散精力到基础设施
2. **按需付费**: MVP 阶段成本极低，随用量增长
3. **自动扩展**: 无需预先规划容量
4. **性能优秀**: 基准测试满足 NFR-001 (<2 秒检索延迟)

**风险缓解**: 
- 供应商锁定风险 → 抽象 EmbeddingService 接口，未来可切换至其他向量库

---

### ADR-003: 为什么选择阿里云百炼而不是直接调用通义千问 API?

**背景**: 需要选择 LLM 服务提供商

**选项对比**:

| 维度 | 阿里云百炼 | 通义千问直连 | OpenAI |
|------|------------|-------------|--------|
| 模型丰富度 | ✅ 多种模型 (qwen/max/embedding/rerank) | ⚠️ 仅语言模型 | ✅ 齐全 |
| 国内访问速度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 价格 | ¥ 计费，性价比高 | ¥ 计费 | $ 计费，较贵 |
| 合规性 | ✅ 符合中国法规 | ✅ | ⚠️ 数据出境风险 |
| LangChain 集成 | ✅ langchain_openai 兼容 | ⚠️ 需适配 | ✅ 原生支持 |

**最终决定**: **阿里云百炼**

**理由**:
1. **一站式服务**: 同时提供 LLM(qwen-max)、Embedding、Rerank，统一账单
2. **低延迟**: 国内访问速度快于 OpenAI
3. **合规安全**: 数据不出境，符合《生成式 AI 管理办法》
4. **成本优势**: 中文场景下性价比优于 GPT-4

**技术实现**:
```python
from langchain_openai import ChatOpenAI

# 通过 base_url 重定向到百炼端点
llm = ChatOpenAI(
    model="qwen-max",
    openai_api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
)
```

---

### ADR-004: 为什么选择单体架构而不是微服务？

**背景**: 确定系统初始架构风格

**选项对比**:

| 维度 | 单体架构 | 微服务架构 |
|------|----------|-----------|
| 开发效率 | ⭐⭐⭐⭐⭐ (代码集中) | ⭐⭐⭐ (需协调多服务) |
| 部署复杂度 | ⭐⭐⭐⭐⭐ (单次部署) | ⭐⭐ (需编排多个服务) |
| 调试难度 | ⭐⭐⭐⭐ (本地调试) | ⭐⭐ (分布式追踪) |
| 扩展粒度 | ⭐⭐ (整体扩展) | ⭐⭐⭐⭐⭐ (按需扩展) |
| 团队要求 | ⭐⭐⭐⭐ (1-2 人即可) | ⭐⭐ (需 DevOps 支持) |
| 初期成本 | ⭐⭐⭐⭐⭐ (低) | ⭐⭐ (高) |

**最终决定**: **单体架构，预留模块化拆分能力**

**理由**:
1. **团队规模**: MVP 阶段 2-3 人，微服务过度设计
2. **快速迭代**: 需求变化快，单体更灵活
3. **成本控制**: 减少服务器和运维开销
4. **退出策略**: 通过清晰的服务接口抽象，未来可按模块拆分为微服务

**演进路线**:
```
Phase 1 (MVP): 单体 FastAPI 应用
       ↓
Phase 2 (增长): 抽离 DocumentService 为独立服务
       ↓
Phase 3 (规模化): 抽离 RAGService、ChatService
```

---

## 6. 部署配置示例

### Docker Compose (开发环境)
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
      - PINECONE_HOST=${PINECONE_HOST}
    volumes:
      - ./backend:/app
      - document_storage:/app/storage
    restart: unless-stopped
  
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  document_storage:
```

### 生产环境 Nginx 配置
```nginx
server {
    listen 80;
    server_name rag-system.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name rag-system.example.com;
    
    ssl_certificate /etc/letsencrypt/live/rag-system.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/rag-system.example.com/privkey.pem;
    
    # 前端静态文件
    location / {
        root /var/www/frontend;
        try_files $uri $uri/ /index.html;
    }
    
    # 后端 API 代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # SSE 支持
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
    }
}
```

---

## 7. 监控与告警策略

### 关键指标监控
```yaml
metrics:
  - name: api_response_time
    threshold: p95 < 2000ms
    alert_if_exceeded: true
  
  - name: error_rate
    threshold: < 5%
    alert_if_exceeded: true
  
  - name: pinecone_query_latency
    threshold: p95 < 500ms
    alert_if_exceeded: true
  
  - name: active_conversations
    threshold: > 100
    alert_if_exceeded: false  # 仅记录，不告警
```

### 日志级别规范
```python
LOG_LEVELS = {
    "DEBUG": "详细调试信息（本地开发）",
    "INFO": "关键业务操作（上传、查询、删除）",
    "WARNING": "可恢复的异常（API 超时重试）",
    "ERROR": "需要人工介入的错误（数据库连接失败）"
}
```

---

## 8. 附录：架构演进路线图

```mermaid
graph LR
    A[MVP 阶段<br/>单体架构<br/>单实例部署] --> B[增长阶段<br/>单体 + 缓存层<br/>负载均衡]
    B --> C[成熟阶段<br/>服务拆分<br/>容器化部署]
    C --> D[规模化阶段<br/>微服务 + 服务网格<br/>多区域部署]
    
    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#e8f5e9
    style D fill:#f3e5f5
```

---

**文档审批签字**:

| 角色 | 姓名 | 签字 | 日期 |
|------|------|------|------|
| 首席架构师 | | | |
| 技术负责人 | | | |
| 运维负责人 | | | |

---

**变更历史**:
| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|----------|
| v1.0 | 2026-03-04 | AI 首席架构师 | 初始版本 |
