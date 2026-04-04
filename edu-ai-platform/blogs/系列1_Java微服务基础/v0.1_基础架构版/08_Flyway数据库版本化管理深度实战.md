# Flyway 数据库版本化管理深度实战

> 本文为 AI 教育平台系列博客第八篇，讲解 Flyway 数据库版本化管理
> 
> 仓库地址：https://github.com/anomalyco/edu-ai-platform

---

## 一、背景

在微服务架构中，每个服务都有自己独立的数据库表结构。随着项目迭代，数据库 Schema 会不断变化：新增表、添加字段、修改索引等。如何管理这些变更？如何在团队中同步数据库结构？如何追踪每次变更的历史？

**Flyway** 是目前最流行的数据库版本管理工具，它通过 SQL 脚本记录所有数据库变更，支持版本回滚，是团队协作开发的标准实践。

---

## 二、Flyway 核心原理

### 2.1 版本化理念

Flyway 采用**版本号 + 描述**的命名规则管理 SQL 脚本：

```
V1__create_user.sql
V2__add_role.sql
V3__modify_permission.sql
```

每个脚本对应一个版本，执行后记录到 `flyway_schema_history` 表，确保只执行未迁移的脚本。

### 2.2 工作流程

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ 应用启动    │───▶│ 检查 schema_history │───▶│ 执行未迁移脚本  │
└─────────────┘    └──────────────────┘    └─────────────────┘
       │                  │                        │
       ▼                  ▼                        ▼
  读取SQL脚本      比对版本号                 更新历史记录
```

### 2.3 undo 机制（企业版）

Flyway 分为社区版（免费）和企业版。企业版支持 `U1__undo.sql` 撤销脚本，可回滚历史版本。社区版建议通过修复脚本处理错误。

### 2.4 支持的数据库

| 数据库 | 支持情况 |
|--------|----------|
| PostgreSQL | ✅ 原生支持 |
| MySQL | ✅ 原生支持 |
| Oracle | ✅ 原生支持 |
| SQL Server | ✅ 原生支持 |
| MariaDB | ✅ 原生支持 |

---

## 三、Flyway 在教育平台的应用

### 3.1 依赖配置

#### 父项目 pom.xml 版本管理

```xml
<!-- pom.xml -->
<properties>
    <flyway.version>10.10.0</flyway.version>
</properties>

<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.flywaydb</groupId>
            <artifactId>flyway-core</artifactId>
            <version>${flyway.version}</version>
        </dependency>
        <dependency>
            <groupId>org.flywaydb</groupId>
            <artifactId>flyway-database-postgresql</artifactId>
            <version>${flyway.version}</version>
        </dependency>
    </dependencies>
</dependencyManagement>
```

#### 子模块依赖声明

```xml
<!-- edu-user-service/pom.xml -->
<dependencies>
    <dependency>
        <groupId>org.flywaydb</groupId>
        <artifactId>flyway-core</artifactId>
    </dependency>
    <dependency>
        <groupId>org.flywaydb</groupId>
        <artifactId>flyway-database-postgresql</artifactId>
    </dependency>
</dependencies>
```

### 3.2 应用配置

```yaml
# edu-user-service/src/main/resources/application.yml
spring:
  datasource:
    url: "jdbc:postgresql://localhost:5432/postgresql"
    username: postgresql
    password: your_password
  flyway:
    enabled: true                    # 启用 Flyway
    baseline-on-migrate: true         # 已有数据库时基线化
    locations: classpath:db/migration # SQL 脚本路径
    baseline-version: 1               # 基线版本号
    validate-on-migrate: true         # 启动时校验
```

### 3.3 目录结构

```
edu-user-service/
├── src/main/
│   ├── java/...
│   └── resources/
│       ├── application.yml
│       └── db/migration/
│           ├── V1__create_sys_user.sql
│           ├── V2__add_role_table.sql
│           └── V3__add_permission_table.sql
```

---

## 四、SQL 迁移脚本实战

### 4.1 初始化用户表

```sql
-- V1__create_sys_user.sql
-- 用户表结构初始化
CREATE TABLE sys_user (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    nickname VARCHAR(100),
    avatar VARCHAR(255),
    status INTEGER DEFAULT 1,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted INTEGER DEFAULT 0
);

-- 用户名索引
CREATE INDEX idx_sys_user_username ON sys_user(username);

-- 邮箱索引
CREATE INDEX idx_sys_user_email ON sys_user(email);
```

### 4.2 新增角色表

```sql
-- V2__create_sys_role.sql
-- 角色表
CREATE TABLE sys_role (
    id BIGSERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    role_key VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    status INTEGER DEFAULT 1,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted INTEGER DEFAULT 0
);

-- 角色名索引
CREATE INDEX idx_sys_role_role_name ON sys_role(role_name);
```

### 4.3 用户角色关联表

```sql
-- V3__create_sys_user_role.sql
-- 用户角色关联表
CREATE TABLE sys_user_role (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 联合索引
CREATE INDEX idx_sys_user_role_uid_rid ON sys_user_role(user_id, role_id);
```

---

## 五、多模块 Flyway 管理策略

### 5.1 每个服务独立管理

在微服务架构中，**每个服务使用独立的数据库**，Flyway 脚本放在各自模块的 `src/main/resources/db/migration/` 目录下：

```
edu-user-service/src/main/resources/db/migration/
├── V1__create_sys_user.sql
├── V2__create_sys_role.sql
└── V3__create_sys_user_role.sql

edu-course-service/src/main/resources/db/migration/
├── V1__create_course.sql
└── V2__create_chapter.sql
```

### 5.2 避免跨服务依赖

- 各服务的 Flyway 脚本独立管理
- 禁止在用户服务的迁移脚本中创建课程相关表
- 如需共享数据，通过 API 或消息队列同步

### 5.3 迁移脚本命名规范

| 类型 | 命名规则 | 示例 |
|------|----------|------|
| 版本迁移 | `V{version}__{description}.sql` | `V1__create_user.sql` |
| 可撤销迁移 | `U{version}__{description}.sql` | `U1__undo_create_user.sql` |
| 可重复执行 | `R__{description}.sql` | `R__insert_init_data.sql` |

---

## 六、生产环境最佳实践

### 6.1 baseline-on-migrate

已有数据库时，需要先基线化：

```yaml
spring:
  flyway:
    baseline-on-migrate: true        # 首次运行自动创建基线
    baseline-version: 1              # 基线版本号
```

### 6.2 多环境管理

```yaml
# 开发环境
spring:
  flyway:
    locations: classpath:db/migration/dev

# 生产环境
spring:
  flyway:
    locations: classpath:db/migration/prod
```

### 6.3 CI/CD 集成

```bash
# Maven 构建时执行迁移
mvn flyway:migrate

# 查看迁移状态
mvn flyway:info

# 回滚到指定版本
mvn flyway:undo -Dflyway.target=1
```

### 6.4 常见错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| Migration V1 failed | SQL 语法错误 | 修复 SQL 后重试 |
| Schema history table not found | 未配置数据库连接 | 检查 datasource 配置 |
| Validation failed | 本地与线上版本不一致 | 执行 `flyway repair` |

---

## 七、与其他工具对比

### 7.1 Flyway vs Liquibase

| 特性 | Flyway | Liquibase |
|------|--------|-----------|
| 脚本格式 | SQL/版本控制 | XML/YAML/JSON |
| 回滚支持 | 企业版 | ✅ 支持 |
| 学习成本 | 低 | 中 |
| 社区活跃度 | 高 | 高 |

### 7.2 选型建议

- **小型项目**：Flyway（简单易用）
- **企业级项目**：Liquibase（支持复杂变更）
- **本文方案**：Flyway（已集成到教育平台）

---

## 八、项目代码

完整代码见：
- [edu-user-service/pom.xml](https://github.com/anomalyco/edu-ai-platform/tree/main/edu-user-service/pom.xml)
- [V1__create_sys_user.sql](https://github.com/anomalyco/edu-ai-platform/tree/main/edu-user-service/src/main/resources/db/migration/)
- [application.yml 配置](https://github.com/anomalyco/edu-ai-platform/tree/main/edu-user-service/src/main/resources/application.yml)

---

## 九、总结

Flyway 数据库版本化管理核心：

1. **SQL 脚本版本化**：每个变更对应一个版本脚本
2. **自动迁移**：应用启动时自动执行未迁移脚本
3. **多模块独立**：每个微服务独立管理自己的数据库变更
4. **团队协作**：通过 Git 管理 SQL 脚本，追踪变更历史
5. **最佳实践**：baseline-on-migrate 处理已有数据库

---

## 十、下篇预告

v0.1 基础架构版已完结！接下来进入 **v0.2 业务完善版**，我们将学习：

- PostgreSQL 事务与 MVCC 机制
- Redis 高可用架构
- 课程管理模块设计
- 单元测试进阶

---

**参考**：
- [Flyway 官方文档](https://flyway.db.org/)
- PostgreSQL 15 官方文档
- Spring Boot 3.2 集成 Flyway
