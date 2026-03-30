# AI教育平台全栈工程师学习蓝图（最终版）

---

## 一、总体目标

构建一个以**Java为核心**、**AI为能力增强**的智能教育平台，培养具备以下能力的全栈工程师：

- **Java后端**：10年Java工程师核心能力（分布式、微服务、高并发、性能优化）
- **Python AI**：LLM应用开发、RAG知识库构建、AI Agent开发
- **前端**：uni-app多端开发（Web/小程序/App）
- **架构**：微服务架构 + K3s容器化部署

---

## 二、技术栈总览

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| **后端-业务** | Java 17 + Spring Boot 3.x + Spring Cloud Alibaba | 核心业务逻辑 |
| **后端-AI** | Python 3.11 + FastAPI + LangChain | AI推理服务 |
| **后端-网关** | NestJS + Fastify | 高性能API网关 |
| **数据库** | PostgreSQL 15 + pgvector | 统一存储（业务+向量） |
| **缓存** | Redis 7 + Redis Stack | 分布式缓存 |
| **消息队列** | Kafka 3.x | 异步通信 |
| **注册中心** | Nacos 2.x | 服务注册与配置 |
| **LLM** | 通义千问（Qwen） | OpenAI兼容API |
| **前端** | uni-app + TailwindCSS + uView Plus | 多端统一开发 |
| **部署** | K3s + Docker + Helm | 轻量级K8s |

---

## 三、项目命名

| 项目 | 名称 |
|------|------|
| **父项目** | `edu-ai-platform` |
| **用户服务** | `edu-user-service` |
| **课程服务** | `edu-course-service` |
| **作业服务** | `edu-homework-service` |
| **考试服务** | `edu-exam-service` |
| **AI服务** | `edu-ai-service` |
| **网关** | `edu-gateway` |
| **前端** | `edu-web` |

---

## 四、版本演进总览

| 版本 | 阶段 | 后端技术 | 前端技术 | AI能力 | 产品形态 | 博客数 | 周期 |
|------|------|----------|----------|--------|----------|--------|------|
| **v0.1** | 基础架构 | Java + Nacos | uni-app | - | 用户/权限系统 | 7篇 | 2周 |
| **v0.2** | 业务完善 | Java + Redis | uni-app | - | 课程/作业/考试/答疑 | 7篇 | 2周 |
| **v0.3** | 分布式基础 | Java + Kafka | uni-app | - | 服务治理/分布式事务 | 7篇 | 2周 |
| **v1.0** | AI接入 | Java + Python | uni-app | LLM对话 | AI智能问答 | 8篇 | 2周 |
| **v1.1** | 向量检索 | Java + Python | uni-app | RAG | 知识库问答 | 8篇 | 2周 |
| **v1.2** | 基础Agent | Java + Python | uni-app | 单Agent | 作业批改/智能出题 | 8篇 | 2周 |
| **v1.3** | 高级Agent | Java + Python | uni-app | 多Agent | 学习规划/Agent协作 | 8篇 | 3周 |
| **v1.5** | 高并发 | Java + Python + NestJS | uni-app | 性能优化 | 网关/限流/缓存 | 8篇 | 2周 |
| **v2.0** | 完整版 | 全部微服务 | uni-app多端 | 完整AI | Web/小程序/App | 8篇 | 2周 |

**总计**：9个版本，61篇博客，约17周

---

## 五、10年Java核心能力覆盖

| 能力模块 | 版本覆盖 | 核心技术点 |
|----------|----------|------------|
| **基础原理** | v0.1 | Spring Boot自动装配、IoC/AOP、类加载器 |
| **数据库** | v0.2/v0.3 | PostgreSQL事务、MVCC、索引优化、分库分表 |
| **缓存** | v0.2/v0.3 | Redis主从、Sentinel、Cluster、缓存策略 |
| **微服务** | v0.1/v0.3 | Nacos、Sentinel、Seata、Feign |
| **消息队列** | v0.3/v1.5 | Kafka生产者、消费者、顺序消息、事务消息 |
| **网关** | v1.5 | NestJS、Fastify、JWT鉴权、限流 |
| **性能优化** | v1.5/v2.0 | JVM调优、连接池优化、异步编程 |
| **源码解读** | 全程 | Spring/Spring Cloud Alibaba源码分析 |

---

## 六、LLM应用开发覆盖

| 能力模块 | 版本覆盖 | 核心技术点 |
|----------|----------|------------|
| **LLM基础** | v1.0 | Transformer、注意力机制、Prompt工程 |
| **API开发** | v1.0 | FastAPI、Pydantic、SSE流式输出 |
| **RAG知识库** | v1.1 | pgvector、Embedding、混合搜索、RRF |
| **LangChain** | v1.1/v1.2 | Loader、Splitter、VectorStore、Chain |
| **基础Agent** | v1.2 | ReAct、Tool、Agent、LangGraph |
| **高级Agent** | v1.3 | 多Agent、记忆系统、状态机、工作流 |
| **AI工程化** | v1.5/v2.0 | 监控、日志、CI/CD |

---

## 七、详细版本计划

### v0.1 基础架构版

**周期**：2周 | **目标**：搭建技术底座，理解微服务架构核心

#### 产品功能
- 用户模块：注册、登录（短信/邮箱）、JWT鉴权
- 权限模块：角色、权限、菜单
- 项目框架：Maven多模块、Nacos服务注册
- 前端基础：uni-app + TailwindCSS + uView Plus

#### 博客列表（7篇）

| # | 类型 | 标题 | 核心内容 |
|---|------|------|----------|
| 1 | 原理 | Spring Boot 3.x核心原理与自动装配机制 | @SpringBootApplication、starter原理、auto-config、@Conditional |
| 2 | 原理 | Nacos注册中心原理与服务发现机制 | 心跳检测、AP/CP模式、命名空间隔离、集群选举 |
| 3 | 实战 | 教育平台项目初始化与Maven多模块设计 | parent pom、dependencyManagement、模块划分（api/domain/infrastructure） |
| 4 | 实战 | Spring Boot + Nacos实现服务注册与调用 | @NacosInjected、OpenFeign、负载均衡 |
| 5 | 实战 | uni-app + TailwindCSS + uView Plus环境搭建 | Vite构建、SCSS变量、组件复用、主题配置 |
| 6 | 实战 | uni-app登录注册页面与JWT鉴权实现 | token存储、路由守卫、权限控制、SSO概念 |
| 7 | 原理 | 理解RESTful API设计与OpenAPI 3.0规范 | 资源命名、HATEOAS、版本控制策略、API文档生成 |

---

### v0.2 业务完善版

**周期**：2周 | **目标**：完成教育核心业务，掌握数据库设计与事务

#### 产品功能
- 课程管理：课程列表、详情、章节、评价
- 作业管理：作业发布、提交、批改状态
- 考试系统：题库管理、随机组卷、在线答题
- 答疑社区：提问、回答、评论、点赞、@通知

#### 博客列表（7篇）

| # | 类型 | 标题 | 核心内容 |
|---|------|------|----------|
| 1 | 原理 | PostgreSQL高级特性：事务、MVCC、锁机制 | ACID、隔离级别、VACUUM、死锁检测、REPEATABLE READ |
| 2 | 原理 | 分布式Session与Redis高可用架构 | 主从复制、Sentinel、Cluster模式、Pub/Sub |
| 3 | 实战 | 课程管理模块设计与MyBatis-Plus实战 | @TableLogic、乐观锁、逻辑删除、自动填充 |
| 4 | 实战 | 作业管理模块：文件上传与存储设计 | OSS集成、MinIO、本地存储、切片上传、断点续传 |
| 5 | 实战 | 考试系统设计：题库、试卷、答题卡 | 随机抽题算法、计时器、答案加密存储、自动评分 |
| 6 | 实战 | 答疑社区模块：富文本编辑器与Markdown | Editor.md、评论树形结构、@消息通知、敏感词过滤 |
| 7 | 原理 | SaaS多租户架构设计：数据隔离策略 | 独立数据库、共享数据库、字段级隔离、行级隔离 |

---

### v0.3 分布式基础版

**周期**：2周 | **目标**：掌握分布式核心技术与微服务治理

#### 产品功能
- 分布式事务：Seata AT模式
- 服务治理：Sentinel限流熔断
- 分布式锁：Redis/ZooKeeper锁
- 分布式配置：Nacos配置管理
- 消息队列：Kafka基础

#### 博客列表（7篇）

| # | 类型 | 标题 | 核心内容 |
|---|------|------|----------|
| 1 | 原理 | 分布式事务理论：CAP定理与BASE理论 | CAP权衡、BASE原则、2PC/3PC、TCC |
| 2 | 原理 | Seata原理：AT模式与TCC模式 | undo log、分支事务、全局事务管理 |
| 3 | 实战 | Seata集成：分布式事务实战 | @GlobalTransactional、超时回滚、悬挂问题 |
| 4 | 原理 | Sentinel核心原理：限流与熔断 | 滑动窗口、令牌桶、漏桶、熔断器状态机 |
| 5 | 实战 | Sentinel实战：流控规则与熔断规则 | QPS限流、关联限流、慢调用熔断、异常熔断 |
| 6 | 原理 | 分布式锁原理：Redis与ZooKeeper | Redisson、Watch机制、可重入锁、公平锁 |
| 7 | 实战 | Kafka实战：生产者与消费者 | 分区策略、顺序消息、消费者组、offset管理 |

---

### v1.0 AI接入版

**周期**：2周 | **目标**：首次接入LLM，理解AI应用开发范式

#### 产品功能
- AI助手：基于通义千问的智能问答
- 课程问答：针对课程内容的智能答疑
- SSE流式输出：实时对话体验

#### 博客列表（8篇）

| # | 类型 | 标题 | 核心内容 |
|---|------|------|----------|
| 1 | 原理 | LLM工作原理：Transformer与注意力机制 | Encoder-Decoder、位置编码、多头注意力、GPT vs BERT |
| 2 | 原理 | Prompt工程：从入门到实战技巧 | Few-shot、CoT思维链、角色扮演、提示词模板 |
| 3 | 原理 | FastAPI高级特性：依赖注入与生命周期 | @app.on_event、Dependency、lifespan、中间件 |
| 4 | 实战 | Python AI服务搭建：FastAPI + Pydantic | 请求验证、响应模型、错误处理、异常统一封装 |
| 5 | 实战 | 通义千问API对接：OpenAI兼容模式 | base_url配置、API Key管理、模型选择、超参调优 |
| 6 | 实战 | 后端AI服务封装：流式输出与SSE | Server-Sent Events、yield、chunk传输、终止符处理 |
| 7 | 实战 | 前端AI对话页面：Markdown渲染与代码高亮 | markdown-it、highlight.js、typing效果、流式渲染 |
| 8 | 实战 | Java与Python服务通信：Feign与HTTPClient | 服务间调用、异常传递、负载均衡策略、重试机制 |

---

### v1.1 向量检索版

**周期**：2周 | **目标**：构建RAG知识库，掌握向量检索

#### 产品功能
- 知识库管理：文档上传、解析、向量化
- RAG问答：基于课程文档的精准问答
- 混合搜索：关键词 + 向量检索融合

#### 博客列表（8篇）

| # | 类型 | 标题 | 核心内容 |
|---|------|------|----------|
| 1 | 原理 | 向量数据库原理：Embedding与相似度计算 | 余弦相似度、欧氏距离、HNSW索引、IVF索引 |
| 2 | 原理 | RAG架构深度解析：检索增强生成 | LangChain Loader、Splitter、VectorStore、Retriever |
| 3 | 原理 | pgvector安装与PostgreSQL向量扩展 | vector类型、ivfflat索引、hnsw索引、距离函数 |
| 4 | 实战 | 文档处理流水线：PDF/Word/MD解析 | PyMuPDF、python-docx、markdown2text、正则提取 |
| 5 | 实战 | 文本向量化：Embedding模型选型与部署 | sentence-transformers、Qwen Embedding、本地部署 |
| 6 | 实战 | RAG检索实战：查询改写与重排序 | HyDE、cross-encoder rerank、上下文压缩、意图识别 |
| 7 | 实战 | 混合搜索：关键词+向量检索RRF融合 | BM25、reciprocal_rank_fusion算法、分数归一化 |
| 8 | 实战 | 教育知识库构建：课程文档自动向量化 | 增量更新、版本管理、CDC实时同步、定时任务 |

---

### v1.2 基础Agent版

**周期**：2周 | **目标**：构建基础AI Agent，实现简单自动化任务

#### 产品功能
- 作业批改Agent：OCR识别 + AI评分 + 反馈生成
- 智能出题Agent：知识点提取 + 题目生成 + 难度控制
- Agent任务面板：任务提交、进度查看、结果展示

#### 博客列表（8篇）

| # | 类型 | 标题 | 核心内容 |
|---|------|------|----------|
| 1 | 原理 | Agent架构解析：LLM + Tools + Memory | ReAct模式、Plan-and-Execute、Reflexion |
| 2 | 原理 | LangChain核心组件：Chain/LLMChain/Agent | LCEL、Runnable接口、输出解析、JSON parser |
| 3 | 原理 | LangGraph基础：状态机驱动的Agent工作流 | Node/Edge/State定义、编译运行、持久化checkpoint |
| 4 | 实战 | Agent工具开发：Python函数作为Tool | @tool装饰器、参数校验、返回格式、ToolKit |
| 5 | 实战 | 作业批改Agent：OCR识别与AI评分 | PaddleOCR、表格识别、评分标准、反馈生成 |
| 6 | 实战 | 智能出题Agent：知识点提取与题目生成 | 大纲解析、题型模板、多样性控制、难度评估 |
| 7 | 实战 | Agent任务调度：异步执行与结果回调 | 任务队列、Celery、WebSocket推送、状态管理 |
| 8 | 实战 | 前端Agent面板：任务提交与进度展示 | 任务卡片、进度条、结果渲染、Markdown预览 |

---

### v1.3 高级Agent版

**周期**：3周 | **目标**：构建复杂Agent工作流，实现多Agent协作

#### 产品功能
- 学习规划Agent：个性化学习路径推荐
- 多Agent协作：Agent间通信与任务分发
- Agent可视化：思维过程展示、调试工具
- Agent市场：预定义Agent模板共享

#### 博客列表（8篇）

| # | 类型 | 标题 | 核心内容 |
|---|------|------|----------|
| 1 | 原理 | 多Agent系统架构：通信协议与协作模式 | Agent间通信、任务分发、状态同步、共识机制 |
| 2 | 原理 | LangGraph高级：子图与检查pointer | 条件分支、循环、持久化状态、human-in-loop |
| 3 | 原理 | 记忆系统：短期记忆与长期记忆设计 | BufferMemory、ConversationSummaryMemory、向量记忆 |
| 4 | 实战 | 学习规划Agent：用户画像与路径规划 | 知识图谱、能力评估、路径算法、进度追踪 |
| 5 | 实战 | 多Agent协作：任务分解与结果汇总 | Master-Worker模式、并行执行、结果合并 |
| 6 | 实战 | Agent可视化：思维链展示与调试 | 步骤追踪、中间结果、token统计、成本控制 |
| 7 | 实战 | Agent市场：模板定义与动态加载 | Agent模板JSON、动态加载、热更新 |
| 8 | 实战 | Agent日志与审计：完整链路追踪 | 链路ID、审计日志、成本分析、异常告警 |

---

### v1.5 高并发版

**周期**：2周 | **目标**：掌握高并发架构，实现性能优化

#### 产品功能
- NestJS网关：统一入口、鉴权、限流
- 服务治理：Sentinel Dashboard
- 缓存优化：多级缓存、热点key
- 异步处理：Kafka可靠投递

#### 博客列表（8篇）

| # | 类型 | 标题 | 核心内容 |
|---|------|------|----------|
| 1 | 原理 | NestJS设计模式：依赖注入与模块化 | IOC容器、Module、Guard、Interceptor、Pipe |
| 2 | 原理 | 高并发架构：限流、熔断、降级 | Token Bucket、Sentinel、热点防护、系统自适应 |
| 3 | 原理 | 分布式缓存：Redis设计与最佳实践 | 缓存策略、热点key、内存优化、BigKey处理 |
| 4 | 实战 | NestJS + Fastify网关设计与实现 | 中间件、拦截器、管道验证、异常过滤 |
| 5 | 实战 | 网关鉴权：JWT + OAuth2 + 分布式Session | 令牌刷新、黑名单、SSO、扫码登录 |
| 6 | 实战 | 服务治理：Sentinel配置与Dashboard | 流控规则、熔断规则、热点参数、系统自适应 |
| 7 | 实战 | 数据库性能优化：索引、慢查询、分库分表 | Explain分析、联合索引、ShardingSphere |
| 8 | 实战 | 异步处理：Kafka消息队列与可靠投递 | 顺序消息、事务消息、幂等性、消费确认 |

---

### v2.0 多端完整版

**周期**：2周 | **目标**：全端部署，实现完整AI教育平台

#### 产品功能
- uni-app多端：Web/小程序/App全端编译
- K3s部署：容器化、弹性伸缩
- 监控运维：Prometheus + Grafana
- CI/CD：自动化部署流水线

#### 博客列表（8篇）

| # | 类型 | 标题 | 核心内容 |
|---|------|------|----------|
| 1 | 原理 | uni-app多端编译：Web/小程序/App原理 | 条件编译、运行时差异、平台API适配 |
| 2 | 原理 | K3s轻量级Kubernetes：架构与核心组件 | k3s vs k8s、Traefik、ServingsLB |
| 3 | 实战 | uni-app多端适配：条件编译实战 | #ifdef、uni-API、生命周期差异处理 |
| 4 | 实战 | 小程序适配：微信登录与支付集成 | wx.login、wx.requestPayment、uni.requestPayment |
| 5 | 实战 | App打包：Flutter热更新与原生插件 | CodePush、platform-channel、原生模块开发 |
| 6 | 实战 | K3s集群部署：Docker镜像与Helm Chart | Dockerfile优化、Helm模板、HPA、滚动更新 |
| 7 | 实战 | CI/CD流水线：GitHub Actions自动化部署 | 构建、测试、部署脚本、镜像推送 |
| 8 | 实战 | 监控与日志：Prometheus + Grafana + Loki | 指标采集、可视化面板、告警规则、日志聚合 |

---

## 八、博客系列划分

| 系列 | 对应版本 | 博客数 | 主题 |
|------|----------|--------|------|
| **系列1** | v0.1-v0.3 | 21篇 | Java微服务基础 |
| **系列2** | v1.0 | 8篇 | LLM应用入门 |
| **系列3** | v1.1 | 8篇 | RAG知识库实战 |
| **系列4** | v1.2-v1.3 | 16篇 | AI Agent开发 |
| **系列5** | v1.5 | 8篇 | 高并发架构 |
| **系列6** | v2.0 | 8篇 | 多端与部署 |

---

## 九、博客发布平台

| 平台 | 用途 |
|------|------|
| **OpenWrite** | 多平台博客首发 |
| **掘金** | 国内技术社区同步 |
| **CSDN** | 国内技术社区同步 |
| **doocs/md** | 微信公众平台编辑 |

---

## 十、项目仓库规划

| 项目 | 技术栈 | 用途 |
|------|--------|------|
| `edu-ai-platform` | Maven | 父项目 |
| `edu-user-service` | Java | 用户服务 |
| `edu-course-service` | Java | 课程服务 |
| `edu-homework-service` | Java | 作业服务 |
| `edu-exam-service` | Java | 考试服务 |
| `edu-ai-service` | Python | AI推理服务 |
| `edu-gateway` | NestJS | API网关 |
| `edu-web` | uni-app | Web/小程序/App |

---

## 十一、成本估算

| 项目 | 费用 |
|------|------|
| 域名 | ¥30/年 |
| 云服务器（2核4G） | ¥80/月 |
| API调用配额 | ¥200-300/月 |
| **总计** | ¥280-380/月 |

---

## 十二、学习路径图

```
v0.1 (2周) → v0.2 (2周) → v0.3 (2周) → v1.0 (2周) → v1.1 (2周) → v1.2 (2周) → v1.3 (3周) → v1.5 (2周) → v2.0 (2周)
   ↓           ↓           ↓           ↓           ↓           ↓           ↓           ↓           ↓
Java基础   业务开发    分布式     LLM接入    RAG        基础Agent   高级Agent   高并发      完整部署
           +DB设计    +事务      +Prompt    +向量       +LangChain  +多Agent    +网关       +多端
```

**蓝图版本**：v6.0
**更新时间**：2026-03-30
