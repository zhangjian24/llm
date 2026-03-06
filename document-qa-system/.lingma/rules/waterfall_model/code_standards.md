---
trigger: always_on
---
# RAG 文档问答系统 - 代码规范与实现说明

## 1. 目录结构

```
document-qa-system/
├── backend/                          # FastAPI 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI 应用入口
│   │   ├── config.py                # 配置管理（Pydantic Settings）
│   │   ├── dependencies.py          # 依赖注入（DI）
│   │   ├── exceptions.py            # 自定义异常类
│   │   ├── middleware/              # 中间件
│   │   │   ├── __init__.py
│   │   │   ├── logging_middleware.py    # 日志中间件
│   │   │   └── cors_middleware.py       # CORS 中间件
│   │   ├── api/                     # API 路由层
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── documents.py     # 文档管理接口
│   │   │   │   ├── chat.py          # 对话接口
│   │   │   │   └── conversations.py # 会话历史接口
│   │   │   └── deps.py              # API 依赖
│   │   ├── services/                # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── document_service.py  # DocumentService
│   │   │   ├── rag_service.py       # RAGService
│   │   │   ├── chat_service.py      # ChatService
│   │   │   ├── embedding_service.py # EmbeddingService
│   │   │   └── rerank_service.py    # RerankService
│   │   ├── repositories/            # 数据访问层
│   │   │   ├── __init__.py
│   │   │   ├── document_repository.py
│   │   │   └── conversation_repository.py
│   │   ├── models/                  # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── document.py          # Document 实体
│   │   │   ├── chunk.py             # Chunk 实体
│   │   │   └── conversation.py      # Conversation 实体
│   │   ├── schemas/                 # Pydantic Schema
│   │   │   ├── __init__.py
│   │   │   ├── document.py          # DocumentDTO
│   │   │   ├── chat.py              # ChatDTO
│   │   │   └── common.py            # 通用 DTO
│   │   ├── parsers/                 # 文档解析器
│   │   │   ├── __init__.py
│   │   │   ├── base_parser.py       # Parser 接口
│   │   │   ├── pdf_parser.py        # PDF 解析
│   │   │   ├── docx_parser.py       # Word 解析
│   │   │   └── text_parser.py       # TXT解析
│   │   ├── chunkers/                # 文本分块器
│   │   │   ├── __init__.py
│   │   │   └── semantic_chunker.py  # 语义分块算法
│   │   ├── utils/                   # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── logger.py            # 日志配置
│   │   │   └── security.py          # 安全工具
│   │   └── core/                    # 核心组件
│   │       ├── __init__.py
│   │       ├── database.py          # 数据库连接
│   │       └── pinecone_client.py   # Pinecone 客户端
│   ├── tests/                       # 测试目录
│   │   ├── __init__.py
│   │   ├── conftest.py              # pytest 配置
│   │   ├── unit/                    # 单元测试
│   │   │   ├── test_document_service.py
│   │   │   └── test_rag_service.py
│   │   └── integration/             # 集成测试
│   │       └── test_api_endpoints.py
│   ├── requirements.txt             # Python 依赖
│   ├── requirements-dev.txt         # 开发依赖
│   └── Dockerfile                   # 后端 Docker 镜像
│
├── frontend/                         # React 前端
│   ├── src/
│   │   ├── main.tsx                 # 入口文件
│   │   ├── App.tsx                  # 根组件
│   │   ├── vite-env.d.ts            # Vite 类型定义
│   │   ├── components/              # 通用组件
│   │   │   ├── ui/                  # UI 基础组件
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   └── Loading.tsx
│   │   │   ├── documents/           # 文档相关组件
│   │   │   │   ├── DocumentUpload.tsx
│   │   │   │   └── DocumentList.tsx
│   │   │   └── chat/                # 对话相关组件
│   │   │       ├── ChatInput.tsx
│   │   │       ├── ChatMessage.tsx
│   │   │       └── ConversationList.tsx
│   │   ├── pages/                   # 页面组件
│   │   │   ├── HomePage.tsx         # 首页/对话页
│   │   │   ├── DocumentsPage.tsx    # 文档管理页
│   │   │   └── SettingsPage.tsx     # 设置页
│   │   ├── services/                # API 服务
│   │   │   ├── api.ts               # Axios 实例配置
│   │   │   ├── documents.ts         # 文档 API
│   │   │   └── chat.ts              # 对话 API
│   │   ├── stores/                  # Zustand 状态管理
│   │   │   ├── useChatStore.ts      # 对话状态
│   │   │   └── useDocumentStore.ts  # 文档状态
│   │   ├── hooks/                   # 自定义 Hooks
│   │   │   ├── useSSE.ts            # SSE Hook
│   │   │   └── useDebounce.ts       # 防抖 Hook
│   │   ├── types/                   # TypeScript 类型
│   │   │   ├── document.ts          # 文档类型
│   │   │   └── chat.ts              # 对话类型
│   │   ├── utils/                   # 工具函数
│   │   │   ├── format.ts            # 格式化函数
│   │   │   └── validation.ts        # 验证函数
│   │   └── styles/                  # 样式文件
│   │       ├── index.css            # 全局样式
│   │       └── tailwind.css         # TailwindCSS 配置
│   ├── public/                      # 静态资源
│   ├── index.html                   # HTML 模板
│   ├── package.json                 # Node 依赖
│   ├── tsconfig.json                # TypeScript 配置
│   ├── vite.config.ts               # Vite 配置
│   └── tailwind.config.js           # TailwindCSS 配置
│
├── docs/                            # 项目文档
│   ├── project_plan.md              # 项目计划书
│   ├── SRS.md                       # 软件需求规格说明书
│   ├── SAD.md                       # 系统架构说明书
│   ├── DBD.md                       # 数据库设计说明书
│   └── DDD.md                       # 详细设计说明书
│
├── scripts/                         # 脚本工具
│   ├── init_db.sql                  # 数据库初始化脚本
│   ├── seed_data.py                 # 测试数据生成
│   └── deploy.sh                    # 部署脚本
│
├── .env.example                     # 环境变量示例
├── .gitignore                       # Git 忽略配置
├── docker-compose.yml               # Docker Compose 配置
├── README.md                        # 项目说明
└── LICENSE                          # 开源协议
```

---

## 2. 编码标准

### 命名规范

#### 变量命名

```python
# ✅ 正确：使用小写 + 下划线（snake_case）
user_name = "张三"
file_size = 1024
is_processing = True

# ❌ 错误：驼峰命名
userName = "张三"  # Java/JS 风格
FileSize = 1024    # 常量风格
```

```typescript
// ✅ 正确：使用小驼峰（camelCase）
const userName = "张三";
const fileSize = 1024;

// ❌ 错误：下划线命名
const user_name = "张三";  // Python 风格
```

#### 常量命名

```python
# ✅ 正确：全大写 + 下划线
MAX_FILE_SIZE = 50 * 1024 * 1024
ALLOWED_MIME_TYPES = {"application/pdf", "text/plain"}
CHUNK_SIZE = 800

# ❌ 错误：小写
max_file_size = 50 * 1024 * 1024  # 易与普通变量混淆
```

#### 类命名

```python
# ✅ 正确：大驼峰（PascalCase）
class DocumentService:
    pass

class TextChunker:
    pass

class UnsupportedFileTypeError(Exception):
    pass

# ❌ 错误：小写
class documentService:  # 像变量名
    pass
```

#### 函数/方法命名

```python
# ✅ 正确：动词 + 名词（清晰表达意图）
async def upload_document(file: UploadFile) -> DocumentDTO:
    """上传文档"""
    pass

async def retrieve_similar_chunks(query_vector: List[float]) -> List[ChunkDTO]:
    """检索相似文档块"""
    pass

def chunk_by_semantic(text: str) -> List[TextChunk]:
    """按语义分块"""
    pass

# ❌ 错误：模糊命名
async def process(data):  # 不知道处理什么
    pass

def do_something(text):  # 不知道做什么
    pass
```

#### 文件命名

```bash
# ✅ 正确：Python 使用 snake_case
document_service.py
rag_service.py
pdf_parser.py

# ✅ 正确：TypeScript/React 使用 PascalCase（组件）或 camelCase（工具）
DocumentUpload.tsx
ChatMessage.tsx
api.ts
format.ts

# ❌ 错误：混合风格
DocumentService.py  # Python 文件不应使用 PascalCase
chat-message.tsx    # 不要用中划线
```

---

### 注释规范

#### 文档字符串（Docstring）

**所有公共函数、类必须包含文档字符串**

```python
async def upload_document(
    self, 
    file: UploadFile, 
    metadata: DocumentMetadataDTO
) -> DocumentDTO:
    """
    上传并处理文档
    
    处理流程:
    1. 验证文件格式和大小
    2. 保存原始文件到本地存储
    3. 创建文档元数据记录
    4. 异步启动文档处理任务（解析→分块→向量化）
    
    Args:
        file (UploadFile): 上传的文件对象，支持 PDF/DOCX/TXT格式
        metadata (DocumentMetadataDTO): 文档元数据，包含标题、标签等
    
    Returns:
        DocumentDTO: 文档传输对象，包含文档 ID 和处理状态
    
    Raises:
        FileTooLargeError: 当文件大小超过 50MB 时抛出
        UnsupportedFileTypeError: 当文件格式不支持时抛出
        DocumentSaveError: 当文件保存失败时抛出
    
    Example:
        >>> file = UploadFile(filename="report.pdf", content_type="application/pdf")
        >>> result = await service.upload_document(file, metadata)
        >>> print(result.id)
        'doc_abc123'
    
    Note:
        该函数会立即返回，文档处理在后台异步执行
        可通过 GET /api/documents/{id} 查询处理进度
    
    See Also:
        - _process_document_async: 异步处理方法
        - get_document_status: 查询文档状态
    """
    pass
```

#### 类文档字符串

```python
class RAGService:
    """
    检索增强生成（RAG）服务
    
    负责完整的 RAG 流程:
    1. 将用户问题转换为向量
    2. 从 Pinecone 检索相似文档块
    3. 使用重排序模型优化结果
    4. 构建 Prompt 并调用 LLM 生成回答
    
    Attributes:
        embedding_svc (EmbeddingService): 嵌入向量化服务
        pinecone_svc (PineconeService): Pinecone 向量数据库服务
        rerank_svc (RerankService): 重排序服务
        llm_svc (LLMService): 大语言模型服务
    
    Example:
        >>> rag_svc = RAGService(embedding_svc, pinecone_svc, rerank_svc, llm_svc)
        >>> async for token in rag_svc.query("如何申请年假？"):
        ...     print(token, end="")
    
    Yields:
        str: 流式输出的 token
    
    Dependencies:
        - 阿里云百炼 API (qwen-max, text-embedding-v4, rerank-v3)
        - Pinecone Serverless 向量数据库
    """
    pass
```

#### 行内注释

```python
# ✅ 正确：解释"为什么"而不是"是什么"
# 使用指数退避策略，避免频繁重试导致 API 限流
retry_delay = min(2 ** attempt, 30)

# ❌ 错误：重复代码含义
i += 1  # i 加 1

# ✅ 正确：标记待优化项
# TODO(v2.0): 实现批量向量化，减少 API 调用次数
# FIXME: 处理长文档时内存占用过高，需优化分块策略
# HACK: 临时解决方案，等待 LangChain 官方修复 bug
```

---

### 错误处理

#### 异常类定义

```python
# exceptions.py
from typing import Optional

class BaseAppException(Exception):
    """
    应用基础异常类
    
    Attributes:
        code: 错误码（用于前端展示）
        message: 错误消息（对用户友好）
        details: 详细错误信息（用于调试）
        status_code: HTTP 状态码
    """
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: Optional[dict] = None,
        status_code: int = 500
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)

class DocumentException(BaseAppException):
    """文档处理相关异常"""
    pass

class FileTooLargeError(DocumentException):
    """文件过大异常"""
    def __init__(self, file_size: int, max_size: int = 50 * 1024 * 1024):
        super().__init__(
            message=f"文件大小 {file_size / 1024 / 1024:.2f}MB，超过限制 {max_size / 1024 / 1024:.2f}MB",
            code="FILE_TOO_LARGE",
            status_code=413
        )

class UnsupportedFileTypeError(DocumentException):
    """不支持的文件类型"""
    def __init__(self, mime_type: str):
        super().__init__(
            message=f"不支持的文件格式：{mime_type}",
            code="UNSUPPORTED_FILE_TYPE",
            status_code=400
        )

class RetrievalException(BaseAppException):
    """检索失败异常"""
    def __init__(self, reason: str):
        super().__init__(
            message="文档检索失败",
            code="RETRIEVAL_FAILED",
            details={"reason": reason},
            status_code=500
        )
```

#### 异常捕获最佳实践

```python
# ✅ 正确：精确捕获具体异常
async def process_document(doc_id: UUID):
    try:
        doc = await repo.find_by_id(doc_id)
        if not doc:
            raise DocumentNotFoundException(doc_id)
        
        text = await parser.parse(doc.file_path)
        chunks = chunker.chunk(text)
        await vectorize_and_store(chunks)
        
    except DocumentNotFoundException as e:
        logger.warning(f"Document not found: {e}")
        raise  # 重新抛出，让上层处理
    
    except FileParseError as e:
        logger.error(f"Parse failed: {e}", exc_info=True)
        await repo.update_status(doc_id, "failed")
        raise DocumentProcessingError("文档解析失败") from e
    
    except Exception as e:
        # 兜底异常处理
        logger.critical(f"Unexpected error: {e}", exc_info=True)
        await repo.update_status(doc_id, "failed")
        raise InternalError("服务器内部错误") from e

# ❌ 错误：过度宽泛的异常捕获
async def process_document(doc_id: UUID):
    try:
        # ... 代码
    except Exception:
        # 吞掉所有异常，难以调试
        pass
```

#### 异常链传递

```python
# ✅ 正确：保留异常链
try:
    response = await httpx.post(api_url, json=data)
    response.raise_for_status()
except httpx.HTTPStatusError as e:
    # 使用 from 保留原始异常堆栈
    raise APIRequestError(f"API 请求失败：{e.response.status_code}") from e
except httpx.RequestError as e:
    raise NetworkError(f"网络错误：{e}") from e
```

---

### 日志规范

#### 日志级别使用

```python
import structlog

logger = structlog.get_logger()

# DEBUG: 详细调试信息（仅开发环境）
logger.debug(
    "Parsing document",
    doc_id=doc_id,
    file_path=file_path,
    mime_type=mime_type
)

# INFO: 关键业务操作
logger.info(
    "Document uploaded",
    doc_id=doc_id,
    filename=filename,
    size_mb=file_size / 1024 / 1024
)

logger.info(
    "RAG query completed",
    query=query[:50],
    retrieval_time_ms=retrieval_time,
    generation_time_ms=generation_time,
    total_tokens=total_tokens
)

# WARNING: 可恢复的异常
logger.warning(
    "API retry succeeded",
    attempt=retry_count,
    delay_seconds=delay
)

# ERROR: 需要关注的错误
logger.error(
    "Document processing failed",
    doc_id=doc_id,
    error=str(e),
    traceback=traceback.format_exc()
)

# CRITICAL: 严重错误（需立即处理）
logger.critical(
    "Database connection lost",
    db_url=database_url,
    retry_count=retry_count
)
```

#### 结构化日志格式

```python
# 配置 structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()  # 输出 JSON 格式
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# 输出示例:
# {
#   "event": "rag_query_completed",
#   "level": "info",
#   "timestamp": "2026-03-04T10:00:00.000Z",
#   "query": "如何申请年假？",
#   "retrieval_time_ms": 1200,
#   "generation_time_ms": 3500,
#   "total_tokens": 450
# }
```

---

## 3. 错误处理

### 全局异常捕获机制

```python
# main.py
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.exceptions import BaseAppException

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """参数验证异常处理"""
    return JSONResponse(
        status_code=400,
        content={
            "code": "VALIDATION_ERROR",
            "message": "请求参数验证失败",
            "errors": [
                {
                    "field": ".".join(map(str, err["loc"])),
                    "message": err["msg"],
                    "type": err["type"]
                }
                for err in exc.errors()
            ]
        },
        headers={"Access-Control-Allow-Origin": "*"}
    )

@app.exception_handler(BaseAppException)
async def app_exception_handler(request, exc: BaseAppException):
    """应用自定义异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details if exc.details else None
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常兜底处理"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_ERROR",
            "message": "服务器内部错误，请稍后重试"
        }
    )
```

### 事务管理

```python
# dependencies.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # 生产环境关闭 SQL 日志
    pool_pre_ping=True,  # 连接前检查
    pool_size=20,  # 连接池大小
    max_overflow=40  # 最大溢出连接数
)

# 创建会话工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

@asynccontextmanager
async def get_db_session():
    """
    数据库会话依赖（带事务管理）
    
    Usage:
        async with get_db_session() as session:
            # 自动 commit 或 rollback
            result = await session.execute(query)
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()  # 成功则提交
    except Exception as e:
        await session.rollback()  # 失败则回滚
        logger.error(f"Transaction failed: {e}")
        raise
    finally:
        await session.close()  # 始终关闭连接
```

### 异步上下文管理

```python
# services/document_service.py
from contextlib import asynccontextmanager

class DocumentService:
    @asynccontextmanager
    async def document_lock(self, doc_id: UUID):
        """
        文档处理锁（防止并发处理同一文档）
        
        Usage:
            async with service.document_lock(doc_id):
                await self._process_document(doc_id)
        """
        lock_key = f"doc_lock:{doc_id}"
        acquired = await redis.set(lock_key, "1", nx=True, ex=300)
        
        if not acquired:
            raise DocumentProcessingConflictError(doc_id)
        
        try:
            yield
        finally:
            await redis.delete(lock_key)
```

---

## 4. 单元测试

### 测试框架配置

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.main import app

@pytest.fixture
async def db_session():
    """测试数据库会话"""
    engine = create_async_engine(
        "postgresql+asyncpg://localhost/rag_qa_test",
        echo=True
    )
    
    async with engine.begin() as conn:
        # 创建测试表
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine) as session:
        yield session
    
    async with engine.begin() as conn:
        # 清理测试数据
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client(db_session):
    """测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

### 单元测试示例

```python
# tests/unit/test_document_service.py
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.document_service import DocumentService
from app.exceptions import FileTooLargeError, UnsupportedFileTypeError

class TestDocumentService:
    """DocumentService 单元测试"""
    
    @pytest.fixture
    def mock_repo(self):
        return Mock()
    
    @pytest.fixture
    def mock_parser(self):
        return Mock()
    
    @pytest.fixture
    def service(self, mock_repo, mock_parser):
        return DocumentService(mock_repo, mock_parser)
    
    @pytest.mark.asyncio
    async def test_upload_document_success(self, service, mock_repo):
        """测试文档上传成功"""
        # Arrange
        mock_file = Mock()
        mock_file.filename = "test.pdf"
        mock_file.size = 1024 * 100  # 100KB
        mock_file.content_type = "application/pdf"
        
        mock_repo.save = AsyncMock(return_value=UUID("12345678-1234-5678-1234-567812345678"))
        
        # Act
        result = await service.upload_document(mock_file, None)
        
        # Assert
        assert result.status == "processing"
        mock_repo.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_upload_document_file_too_large(self, service):
        """测试文件过大抛出异常"""
        # Arrange
        mock_file = Mock()
        mock_file.size = 60 * 1024 * 1024  # 60MB
        
        # Act & Assert
        with pytest.raises(FileTooLargeError):
            await service.upload_document(mock_file, None)
    
    @pytest.mark.asyncio
    async def test_upload_document_unsupported_type(self, service):
        """测试不支持的文件类型"""
        # Arrange
        mock_file = Mock()
        mock_file.content_type = "image/png"
        
        # Act & Assert
        with pytest.raises(UnsupportedFileTypeError):
            await service.upload_document(mock_file, None)
    
    @pytest.mark.asyncio
    async def test_chunk_by_semantic(self, service):
        """测试语义分块算法"""
        # Arrange
        text = "第一段内容。\n\n第二段内容。\n\n第三段内容。"
        
        # Act
        chunks = service.chunk_by_semantic(text, chunk_size=50, overlap=10)
        
        # Assert
        assert len(chunks) >= 1
        assert all(len(chunk.content) <= 50 for chunk in chunks)
```

### 集成测试示例

```python
# tests/integration/test_api_endpoints.py
import pytest
from httpx import AsyncClient

class TestDocumentsAPI:
    """文档管理 API 集成测试"""
    
    @pytest.mark.asyncio
    async def test_upload_document(self, client, db_session):
        """测试上传文档接口"""
        # Prepare test file
        test_file = b"%PDF-1.4 test pdf content"
        
        files = {
            "file": ("test.pdf", test_file, "application/pdf")
        }
        data = {
            "metadata": '{"title": "Test Document"}'
        }
        
        # Send request
        response = await client.post("/api/v1/documents/upload", files=files, data=data)
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert result["code"] == 0
        assert "id" in result["data"]
        assert result["data"]["status"] == "processing"
    
    @pytest.mark.asyncio
    async def test_get_documents_list(self, client, db_session):
        """测试获取文档列表"""
        # Send request
        response = await client.get("/api/v1/documents?page=1&limit=10")
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "items" in result["data"]
        assert isinstance(result["data"]["items"], list)
```

### 测试覆盖率要求

```bash
# 执行测试并生成覆盖率报告
pytest --cov=app --cov-report=html --cov-report=term-missing

# 覆盖率目标 (>80%)
# Name                           Stmts   Miss  Cover   Missing
# --------------------------------------------------------------
# app/services/document_service.py  120      8    93%   45-48, 89-92
# app/services/rag_service.py       150     15    90%   78-82, 120-125
# app/parsers/pdf_parser.py          45      5    89%   23-27
# --------------------------------------------------------------
# TOTAL                              800     65    92%

# 强制要求:
# - 总体覆盖率 > 80%
# - 核心模块（services/）覆盖率 > 90%
# - 无未测试的关键路径
```

---

## 5. 构建与运行

### 环境要求

**后端**:
- Python 3.9+
- PostgreSQL 14+ (可选，MVP 可只用 Pinecone)
- Redis 6+ (可选，用于缓存)

**前端**:
- Node.js 18+
- npm 9+ 或 pnpm 8+

**基础设施**:
- Pinecone Serverless 账号
- 阿里云百炼 API Key

### 安装步骤

#### 后端

```bash
cd backend

# 1. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 复制环境变量配置
cp ../.env.example .env
# 编辑 .env 填入实际配置

# 4. 初始化数据库（如使用 PostgreSQL）
python -m sqlalchemy db init
python -m sqlalchemy db migrate

# 5. 运行开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端

```bash
cd frontend

# 1. 安装依赖
npm install

# 2. 复制环境变量
cp .env.example .env.local

# 3. 启动开发服务器
npm run dev

# 访问 http://localhost:5173
```

### Docker 部署

```bash
# 使用 Docker Compose 一键部署
docker-compose up -d

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 停止服务
docker-compose down

# 清理数据卷（谨慎使用）
docker-compose down -v
```

---

## 6. 性能优化指南

### 异步 I/O 最佳实践

```python
# ✅ 正确：使用异步 HTTP 客户端
import httpx

async def call_embedding_api(texts: List[str]):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.example.com/embeddings",
            json={"texts": texts},
            timeout=30.0
        )
        return response.json()

# ❌ 错误：阻塞式同步调用（会降低并发性能）
import requests

def call_embedding_api_sync(texts: List[str]):
    response = requests.post(...)  # 阻塞整个事件循环
    return response.json()
```

### 批量处理优化

```python
# ✅ 正确：批量向量化减少 API 调用
async def batch_embed_documents(texts: List[str], batch_size: int = 32):
    """批量向量化（32 个一组）"""
    batches = [texts[i:i+batch_size] for i in range(0, len(texts), batch_size)]
    
    # 并发执行多个批量请求
    tasks = [embed_batch(batch) for batch in batches]
    results = await asyncio.gather(*tasks)
    
    return [vec for batch_result in results for vec in batch_result]

# ❌ 错误：逐个调用（效率低）
async def embed_documents_one_by_one(texts: List[str]):
    results = []
    for text in texts:
        vec = await embed_single(text)  # 每次都发起新请求
        results.append(vec)
    return results
```

### 缓存策略

```python
from functools import lru_cache
from cachetools import TTLCache

# LRU 缓存（适合不变数据）
@lru_cache(maxsize=100)
def get_document_metadata(doc_id: str):
    return db.query(Document).filter(Document.id == doc_id).first()

# TTL 缓存（适合有过期时间的数据）
embedding_cache = TTLCache(maxsize=1000, ttl=3600)  # 1 小时过期

async def get_cached_embedding(text: str):
    if text in embedding_cache:
        return embedding_cache[text]
    
    vector = await call_embedding_api(text)
    embedding_cache[text] = vector
    return vector
```

---

## 7. 安全规范

### 输入验证

```python
from pydantic import BaseModel, Field, validator
import re

class DocumentUploadSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    tags: List[str] = Field(default_factory=list)
    
    @validator('title')
    def validate_title(cls, v):
        # 防止 XSS
        if re.search(r'<script.*?>', v, re.IGNORECASE):
            raise ValueError("标题包含非法 HTML 标签")
        return v.strip()
    
    @validator('tags')
    def validate_tags(cls, v):
        # 限制标签数量和长度
        if len(v) > 10:
            raise ValueError("最多 10 个标签")
        if any(len(tag) > 50 for tag in v):
            raise ValueError("标签长度不能超过 50")
        return v
```

### 速率限制

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/chat")
@limiter.limit("60/minute")  # 单 IP 每分钟最多 60 次
async def chat_endpoint(request: Request, query: ChatQuery):
    ...
```

---

**版本**: v1.0  
**更新日期**: 2026-03-04  
**审批人**: [技术负责人]
