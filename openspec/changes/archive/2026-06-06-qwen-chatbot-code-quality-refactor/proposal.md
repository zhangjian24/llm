# Proposal: qwen-chatbot-code-quality-refactor

## 摘要

qwen-chatbot 是一个 Next.js 16 + React 19 + LangChain 的通义千问聊天机器人，当前存在 4 处类型重复、Hook 引用不稳定、流式响应双重渲染、零测试覆盖等 50+ 项质量问题。本次变更在保持产品行为 100% 不变的前提下，按 13 个任务系统性改造：统一类型源、拆分 Context、稳定 Hook 引用、抽取共享组件、补齐 ESLint+Prettier+单元+组件+E2E 测试体系，达到 `tsc 0 错 / lint 0 警 / 覆盖 ≥ 80% / E2E 全绿 / Lighthouse ≥ 90` 的质量门禁。

## Why

**现况痛点**：通过对 22 个源文件全面审查，识别出严重问题 6 项、重要 14 项、次要 22 项。突出矛盾包括：① 4 个核心类型接口在 5 个组件中重复定义，演进时易失同步；② `useRoleStorage.updateRole` 多次 `setState` 导致状态/存储错位；③ 流式响应同时维护 `messages` 数组末尾与 `currentResponse` 两份内容，UI 重复渲染；④ `AppContext` 每次 dispatch 序列化全量状态（含每次按键的 inputMessage），性能差且 5MB 容量风险；⑤ `useEffect` 依赖未稳定的 Hook 函数引用；⑥ 零测试 + ESLint 缺失导致 `pnpm run lint` 名存实亡。

**为什么现在处理**：本项目为单人维护，下一次接手或 AI 协作时，类型不一致与状态 bug 将成倍放大修复成本。早投入 2-3 周系统性改造，长期维护成本可降低 50% 以上。

**预期收益**：① 单一类型源后，组件 props/接口演进 0 同步成本；② 状态可预测，避免隐藏 bug；③ 流式渲染路径清晰，性能提升；④ 测试覆盖保护后续改动安全；⑤ 工具链就绪，CI 自动化质量门禁。

## 用户价值

**N/A — 本次为纯工程改造，用户行为 100% 不变。**

- 目标用户：项目开发者 / 维护者
- 受益场景：日常维护、二次开发、AI 辅助协作
- 用户感知：当前功能、UI、交互、性能基线全部保留；唯一可感知的是构建产物体积可能略减（移除调试代码后）

## 成功标准

| # | 指标 | 当前基线 | 目标值 | 数据来源 |
|---|------|----------|--------|----------|
| 1 | tsc 编译错误 | 未统计 | 0 | `tsc --noEmit` |
| 2 | ESLint 警告 | 未配置 | 0 | `pnpm run lint` |
| 3 | 单元 + 组件测试覆盖率 | 0% | ≥ 80% | `vitest run --coverage` |
| 4 | E2E 关键路径通过 | 无 | 100% | Playwright |
| 5 | 生产构建中 `console.log` 数量 | 1+ | 0 | `grep -r "console.log" dist/` |
| 6 | Lighthouse Performance | 未测 | ≥ 90 | `lighthouse http://localhost:3000` |
| 7 | 跨文件同名 interface 数量 | 4 | ≤ 1 | `grep -r "^interface" components/ lib/ types/` |
| 8 | useEffect 依赖中非稳定函数 | 多 | 0（除原生 setter） | 人工审查 + ESLint `react-hooks/exhaustive-deps` |

**关键路径**（E2E 必须覆盖）：
1. 进入 `/chat` 发送消息并收到流式响应
2. 在 `/roles` 创建 → 编辑 → 设为默认 → 删除角色
3. 配置 API Key → 测试连接 → 保存
4. 打开历史模态框 → 编辑评价
5. 切换角色后 ModelConfigPanel 锁定

## What Changes

### 类型系统

- From: `Role`、`Message`、`ConversationHistory`、`ModelConfig` 在 5 个文件中分别重复定义
- To: 全部集中在 `types/index.ts` 单一源，其他文件 `import type`
- Reason: 消除类型演进不同步风险
- Impact: 非破坏性，纯合并；`tsc` 应保持兼容

### 状态管理

- From: `AppContext` 统一管理 4 类状态（messages / history / inputMessage / selectedRoleId）；每次 dispatch 全量序列化 localStorage
- To: 拆分为 `ChatContext`（持久化）+ `UIContext`（临时态）+ `RoleContext`（角色）；持久化用 debounce + setter 回调
- Reason: 性能 + 关注点分离 + 临时态不进入存储
- Impact: 非破坏性（提供兼容层），功能 1:1 复现

### Hook 引用

- From: `useRoleStorage`、`useAISettings` 返回的函数未用 `useCallback` 包装
- To: 全部用 `useCallback` 包装，引用 state 通过 setter 回调（`setRoles(prev => ...)`）
- Reason: 避免下游 `useEffect` 因引用变化而重复执行
- Impact: 非破坏性，行为一致

### 流式响应

- From: `pages/chat.tsx` 同时维护 `messages` 末尾与 `currentResponse`，UI 双重渲染
- To: 二选一，统一从 `messages[messages.length-1].content` 驱动；移除 `currentResponse` state
- Reason: 消除视觉重复，简化数据流
- Impact: 非破坏性（用户看到的内容相同）

### 错误处理

- From: `pages/chat.tsx` 错误分支使用闭包中的 `inputMessage`（已被清空）做历史记录
- To: 在 dispatch 前用本地变量缓存 `userInput`
- Reason: 错误路径下历史记录数据正确
- Impact: 错误处理更准确，正常路径行为不变

### 工具链

- From: 无 ESLint、无 Prettier、无 Vitest、无 Playwright
- To: 完整工具链 + npm scripts (`lint` / `lint:fix` / `format` / `test` / `test:e2e` / `coverage`)
- Reason: 自动化质量门禁
- Impact: 新增 devDeps 约 8 个；CI 时间增加约 30s

### 生产化

- From: `components/ChatWindow.tsx` 含 `console.log` 调试；`pages/api/verify-key.ts` 错误时仍返回 200
- To: 移除调试日志（统一 logger）；错误时返回对应 4xx 状态码
- Reason: 生产净化 + HTTP 语义正确
- Impact: 错误情况下 HTTP 状态码变化（仅开发者感知）

## Capabilities

### New Capabilities

- **`type-system`**: 统一类型源；规定 `types/index.ts` 为项目唯一类型定义入口；规定所有组件/页面/库通过 `import type` 消费
  - 范围：包含 `Role`、`Message`、`ConversationHistory`、`ModelConfig`、`QwenChatOptions`、`TokenUsage`、`ChatResponse`
  - 不包含：运行时 schema 校验（Zod）—— 后续独立 capability
  - 依赖：无

- **`chat-state-management`**: 聊天状态管理；持久化 messages 与 history，临时 UI 态分离，Context 拆分
  - 范围：包含 `ChatContext`、`useChatState`、localStorage debounce 持久化
  - 不包含：服务端同步 / IndexedDB 升级
  - 依赖：依赖于 `type-system`

- **`role-state-management`**: AI 角色管理；CRUD、默认角色迁移、localStorage 持久化、Hook 引用稳定
  - 范围：包含 `RoleContext`、`useRoleStorage` 重构、纯函数化 reducer
  - 依赖：依赖于 `type-system`

- **`ui-component-library`**: 共享 UI 组件；抽取 `<LoadingState>`、`<ModelOptions>`、`<HistoryTable>`、`<MarkdownRenderer>`，删除冗余副本
  - 范围：抽取的 4 个共享组件 + 类型化 props
  - 依赖：依赖于 `type-system`

- **`streaming-chat`**: 流式聊天体验；统一数据流、RAF 批量打字机、结构化错误处理
  - 范围：包含 `useStreamingChat` Hook、`<TypeWriterEffect>` 性能版
  - 依赖：依赖于 `chat-state-management`

- **`engineering-tooling`**: 工程质量工具链；ESLint + Prettier + Vitest + Playwright + npm scripts 编排
  - 范围：配置文件 + scripts + 覆盖率门槛
  - 依赖：无（基础设施层）

- **`frontend-quality`**: 前端体验质量；React.memo + next/dynamic 懒加载 + ARIA + focus trap + 颜色对比
  - 范围：包含性能优化 + 可访问性补齐
  - 依赖：依赖于 `ui-component-library`

### Modified Capabilities

无（项目当前无现有 spec，全部为新建）

## Impact

### 技术影响

| 类别 | 内容 |
|------|------|
| 改动文件 | ~13 个（components / pages / lib / contexts / types） |
| 新增文件 | ~6 个（Context 拆分 + 共享组件 + tests） |
| 删除文件 | 1 个（`components/ConversationHistoryTable.tsx`） |
| 新增依赖 | `eslint` `eslint-config-next` `prettier` `vitest` `@vitest/ui` `@testing-library/react` `@testing-library/jest-dom` `jsdom` `@playwright/test` `lighthouse` |
| 修改依赖 | 移除 debug 残留 import |
| 配置文件 | 新增 `.eslintrc.json`、`.prettierrc`、`.editorconfig`、`vitest.config.ts`、`playwright.config.ts` |
| API 行为 | `/api/verify-key` 错误时 HTTP 状态码从 200 改为 401/400（仅开发者感知） |

### 用户影响

- ❌ 无需用户迁移 / 重新配置
- ❌ 无功能变化
- ❌ 无 UI 变化
- ✅ localStorage 数据格式保持兼容（schema 字段不变）

### 文档影响

- `README.md` 需补齐：测试命令、Lint 命令、覆盖率门槛说明
- 新增 `CONTRIBUTING.md`（可选，本次可不创建）

### 支持影响

- 无客服影响（无功能变化）

## 发布策略

**一次性上线（单 PR 合并即生效）**

- 实施方式：单 git worktree 隔离，13 任务按依赖顺序串行 commit
- 合并时机：所有质量门禁通过、E2E 全绿
- 兼容性：100% 向后兼容，localStorage 现有数据无需迁移
- 回滚窗口：PR 未合并前可随时丢弃；合并后通过 git revert 即可（详见回滚方案）

## 回滚方案

### 回滚触发条件

- E2E 关键路径任何一条失败
- tsc / lint / 覆盖率门槛未达标
- 性能回归（Lighthouse < 90 或交互 P95 > 200ms）
- 生产构建报错
- 用户反馈功能性 regression

### 回滚步骤

1. **未合并前**：直接删除 worktree / 关闭 PR
2. **已合并后**：
   - 主分支：`git revert <merge-commit-sha>` → 推送 → 触发 CI
   - 紧急：`git reset --hard <last-good-sha> && git push --force`（仅当 revert 不足以恢复时）
3. **数据层**：本变更**不修改** localStorage schema，无需数据回滚
4. **依赖层**：新增 devDeps 不影响生产构建；如需彻底回滚，运行 `pnpm remove` 对应包

### 回滚影响

| 维度 | 影响 |
|------|------|
| 功能 | 100% 恢复至变更前（无功能变化） |
| 数据 | 0 损失（localStorage schema 不变） |
| 性能 | 0 影响（仅移除调试代码可能轻微减包） |
| 工具链 | 新增的 ESLint / Vitest 配置可保留，不影响运行时 |

## 待定事项

无。所有关键决策已通过对话收敛。

如需调整任一决策（D1-D10），应在新 OpenSpec change 中提出，本次不修改 proposal。
