# AGENTS.md - edu-ai-platform

AI 教育平台 - Java 微服务后端 + uni-app 前端。

## 项目结构

```
edu-ai-platform/                    # Maven 父项目 (groupId: com.edu)
├── edu-user-service/               # 用户服务 (端口 8081) - Spring Boot 3.2
├── edu-gateway/                    # API 网关 (端口 8082) - Spring Cloud Gateway
└── edu-web/                        # 前端 - uni-app + Vue 3 + Vite (端口 3000)
```

## 构建与测试命令

### Java (Maven 多模块)

```bash
# 构建所有模块
mvn clean install

# 构建单个模块
mvn clean install -pl edu-user-service -am

# 运行单个测试类
mvn test -pl edu-user-service -Dtest=UserControllerTest

# 运行单个测试方法
mvn test -pl edu-user-service -Dtest=UserControllerTest#testLogin

# 运行测试并输出详细结果
mvn test -pl edu-user-service -Dsurefire.useFile=false

# 构建时跳过测试
mvn clean install -DskipTests

# 本地运行单个服务
cd edu-user-service && mvn spring-boot:run
cd edu-gateway && mvn spring-boot:run
```

### 前端 (edu-web)

```bash
cd edu-web

# 开发服务器 (H5)
pnpm dev:h5              # http://localhost:3000

# 构建
pnpm build:h5            # 生产构建

# 其他目标
pnpm dev:mp-weixin       # 微信小程序开发
pnpm build:mp-weixin     # 微信小程序构建
pnpm build:app           # App 构建
```

### E2E 测试 (Playwright)

```bash
# 通过 OpenCode agent 执行
@playwright-e2e-tester 测试 http://localhost:3000
@playwright-e2e-tester 测试 http://localhost:3000，报告放到 ./reports/test1/
```

## 代码规范

### Java 规范

- **缩进**: 4 个空格，UTF-8 编码
- **大括号风格**: K&R（左大括号在同一行）
- **包命名**: `com.edu.<模块名>`（如 `com.edu.user`、`com.edu.gateway`）
- **类命名**:
  - 控制器: `<Entity>Controller`（如 `UserController`）
  - 服务: `<Entity>Service`（具体类，无接口）
  - Mapper: `<Entity>Mapper`（继承 `BaseMapper<Entity>`）
  - DTO: `<Action>Request` / `<Action>Response`
  - 配置: `<Purpose>Config`
  - 过滤器: `<Purpose>Filter`
  - 工具类: `<Domain>Util`
- **字段注入**: 使用 `@Autowired` 字段注入（项目规范，非构造器注入）
- **Lombok**: 实体和 DTO 使用 `@Data`。版本 1.18.32。
- **导入**: 标准 Java 优先，然后第三方，最后项目内部。`annotation.*` 包允许使用通配符导入。
- **响应格式**: 控制器当前返回 `ResponseEntity<Map>` 配合 `Map.of()`。`common.result` 中定义了 `Result<T>` 包装类但尚未使用——为保持与现有代码一致，优先使用 `ResponseEntity<Map>`。
- **错误消息**: 用户服务使用中文消息；网关使用英文。遵循模块现有约定。
- **参数校验**: DTO 使用 Jakarta Validation（`@NotBlank`、`@Email`）配合中文消息。控制器方法应在 `@RequestBody` 参数上添加 `@Valid`。

### 关键注解

```java
@SpringBootApplication, @EnableDiscoveryClient, @EnableFeignClients  // 应用启动
@RestController, @RequestMapping, @PostMapping, @GetMapping          // 控制器
@Autowired, @Service, @Mapper, @Configuration, @Bean                // 依赖注入
@Data, @TableName, @TableId(type = IdType.AUTO), @TableLogic        // 实体
@NotBlank, @Email                                                   // DTO 校验
@FeignClient(name = "...", fallback = ...)                          // Feign 客户端
@RestControllerAdvice, @ExceptionHandler                            // 异常处理
```

### 前端规范 (edu-web)

- **框架**: uni-app + Vue 3 组合式 API（`<script setup>`）
- **样式**: `.vue` 文件中使用内联 CSS（Tailwind 已配置但未 actively 使用）
- **API 调用**: `uni.request` 封装在 `src/utils/api.js` 的 Promise 工具函数中
- **认证**: Token 通过 `uni.setStorageSync` 存储，请求头携带 Bearer token
- **路由**: Hash 模式，定义在 `src/pages.json`
- **校验**: 客户端校验，使用 `uni.showToast` 显示错误反馈
- **生命周期**: 从 `@dcloudio/uni-app` 导入（如 `import { onShow } from '@dcloudio/uni-app'`）

### 配置规范

- **格式**: YAML（`application.yml`）
- **网关**: 使用带默认值的环境变量占位符：`${NACOS_SERVER:127.0.0.1:8848}`
- **用户服务**: 硬编码值（暂无环境变量占位符）
- **日志**: `com.edu` 包使用 `debug` 级别

## 架构说明

- **Spring Boot 3.2.5** + **Spring Cloud 2023.0.1** + **Spring Cloud Alibaba 2023.0.1.2**
- **Java 17**、**PostgreSQL 42.7.3**、**MyBatis-Plus 3.5.6**
- **Nacos** 用于服务发现（默认: `127.0.0.1:8848`）
- **JWT** 认证使用 `jjwt 0.12.6`，网关通过 `X-User-Id` / `X-User-Name` 请求头转发用户身份
- **网关路由**: `/api/user/**` → 去除前缀 → `/user/**` → `edu-user-service`
- **暂无测试**——测试基础设施（JUnit 5、Mockito、AssertJ）已声明但未使用

## 已知待修复问题

1. `GlobalExceptionHandler` 已定义但控制器未使用（直接返回 `ResponseEntity`）
2. `Result<T>` 包装类已定义但从未使用
3. `QueryWrapper` 使用全限定名引用而非导入
4. 控制器 `@RequestBody` 参数缺少 `@Valid` 注解
5. 网关存在重复路由定义（YAML + Java 配置）
6. 数据库密码硬编码在 `application.yml` 中
7. 未配置代码格式化/静态检查工具
