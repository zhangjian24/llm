## Context

qwen-chatbot 是一个基于 Next.js 16 + React 19 的全栈聊天应用，通过 LangChain 调用阿里云 DashScope 兼容 API。当前 API Key 硬编码在 `.env.local` 环境变量中，运行时不可更改。已有两套 localStorage 持久化模式（AppContext 和 useRoleStorage），新增的 API Key 配置将沿用相同的 localStorage 方案。

## Goals / Non-Goals

**Goals:**
- 用户可在 UI 中填写/修改/保存 API Key
- handleSubmit 入口自动检查 Key，缺失则提示+跳转
- 提供"测试连接"功能验证 Key 有效性
- 向后兼容已有 `.env.local` 配置

**Non-Goals:**
- 不提供 baseURL / model 等额外配置项
- 不涉及用户认证或加密存储（localStorage 明文存储）
- 不改动现有消息/角色/历史逻辑

## Decisions

### D1：API Key 存储方式

- **选择**：`localStorage("qwen_chatbot_api_key")`，独立 Hook 管理
- **理由**：与 useRoleStorage 模式一致，独立于 AppContext，降低耦合
- **已考虑 alternative**：存入 AppContext → 不合适，AppContext 已有 messages/history 等聊天状态，API Key 是独立配置

### D2：API Key 传递路径

- **选择**：chat.tsx 从 useAISettings 读取 Key → POST body 传给 `/api/qwen` → `createQwenChatModel({ apiKey })` 优先使用参数，fallback `process.env.OPENAI_API_KEY`
- **理由**：API 路由是无状态的，每次请求需要显式传递 Key；双通道保证向后兼容
- **已考虑 alternative**：服务端 session 缓存 → 不必要，Next.js API Routes 无状态设计

### D3：Key 缺失拦截策略

- **选择**：handleSubmit 函数入口同步检查，Key 为空时 `alert()` 提示 + `router.push('/settings')`
- **理由**：在发送请求前就阻断，避免无效网络请求
- **已考虑 alternative**：禁用发送按钮 → 用户可能困惑为什么不能发；API 调用后返回 401 → 浪费一次请求

### D4：验证连接机制

- **选择**：新增 `POST /api/verify-key` 端点，接收 `{ apiKey }`，尝试调用 DashScope 模型列表或最小请求，返回 `{ success: true/false, error?: string }`
- **理由**：独立端点，不干扰现有 `/api/qwen` 逻辑
- **已考虑 alternative**：在 Settings 页面发一条实际 chat 请求 → 太重且会创建无用对话

## Risks / Trade-offs

- [Risk] localStorage 明文存储 API Key → 同域脚本均可读取。Mitigation: 本项目为纯客户端应用，Key 仅用于 DashScope API 调用，风险和现有 `.env.local` 一致。
- [Risk] useAISettings 从 localStorage 读取 Key 存在竞态 → 同步读取，不存在竞态问题
- [Trade-off] 只配 Key 不配 baseURL → 部分用户可能需要自定义 endpoint。接受理由：用户明确要求仅配 Key，baseURL 指向 DashScope 是大多数场景的最优默认

## Migration Plan

1. 新建 `components/useAISettings.ts` — Hook 层
2. 新建 `pages/settings.tsx` — 设置页面 UI
3. 新建 `pages/api/verify-key.ts` — 验证连接端点
4. 修改 `lib/langchain/index.ts` — `createQwenChatModel` 增加 apiKey 参数
5. 修改 `pages/api/qwen.ts` — 从 body 取 apiKey
6. 修改 `pages/chat.tsx` — 注入 Key 检查 + 传递 Key
7. 修改 `components/Sidebar.tsx` — 加"设置"导航项

回滚：删除新增文件，git revert 修改文件即可。

## Frontend Architecture

### 技术栈
- Next.js 16 + React 19 + TypeScript
- TailwindCSS 3（桌面优先，侧边栏固定宽度 w-64）
- React Icons（Feather 图标集）
- 页面路由：Pages Router（`pages/`）

### 页面结构
```
Layout (flex min-h-screen bg-gray-50)
├── Sidebar (w-64, 桌面常驻, lg 以下可折叠)
│   ├── Logo + 应用名
│   ├── 新建对话
│   ├── 对话列表
│   └── "设置"导航项（新增）
└── 主内容区 (flex-1, lg:ml-64)
    └── pages/settings.tsx (新增)
        ├── Header: 标题 "设置" + 副标题
        └── Card (max-w-lg mx-auto)
            ├── API Key 输入框
            ├── 保存配置按钮 + 测试连接按钮
            └── 状态提示（成功/失败）
```

### 目标平台
- 平台类型：桌面端（PC Web）
- 画布尺寸：1200px（桌面端设计稿）
- 布局模式：固定侧边栏 + 弹性主内容区
- 页面内容区宽度：max-w-lg（512px），居中显示

### 组件树
```
pages/settings.tsx
└── Layout
    └── div.space-y-6
        ├── header (text-center, border-bottom)
        │   ├── h1 "设置"
        │   └── p "配置 AI 服务连接信息"
        └── div.max-w-lg.mx-auto
            └── Card (bg-white, border, rounded-lg, p-6)
                ├── Label "API Key"
                ├── Input[type=password] (w-full)
                │   └── 显示/隐藏按钮
                ├── p.hint "从阿里云百炼控制台获取"
                ├── div.flex.gap-3
                │   ├── Button "保存配置" (bg-blue-600)
                │   └── Button "测试连接" (bg-gray-100)
                ├── p.success "✓ 配置已保存" (条件显示)
                ├── p.error "✗ 错误信息" (条件显示)
                └── p.info "当前已配置 API Key" (条件显示)
```

## UI Design Tokens

### 配色方案
- 页面背景：`bg-gray-50` (#F9FAFB)
- 侧边栏背景：`bg-white` (#FFFFFF)
- 卡片背景：`bg-white` (#FFFFFF)
- 主色：`bg-blue-600 text-white` (#2563EB)
- 次按钮：`bg-gray-100 text-gray-700` (#F3F4F6 / #374151)
- 正文字色：`text-gray-800` (#1F2937)
- 次要文字：`text-gray-500/600` (#6B7280 / #4B5563)
- 成功色：`text-green-600` (#16A34A)
- 错误色：`text-red-600` (#DC2626)
- 描边：`border-gray-200/300` (#E5E7EB / #D1D5DB)

### 字体
- 系统字体栈（TailwindCSS 默认）
- Heading 标题：`text-3xl font-bold` (30px)
- 副标题：`text-base text-gray-600` (16px)
- Label：`text-sm font-medium` (14px)
- 输入框：`text-base` (16px)
- 提示文字：`text-xs text-gray-500` (12px)
- 按钮文字：`font-medium` (14-16px)

### 间距
- 页面内边距：`p-4 sm:p-6 md:p-8` (16/24/32px)
- 卡片内边距：`p-6` (24px)
- 组件间距：`space-y-4` → gap 16px
- 按钮间距：`gap-3` → 12px

### 圆角
- 卡片：`rounded-lg` (8px)
- 输入框：`rounded-lg` (8px)
- 按钮：`rounded-lg` (8px)
- 侧边栏：无圆角

## Open Questions

- 无
