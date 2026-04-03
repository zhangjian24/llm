# 教育平台 Maven 多模块设计与项目初始化

> 本文为 AI 教育平台系列博客第三篇，讲解 Maven 多模块设计
> 
> 仓库地址：https://github.com/anomalyco/edu-ai-platform

---

## 一、背景

Maven 多模块项目是微服务架构的基础，本文详细介绍教育平台的多模块设计。

---

## 二、模块划分原则

### 2.1 经典四层架构

```
edu-ai-platform/
├── edu-api/           # API模块（接口定义）
│   └── com.edu.xxx.api
├── edu-domain/        # 领域模块（实体、枚举）
│   └── com.edu.xxx.domain
├── edu-infrastructure/# 基础设施模块（DB、Redis）
│   └── com.edu.xxx.infrastructure
└── edu-web/           # Web模块（Controller）
    └── com.edu.xxx.web
```

### 2.2 微服务模块划分

```
edu-ai-platform/
├── pom.xml                    # 父项目
├── edu-user-service/          # 用户服务
│   ├── pom.xml
│   └── src/main/java/...
├── edu-course-service/        # 课程服务
├── edu-homework-service/      # 作业服务
├── edu-exam-service/          # 考试服务
├── edu-ai-service/            # AI服务（Python）
├── edu-gateway/                # 网关服务
└── edu-web/                   # 前端
```

---

## 三、父项目 pom.xml 设计

### 3.1 版本管理

```xml
<properties>
    <java.version>17</java.version>
    <maven.compiler.source>17</maven.compiler.source>
    <maven.compiler.target>17</maven.compiler.target>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    
    <spring-boot.version>3.2.5</spring-boot.version>
    <spring-cloud.version>2023.0.1</spring-cloud.version>
    <spring-cloud-alibaba.version>2023.0.1.2</spring-cloud-alibaba.version>
</properties>
```

### 3.2 依赖管理

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-dependencies</artifactId>
            <version>${spring-boot.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
        
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-dependencies</artifactId>
            <version>${spring-cloud.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

### 3.3 插件管理

```xml
<build>
    <pluginManagement>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <version>${spring-boot.version}</version>
            </plugin>
        </plugins>
    </pluginManagement>
</build>
```

---

## 四、子模块 pom.xml

### 4.1 继承父项目

```xml
<project>
    <modelVersion>4.0.0</modelVersion>
    
    <parent>
        <groupId>com.edu</groupId>
        <artifactId>edu-ai-platform</artifactId>
        <version>0.1.0-SNAPSHOT</version>
    </parent>
    
    <artifactId>edu-user-service</artifactId>
    <packaging>jar</packaging>
</project>
```

### 4.2 依赖声明

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    
    <dependency>
        <groupId>com.alibaba.cloud</groupId>
        <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
    </dependency>
    
    <dependency>
        <groupId>com.baomidou</groupId>
        <artifactId>mybatis-plus-spring-boot3-starter</artifactId>
    </dependency>
</dependencies>
```

---

## 五、项目结构

### 5.1 edu-user-service 结构

```
edu-user-service/
├── pom.xml
└── src/
    ├── main/
    │   ├── java/
    │   │   └── com/edu/user/
    │   │       ├── UserServiceApplication.java
    │   │       ├── config/           # 配置类
    │   │       ├── controller/       # 控制器
    │   │       ├── service/          # 服务层
    │   │       ├── mapper/            # 数据访问层
    │   │       ├── entity/            # 实体类
    │   │       ├── dto/               # 数据传输对象
    │   │       ├── vo/                # 视图对象
    │   │       ├── feign/             # Feign客户端
    │   │       ├── security/          # 安全相关
    │   │       └── common/            # 公共组件
    │   └── resources/
    │       ├── application.yml        # 应用配置
    │       └── mapper/                 # MyBatis映射文件
    └── test/
        └── java/
```

---

## 六、Feign 客户端示例

### 6.1 定义接口

```java
// edu-user-service/src/main/java/.../feign/UserFeignClient.java
@FeignClient(name = "edu-user-service", fallback = UserFeignClientFallback.class)
public interface UserFeignClient {
    
    @GetMapping("/user/{id}")
    Map<String, Object> getUserById(@PathVariable("id") Long id);
}
```

### 6.2 Fallback 实现

```java
@Component
public class UserFeignClientFallback implements UserFeignClient {
    
    @Override
    public Map<String, Object> getUserById(Long id) {
        return Map.of("error", "service unavailable");
    }
}
```

### 6.3 启用 Feign

```java
@SpringBootApplication
@EnableDiscoveryClient
@EnableFeignClients
public class UserServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(UserServiceApplication.class, args);
    }
}
```

---

## 七、最佳实践

### 7.1 dependencyManagement 的作用

- 统一管理所有子模块的依赖版本
- 子模块只需声明 groupId 和 artifactId
- 版本由父项目统一控制

### 7.2 聚合与继承

```
聚合(packaging=pom) + 继承(parent) = 标准Maven多模块项目
```

### 7.3 常用命令

```bash
# 构建所有模块
mvn clean install

# 构建指定模块
mvn clean install -pl edu-user-service

# 跳过测试
mvn clean install -DskipTests

# 查看依赖树
mvn dependency:tree
```

---

## 八、项目代码

完整代码见：
- [edu-ai-platform/pom.xml](https://github.com/anomalyco/edu-ai-platform/pom.xml)
- [edu-user-service/pom.xml](https://github.com/anomalyco/edu-ai-platform/tree/main/edu-user-service)

---

## 九、总结

Maven 多模块设计核心：
1. **版本统一管理**：父项目统一版本号
2. **依赖统一管理**：dependencyManagement
3. **模块职责清晰**：按功能划分模块
4. **聚合与继承**：构建效率提升

---

**下篇预告**：Spring Boot + Nacos 服务注册与调用

---

**参考**：
- Maven 3.9+ 官方文档
- Spring Cloud Alibaba 2023.0.1.2
