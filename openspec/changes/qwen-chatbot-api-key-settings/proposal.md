## Why

qwen-chatbot 当前 API Key 通过 `.env.local` 环境变量注入，用户无法在运行时查看、修改或验证 Key 有效性。这对非开发者用户构成使用障碍：启动前必须手动配环境变量，改 Key 需重启服务。随着项目面向更广泛用户，需要提供 UI 级别的 Key 管理能力。

## What Changes

**API Key 配置方式**

- From: 仅通过 `.env.local` 环境变量 `OPENAI_API_KEY` 加载，不可在 UI 修改
- To: 新增 `/settings` 页面可填写/修改 API Key，写入 localStorage；API 调用时优先使用 UI 配置的 Key，`process.env.OPENAI_API_KEY` 作为 fallback
- Reason: 用户可运行时管理 Key，无需重启服务
- Impact: non-breaking；向后兼容，已配 `.env.local` 的用户不受影响

**API Key 缺失拦截**

- From: 未配 Key 时发送请求，DashScope 返回 401 后前端显示原始错误
- To: handleSubmit 入口检查 Key 是否存在，缺失则弹窗提示并引导至 `/settings`
- Reason: 提前拦截，用户体验更好

**新增测试连接功能**

- From: 无法在 UI 验证 Key 是否有效
- To: `/settings` 页面提供"测试连接"按钮，调用 `POST /api/verify-key` 验证 Key
- Reason: 用户配 Key 后可即时确认有效性

## Capabilities

### New Capabilities

- `api-key-config`: API Key 配置页面，包含 Key 填写/保存、缺失拦截、测试连接功能

### Modified Capabilities

- None

## Impact

- **新增文件**: `components/useAISettings.ts`、`pages/settings.tsx`、`pages/api/verify-key.ts`
- **修改文件**: `components/Sidebar.tsx`、`pages/chat.tsx`、`pages/api/qwen.ts`、`lib/langchain/index.ts`
- **数据库**: 无变更（使用 localStorage）
- **依赖**: 无新增

## 回滚方案

删除新增文件，还原修改文件即可回滚。Key 配置回退至 `.env.local` 方式。
