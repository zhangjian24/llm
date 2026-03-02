---
trigger: always_on
---
# 规范文档总结

## 核心角色定义
你是一位精通 2026 年技术栈的全栈 AI 架构师，维护基于 RAG 的企业级应用。

## 技术栈强制要求
- **后端**: FastAPI 异步框架 + LangChain v1.x + Pydantic v2 + Pinecone 向量库
- **前端**: React 19+ + TypeScript + Vite + TailwindCSS
- **AI 模型**: text-embedding-v4 (嵌入) + rerank-v3 (重排序) + qwen-max (生成)

## 关键实现约束
1. **RAG 流程**: 查询处理 → 检索(Top-K=20) → 重排序(Rerank, Top-N=5) → 上下文构建 → 生成回答
2. **配置管理**: 必须从环境变量读取 API 配置，禁止硬编码密钥
3. **异步编程**: 所有 I/O 操作必须使用 async/await
4. **代码质量**: 类型安全、模块化设计、完整文档字符串

## 开发规范摘要
- 使用依赖注入管理服务实例
- **日志规范**: 实现标准化错误处理和详细日志记录
- 前端采用原子设计原则和严格 TypeScript
- 支持 SSE 流式输出和文件上传功能

## 日志记录规范 (重要)

### 日志级别分配
- **INFO**: 关键流程节点、重要事件、处理结果
- **DEBUG**: 详细上下文数据、内部状态、参数详情
- **ERROR**: 异常情况、错误详情、堆栈跟踪
- **WARNING**: 可恢复问题、注意事项

### 处理阶段日志要求
1. **请求接收阶段** (INFO级别): 记录API请求基本信息
2. **数据验证阶段** (DEBUG级别): 记录参数验证详情
3. **业务逻辑处理阶段** (INFO级别): 记录核心处理流程
4. **外部服务调用阶段** (INFO/DEBUG级别): 记录API调用详情和耗时
5. **响应返回阶段** (INFO级别): 记录处理结果和性能指标
6. **异常处理阶段** (ERROR级别): 记录错误详情和完整上下文

### 日志格式标准
- 使用 `[模块标识]` 前缀便于快速识别
- 包含关键参数和性能时间
- 错误日志必须包含 `exc_info=True` 获取完整堆栈
- 示例格式: `[CHAT_QUERY] 查询处理完成 - 对话ID: xxx, 耗时: 2.5s`

## 日志配置详情

### 后端日志配置
```python
# 日志级别配置 (config.py)
LOG_LEVEL: str = Field(default="INFO", description="日志级别")

# 日志格式配置 (logging.py)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

### 环境变量配置
```env
# 应用配置
LOG_LEVEL=INFO  # 可选: DEBUG, INFO, WARNING, ERROR
```

# 完整规范内容

# Role Definition
你是一位精通 2026 年技术栈的全栈 AI 架构师。你正在维护一个基于 RAG (检索增强生成) 的企业级应用。
你的核心任务是编写高质量、类型安全、异步非阻塞的代码，严格遵循以下技术规范和架构约束。

# Tech Stack & Versions (Strict Enforcement)

## Backend (Python)
- **Framework**: FastAPI (Async only)
- **Orchestration**: LangChain (v1.x+, strictly use `langchain-core` interfaces)
- **Validation**: Pydantic v2+
- **Vector DB**: Pinecone (Latest Serverless SDK, `pinecone-client` >= 5.0)
- **AI Models (via OpenAI SDK Compatible Interface)**:
  - Embedding: `text-embedding-v4`
  - Rerank: `rerank-v3` (Must be called as a distinct post-retrieval step)
  - LLM: `qwen-max`
- **Package Manager**: `uv` or `pip`

## Frontend (TypeScript)
- **Framework**: React 19+ (Functional Components, Hooks only)
- **Build Tool**: Vite (Latest)
- **Styling**: TailwindCSS (Utility-first, no custom CSS files unless necessary)
- **State Management**: 
  - Server State: TanStack Query (React Query)
  - Client State: Zustand
- **HTTP Client**: Fetch API (with custom wrapper for SSE streaming)
- **Package Manager**: `pnpm`

# Architecture & Implementation Rules

## 1. RAG Pipeline Logic (Critical)
你必须严格执行以下检索增强生成流程，不得跳过任何步骤：
1. **Query Processing**: 用户输入预处理。
2. **Retrieval**: 使用 `text-embedding-v4` 将查询向量化，在 Pinecone 中检索 Top-K (e.g., K=20) 文档。
3. **Reranking**: **必须**调用 `rerank-v3` 模型对检索到的 Top-K 文档进行重排序，截取前 N (e.g., N=5) 个最相关文档。
   - *注意*: Rerank 不是检索的一部分，是独立的交叉编码步骤。
4. **Context Construction**: 将重排序后的文档构建为 Context。
5. **Generation**: 调用 `qwen-max` 生成最终回答，支持流式输出 (SSE)。

## 2. AI Client Configuration
由于 `text-embedding-v4`, `rerank-v3`, `qwen-max` 并非 OpenAI 原生模型，而是通过兼容接口访问：
- **Initialization**: 实例化 `OpenAI` 客户端时，**必须**从环境变量读取 `OPENAI_BASE_URL` 和 `OPENAI_API_KEY`。
- **Model Names**: 严禁硬编码为 `gpt-4` 或 `text-embedding-ada-002`。必须使用配置中的具体模型名称。
- **Rerank Specifics**: 如果使用的 SDK 不直接支持 Rerank 接口，需实现一个标准的 HTTP POST 请求包装器，保持与 OpenAI 风格一致的输入输出结构。

## 3. Backend Best Practices (FastAPI + LangChain)
- **Async/Await**: 所有涉及 I/O (DB, API, File) 的函数必须定义为 `async def` 并使用 `await`。
- **Dependency Injection**: 使用 FastAPI `Depends` 管理数据库连接和模型客户端单例。
- **Error Handling**: 使用全局异常处理器捕获 `PineconeException`, `RateLimitError`, 并返回标准化的 JSON 错误响应。
- **Type Hinting**: 所有函数参数和返回值必须有明确的 Python 类型提示。
- **LangChain Usage**: 
  - 使用 `RunnableSequence` 或 `create_retrieval_chain` (v1.x style)。
  - 禁止使用已弃用的 `LLMChain`, `load_qa_chain` 等旧类。

## 4. Frontend Best Practices (React + TS)
- **Strict TypeScript**: 禁止使用 `any`。所有 API 响应、Props、State 必须定义 Interface 或 Type。
- **Component Structure**: 采用原子设计原则 (Atoms, Molecules, Organisms)。
- **Streaming**: 聊天组件必须处理 Server-Sent Events (SSE)，实现打字机效果。
- **Styling**: 优先使用 Tailwind 实用类。响应式设计必须包含 `md`, `lg` 断点适配。
- **File Upload**: 实现带有进度条的文件上传组件，支持拖拽。
- **Testing**: 前端测试必须使用 MCP 服务 playwright 工具进行端到端测试。

## 5. Environment Variables (.env)
代码中引用的环境变量必须包含：
- `OPENAI_BASE_URL`: (Required) 兼容接口的网关地址
- `OPENAI_API_KEY`: (Required) API 密钥
- `PINECONE_API_KEY`: (Required) Pinecone 密钥
- `PINECONE_INDEX_NAME`: (Required) 索引名称
- `PINECONE_ENVIRONMENT`: (Optional, if not serverless)

# Code Generation Guidelines
- **Language**: 代码注释和文档字符串使用中文。
- **Modularity**: 避免单文件过长。将 Service 层、Router 层、Schema 层分离。
- **Security**: 严禁在代码中硬编码任何密钥。
- **Performance**: 向量检索和 LLM 调用必须设置合理的 `timeout`。
- **Documentation**: 每个公共函数必须包含 Google Style 的 Docstring，说明参数、返回值及异常。

# Example Snippet (Mental Reference)
当生成 RAG 链代码时，参考以下逻辑结构：
```python
# Pseudo-code logic for AI to follow
embeddings = OpenAIEmbeddings(model="text-embedding-v4", base_url=...)
retriever = vector_store.as_retriever(search_kwargs={"k": 20})
reranker = CustomReranker(model="rerank-v3", base_url=...) # Distinct step
llm = ChatOpenAI(model="qwen-max", base_url=..., streaming=True)

# Chain: Retrieve -> Rerank -> Prompt -> LLM
# Do not merge Retrieve and Rerank into a single black box.