# API Key 配置页面 - 实施计划

> **For agentic workers:** Use superpowers:subagent-driven-development
> to implement this plan task-by-task.

**Goal:** qwen-chatbot 新增 `/settings` 页面，用户可在 UI 中配置 API Key，handleSubmit 入口自动检查 Key，并提供测试连接功能。

**Architecture:** API Key 存储在 localStorage（key: `qwen_chatbot_api_key`），通过独立 Hook `useAISettings` 管理。chat.tsx handleSubmit 同步检查 Key，缺失则弹窗跳转。API 调用时通过 POST body 传递 Key 到后端，服务端优先使用参数 Key，fallback `process.env.OPENAI_API_KEY`。测试连接通过独立端点 `/api/verify-key` 验证 Key 有效性。

**Tech Stack:** Next.js 16 API Routes, React 19, TailwindCSS 3, LangChain ChatOpenAI

---

## Task 1: useAISettings Hook

- [ ] **Step 1:** 新建 `components/useAISettings.ts`
  - 定义 `AISettings` 接口：`{ apiKey: string }`
  - `STORAGE_KEY = 'qwen_chatbot_api_key'`
  - 实现 `getStoredApiKey(): string` 纯函数（同步读取 localStorage）
  - 实现 `useAISettings()` Hook，返回 `{ apiKey, setApiKey, saveApiKey, clearApiKey, hasKey }`
  - `saveApiKey` 写入 localStorage + 更新 state
  - `clearApiKey` 移除 localStorage + 清空 state

- [ ] **Step 2:** 导出 `getStoredApiKey` 供 chat.tsx 同步调用

## Task 2: /api/verify-key 验证端点

- [ ] **Step 1:** 新建 `pages/api/verify-key.ts`
  - 仅接受 POST
  - 从 `req.body` 获取 `{ apiKey }`
  - 实例化 `ChatOpenAI({ apiKey, baseURL: dashscope 地址 })`
  - 调用一次最小请求（如 models list）
  - 成功 → `{ success: true }`
  - 失败 → `{ success: false, error: error.message }`

## Task 3: /settings 设置页面

- [ ] **Step 1:** 新建 `pages/settings.tsx`
  - 导入 Layout 和 useAISettings
  - 页面标题"设置"
  - API Key 输入框（建议 type="password" 带显示切换）
  - 保存按钮：写入 localStorage + 显示 "✓ 配置已保存"
  - 测试连接按钮：调用 `/api/verify-key` + 显示结果状态

## Task 4: API Key 传递链路

- [ ] **Step 1:** 修改 `lib/langchain/index.ts` — `createQwenChatModel` 增加 `apiKey?: string` 参数
  - `apiKey` 参数优先 → fallback `process.env.OPENAI_API_KEY`

- [ ] **Step 2:** 修改 `pages/api/qwen.ts`
  - 从 `req.body` 解构 `apiKey`
  - 传给 `createQwenChatModel({ apiKey })`
  - 可同时传入 model / temperature 等参数

## Task 5: chat.tsx 拦截与传递

- [ ] **Step 1:** 修改 `pages/chat.tsx`
  - 导入 `getStoredApiKey` 和 `useRouter`
  - `handleSubmit` 入口顶部调用 `getStoredApiKey()`
  - `if (!apiKey)` → `alert('请先配置 API Key')` → `router.push('/settings')` → `return`
  - API Key 存在时，POST body 添加 `apiKey` 字段

## Task 6: 导航入口

- [ ] **Step 1:** 修改 `components/Sidebar.tsx`
  - 菜单项数组新增：`{ id: 'settings', title: '设置', path: '/settings', icon: <FiSettings> }`
  - 确保 icon 已正确导入
