## ADDED Requirements

### Requirement: API Key 配置页面
系统 SHALL 提供独立的设置页面（`/settings`），用户可在其中填写、修改和保存 API Key。

#### Scenario: 正常填写并保存 API Key
- **WHEN** 用户在设置页面输入有效的 API Key 并点击保存
- **THEN** 系统将 Key 写入 localStorage，页面显示保存成功提示

#### Scenario: 清空 API Key 并保存
- **WHEN** 用户清空 API Key 输入框并点击保存
- **THEN** 系统从 localStorage 移除 Key 并保存空值

---

### Requirement: API Key 缺失拦截
系统 SHALL 在用户发送消息前检查 API Key 是否存在，缺失时阻止发送并引导配置。

#### Scenario: 未配 Key 时尝试发送消息
- **WHEN** API Key 为空且用户点击发送按钮
- **THEN** 系统弹出提示"请先配置 API Key"，并自动跳转至 `/settings` 页面

#### Scenario: 已配 Key 时正常发送
- **WHEN** API Key 已配置且用户点击发送按钮
- **THEN** 系统正常发送消息至 API 路由

---

### Requirement: API Key 调用传递
系统 SHALL 在调用 AI 服务时将用户配置的 Key 传递给 API 路由。

#### Scenario: 使用 UI 配置的 Key 调用
- **WHEN** 用户已通过 UI 配置 Key 并发送消息
- **THEN** POST `/api/qwen` 请求体包含 `apiKey` 字段，服务端优先使用该 Key

#### Scenario: 无 UI 配置时 fallback 到环境变量
- **WHEN** localStorage 中无 API Key 但 `.env.local` 配置了 `OPENAI_API_KEY`
- **THEN** 系统使用环境变量中的 Key 调用 DashScope API

---

### Requirement: 测试连接功能
系统 SHALL 提供"测试连接"功能，验证 API Key 是否能成功连接 DashScope。

#### Scenario: 有效 Key
- **WHEN** 用户在设置页面点击"测试连接"，且 API Key 有效
- **THEN** 系统调用 `/api/verify-key`，返回 `{ success: true }`，页面显示连接成功状态

#### Scenario: 无效 Key
- **WHEN** 用户在设置页面点击"测试连接"，且 API Key 无效
- **THEN** 系统返回 `{ success: false, error: "..." }`，页面显示错误信息

#### Scenario: Key 为空时点击测试连接
- **WHEN** 用户未填写 Key 即点击"测试连接"
- **THEN** 页面提示"请先填写 API Key"，不发起网络请求
