# Brainstorm: qwen-chatbot API Key 配置页面

## 背景

qwen-chatbot 当前通过 `.env.local` 中的 `OPENAI_API_KEY` 环境变量配置 API Key。
这种方式有多个问题：

- 用户无法在 UI 中配置或修改 Key
- 启动前必须配好，启动后改 Key 需要重启
- 对非开发者用户不友好

## 当前架构分析

### 配置读取链路

```
.env.local
  → process.env.OPENAI_API_KEY
  → createQwenChatModel() { apiKey: process.env.OPENAI_API_KEY }
  → @langchain/openai ChatOpenAI 实例
  → 阿里云 DashScope 兼容 API
```

Key 无 fallback，缺则直接 401。

### 状态管理层

项目已有两套 localStorage 持久化模式：

| 存储 | Key | 管理方式 | 数据 |
|------|-----|----------|------|
| AppContext | `appState` | useReducer | messages, history, input, selectedRole |
| useRoleStorage | `qwen_chatbot_roles` | useState + 独立读写 | 角色 CRUD |

### 消息流程

```
chat.tsx handleSubmit
  → POST /api/qwen { messages, stream, model, temperature, ... }
  → pages/api/qwen.ts 解析请求
  → lib/langchain/index.ts createQwenChatModel()
  → DashScope API
```

## 方案讨论

### 方案 A：独立 Settings 页面 ✅ 采纳

在 Sidebar 新增设置导航项，创建 `/settings` 页面，仅含 API Key 输入框。
HandleSubmit 入口检查 Key，缺失则弹窗提示 + 跳转。

- + 导航清晰，与 roles 页面平级
- + 可做 Test Connection
- - 需要新增一个路由

### 方案 B：模态框嵌在 /chat 页面（否决）

- - 空间受限
- - 与聊天界面混杂

### 方案 C：环境变量 + UI 双通道（采纳核心思路）

保留 `.env.local` 作为 fallback，UI 配置优先。
向后兼容已有部署。

## 设计决策

| 决策 | 结论 | 理由 |
|------|------|------|
| 配置字段 | 仅 API Key | 用户要求只配 Key |
| 存储方式 | `localStorage("qwen_chatbot_api_key")` | 与现有持久化模式一致 |
| 状态管理 | 独立 hook `useAISettings` | 不与 AppContext 耦合，简单独立 |
| 向后兼容 | key 参数优先，fallback `process.env.OPENAI_API_KEY` | 不破坏现有部署 |
| Key 缺失行为 | handleSubmit 入口检查，弹窗提示+跳转 /settings | 阻止无效请求 |
| 测试连接 | `POST /api/verify-key` → DashScope 小请求验证 | 用户可确认 Key 有效 |

## 涉及文件

| 文件 | 操作 |
|------|------|
| `components/useAISettings.ts` | 新建 |
| `pages/settings.tsx` | 新建 |
| `pages/api/verify-key.ts` | 新建 |
| `components/Sidebar.tsx` | 修改 |
| `pages/chat.tsx` | 修改 |
| `pages/api/qwen.ts` | 修改 |
| `lib/langchain/index.ts` | 修改 |

## 不做的事

- 不配 baseURL（默认指向 dashscope）
- 不配默认模型
- 不移除 `.env.local` 支持
- 不改 AppContext / useRoleStorage / types
