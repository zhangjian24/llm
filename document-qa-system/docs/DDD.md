# RAG 文档问答系统 - 详细设计说明书 (DDD)

## 1. DocumentService 模块详细设计

### 模块名称：DocumentService

**职责描述**: 负责文档的上传、解析、分块、向量化编排及元数据管理

### 类/组件设计

#### 类图

```mermaid
classDiagram
    class DocumentService {
        -DocumentRepository doc_repo
        -EmbeddingService embedding_svc
        -PineconeService pinecone_svc
        +upload_document(file, metadata) DocumentDTO
        +parse_document(file) str
        +chunk_document(text) List[ChunkDTO]
        +vectorize_chunks(chunks, doc_id) void
        +get_document_list(page, limit) Page~DocumentDTO~
        +delete_document(doc_id) void
    }
    
    class DocumentParser {
        <<interface>>
        +parse(file: bytes) str
    }
    
    class PDFParser {
        -PyMuPDF pdf
        +parse(file: bytes) str
        -extract_text_from_page(page_num) str
    }
    
    class DocxParser {
        -python-docx doc
        +parse(file: bytes) str
    }
    
    class TextChunker {
        -int chunk_size
        -int overlap
        +chunk_by_semantic(text) List[TextChunk]
        -split_by_paragraph(text) List[str]
        -merge_to_target_size(segments) List[str]
    }
    
    class DocumentRepository {
        -Database db
        +save(doc: DocumentEntity) UUID
        +find_by_id(doc_id) Optional[DocumentEntity]
        +find_all(page, limit) Page~DocumentEntity~
        +delete(doc_id) void
        +update_status(doc_id, status, chunks_count) void
    }
    
    DocumentService --> DocumentParser : uses
    DocumentService --> TextChunker : uses
    DocumentService --> DocumentRepository : uses
    DocumentParser <|.. PDFParser : implements
    DocumentParser <|.. DocxParser : implements
```

#### 核心类说明

##### 1. `DocumentService`

**职责**: 文档处理流程编排

**核心方法**:

```python
async def upload_document(
    self, 
    file: UploadFile, 
    metadata: DocumentMetadataDTO
) -> DocumentDTO:
    """
    上传并处理文档
    
    参数:
        file: 上传的文件对象
        metadata: 元数据（标题、标签等）
    
    返回:
        DocumentDTO: 文档 DTO（包含 id, status）
    
    异常:
        UnsupportedFileTypeError: 文件格式不支持
        FileTooLargeError: 文件超过 50MB
        DocumentParseError: 解析失败
    """
    # 1. 验证文件
    await self._validate_file(file)
    
    # 2. 保存原始文件
    file_path = await self._save_file(file)
    
    # 3. 创建文档记录
    doc_id = await self.doc_repo.save(
        DocumentEntity(
            filename=file.filename,
            file_path=file_path,
            file_size=file.size,
            mime_type=file.content_type,
            status="processing"
        )
    )
    
    # 4. 异步处理文档（不阻塞响应）
    asyncio.create_task(self._process_document_async(doc_id))
    
    return DocumentDTO(id=doc_id, status="processing")
```

```python
async def _process_document_async(self, doc_id: UUID):
    """
    异步处理文档（解析→分块→向量化）
    
    异常处理:
        任何步骤失败都会更新状态为 failed
    """
    try:
        # 1. 获取文档信息
        doc = await self.doc_repo.find_by_id(doc_id)
        
        # 2. 读取文件内容
        async with aiofiles.open(doc.file_path, 'rb') as f:
            file_content = await f.read()
        
        # 3. 解析文档
        parser = self._get_parser(doc.mime_type)
        text_content = await parser.parse(file_content)
        
        # 4. 文本分块
        chunker = TextChunker(chunk_size=800, overlap=150)
        chunks = chunker.chunk_by_semantic(text_content)
        
        # 5. 向量化并存储到 Pinecone
        await self.vectorize_chunks(chunks, doc_id)
        
        # 6. 更新状态为 ready
        await self.doc_repo.update_status(
            doc_id, 
            status="ready", 
            chunks_count=len(chunks)
        )
        
    except Exception as e:
        # 失败时更新状态
        await self.doc_repo.update_status(doc_id, status="failed")
        logger.error(f"Document processing failed: {e}")
        raise
```

##### 2. `TextChunker`

**职责**: 智能文本分块（按语义边界）

**核心算法逻辑**:

```python
def chunk_by_semantic(self, text: str) -> List[TextChunk]:
    """
    基于语义边界的分块算法
    
    策略:
    1. 先按段落分割（保留语义完整性）
    2. 过大的段落按句子二次分割
    3. 合并小段落至目标大小范围
    """
    # Step 1: 按段落分割
    paragraphs = self._split_by_paragraph(text)
    
    # Step 2: 过滤空段落
    paragraphs = [p for p in paragraphs if p.strip()]
    
    # Step 3: 合并段落至目标大小
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) <= self.chunk_size:
            # 可以合并到当前块
            current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        else:
            # 当前块已满，保存并开始新块
            if current_chunk:
                chunks.append(TextChunk(content=current_chunk))
            current_chunk = paragraph
    
    # 添加最后一个块
    if current_chunk:
        chunks.append(TextChunk(content=current_chunk))
    
    return chunks
```

**流程图**:

```mermaid
graph TD
    A[原始文本] --> B[按段落分割]
    B --> C[过滤空段落]
    C --> D{当前段落 + 当前块 <= 800 tokens?}
    D -->|是 | E[合并到当前块]
    D -->|否 | F[保存当前块]
    F --> G[开始新块]
    E --> H{还有段落？}
    G --> H
    H -->|是 | D
    H -->|否 | I[保存最后块]
    I --> J[输出 chunks 列表]
```

---

### 时序流程

#### 文档上传与处理完整流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant FE as 前端
    participant API as DocumentAPI
    participant DS as DocumentService
    participant Parser as DocumentParser
    participant Chunker as TextChunker
    participant EmbSvc as EmbeddingService
    participant Pinecone as PineconeService
    participant Repo as DocumentRepository
    
    User->>FE: 选择文件并上传
    FE->>API: POST /api/documents/upload (multipart/form-data)
    API->>DS: upload_document(file, metadata)
    
    DS->>DS: validate_file(file)
    DS->>Repo: save(DocumentEntity)
    Repo-->>DS: doc_id
    
    DS-->>API: DocumentDTO(id, status="processing")
    API-->>FE: 200 OK + document info
    FE-->>User: 显示"上传成功，处理中"
    
    Note over DS: 异步处理开始
    
    DS->>Parser: parse(file_content)
    Parser-->>DS: text_content
    
    DS->>Chunker: chunk_by_semantic(text)
    Chunker-->>DS: List[TextChunk]
    
    loop 每个 chunk
        DS->>EmbSvc: embed(chunk.content)
        EmbSvc->>Bailian: text-embedding-v4 API
        Bailian-->>EmbSvc: vector[1536]
        EmbSvc-->>DS: embedding
        
        DS->>Pinecone: upsert(id, vector, metadata)
        Pinecone-->>DS: success
    end
    
    DS->>Repo: update_status(doc_id, "ready", chunks_count)
    Repo-->>DS: success
```

---

## 2. RAGService 模块详细设计

### 模块名称：RAGService

**职责描述**: 负责检索增强生成流程（语义检索→重排序→回答生成）

### 类/组件设计

#### 类图

```mermaid
classDiagram
    class RAGService {
        -EmbeddingService embedding_svc
        -PineconeService pinecone_svc
        -RerankService rerank_svc
        -LLMService llm_svc
        -ChatService chat_svc
        +query(question, conversation_id) AsyncGenerator
        -embed_query(question) vector
        -retrieve_similar_chunks(query_vector, top_k) List[ChunkDTO]
        -rerank_results(chunks, question) List[ChunkDTO]
        -build_prompt(question, context, history) str
        -generate_stream(prompt) AsyncGenerator
    }
    
    class RerankService {
        -str model_name
        +rerank(chunks, query) List[RerankedChunk]
        -call_bailian_rerank(query, texts) RerankResponse
    }
    
    class LLMService {
        -ChatOpenAI llm
        -float temperature
        +generate_stream(prompt) AsyncGenerator[str]
        +generate(prompt) str
    }
    
    class PromptBuilder {
        -str system_template
        +build(question, context, history) str
        -format_context(chunks) str
        -format_history(messages) str
    }
    
    RAGService --> EmbeddingService : uses
    RAGService --> PineconeService : uses
    RAGService --> RerankService : uses
    RAGService --> LLMService : uses
    RAGService --> PromptBuilder : uses
```

#### 核心方法说明

##### `RAGService.query()`

```python
async def query(
    self,
    question: str,
    conversation_id: Optional[UUID] = None,
    top_k: int = 10,
    rerank_top_k: int = 5
) -> AsyncGenerator[str, None]:
    """
    RAG 查询主流程（流式响应）
    
    参数:
        question: 用户问题
        conversation_id: 对话 ID（可选，用于上下文）
        top_k: 初始检索数量
        rerank_top_k: 重排序后保留数量
    
    返回:
        AsyncGenerator[str]: 流式输出的 token
    
    异常:
        RetrievalError: 检索失败
        GenerationError: 生成失败
    """
    # 1. 加载对话历史
    history = await self.chat_svc.get_conversation(conversation_id) \
              if conversation_id else []
    
    # 2. 将问题转换为向量
    query_vector = await self.embed_query(question)
    
    # 3. 语义检索
    similar_chunks = await self.retrieve_similar_chunks(
        query_vector, 
        top_k=top_k
    )
    
    # 4. 重排序优化
    reranked_chunks = await self.rerank_results(
        similar_chunks, 
        question,
        keep_top_k=rerank_top_k
    )
    
    # 5. 过滤低相关性结果
    filtered_chunks = [
        chunk for chunk in reranked_chunks 
        if chunk.score >= 0.7
    ]
    
    # 6. 构建 Prompt
    prompt = self.build_prompt(
        question=question,
        context=filtered_chunks,
        history=history
    )
    
    # 7. 流式生成回答
    async for token in self.generate_stream(prompt):
        yield token
    
    # 8. 保存对话记录
    if conversation_id:
        await self.chat_svc.add_message(
            conversation_id,
            role="user",
            content=question
        )
        await self.chat_svc.add_message(
            conversation_id,
            role="assistant",
            content="".join([token async for token in self.generate_stream(prompt)])
        )
```

##### `RerankService.rerank()`

```python
async def rerank(
    self,
    chunks: List[ChunkDTO],
    query: str,
    keep_top_k: int = 5
) -> List[RerankedChunk]:
    """
    使用阿里云百炼 rerank-v3 进行重排序
    
    参数:
        chunks: 初始检索结果
        query: 用户问题
        keep_top_k: 保留数量
    
    返回:
        List[RerankedChunk]: 重排序后的结果
    """
    # 准备输入
    texts = [chunk.content for chunk in chunks]
    
    # 调用百炼 API
    response = await self._call_bailian_rerank(
        query=query,
        texts=texts,
        model="rerank-v3"
    )
    
    # 解析结果
    reranked_results = []
    for item in response.results:
        original_chunk = chunks[item.index]
        reranked_chunk = RerankedChunk(
            **original_chunk.dict(),
            score=item.relevance_score
        )
        reranked_results.append(reranked_chunk)
    
    # 按分数降序排列
    reranked_results.sort(key=lambda x: x.score, reverse=True)
    
    return reranked_results[:keep_top_k]
```

---

### RAG 问答时序图

```mermaid
sequenceDiagram
    participant User as 用户
    participant FE as 前端
    participant ChatAPI as ChatAPI
    participant RAG as RAGService
    participant EmbSvc as EmbeddingService
    participant Pinecone as Pinecone
    participant Rerank as RerankService
    participant LLM as LLMService
    
    User->>FE: 输入问题
    FE->>ChatAPI: POST /api/chat (SSE)
    ChatAPI->>RAG: query(question, conversation_id)
    
    RAG->>EmbSvc: embed_query(question)
    EmbSvc->>Bailian: embedding API
    Bailian-->>EmbSvc: query_vector[1536]
    EmbSvc-->>RAG: query_vector
    
    RAG->>Pinecone: similarity_search(vector, top_k=10)
    Pinecone-->>RAG: 10 chunks
    
    RAG->>Rerank: rerank(chunks, question)
    Rerank->>Bailian: rerank-v3 API
    Bailian-->>Rerank: relevance_scores
    Rerank-->>RAG: 5 reranked chunks
    
    RAG->>RAG: build_prompt(question, context, history)
    RAG->>LLM: generate_stream(prompt)
    LLM->>Bailian: qwen-max stream
    Bailian-->>LLM: token stream
    
    loop 每个 token
        LLM-->>RAG: token
        RAG-->>ChatAPI: SSE data: {"token": "..."}
        ChatAPI-->>FE: Server-Sent Event
        FE-->>User: 逐字显示
    end
    
    Bailian-->>LLM: done
    LLM-->>RAG: generation complete
    RAG-->>ChatAPI: SSE data: {"done": true}
```

---

## 3. 接口设计 (API Specification)

### 接口列表

#### 3.1 `POST /api/v1/documents/upload`

**描述**: 上传单个文档

**请求头**:
```http
Content-Type: multipart/form-data
Authorization: Bearer {token} (可选，MVP 无需认证)
```

**请求体**:
```json
{
  "file": "<binary>",
  "metadata": {
    "title": "员工手册",
    "tags": ["HR", "制度"]
  }
}
```

**响应体 (200 OK)**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "doc_abc123",
    "filename": "employee_handbook.pdf",
    "status": "processing",
    "chunks_count": null,
    "created_at": "2026-03-04T10:00:00Z"
  }
}
```

**错误码定义**:

| 错误码 | HTTP 状态码 | 说明 |
|--------|-------------|------|
| `FILE_TOO_LARGE` | 413 | 文件超过 50MB |
| `UNSUPPORTED_FILE_TYPE` | 400 | 文件格式不支持 |
| `FILE_CORRUPTED` | 400 | 文件损坏 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |

---

#### 3.2 `GET /api/v1/documents`

**描述**: 获取文档列表（分页、筛选、排序）

**请求参数**:
```http
GET /api/v1/documents?page=1&limit=20&status=ready&sort=-created_at
```

**响应体 (200 OK)**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 45,
    "items": [
      {
        "id": "doc_abc123",
        "filename": "report.pdf",
        "file_size": 2458624,
        "mime_type": "application/pdf",
        "status": "ready",
        "chunks_count": 32,
        "created_at": "2026-03-04T10:00:00Z"
      }
    ],
    "page": 1,
    "limit": 20,
    "total_pages": 3
  }
}
```

---

#### 3.3 `DELETE /api/v1/documents/{id}`

**描述**: 删除文档（级联删除 Pinecone 中的向量）

**请求参数**:
```http
DELETE /api/v1/documents/doc_abc123
```

**响应体 (204 No Content)**:
```http
HTTP/1.1 204 No Content
```

**错误码**:

| 错误码 | HTTP 状态码 | 说明 |
|--------|-------------|------|
| `DOCUMENT_NOT_FOUND` | 404 | 文档不存在 |

---

#### 3.4 `POST /api/v1/chat`

**描述**: 发起对话（流式 SSE）

**请求头**:
```http
Content-Type: application/json
Accept: text/event-stream
```

**请求体**:
```json
{
  "query": "如何申请年假？",
  "top_k": 5,
  "stream": true,
  "conversation_id": "conv_xyz789"
}
```

**响应体 (SSE Stream)**:
```
data: {"token": "根"}
data: {"token": "据"}
data: {"token": "公"}
...
data: {"done": true, "conversation_id": "conv_xyz789"}
```

**错误码**:

| 错误码 | HTTP 状态码 | 说明 |
|--------|-------------|------|
| `QUERY_EMPTY` | 400 | 问题不能为空 |
| `RETRIEVAL_FAILED` | 500 | 检索失败 |
| `GENERATION_FAILED` | 500 | 生成失败 |

---

#### 3.5 `GET /api/v1/conversations`

**描述**: 获取对话历史列表

**请求参数**:
```http
GET /api/v1/conversations?limit=10
```

**响应体 (200 OK)**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "conv_xyz789",
        "title": "年假申请流程",
        "last_message": "根据公司规定...",
        "turns": 5,
        "updated_at": "2026-03-04T12:30:00Z"
      }
    ]
  }
}
```

---

## 4. 异常处理设计

### 全局异常捕获机制

```python
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """参数验证异常处理"""
    return JSONResponse(
        status_code=400,
        content={
            "code": "VALIDATION_ERROR",
            "message": "请求参数验证失败",
            "errors": exc.errors()
        }
    )

@app.exception_handler(DocumentException)
async def document_exception_handler(request, exc):
    """文档处理异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message
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

**事务边界**:
```python
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

@asynccontextmanager
async def transactional_session(db: AsyncSession):
    """
    事务上下文管理器
    """
    try:
        yield db
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise
    finally:
        await db.close()

# 使用示例
async def upload_document(self, file: UploadFile):
    async with transactional_session(self.db) as session:
        # 1. 保存文档记录
        doc_id = await self.repo.save(session, doc_entity)
        
        # 2. 保存文件到本地
        await self._save_file(session, file)
        
        # 3. 提交事务（自动 commit 或 rollback）
```

**隔离级别**: Read Committed（PostgreSQL 默认）

**回滚策略**:
- 数据库操作失败 → 自动 rollback
- Pinecone 操作失败 → 手动 rollback + 清理已插入向量

---

### 日志记录

**关键日志点**:

```python
import structlog

logger = structlog.get_logger()

# 1. 文档上传
logger.info(
    "document_upload_started",
    doc_id=doc_id,
    filename=file.filename,
    size=file.size
)

# 2. 向量化完成
logger.info(
    "document_vectorized",
    doc_id=doc_id,
    chunks_count=len(chunks),
    duration_ms=duration_ms
)

# 3. RAG 查询
logger.info(
    "rag_query_executed",
    query=question[:50],
    retrieval_time_ms=retrieval_time,
    rerank_time_ms=rerank_time,
    generation_time_ms=generation_time
)

# 4. 异常日志
logger.error(
    "document_processing_failed",
    doc_id=doc_id,
    error=str(e),
    traceback=traceback.format_exc()
)
```

**日志格式**:
```json
{
  "timestamp": "2026-03-04T10:00:00Z",
  "level": "INFO",
  "event": "document_upload_started",
  "doc_id": "abc123",
  "filename": "report.pdf",
  "size": 2458624
}
```

---

## 5. 安全实现细节

### 输入验证

#### 防 SQL 注入

```python
# ✅ 使用 ORM 参数化查询（安全）
async def get_document_by_id(self, doc_id: UUID):
    result = await self.db.execute(
        select(Document).where(Document.id == doc_id)
    )
    return result.scalar_one_or_none()

# ❌ 禁止字符串拼接（危险）
async def get_document_unsafe(self, doc_id: str):
    sql = f"SELECT * FROM documents WHERE id = '{doc_id}'"
    result = await self.db.execute(sql)  # SQL 注入风险！
```

#### 防 XSS 攻击

```python
from html import escape

def sanitize_user_input(text: str) -> str:
    """
    过滤用户输入中的 HTML 标签
    """
    # 转义特殊字符
    text = escape(text, quote=True)
    
    # 移除 script 标签
    text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    return text

# 在保存到数据库前调用
async def add_message(self, content: str):
    sanitized_content = sanitize_user_input(content)
    # ... 保存逻辑
```

### 权限控制

**MVP 阶段**: 无需登录（公开访问）

**未来扩展（RBAC 模型）**:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserDTO:
    """
    解析 JWT Token 获取当前用户
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return UserDTO(id=user_id)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token expired")

# 路由保护
@router.delete("/documents/{id}")
async def delete_document(
    doc_id: UUID,
    current_user: UserDTO = Depends(get_current_user)
):
    """
    仅允许文档所有者删除
    """
    doc = await doc_service.get_document(doc_id)
    if doc.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )
    await doc_service.delete_document(doc_id)
```

---

## 6. 配置管理

### 环境变量配置

```python
# config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "RAG Document QA System"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://localhost/rag_qa"
    
    # Pinecone 配置
    PINECONE_API_KEY: str
    PINECONE_HOST: str
    PINECONE_INDEX_NAME: str = "rag-documents"
    
    # 阿里云百炼配置
    DASHSCOPE_API_KEY: str
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/api/v1"
    
    # 模型配置
    LLM_MODEL: str = "qwen-max"
    EMBEDDING_MODEL: str = "text-embedding-v4"
    RERANK_MODEL: str = "rerank-v3"
    
    # RAG 配置
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150
    RAG_TOP_K: int = 10
    RERANK_TOP_K: int = 5
    RELEVANCE_THRESHOLD: float = 0.7
    
    # 文件上传配置
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_MIME_TYPES: set = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/markdown",
        "text/plain"
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

### .env.example

```bash
# 应用配置
APP_NAME=RAG Document QA System
DEBUG=true
VERSION=1.0.0

# 数据库配置
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/rag_qa

# Pinecone 配置
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_HOST=your-pinecone-host
PINECONE_INDEX_NAME=rag-documents

# 阿里云百炼配置
DASHSCOPE_API_KEY=your-dashscope-api-key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/api/v1

# 模型配置
LLM_MODEL=qwen-max
EMBEDDING_MODEL=text-embedding-v4
RERANK_MODEL=rerank-v3

# RAG 配置
CHUNK_SIZE=800
CHUNK_OVERLAP=150
RAG_TOP_K=10
RERANK_TOP_K=5
RELEVANCE_THRESHOLD=0.7

# 文件上传配置
MAX_FILE_SIZE_MB=50
```

---

**文档审批签字**:

| 角色 | 姓名 | 签字 | 日期 |
|------|------|------|------|
| 技术负责人 | | | |
| 后端负责人 | | | |
| 前端负责人 | | | |

---

**变更历史**:
| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|----------|
| v1.0 | 2026-03-04 | AI 技术负责人 | 初始版本 |
