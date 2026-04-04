# AI教育平台全栈工程师学习蓝图（最终版）

---

## 一、总体目标

构建一个以**Java为核心**、**AI为能力增强**的智能教育平台，培养具备以下能力的全栈工程师：

- **Java后端**：10年Java工程师核心能力（分布式、微服务、高并发、性能优化）
- **Python AI**：LLM应用开发、RAG知识库构建、AI Agent开发
- **前端**：uni-app多端开发（Web/小程序/App）
- **测试工程**：功能测试、性能测试、安全测试、自动化测试
- **架构**：微服务架构 + K3s容器化部署

**核心原则**：
- 博客与项目同步进行，每篇博客产出即项目代码
- 每个版本可运行展示，里程碑式交付
- 原理深入到架构师级别，代码展示关键逻辑并附仓库地址

---

## 二、技术栈总览

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| **后端-业务** | Java 17 + Spring Boot 3.x + Spring Cloud Alibaba | 核心业务逻辑 |
| **后端-AI** | Python 3.11 + FastAPI + LangChain | AI推理服务 |
| **后端-网关** | Spring Cloud Gateway | 统一API网关（替换NestJS） |
| **数据库** | PostgreSQL 15 + pgvector | 统一存储（业务+向量） |
| **缓存** | Redis 7 + Redis Stack | 分布式缓存 |
| **消息队列** | RabbitMQ 3.13.x + Erlang 25.x | 异步通信 |
| **注册/配置中心** | Nacos 2.x | 服务注册与配置 |
| **LLM** | OpenRouter (qwen/qwen2.5-vl-7b-instruct:free) | 多模态免费模型 |
| **本地Rerank** | Ollama + BGE-Reranker-v2-M3 | 本地Rerank模型 |
| **前端** | uni-app + TailwindCSS + uView Plus | 多端统一开发 |
| **部署** | K3s + Docker + Helm | 轻量级K8s |

---

## 三、项目命名

| 项目 | 名称 | 技术栈 |
|------|------|--------|
| **父项目** | `edu-ai-platform` | Maven |
| **用户服务** | `edu-user-service` | Java |
| **课程服务** | `edu-course-service` | Java |
| **作业服务** | `edu-homework-service` | Java |
| **考试服务** | `edu-exam-service` | Java |
| **AI服务** | `edu-ai-service` | Python (FastAPI) |
| **网关** | `edu-gateway` | **Spring Cloud Gateway** |
| **前端** | `edu-web` | uni-app |

---

## 四、版本演进总览

| 版本 | 阶段 | 后端技术 | 前端技术 | AI能力 | 产品形态 | 博客数 | 周期 | 可展示 |
|------|------|----------|----------|--------|----------|--------|------|--------|
| **v0.1** | 基础架构 | Java + Nacos + SC Gateway | uni-app | - | 用户/权限系统 | 8篇 | 2周 | ✅ 登录注册 |
| **v0.2** | 业务完善 | Java + Redis | uni-app | - | 课程/作业/考试 | 11篇 | 2周 | ✅ 核心功能 |
| **v0.3** | 分布式 | Java + RabbitMQ | uni-app | - | 服务治理/分布式事务 | 9篇 | 2周 | ✅ 微服务治理 |
| **v1.0** | AI接入 | Java + Python | uni-app | LLM对话 | AI智能问答 | 10篇 | 2周 | ✅ 智能问答 |
| **v1.1** | 向量检索 | Java + Python | uni-app | RAG+Rerank+AI搜索 | 知识库问答/AI课程搜索 | 12篇 | 2周 | ✅ 文档问答 |
| **v1.2** | Agent | Java + Python | uni-app | Agent+多模态+AI推荐 | 作业批改/AI智能推荐 | 20篇 | 3周 | ✅ Agent任务 |
| **v1.5** | 高并发 | Java + Python + SC Gateway | uni-app | 性能优化+安全 | 网关/限流/安全 | 13篇 | 2周 | ✅ 压测报告 |
| **v2.0** | 完整部署 | 全部微服务 | uni-app多端 | 完整AI | Web/小程序/App | 10篇 | 2周 | ✅ 三端运行 |

**总计**：8个版本，93篇博客，约19周，8个可运行版本

---

## 六、10年Java核心能力覆盖

| 能力模块 | 版本覆盖 | 核心技术点 |
|----------|----------|------------|
| **基础原理** | v0.1 | Spring Boot自动装配、IoC/AOP、类加载器 |
| **数据库** | v0.2/v0.3 | PostgreSQL事务、MVCC、索引优化、分库分表 |
| **缓存** | v0.2/v0.3 | Redis主从、Sentinel、Cluster、缓存策略 |
| **微服务** | v0.1/v0.3 | Nacos、Sentinel、Seata、Feign |
| **消息队列** | v0.3/v1.5 | RabbitMQ交换机类型、队列模型、消息确认、延迟队列、TTL、Dead Letter |
| **网关** | v0.1/v1.5 | Spring Cloud Gateway、JWT鉴权、限流 |
| **性能优化** | v1.5/v2.0 | JVM调优、连接池优化、异步编程 |
| **源码解读** | 全程 | Spring/Spring Cloud Alibaba源码分析 |

---

## 七、LLM应用开发覆盖

| 能力模块 | 版本覆盖 | 核心技术点 |
|----------|----------|------------|
| **LLM基础** | v1.0 | Transformer、注意力机制、Prompt工程 |
| **API开发** | v1.0 | FastAPI、Pydantic、SSE流式输出 |
| **RAG知识库** | v1.1 | pgvector、Embedding、混合搜索、RRF |
| **Rerank** | v1.1 | Ollama、BGE-Reranker-v2-M3、两阶段召回 |
| **AI搜索** | v1.1 | 语义搜索、意图识别、查询改写 |
| **LangChain** | v1.1/v1.2 | Loader、Splitter、VectorStore、Chain |
| **AI推荐** | v1.2 | 用户画像、协同过滤、LLM推荐生成 |
| **基础Agent** | v1.2 | ReAct、Tool、Agent、LangGraph |
| **高级Agent** | v1.2 | 多Agent、记忆系统、状态机、工作流 |
| **多模态** | v1.2 | Qwen2.5-VL、图像理解、OCR |
| **AI安全** | v1.2 | Prompt注入防御、输出过滤、敏感词检测 |
| **AI工程化** | v1.5/v2.0 | 监控、日志、CI/CD |

---

## 五、测试工程覆盖

| 能力模块 | 版本覆盖 | 核心技术点 |
|----------|----------|------------|
| **单元测试** | v0.2 | JUnit5、AssertJ、Mockito、Jacoco覆盖率 |
| **Mock服务** | v0.2 | WireMock、Testcontainers、MockServer |
| **接口测试** | v0.2/v0.3 | REST Assured、参数化测试、MockMvc |
| **集成测试** | v0.3 | 服务集成测试、契约测试、数据库集成测试 |
| **AI功能测试** | v1.0 | 响应验证、流式输出测试、SSE测试 |
| **AI安全测试** | v1.2 | Prompt注入测试、输出过滤测试、敏感词检测 |
| **性能测试** | v1.5 | JMeter、Locust、压测场景设计、性能基线 |
| **安全扫描** | v1.5 | SonarQube、Trivy、OWASP ZAP |
| **E2E测试** | v2.0 | Cypress、Playwright、跨浏览器测试 |
| **CI/CD测试** | v2.0 | 自动化流水线、测试门禁、Allure报告 |

---

## 八、详细版本计划

### v0.1 基础架构版

**周期**：2周 | **目标**：搭建技术底座，理解微服务架构核心

#### 产品功能
- 用户模块：注册、登录（短信/邮箱）、JWT鉴权
- 权限模块：角色、权限、菜单
- 项目框架：Maven多模块、Nacos服务注册、Spring Cloud Gateway网关
- 前端基础：uni-app + TailwindCSS + uView Plus

#### 项目交付
- edu-user-service 可运行
- edu-gateway (SC Gateway) 可运行
- edu-web 登录页面可展示

#### 博客列表（8篇）

| # | 系列 | 类型 | 标题 | 核心内容 |
|---|------|------|------|----------|
| 1 | 系列1 | 原理 | Spring Boot 3.x自动装配原理深度解析 | @SpringBootApplication源码级分析、@Conditional条件装配、自定义Starter、启动性能优化 |
| 2 | 系列1 | 原理 | Nacos注册中心核心原理与生产环境最佳实践 | 心跳检测机制源码、AP/CP模式深度对比、命名空间隔离、集群选举Raft协议 |
| 3 | 系列1 | 实战 | 教育平台项目初始化与Maven多模块设计 | parent pom统一版本管理、模块划分(api/domain/infrastructure)、dependencyManagement |
| 4 | 系列1 | 实战 | Spring Boot + Nacos实现服务注册与调用 | @NacosInjected源码解析、OpenFeign原理、负载均衡策略对比 |
| 5 | 系列1 | 原理 | Spring Cloud Gateway核心原理与源码深度 | 路由机制与RouteLocator、过滤器链原理、全局过滤器、响应式编程原理 |
| 6 | 系列1 | 实战 | Spring Cloud Gateway + Nacos深度集成实战 | 服务发现配置、动态路由、权重路由、本地限流、与Sentinel整合 |
| 7 | 系列1 | 实战 | uni-app环境搭建与JWT鉴权实现 | Vite构建原理、SCSS变量与主题系统、组件复用、token存储安全策略、路由守卫与权限控制 |
| 8 | 系列1 | 实战 | Flyway数据库版本化管理深度实战 | SQL脚本版本化、多模块迁移脚本协调、迁移策略与回滚、undo log原理 |

#### 技术点应用

| 技术点 | 项目代码位置 |
|--------|--------------|
| Nacos服务注册 | edu-user-service/src/main/java/.../config/NacosConfig.java |
| JWT鉴权 | edu-user-service/src/main/java/.../security/JwtUtil.java |
| SC Gateway路由 | edu-gateway/src/main/java/.../config/GatewayRoutesConfig.java |
| 服务调用 | edu-user-service/src/main/java/.../feign/UserFeignClient.java |
| Flyway迁移脚本 | edu-user-service/src/main/resources/db/migration/V1__create_sys_user.sql |
| Flyway迁移脚本 | edu-course-service/src/main/resources/db/migration/ |
| Flyway迁移脚本 | edu-homework-service/src/main/resources/db/migration/ |
| Flyway迁移脚本 | edu-exam-service/src/main/resources/db/migration/ |

---

### v0.2 业务完善版

**周期**：2周 | **目标**：完成教育核心业务，掌握数据库设计与事务

#### 产品功能
- 课程管理：课程列表、详情、章节、评价
- 作业管理：作业发布、提交、批改状态
- 考试系统：题库管理、随机组卷、在线答题

#### 项目交付
- edu-course-service 可运行
- edu-homework-service 可运行
- edu-exam-service 可运行

#### 博客列表（11篇）

| # | 系列 | 类型 | 标题 | 核心内容 |
|---|------|------|------|----------|
| 1 | 系列1 | 原理 | PostgreSQL事务、MVCC与锁机制深度剖析 | ACID实现原理、MVCC可见性判断、隔离级别对比、VACUUM原理、死锁检测 |
| 2 | 系列1 | 原理 | Redis高可用架构：主从/Sentinel/Cluster深度对比 | 主从复制原理、Sentinel故障检测、Cluster数据分片(槽)、Pub/Sub消息订阅 |
| 3 | 系列1 | 实战 | 课程管理模块设计与MyBatis-Plus实战 | @TableLogic逻辑删除、乐观锁@Version、自动填充@Field、查询性能优化 |
| 4 | 系列1 | 实战 | 作业管理模块：文件上传与存储设计 | MinIO分布式存储、文件切片上传、断点续传、CDN加速策略 |
| 5 | 系列1 | 实战 | 考试系统设计：题库、试卷、答题卡全解析 | 随机抽题算法、计时器防作弊、答案加密存储、自动评分引擎 |
| 6 | 系列1 | 原理 | SaaS多租户架构设计：数据隔离策略深度对比 | 三种隔离方案对比、租户标识路由、数据权限控制、成本与性能权衡 |
| 7 | 系列1 | 实战 | 分布式Session与Redis缓存实战 | Redis主从配置、Session共享、缓存策略、热点key处理 |
| 8 | 系列1 | 实战 | 单元测试进阶：JUnit5与Mockito深度实践 | @SpringBootTest、@DataJpaTest、@WebMvcTest分层测试、@Mock与@Spy区别、断言库AssertJ |
| 9 | 系列1 | 实战 | Mock服务与测试数据管理：WireMock+Testcontainers | WireMock外部依赖Mock、Testcontainers数据库容器、测试数据Factory、测试DB隔离策略 |
| 10 | 系列1 | 实战 | 接口自动化测试：REST Assured与参数化测试 | REST Assured接口测试、@ParameterizedTest参数化、Cookie/Session管理、响应断言封装 |
| 11 | 系列1 | 实战 | 测试覆盖率与Jacoco配置 | Jacoco覆盖率配置、覆盖率指标(分支>70%)、测试报告集成、测试策略制定 |

#### 技术点应用

| 技术点 | 项目代码位置 |
|--------|--------------|
| MyBatis-Plus CRUD | edu-course-service/src/main/java/.../mapper/ |
| Redis缓存 | edu-user-service/src/main/java/.../config/RedisConfig.java |
| 文件上传 | edu-homework-service/src/main/java/.../controller/UploadController.java |
| 分布式锁 | edu-exam-service/src/main/java/.../lock/DistributedLock.java |
| Flyway迁移脚本 | edu-course-service/src/main/resources/db/migration/ |
| Flyway迁移脚本 | edu-homework-service/src/main/resources/db/migration/ |
| Flyway迁移脚本 | edu-exam-service/src/main/resources/db/migration/ |

---

### v0.3 分布式基础版

**周期**：2周 | **目标**：掌握分布式核心技术与微服务治理

#### 产品功能
- 分布式事务：Seata AT模式
- 服务治理：Sentinel限流熔断
- 分布式锁：Redis锁
- 消息队列：RabbitMQ基础

#### 项目交付
- Seata服务集成
- Sentinel Dashboard可展示
- RabbitMQ消息发送/消费演示

#### 博客列表（9篇）

| # | 系列 | 类型 | 标题 | 核心内容 |
|---|------|------|------|----------|
| 1 | 系列1 | 原理 | 分布式事务核心原理：CAP定理与BASE理论深度解析 | CAP三选二权衡、BASE理论四要素、2PC/3PC原理与缺陷、TCC补偿模式 |
| 2 | 系列1 | 原理 | Seata原理深度剖析：AT模式与TCC模式对比 | AT模式undo log原理、分支事务注册与提交、全局事务管理器、TCC模式与事务悬挂 |
| 3 | 系列1 | 实战 | Seata生产级实战：事务悬挂与级联故障全搞定 | @GlobalTransactional详解、超时回滚配置、悬挂问题根因分析、高并发事务优化 |
| 4 | 系列1 | 原理 | Sentinel核心原理：限流算法与熔断器状态机 | 滑动窗口算法实现、令牌桶与漏桶对比、熔断器状态机、热点参数限流 |
| 5 | 系列1 | 实战 | Sentinel流控/熔断/热点规则深度实战 | QPS/并发线程限流、关联限流与链路限流、慢调用/异常比例熔断、Sentinel Dashboard配置 |
| 6 | 系列1 | 原理 | 分布式锁原理深度剖析：Redis与ZooKeeper对比 | Redisson可重入锁原理、Watch机制与乐观锁、公平锁vs非公平锁、锁超时与脑裂问题 |
| 7 | 系列1 | 实战 | RabbitMQ深度实战：交换机、队列与消息确认 | 交换机类型(Direct/Topic/Fanout)、队列模型、消息确认机制(ACK)、Lazy Queue、镜像队列 |
| 8 | 系列1 | 实战 | 服务集成测试：跨服务调用与契约测试 | Feign Client Mock测试、服务间契约测试、@SpringCloudTest微服务测试、MockServer实战 |
| 9 | 系列1 | 实战 | 数据库集成测试：事务与性能测试 | @DataJpaTest深度、事务传播行为测试、批量操作性能、SQL日志分析 |

#### 技术点应用

| 技术点 | 项目代码位置 |
|--------|--------------|
| Seata分布式事务 | edu-course-service/src/main/java/.../config/SeataConfig.java |
| Sentinel限流 | edu-gateway/src/main/java/.../filter/SentinelFilter.java |
| 分布式锁 | edu-exam-service/src/main/java/.../lock/RedisLock.java |
| RabbitMQ消息 | edu-homework-service/src/main/java/.../rabbitmq/ |

---

### v1.0 AI接入版

**周期**：2周 | **目标**：首次接入LLM，理解AI应用开发范式

#### 产品功能
- AI助手：基于OpenRouter免费模型的智能问答
- 课程问答：针对课程内容的智能答疑
- SSE流式输出：实时对话体验

#### 项目交付
- edu-ai-service (Python) 可运行
- Java-Python服务通信正常
- AI对话页面可展示

#### 博客列表（10篇）

| # | 系列 | 类型 | 标题 | 核心内容 |
|---|------|------|------|----------|
| 1 | 系列2 | 原理 | LLM核心原理：Transformer与注意力机制深度解析 | Encoder-Decoder架构、多头注意力机制源码、位置编码与旋转位置编码、GPT vs BERT对比 |
| 2 | 系列2 | 原理 | Prompt工程深度实践：从入门到高级技巧 | Few-shot与Zero-shot、CoT思维链原理、ReAct推理框架、角色扮演与提示注入 |
| 3 | 系列2 | 原理 | FastAPI高级特性：依赖注入与生命周期管理 | @app.on_event生命周期、Depends依赖注入原理、lifespan上下文管理、中间件原理 |
| 4 | 系列2 | 实战 | Python AI服务搭建：FastAPI + Pydantic深度实战 | Pydantic请求验证、Response模型设计、错误处理与异常统一、日志最佳实践 |
| 5 | 系列2 | 实战 | OpenRouter API深度对接：OpenAI兼容模式实战 | base_url配置与模型选择、API Key安全管理、超参数调优、流式与非流式对比 |
| 6 | 系列2 | 实战 | 后端AI服务封装：SSE流式输出深度实战 | Server-Sent Events原理、yield与chunk传输、终止符处理、前端流式渲染 |
| 7 | 系列2 | 实战 | 前端AI对话页面：Markdown渲染与代码高亮 | markdown-it集成、highlight.js代码高亮、typing打字效果、流式渲染实现 |
| 8 | 系列2 | 实战 | Java与Python服务通信：Feign/HTTPClient实战 | OpenFeign调用Python、HTTPClient连接池、异常传递与降级、负载均衡策略 |
| 9 | 系列2 | 实战 | AI响应质量评估：格式验证与语义一致性测试 | JSON Schema验证、响应格式断言、语义一致性评估、异常场景测试（超时/降级） |
| 10 | 系列2 | 实战 | 流式输出测试：SSE连接与chunk完整性验证 | SSE连接测试、chunk传输验证、断连重连测试、流式渲染验证 |

#### 技术点应用

| 技术点 | 项目代码位置 |
|--------|--------------|
| FastAPI服务 | edu-ai-service/src/main.py |
| SSE流式 | edu-ai-service/src/routes/chat.py |
| LLM调用 | edu-ai-service/src/llm/client.py |
| Java调用Python | edu-user-service/src/main/java/.../feign/AiFeignClient.java |

---

### v1.1 向量检索版

**周期**：2周 | **目标**：构建RAG知识库，掌握向量检索与Rerank

#### 产品功能
- 知识库管理：文档上传、解析、向量化
- RAG问答：基于课程文档的精准问答
- Rerank优化：两阶段召回
- 本地Rerank模型部署
- **AI课程搜索：语义搜索、意图识别、查询改写**

#### 项目交付
- 知识库问答可演示
- Ollama + Rerank模型可运行
- RAG流程可展示

#### 博客列表（10篇）

| # | 系列 | 类型 | 标题 | 核心内容 |
|---|------|------|------|----------|
| 1 | 系列3 | 原理 | 向量数据库原理深度：Embedding与相似度计算 | 向量Embedding原理、余弦相似度vs欧氏距离、HNSW索引原理、IVF索引与聚类 |
| 2 | 系列3 | 原理 | RAG架构深度解析：检索增强生成全流程 | RAG架构演进(Naive/RDF/Modular)、LangChain核心组件、Loader/Splitter/VectorStore、Retriever与查询分析 |
| 3 | 系列3 | 原理 | pgvector深度实践：PostgreSQL向量扩展 | vector类型与操作符、ivfflat索引原理、hnsw索引配置、距离函数与排序 |
| 4 | 系列3 | 实战 | 文档处理流水线：PDF/Word/MD解析实战 | PyMuPDF文本提取、python-docx解析、markdown2text转换、大文档分片策略 |
| 5 | 系列3 | 实战 | 文本向量化：Embedding模型选型与部署 | OpenRouter Embedding API、nvidia/llama-nemotron对比、多语言支持、向量维度选择 |
| 6 | 系列3 | 实战 | RAG检索实战：查询改写与混合搜索 | HyDE查询增强、RRF Reciprocal Rank Fusion、上下文压缩、意图识别 |
| 7 | 系列3 | 实战 | 混合搜索深度实战：BM25 + 向量检索融合 | BM25算法原理、RRF融合算法、分数归一化、混合搜索调参 |
| 8 | 系列3 | 实战 | 教育知识库构建：课程文档自动向量化 | 增量更新策略、版本管理、CDC实时同步、定时任务设计 |
| 9 | 系列3 | 实战 | Ollama本地部署：BGE-Reranker-v2-M3实战 | Ollama安装配置、模型下载与加速、API封装、Docker部署 |
| 10 | 系列3 | 实战 | Rerank检索优化：两阶段召回深度实战 | 初筛+精排架构、Rerank调用优化、上下文窗口处理、批量Rerank、延迟优化 |
| 11 | 系列3 | 实战 | 课程语义搜索：RAG在教育场景实战 | 课程内容向量化、语义检索、意图识别、查询改写 |
| 12 | 系列3 | 实战 | 搜索体验优化：排序策略与用户意图匹配 | 相关性调优、结果高亮、搜索建议、多轮交互 |

#### 技术点应用

| 技术点 | 项目代码位置 |
|--------|--------------|
| pgvector存储 | edu-ai-service/src/rag/vector_store.py |
| RAG检索 | edu-ai-service/src/rag/retriever.py |
| Ollama服务 | edu-ai-service/src/rerank/ollama_client.py |
| 文档处理 | edu-ai-service/src/rag/document_loader.py |

---

### v1.2 Agent版（合并v1.2+v1.3）

**周期**：3周 | **目标**：构建完整Agent工作流，实现多模态与AI安全

#### 产品功能
- 作业批改Agent：OCR识别 + AI评分 + 反馈生成
- 智能出题Agent：知识点提取 + 题目生成 + 难度控制
- 多模态Agent：图片理解 + 作业拍照批改
- AI安全：Prompt注入防御 + 输出过滤
- 学习规划Agent：个性化路径推荐
- **AI智能推荐：用户画像、个性化课程推荐、智能学习路径**
- 多Agent协作：任务分解与结果汇总

#### 项目交付
- Agent任务面板可演示
- 作业批改功能可展示
- 多模态问答可演示

#### 博客列表（20篇）

| # | 系列 | 类型 | 标题 | 核心内容 |
|---|------|------|------|----------|
| 1 | 系列4 | 原理 | Agent架构深度解析：LLM + Tools + Memory | Agent定义与演进、ReAct模式原理、Plan-and-Execute、Reflexion自省、Agent vs Chain |
| 2 | 系列4 | 原理 | LangChain核心组件深度：Chain/LLMChain/Agent | LCEL语法、Runnable接口、输出解析器、JSON Parser、Agent类型对比 |
| 3 | 系列4 | 原理 | LangGraph深度：状态机驱动的Agent工作流 | Node/Edge/State定义、状态持久化checkpoint、条件分支与循环、Human-in-loop |
| 4 | 系列4 | 实战 | Agent工具开发：Python函数作为Tool深度实战 | @tool装饰器原理、参数校验与Schema、返回格式设计、ToolKit组合 |
| 5 | 系列4 | 实战 | 作业批改Agent：OCR识别与AI评分实战 | PaddleOCR集成、表格识别、评分标准设计、反馈生成、多题型支持 |
| 6 | 系列4 | 实战 | 智能出题Agent：知识点提取与题目生成 | 大纲解析、题型模板、多样性控制、难度评估、题目去重 |
| 7 | 系列4 | 实战 | Agent任务调度：异步执行与结果回调 | Celery任务队列、WebSocket推送、状态管理、失败重试、并发控制 |
| 8 | 系列4 | 实战 | 前端Agent面板：任务提交与进度展示 | 任务卡片设计、进度条实现、结果渲染、Markdown预览、实时更新 |
| 9 | 系列4 | 实战 | 多模态接入：Qwen2.5-VL图像理解深度实战 | 模型选择与配置、图片问答实现、图表解析、视觉推理、多图处理 |
| 10 | 系列4 | 实战 | 多模态实战：作业拍照批改全流程 | 图片上传与压缩、OCR+AI评分、批改结果展示、准确率优化 |
| 11 | 系列4 | 原理 | AI安全深度：Prompt注入与防御机制 | 指令注入原理、角色绕过、恶意输入检测、防御策略、安全测试 |
| 12 | 系列4 | 实战 | AI安全实战：输出过滤与敏感词检测 | OutputParser过滤、正则敏感词、内容审核API、风险分级、审计日志 |
| 13 | 系列4 | 实战 | AI安全测试：Prompt注入攻击测试 | 指令注入测试集、角色绕过测试、边界条件测试、防御验证 |
| 14 | 系列4 | 实战 | AI安全测试：输出安全与有害内容检测 | 敏感信息过滤测试、有害内容检测、注入攻击防御验证、输出过滤规则测试 |
| 15 | 系列4 | 原理 | 多Agent系统架构：通信协议与协作模式 | Agent间通信协议、任务分发策略、状态同步机制、共识算法 |
| 16 | 系列4 | 实战 | 学习规划Agent：用户画像与路径规划实战 | 用户画像构建、知识图谱设计、路径规划算法、进度追踪 |
| 17 | 系列4 | 实战 | AI推荐系统：用户特征提取与向量表示 | 用户画像构建、特征工程、协同过滤、向量化表示 |
| 18 | 系列4 | 实战 | 智能推荐Agent：LLM生成个性化推荐结果 | 推荐Prompt设计、推荐理由生成、反馈优化、多样性控制 |
| 19 | 系列4 | 实战 | 多Agent协作：任务分解与结果汇总实战 | Master-Worker模式、并行执行、结果合并、任务依赖、失败处理 |
| 20 | 系列4 | 实战 | Agent可视化：思维链展示与调试实战 | 步骤追踪、中间结果展示、token统计、成本控制、调试工具 |

#### 技术点应用

| 技术点 | 项目代码位置 |
|--------|--------------|
| LangGraph工作流 | edu-ai-service/src/agent/graph.py |
| Agent工具 | edu-ai-service/src/agent/tools/ |
| 多模态 | edu-ai-service/src/vision/ |
| AI安全 | edu-ai-service/src/security/ |

---

### v1.5 高并发版

**周期**：2周 | **目标**：掌握高并发架构，实现性能优化与安全防护

#### 产品功能
- 网关优化：JWT鉴权、限流、熔断
- 缓存优化：多级缓存、热点key
- 性能测试：JMeter/Locust压测
- 安全防护：OWASP Top 10防御
- APM监控：SkyWalking + Prometheus

#### 项目交付
- 压测报告可展示
- Sentinel Dashboard可展示
- 安全测试报告

#### 博客列表（13篇）

| # | 系列 | 类型 | 标题 | 核心内容 |
|---|------|------|------|----------|
| 1 | 系列5 | 原理 | 高并发架构：限流、熔断、降级深度原理 | Token Bucket算法、自适应限流、熔断器原理、降级策略、热点防护 |
| 2 | 系列5 | 原理 | 分布式缓存深度：Redis设计与最佳实践 | 缓存策略(Cache-Aside/LRU)、热点key处理、内存优化、BigKey处理、集群方案 |
| 3 | 系列5 | 实战 | 网关鉴权深度：JWT + OAuth2 + 分布式Session | JWT原理与验签、令牌刷新机制、黑名单管理、SSO实现、扫码登录 |
| 4 | 系列5 | 实战 | 服务治理深度：Sentinel配置与Dashboard实战 | 流控规则配置、熔断规则、热点参数、系统自适应、Dashboard使用 |
| 5 | 系列5 | 实战 | 数据库性能优化：索引、慢查询、分库分表 | Explain分析、联合索引设计、慢查询优化、ShardingSphere、分片策略 |
| 6 | 系列5 | 实战 | RabbitMQ延迟队列：订单超时与定时任务实战 | 延迟消息插件安装、TTL与Dead Letter Queue、订单超时自动取消、定时任务替代方案对比 |
| 7 | 系列5 | 原理 | 性能基准测试深度：JMeter与Locust实战 | JMeter脚本设计、Locust Python脚本、压测场景设计、性能指标解读 |
| 8 | 系列5 | 实战 | 压测场景设计与性能基线建立 | 基准测试/峰值测试/稳定性测试设计、性能基线库、TPS/响应时间指标、容量规划 |
| 9 | 系列5 | 实战 | APM监控深度：SkyWalking与Prometheus实战 | 链路追踪原理、SkyWalking部署、Prometheus指标、Grafana可视化、告警配置 |
| 10 | 系列5 | 原理 | 安全渗透测试深度：OWASP Top 10实战 | SQL注入原理、XSS攻击防御、CSRF令牌、认证绕过、越权访问 |
| 11 | 系列5 | 实战 | 安全防护深度：防火墙与防护策略实战 | WAF配置、限流防刷、IP黑名单、请求验签、安全日志、应急响应 |
| 12 | 系列5 | 实战 | 安全扫描工具集成：SonarQube+Trivy+ZAP | SonarQube安全规则配置、依赖漏洞扫描Trivy、DAST动态扫描ZAP、扫描报告分析 |
| 13 | 系列5 | 实战 | 安全漏洞管理与修复流程规范 | 漏洞分级标准(CVSS)、修复流程、漏洞生命周期管理、安全测试报告模板 |

#### 技术点应用

| 技术点 | 项目代码位置 |
|--------|--------------|
| JWT鉴权 | edu-gateway/src/main/java/.../filter/JwtFilter.java |
| Sentinel限流 | edu-gateway/src/main/java/.../sentinel/ |
| Redis缓存 | edu-user-service/src/main/java/.../cache/ |
| 压测脚本 | edu-gateway/src/test/jmeter/ |

---

### v2.0 多端完整版

**周期**：2周 | **目标**：全端部署，实现完整AI教育平台

#### 产品功能
- uni-app多端：Web/小程序/App全端编译
- K3s部署：容器化、弹性伸缩
- 监控运维：Prometheus + Grafana
- CI/CD：自动化部署流水线

#### 项目交付
- Web端可访问
- 小程序可体验
- App可安装

#### 博客列表（10篇）

| # | 系列 | 类型 | 标题 | 核心内容 |
|---|------|------|------|----------|
| 1 | 系列6 | 原理 | uni-app多端编译原理：Web/小程序/App深度 | 条件编译原理、运行时差异、平台API适配、性能对比、架构选择 |
| 2 | 系列6 | 原理 | K3s深度：轻量级Kubernetes架构与核心组件 | k3s vs k8s架构、Traefik Ingress、ServiceLB、内置数据库、轻量化优化 |
| 3 | 系列6 | 实战 | uni-app多端适配深度：条件编译实战 | #ifdef用法、uni-API差异、生命周期差异、样式适配、原生API调用 |
| 4 | 系列6 | 实战 | 小程序适配深度：微信登录与支付集成 | wx.login流程、令牌交换、wx.requestPayment、uni.requestPayment |
| 5 | 系列6 | 实战 | App打包深度：Flutter热更新与原生插件 | CodePush热更新、platform-channel原理、原生模块开发、插件市场 |
| 6 | 系列6 | 实战 | K3s集群部署深度：Docker镜像与Helm Chart | Dockerfile优化、镜像构建、Helm模板、HPA配置、滚动更新 |
| 7 | 系列6 | 实战 | CI/CD流水线深度：GitHub Actions自动化部署 | 构建流程、测试门禁、镜像构建与推送、K3s部署、回滚机制 |
| 8 | 系列6 | 实战 | 端到端测试：Cypress/Playwright深度实践 | Cypress/Playwright选型、用户旅程测试、跨浏览器测试、测试用例设计模式 |
| 9 | 系列6 | 实战 | 测试自动化CI/CD：流水线设计与门禁配置 | GitHub Actions测试流水线、自动门禁配置、测试报告集成Allure、失败重试策略 |
| 10 | 系列6 | 实战 | 监控与日志深度：Prometheus + Grafana + Loki | 指标采集、自定义指标、可视化面板、告警规则、日志聚合、故障排查 |

#### 技术点应用

| 技术点 | 项目代码位置 |
|--------|--------------|
| 多端条件编译 | edu-web/src/pages/ |
| K3s部署 | docker/k3s/ |
| Helm Chart | docker/helm/edu-ai-platform/ |
| CI/CD | .github/workflows/ |

---

## 九、博客系列划分

| 系列 | 对应版本 | 博客数 | 主题 |
|------|----------|--------|------|
| **系列1** | v0.1-v0.3 | 23篇 | Java微服务基础 + 分布式 |
| **系列2** | v1.0 | 8篇 | LLM应用入门 |
| **系列3** | v1.1 | 10篇 | RAG + Rerank实战 |
| **系列4** | v1.2 | 20篇 | AI Agent + 多模态 + AI安全测试 |
| **系列5** | v1.5 | 13篇 | 高并发 + 性能测试 + 安全测试 |
| **系列6** | v2.0 | 10篇 | 多端部署 + E2E测试 + CI/CD测试 |

---

## 十、博客内容标准

### 每一篇博客包含三部分

| 部分 | 内容要求 | 篇幅 |
|------|----------|------|
| **一、原理深入（架构师级别）** | 底层机制、源码分析、设计权衡、架构演进 | 40% |
| **二、实战代码（关键代码）** | 核心逻辑、代码片段、完整项目见仓库 | 30% |
| **三、优化建议与最佳实践** | 性能调优、避坑指南、常见问题Q&A | 30% |

### 代码展示标准

```
关键代码展示：
- 核心逻辑代码片段
- 重要配置示例
- 完整项目代码见GitHub仓库

仓库地址：https://github.com/your-repo/edu-ai-platform
```

---

## 十一、版本交付标准

每个版本结束时的交付物：

```
1. 代码：GitHub仓库可查看（每个版本一个tag）
2. 部署：Docker Compose一键启动
3. 演示：功能截图/录屏
4. 文档：README使用说明
```

### 版本里程碑

| 版本 | 里程碑 | 演示方式 |
|------|--------|----------|
| v0.1 | 用户系统运行 | 登录/注册页面截图 + 权限菜单 |
| v0.2 | 核心业务运行 | 课程/作业/考试功能录屏 |
| v0.3 | 微服务架构 | Nacos控制台截图 + 服务列表 |
| v1.0 | AI对话 | 对话页面录屏 + 流式输出 |
| v1.1 | 知识库问答 | 文档问答演示 + RAG流程图 |
| v1.2 | Agent任务 | Agent任务面板 + 批改结果展示 |
| v1.5 | 高并发架构 | 压测报告 + Sentinel Dashboard |
| v2.0 | 全端部署 | Web/小程序/App三端截图 |

---

## 十二、博客发布平台

| 平台 | 用途 |
|------|------|
| **OpenWrite** | 多平台博客首发 |
| **掘金** | 国内技术社区同步 |
| **CSDN** | 国内技术社区同步 |
| **doocs/md** | 微信公众平台编辑 |

---

## 十三、成本估算

| 项目 | 费用 |
|------|------|
| 域名 | ¥30/年 |
| 云服务器（2核4G） | ¥80/月 |
| LLM API | **免费** (OpenRouter) |
| Ollama本地运行 | 自有GPU（可选） |
| **总计** | ¥110/月 |

---

## 十四、学习路径图

```
v0.1 (2周,8篇) → v0.2 (2周,11篇) → v0.3 (2周,9篇) → v1.0 (2周,10篇) → v1.1 (2周,12篇) → v1.2 (3周,20篇) → v1.5 (2周,13篇) → v2.0 (2周,10篇)
    ↓             ↓              ↓             ↓             ↓              ↓              ↓              ↓
 Java基础      业务开发+测试    分布式+集成    LLM接入+AI    RAG+Rerank    Agent+多模态   高并发+性能   完整部署
  +Gateway     +单元测试       +测试         +测试         +AI测试        +安全测试     +安全扫描     +E2E
```

---

## 十五、博客与项目同步策略

### 设计原则

| 原则 | 说明 |
|------|------|
| 一篇博客 = 一个功能模块 | 博客产出即项目代码 |
| 每个版本可运行展示 | 里程碑式交付，每版本有可演示成果 |
| 代码强关联 | 博客中关键代码直接用于项目 |

### 技术点应用对照

| 博客技术点 | 对应项目代码 | 文件位置 |
|------------|--------------|----------|
| Nacos注册 | 服务注册 | edu-user-service/src/main/java/.../NacosConfig.java |
| JWT鉴权 | 登录认证 | edu-user-service/src/main/java/.../security/JwtUtil.java |
| Redis缓存 | Session管理 | edu-user-service/src/main/java/.../config/RedisConfig.java |
| Seata事务 | 分布式事务 | edu-course-service/src/main/java/.../config/SeataConfig.java |
| FastAPI服务 | AI服务 | edu-ai-service/src/main.py |
| RAG检索 | 知识库 | edu-ai-service/src/rag/ |
| LangGraph | Agent | edu-ai-service/src/agent/ |
| SC Gateway | 网关 | edu-gateway/src/main/java/.../GatewayApplication.java |
| Ollama | 本地模型 | edu-ai-service/src/rerank/ |

---

## 十六、企业级预留设计

### 一、预留设计目标

为确保当前学习版本可平滑演进到企业级生产环境，在各版本中预留以下扩展点：

| 演进阶段 | 目标 | 关键预留 |
|----------|------|----------|
| 当前版本 | 学习演示 | 基础功能可运行 |
| v1.5 → v2.0 | 小规模生产 | 可观测、基础监控 |
| 未来演进 | 企业级 | 分库分表、Service Mesh、多活 |

### 二、各版本预留任务清单

#### v0.1 基础架构版 - 链路追踪与日志

| 任务 | 预留内容 | 重要性 |
|------|---------|--------|
| **TraceId链路追踪** | 网关层生成、全服务传递 | ⭐⭐⭐⭐⭐ |
| **JSON结构化日志** | 统一日志格式、便于ELK聚合 | ⭐⭐⭐⭐⭐ |
| **接口版本号** | URL增加 /api/v1/ 版本前缀 | ⭐⭐⭐⭐ |
| **Token黑名单** | Redis存储撤销Token | ⭐⭐⭐⭐ |
| **健康检查接口** | /actuator/health 端点 | ⭐⭐⭐⭐ |

**实现位置**：
- `edu-gateway/src/main/java/.../filter/TraceFilter.java` - 链路追踪
- `edu-user-service/src/main/java/.../config/JsonLogConfig.java` - JSON日志

#### v0.2 业务完善版 - 数据与安全

| 任务 | 预留内容 | 重要性 |
|------|---------|--------|
| **user_id冗余字段** | 业务表增加分片键字段 | ⭐⭐⭐⭐⭐ |
| **Snowflake ID** | 分布式ID算法预留 | ⭐⭐⭐⭐ |
| **RBAC资源权限码** | 权限码统一管理 | ⭐⭐⭐⭐ |
| **操作审计日志** | 关键操作记录 | ⭐⭐⭐⭐ |
| **密码加密升级** | 预留国密算法接口 | ⭐⭐⭐ |

**实现位置**：
- 所有业务表增加 `creator_id` / `owner_id` 字段
- `edu-user-service/src/main/java/.../id/SnowflakeIdGenerator.java`

#### v0.3 分布式基础版 - 消息与事务

| 任务 | 预留内容 | 重要性 |
|------|---------|--------|
| **消息追踪ID** | MessageContext传递traceId | ⭐⭐⭐⭐ |
| **死信队列规范** | DLX/DLQ标准化 | ⭐⭐⭐⭐ |
| **消费重试机制** | 最大重试次数+退避策略 | ⭐⭐⭐ |
| **服务版本Header** | X-Service-Version传递 | ⭐⭐⭐ |

**实现位置**：
- `edu-homework-service/src/main/java/.../rabbitmq/config/MqConfig.java`

#### v1.0 AI接入版 - AI服务抽象

| 任务 | 预留内容 | 重要性 |
|------|---------|--------|
| **统一AI服务接口** | AbstractAIService抽象类 | ⭐⭐⭐⭐⭐ |
| **Token消耗统计** | 请求埋点、计费预留 | ⭐⭐⭐⭐ |
| **模型降级策略** | 主模型失败切备选模型 | ⭐⭐⭐⭐ |
| **模型版本控制** | 模型版本号管理 | ⭐⭐⭐ |

**实现位置**：
- `edu-ai-service/src/ai/base/AIService.py`

#### v1.1 向量检索版 - 向量库扩展

| 任务 | 预留内容 | 重要性 |
|------|---------|--------|
| **向量库抽象层** | 统一VectorStore接口 | ⭐⭐⭐⭐ |
| **批量向量查询** | 预留批量检索能力 | ⭐⭐⭐⭐ |
| **向量索引配置** | HNSW参数可配置化 | ⭐⭐⭐ |
| **增量索引更新** | CDC实时同步预留 | ⭐⭐⭐ |

**实现位置**：
- `edu-ai-service/src/rag/vector_store.py`

#### v1.2 Agent版 - Agent平台预留

| 任务 | 预留内容 | 重要性 |
|------|---------|--------|
| **Agent日志追踪** | 思维链步骤记录 | ⭐⭐⭐⭐ |
| **Token成本统计** | 每个任务成本计算 | ⭐⭐⭐ |
| **任务状态持久化** | Redis存储任务状态 | ⭐⭐⭐⭐ |
| **WebSocket回调** | 异步任务结果推送 | ⭐⭐⭐⭐ |

**实现位置**：
- `edu-ai-service/src/agent/monitoring/`

#### v1.5 高并发版 - 多级缓存与监控

| 任务 | 预留内容 | 重要性 |
|------|---------|--------|
| **多级缓存接口** | L1(本地)+L2(Redis)接口 | ⭐⭐⭐⭐⭐ |
| **JVM监控暴露** | micrometer指标暴露 | ⭐⭐⭐⭐⭐ |
| **数据库连接池** | 连接数可配置化 | ⭐⭐⭐⭐ |
| **热点key告警** | BigKey监控阈值 | ⭐⭐⭐ |

**实现位置**：
- `edu-user-service/src/main/java/.../cache/MultiLevelCache.java`
- `edu-gateway/src/main/java/.../metrics/`

#### v2.0 多端完整版 - K8s生产级配置

| 任务 | 预留内容 | 重要性 |
|------|---------|--------|
| **K8s健康探针** | readiness/liveness探针 | ⭐⭐⭐⭐⭐ |
| **资源限制** | requests/limits配置 | ⭐⭐⭐⭐⭐ |
| **GPU调度配置** | nvidia.com/gpu资源声明 | ⭐⭐⭐⭐ |
| **配置外部化** | ConfigMap + Secret分离 | ⭐⭐⭐⭐ |
| **滚动更新策略** | maxSurge/maxUnavailable | ⭐⭐⭐⭐ |
| **亲和性调度** | 节点亲和性配置 | ⭐⭐⭐ |

**实现位置**：
- `docker/helm/edu-ai-platform/templates/`

### 三、核心预留代码示例

#### 1. 链路追踪Filter（v0.1）

```java
// edu-gateway/src/main/java/.../filter/TraceFilter.java
@Component
public class TraceFilter implements GlobalFilter, Ordered {
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String traceId = generateTraceId();
        exchange.getAttributes().put("traceId", traceId);
        
        // 传递给下游服务
        exchange.getResponse().getHeaders().add("X-Trace-Id", traceId);
        exchange.getResponse().getHeaders().add("X-Span-Id", generateSpanId());
        
        return chain.filter(exchange);
    }
    
    private String generateTraceId() {
        return UUID.randomUUID().toString().replace("-", "");
    }
}
```

#### 2. 多级缓存接口（v1.5）

```java
// edu-user-service/src/main/java/.../cache/MultiLevelCache.java
public interface MultiLevelCache<T> {
    
    // L1 本地缓存
    void setL1(String key, T value, long ttl, TimeUnit unit);
    T getL1(String key);
    void evictL1(String key);
    
    // L2 Redis缓存
    void setL2(String key, T value, long ttl, TimeUnit unit);
    T getL2(String key);
    void evictL2(String key);
    
    // 双检模式（预留实现）
    default T get(String key) {
        T result = getL1(key);
        if (result == null) {
            result = getL2(key);
            if (result != null) {
                setL1(key, result, 30, TimeUnit.MINUTES);
            }
        }
        return result;
    }
}
```

#### 3. 统一AI服务接口（v1.0）

```python
# edu-ai-service/src/ai/base/aiservice.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
import time

@dataclass
class AIRequest:
    model: str
    messages: List[dict]
    temperature: float = 0.7
    max_tokens: int = 2048

@dataclass  
class AIResponse:
    content: str
    model: str
    tokens_used: int
    latency_ms: int
    trace_id: str

class AIService(ABC):
    """AI服务抽象接口 - 预留企业级扩展"""
    
    @abstractmethod
    def chat(self, request: AIRequest) -> AIResponse:
        pass
    
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """预留：模型列表接口"""
        pass
    
    def _build_trace_context(self) -> dict:
        """预留：构建追踪上下文"""
        return {
            "trace_id": trace_id,
            "timestamp": time.time(),
            "service": "edu-ai-service"
        }
```

#### 4. K8s部署配置预留（v2.0）

```yaml
# docker/helm/edu-ai-platform/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: {{ .Values.app.name }}
        image: {{ .Values.image.repository }}:{{ .Values.image.tag }}
        resources:
          limits:
            cpu: "{{ .Values.resources.limits.cpu }}"
            memory: "{{ .Values.resources.limits.memory }}"
            nvidia.com/gpu: "{{ .Values.resources.limits.gpu }}"  # GPU预留
          requests:
            cpu: "{{ .Values.resources.requests.cpu }}"
            memory: "{{ .Values.resources.requests.memory }}"
        readinessProbe:
          httpGet:
            path: /actuator/health/readiness
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /actuator/health/liveness
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 15
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: {{ .Values.environment }}
        - name: TRACE_ENABLED
          value: "{{ .Values.trace.enabled }}"
```

### 四、预留设计检查清单

#### 代码层面

- [ ] 所有服务增加 `/actuator/health` 端点
- [ ] 日志格式统一为 JSON 结构
- [ ] Feign 调用增加 Fallback 降级
- [ ] 数据库表增加 owner_id 分片字段
- [ ] 关键接口增加版本号 `/api/v1/`
- [ ] 密码加密预留多算法支持
- [ ] AI 服务抽象统一接口

#### 配置层面

- [ ] 数据库连接池可外部配置
- [ ] Redis 连接参数可配置化
- [ ] 日志级别可动态调整
- [ ] 限流阈值可配置化管理

#### 部署层面

- [ ] 所有 Deployment 配置探针
- [ ] 资源限制值预留
- [ ] GPU 调度配置预留
- [ ] ConfigMap/Secret 分离

#### 可观测性

- [ ] TraceId 全链路传递
- [ ] 业务埋点标准化
- [ ] JVM 指标暴露
- [ ] AI 服务延迟统计

### 五、演进路径

```
当前版本 (学习演示)
    │
    ├── v0.1 升级：TraceId + JSON日志 + 健康检查
    │
    ├── v0.2 升级：分片字段 + RBAC + 审计日志
    │
    ├── v0.3 升级：消息追踪 + 死信队列
    │
    ├── v1.5 升级：多级缓存 + JVM监控
    │
    └── v2.0 升级：K8s生产配置 + GPU调度
                │
                ▼
         小规模生产 (1-5万用户)
                │
                ├── 分库分表 (ShardingSphere)
                ├── 读写分离 (PgBouncer)
                ├── Redis Cluster
                └── Service Mesh (Istio)
                │
                ▼
         企业级 (10-50万用户)
                ├── 多活架构
                ├── 私有化模型部署
                ├── AIOps 智能运维
                └── 零信任安全
```

---

**蓝图版本**：v8.0
**更新时间**：2026-04-02

