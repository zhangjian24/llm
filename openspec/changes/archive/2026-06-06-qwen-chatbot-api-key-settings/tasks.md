## 1. useAISettings Hook

- [x] 1.1 新建 `components/useAISettings.ts`，封装 apiKey 的 localStorage 读写（key: `qwen_chatbot_api_key`）
- [x] 1.2 导出 `useAISettings()` Hook，返回 `{ apiKey, setApiKey, clearApiKey, hasKey }`
- [x] 1.3 导出纯函数 `getStoredApiKey()` 供 chat.tsx 同步读取

## 2. /settings 设置页面

- [x] 2.1 新建 `pages/settings.tsx`，使用 Layout 组件包裹
- [x] 2.2 添加 API Key 输入框（type="password" / text 切换），绑定 useAISettings
- [x] 2.3 添加"保存配置"按钮，写入 localStorage + 显示成功提示
- [x] 2.4 添加"测试连接"按钮，调用 /api/verify-key，显示成功/失败状态

## 3. /api/verify-key 验证端点

- [x] 3.1 新建 `pages/api/verify-key.ts`，接收 POST `{ apiKey }`
- [x] 3.2 使用 `ChatOpenAI` 实例化后调用一次 listModels 或最小请求验证 Key
- [x] 3.3 返回 `{ success: true }` 或 `{ success: false, error: string }`

## 4. API Key 传递链路

- [x] 4.1 修改 `lib/langchain/index.ts`，`createQwenChatModel` 增加 `apiKey` 参数，优先使用参数值，fallback `process.env.OPENAI_API_KEY`
- [x] 4.2 修改 `pages/api/qwen.ts`，从 `req.body.api_key` 接收 Key，传给 `createQwenChatModel`

## 5. chat.tsx 拦截与传递

- [x] 5.1 修改 `pages/chat.tsx`，handleSubmit 入口调用 `getStoredApiKey()` 检查 Key
- [x] 5.2 Key 为空时 `alert()` 提示 + `router.push('/settings')`，阻止发送
- [x] 5.3 Key 存在时在 POST body 中添加 `api_key` 字段

## 6. 导航入口

- [x] 6.1 修改 `components/Sidebar.tsx`，添加"设置"导航项，path 指向 `/settings`
