# chat-state-management Specification

## Purpose
TBD - created by archiving change qwen-chatbot-code-quality-refactor. Update Purpose after archive.
## Requirements
### Requirement: Context 三拆分架构

**User Story**: As a 项目维护者，I want 聊天状态按"持久化 / 临时态 / 角色"拆分到独立 Context so that 关注点分离，避免临时态进入持久化层。

**Priority**: P0

**Acceptance**: 该 spec MUST: 存在 `ChatContext`、`UIContext`、`RoleContext` 三个独立 Context，临时 UI 态不再进入 localStorage。

**Non-functional**: 性能：单次 dispatch 触发的组件重渲染范围应 ≤ 当前方案

Context 拆分 MUST 满足：

1. `ChatContext`：管理 `messages` 和 `conversationHistory`，与 localStorage 同步
2. `UIContext`：管理 `inputMessage`（仅内存）
3. `RoleContext`：管理 `roles` 和 `selectedRoleId`，与 localStorage 同步
4. `AppContext`（旧）保留为兼容层或在迁移完成后删除
5. 每个 Context MUST 提供语义化方法（如 `addMessage`、`clearMessages`），不直接暴露 `dispatch`

#### Scenario: 三 Context 独立订阅
- **WHEN** `pages/chat.tsx` 同时需要 messages、inputMessage、roles
- **THEN** MUST 分别通过 `useChatContext()`、`useUIContext()`、`useRoleContext()` 获取
- **AND** `inputMessage` 更新 MUST 仅触发 `UIContext` 订阅者重渲染
- **AND** `messages` 更新 MUST 仅触发 `ChatContext` 订阅者重渲染

#### Scenario: 临时态不入存储
- **GIVEN** 用户在 `ChatInput` 中输入文字
- **WHEN** `inputMessage` state 更新
- **THEN** localStorage MUST NOT 写入新数据
- **AND** `ChatContext` 订阅者 MUST 不重渲染
- **AND** 仅 `UIContext` 订阅者重渲染

#### Scenario: 持久化态同步 localStorage
- **GIVEN** 用户发送消息
- **WHEN** `addMessage` 被调用
- **THEN** `ChatContext` MUST 在 ≤ 500ms 内（debounce 阈值）写入 localStorage
- **AND** 写入 MUST 在 try/catch 中，失败 MUST 仅 `console.error`，不崩溃应用

---

### Requirement: 持久化操作 debounce

**User Story**: As a 项目维护者，I want 状态持久化操作节流 so that 高频输入不会导致 localStorage 频繁写入。

**Priority**: P0

**Acceptance**: 该 spec MUST: 单次 dispatch 触发写入的频率 ≤ 2 Hz（500ms 间隔）。

**Non-functional**: 性能：1000 条历史记录下，dispatch 后主线程阻塞 ≤ 50ms

持久化 MUST 使用 debounce 策略：

1. dispatch 后 MUST 经过 500ms debounce 才写入 localStorage
2. 期间再次 dispatch MUST 重置 debounce 计时器
3. 应用卸载时 MUST 立即 flush 待写入数据（`beforeunload` 事件）
4. debounce 实现 MUST 使用 `use-debounce` 库的 `useDebouncedCallback` 或等价自实现

#### Scenario: 高频输入不触发写入
- **GIVEN** 用户在 1 秒内连续输入 10 个字符（10 次 dispatch）
- **WHEN** debounce 计时器到期
- **THEN** localStorage 写入次数 MUST 为 1（而非 10）
- **AND** 写入内容 MUST 为最终完整 state

#### Scenario: 卸载时 flush
- **GIVEN** 用户编辑消息后立即关闭标签页（< 500ms）
- **WHEN** `beforeunload` 事件触发
- **THEN** MUST 同步写入 localStorage
- **AND** 重开应用后 MUST 能恢复最新状态

#### Scenario: 写入失败容错
- **GIVEN** localStorage 已满（QuotaExceededError）
- **WHEN** 尝试写入
- **THEN** MUST 捕获异常并 `console.error`
- **AND** 应用 MUST 继续运行（不崩溃）
- **AND** 下次成功的写入 MUST 覆盖失败数据

---

### Requirement: 容错读取 localStorage

**User Story**: As a 项目维护者，I want localStorage 读取具备完整容错 so that 损坏或旧版数据不会让应用崩溃。

**Priority**: P0

**Acceptance**: 该 spec MUST: 任意 localStorage 数据状态（缺失/损坏/旧版）下应用均能正常初始化。

**Non-functional**: N/A

`getInitialState` MUST 满足：

1. 用 `try/catch` 包裹所有 `localStorage.getItem` 与 `JSON.parse` 操作
2. 解析失败 MUST 回退到 `defaultState` 并 `console.error`
3. 关键数组字段（`messages`、`conversationHistory`）MUST 用 `Array.isArray` 校验，非数组时回退默认值
4. 关键对象字段 MUST 校验类型，缺失字段回退默认值
5. 加载状态 MUST 包含 `schemaVersion` 字段（新增），缺失时默认为 1

#### Scenario: 缺失数据
- **GIVEN** localStorage 中无 `appState` 键
- **WHEN** 应用初始化
- **THEN** MUST 使用 `defaultState`（空数组 + 空字符串 + null）
- **AND** MUST NOT 抛错

#### Scenario: 损坏 JSON
- **GIVEN** localStorage 中 `appState` 为非合法 JSON（如 `"{invalid"`)
- **WHEN** 应用初始化
- **THEN** MUST 捕获 `SyntaxError`
- **AND** MUST 回退到 `defaultState`
- **AND** MUST `console.error` 错误信息

#### Scenario: 字段类型错误
- **GIVEN** localStorage 中 `appState.messages` 为字符串而非数组
- **WHEN** 应用初始化
- **THEN** MUST 将 `messages` 字段重置为空数组
- **AND** 其他字段（如 `inputMessage`）MUST 正常加载

#### Scenario: 旧版本 schema
- **GIVEN** localStorage 中 `appState` 缺少新加的 `selectedRoleId` 字段
- **WHEN** 应用初始化
- **THEN** MUST 补充默认值（`null`）
- **AND** 应用 MUST 正常运行

