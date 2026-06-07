# streaming-chat Specification

## Purpose
TBD - created by archiving change qwen-chatbot-code-quality-refactor. Update Purpose after archive.
## Requirements
### Requirement: 单一数据流

Requirement text: 流式响应过程中 MUST 只看到一条正在增长的助手消息。

**User Story**: As a 用户，I want 流式响应过程中只看到一条正在增长的助手消息 so that 视觉简洁无重复。

**Priority**: P0

**Acceptance**: 该 spec MUST: 移除 `pages/chat.tsx` 中 `currentResponse` state；UI 仅从 `messages` 数组末尾驱动。

**Non-functional**: N/A

`pages/chat.tsx` 流式响应处理 MUST 满足：

1. MUST NOT 持有 `currentResponse` 本地 state
2. MUST NOT 维护独立的 `streamingContent` / `streamingUsage` state（除非为性能优化显式抽取）
3. 流式过程中 MUST 通过 `dispatch({ type: 'SET_MESSAGES', payload: [...] })` 持续更新最后一条助手消息
4. `<TypeWriterEffect>` MUST 接收 `text` prop 为 `messages[messages.length-1].content`（用 `useMemo` 提取）
5. `<ChatWindow>` MUST NOT 同时渲染"messages 末尾"和"打字机 currentResponse"两份内容

#### Scenario: 流式过程视觉无重复
- **GIVEN** 用户发送消息后流式响应进行中
- **WHEN** 检查 DOM
- **THEN** MUST 仅看到一条助手消息气泡（含 typewriter 效果）
- **AND** MUST NOT 看到两条内容相似的气泡

#### Scenario: 流结束后历史记录正确
- **GIVEN** 流式响应结束，最终内容为"完整回答"
- **WHEN** 检查 conversationHistory
- **THEN** 最新历史条目 MUST 包含完整内容
- **AND** 包含 tokenUsage（若有）

#### Scenario: 取消 currentResponse state
- **WHEN** 执行 `grep -n "currentResponse" pages/chat.tsx`
- **THEN** MUST 无匹配项（或仅在 useMemo / prop 中作为 derived value）

---

### Requirement: TypeWriterEffect 性能优化

Requirement text: 用户流式响应过程中 MUST 流畅不卡顿。

**User Story**: As a 用户，I want 流式响应流畅不卡顿 so that 长时间对话体验良好。

**Priority**: P1

**Acceptance**: 该 spec MUST: 1000 字符文本打字机期间，主线程长任务 ≤ 50ms。

**Non-functional**: 性能：单次 RAF 周期内 MUST 最多调用 `setDisplayedText` 1 次

`<TypeWriterEffect>` MUST 满足：

1. MUST 使用 `requestAnimationFrame` 替代 `setTimeout` 触发字符累积
2. MUST 每次 RAF 内累积 `CHUNK_SIZE = 3` 字符（非单字符）
3. 文本变化时 MUST 立即取消上一帧的 RAF，避免竞态
4. 文本清空时 MUST 跳过 RAF，直接退出打字状态
5. `ReactMarkdown` 解析 MUST 通过 `useMemo` 缓存稳定文本
6. **（本次新增）** 文本增长时 MUST 从已显示长度（`displayedRef.current.length`）继续累积到 `text.length`，**MUST NOT** 清空 `displayedRef` 或重启动画（除非 `text` 变短 / 变空）
7. **（本次新增）** 文本长度短于已显示长度时 MUST 直接同步 `displayed = text`（不做动画回退）
8. **（本次新增）** 当 `text === displayedRef.current` 时 MUST 跳过 RAF 调度，保证幂等（避免无 op 调度）

#### Scenario: 字符级 vs 块级累积

- **GIVEN** 100 字符的流式文本，1 秒内到达
- **WHEN** 测量 React 渲染次数
- **THEN** MUST ≤ 60 次（按 RAF 60Hz 速率）
- **AND** 原方案（按字符 setTimeout 100ms）会产生 100 次渲染

#### Scenario: 文本增长持续累积（不重置）

- **GIVEN** `text` 从 `"Hello"` 增长到 `"Hello World"`（模拟 SSE 第二个 chunk 到达）
- **AND** RAF 已累积到 `displayed = "Hello"`（或部分累积如 `"Hell"`）
- **WHEN** 组件接收新的 `text` prop
- **THEN** MUST 立即取消未完成的 RAF
- **AND** MUST 从 `displayedRef.current.length` 继续累积到 `"Hello World"`
- **AND** MUST NOT 清空 `displayedRef.current` 后从 0 重新开始
- **AND** MUST NOT 同时累积 `"Hello"` 和 `"Hello World"` 两份内容
- **AND** 在累积过程中 MUST NOT 出现 `displayed === ""` 的中间状态（除初始空 `text`）

#### Scenario: 文本变短同步

- **GIVEN** `text = "Hello World"` 已完全显示（`displayed = "Hello World"`）
- **WHEN** `text` prop 变更为 `"Hi"`（短于已显示长度）
- **THEN** MUST 直接将 `displayed` 同步为 `"Hi"`
- **AND** MUST NOT 启动动画回退显示
- **AND** MUST NOT 保留陈旧的 `"Hello World"` 残留内容

#### Scenario: 文本 === displayed 时跳过

- **GIVEN** `displayedRef.current === text`（RAF 已追上完整 `text`）
- **WHEN** `text` prop 保持不变或被重新赋相同值
- **THEN** MUST 跳过 RAF 调度
- **AND** MUST NOT 启动新一轮无 op 的动画循环

#### Scenario: 空文本边界

- **WHEN** props text 变为空字符串
- **THEN** MUST 不调用 setState
- **AND** MUST 设置 isTyping 为 false
- **AND** MUST NOT 启动 RAF 循环

#### Scenario: 长文本不阻塞

- **GIVEN** 10000 字符长文本
- **WHEN** 持续打字
- **THEN** 主线程长任务（> 50ms）次数 MUST ≤ 1
- **AND** 视觉上 MUST 每帧推进 3 字符

### Requirement: 错误处理使用本地变量

Requirement text: 错误发生时 MUST 使用本地变量保存用户输入。

**User Story**: As a 用户，I want 错误发生时历史记录仍能正确保存 so that 重试时能看到原始输入。

**Priority**: P0

**Acceptance**: 该 spec MUST: `pages/chat.tsx` catch 分支中 `inputMessage` 引用全部替换为本地变量 `userInput`。

**Non-functional**: N/A

`pages/chat.tsx` `handleSubmit` 函数 MUST 满足：

1. 在 `dispatch({ type: 'SET_INPUT_MESSAGE', payload: '' })` 之前 MUST 缓存 `const userInput = inputMessage`
2. 后续所有引用 `inputMessage` 的位置（MUST NOT 包括 UI 输入框本身的 value）MUST 替换为 `userInput`
3. 包括：
   - 发送到 API 的 `messagesToSend` 中的用户消息
   - catch 分支的 `newHistoryEntry.input`
   - catch 分支的错误消息构造

#### Scenario: 错误路径历史记录正确
- **GIVEN** 用户输入"什么是 React？"
- **WHEN** 发送请求并失败
- **THEN** 历史记录中 `input` 字段 MUST 为 "什么是 React？"
- **AND** MUST NOT 为空字符串（因已 dispatch 清空）

#### Scenario: 正常路径无影响
- **GIVEN** 用户输入"什么是 React？"
- **WHEN** 发送成功
- **THEN** 消息数组 MUST 包含完整 userMessage
- **AND** 历史记录 MUST 正确保存

#### Scenario: 多个 inputMessage 引用检查
- **WHEN** 执行 `grep -n "inputMessage" pages/chat.tsx`
- **THEN** 引用 MUST 仅在以下位置：
  - 初始 `inputMessage = state.inputMessage` 派生
  - ChatInput 组件的 `value` prop
  - `handleSubmit` 入口处的 `userInput` 缓存
- **AND** MUST NOT 在 catch 块、API 请求体、历史记录构造中直接使用

---

### Requirement: 流式响应中断处理

Requirement text: 网络中断或 API 错误时 MUST 优雅降级。

**User Story**: As a 用户，I want 网络中断时能优雅降级 so that 不必刷新页面。

**Priority**: P0

**Acceptance**: 该 spec MUST: 网络中断 / API 错误时，UI 显示明确错误信息，状态正确清理。

**Non-functional**: N/A

`pages/chat.tsx` 流式错误处理 MUST 满足：

1. `fetch` reject 时 MUST 进入 catch 分支
2. `response.ok === false` 时 MUST 抛出包含 `errorData.error` 的 Error
3. `response.body?.getReader()` 为 undefined 时 MUST 抛出明确错误
4. SSE 错误消息（`data: {"error": "..."}`）MUST 被解析并展示
5. 任何 catch 路径 MUST 在 finally 中重置 `isGenerating` / `isThinking` / `setCurrentResponse`

#### Scenario: 网络中断
- **GIVEN** 用户发送消息
- **WHEN** fetch 网络中断（`TypeError: Failed to fetch`）
- **THEN** MUST 显示 "Error: Failed to fetch"
- **AND** 历史记录 MUST 包含错误条目
- **AND** `isGenerating` MUST 变为 false

#### Scenario: HTTP 错误
- **GIVEN** API 返回 500
- **WHEN** 处理响应
- **THEN** MUST 解析 errorData.json 提取 error 字段
- **AND** 显示该错误消息
- **AND** MUST NOT 仅显示 "Failed to get response from API"

#### Scenario: SSE 错误消息
- **GIVEN** API 路由发送 `data: {"error": "AI service error"}\n\n`
- **WHEN** 客户端解析
- **THEN** MUST 捕获并显示该错误
- **AND** MUST NOT 静默忽略

#### Scenario: reader 为 null
- **GIVEN** `response.body` 为 null（极端情况）
- **WHEN** 调用 `getReader()`
- **THEN** MUST 抛出 "Could not read response body" 错误
- **AND** 走 catch 路径，UI 显示错误

#### Scenario: 状态清理完整性
- **GIVEN** 任意 catch 路径触发
- **WHEN** 检查 `finally` 块
- **THEN** MUST 包含 `setIsGenerating(false)` / `setIsThinking(false)` / `setCurrentResponse('')`
- **AND** 至少 MUST 设置 `isGenerating = false`（允许用户重新发送）

