---
trigger: always_on
---
# 详细设计说明书 (Detailed Design Document - DDD)

## 1. 模块 A 详细设计 (按模块重复此结构)
- **模块名称**: [Module Name]
- **职责描述**: [该模块的核心功能]
- **类/组件设计**:
  - **类图**: [Mermaid Class Diagram]
  - **核心类说明**:
    - `ClassName`: [职责]
    - `MethodName`: [功能简述、参数、返回值、异常]
- **时序流程**:
  - **关键业务时序图**: [Mermaid Sequence Diagram，展示对象间交互]
- **算法逻辑**:
  - [伪代码或流程图描述复杂业务逻辑]
  - [状态机图 (State Diagram)，如有复杂状态流转]

## 2. 接口设计 (API Specification)
- **接口列表**:
  - **端点**: `POST /api/v1/resource`
  - **描述**: [功能描述]
  - **请求头**: [Auth, Content-Type]
  - **请求体 (Request Body)**: [JSON Schema 示例]
  - **响应体 (Response Body)**: [成功/失败 JSON 示例]
  - **错误码定义**: [Error Codes]

## 3. 异常处理设计
- **全局异常捕获机制**: [策略]
- **事务管理**: [事务边界、隔离级别、回滚策略]
- **日志记录**: [关键日志点、日志格式]

## 4. 安全实现细节
- **输入验证**: [防SQL注入、XSS的具体实现方式]
- **权限控制**: [RBAC在具体方法上的实现逻辑]