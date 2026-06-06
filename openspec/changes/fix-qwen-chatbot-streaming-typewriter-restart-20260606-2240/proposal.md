# Proposal: 修复 qwen-chatbot 流式输出 TypeWriterEffect 重启 bug

## 摘要

qwen-chatbot 当前流式输出时，AI 回复气泡会"先在一行闪烁几个字符，然后整段突然蹦出"，破坏类 ChatGPT 的逐字体验。根因是 `components/TypeWriterEffect.tsx` 的 useEffect 依赖 `[text, speed]`，导致每次 SSE chunk 到达都清空 `displayed` 并重启 RAF 动画。本次变更用 `displayedRef` 分离动画进度跟踪与渲染触发，让 useEffect 启动的动画从 `displayedRef.current.length` 持续累积到 `text.length`，**不再清空**，实现平滑逐字呈现。改动仅限一个组件文件 + 对应测试。

## Why

**现状痛点**：SSE 流式输出时，`pages/chat.tsx:196` 每次收到 LangChain chunk 都 `chatDispatch SET_MESSAGES`，导致最后一条 assistant 消息的 `content` 增长。`ChatWindow` 在该消息为最后一条且 `isStreaming=true` 时用 `<TypeWriterEffect text={message.content} />` 渲染。TypeWriterEffect 的 useEffect 依赖 `[text, speed]`，text 每次变化都触发 effect 内部 `setDisplayed('')` 清空 + 启动新一轮 RAF 动画。

**用户感知**："AI 思考 5 秒 → 一行字闪一下 → 5 秒后再整段蹦出"。闪烁频率等于 SSE chunk 频率（典型 100ms-2s/次），破坏"AI 在思考 + 实时回复"的心智模型，是 qwen-chatbot 端到端体验的核心障碍。

**为什么现在处理**：项目刚完成 `qwen-chatbot-code-quality-refactor`（openspec/changes/archive/2026-06-06-qwen-chatbot-code-quality-refactor/），工程化基线（OpenSpec 5 阶段 + vitest + Playwright）已就绪；TypeWriterEffect 现有 3 个单元测试覆盖率稳定；本次为组件内部状态机修复，不动公共 API / 后端 / 数据库，是低风险高价值的修复窗口。

**预期收益**：恢复类 ChatGPT 的平滑流式体验；不破坏既有功能；不引入新依赖；改动可单文件 revert。

## 用户价值

- **目标用户**：qwen-chatbot 终端用户（开发者 / 学生 / 内部测试者）
- **使用场景**：在浏览器中向 AI 发送问题，期望逐字/逐块看到 AI 回复
- **可感知变化**：
  - 修复前：回复气泡"在一行闪烁几字符 → 突然整段蹦出"
  - 修复后：回复气泡"平滑逐字 / 逐块累积呈现"
- **价值量化**：
  - 流式输出体感从"破坏体验"提升到"类 ChatGPT 基线"
  - 0 新增依赖、0 后端变更、0 数据库变更
  - 100% 修复覆盖（无新代码路径，只是修复既有路径的 bug）

## 成功标准

| 指标 | 当前值 | 目标值 | 数据来源 |
|---|---|---|---|
| AI 回复呈现行为 | 闪烁 + 突然全蹦 | 平滑逐字累积 | 浏览器手动验证 + Playwright 录屏（既有 e2e 01-send-message） |
| 流式过程中 `displayed === ''` 中间态 | 每次 chunk 都出现 1 次 | 0 次 | 新增单元测试断言 |
| TypeWriterEffect 单元测试通过率 | 3/3 | 5/5（既有 3 + 新增 2） | `pnpm vitest run components/TypeWriterEffect.test.tsx` |
| qwen-chatbot 全量覆盖率 | 待基线 | 维持 ≥ 65/75/70/65 | `pnpm vitest run --coverage` |
| 既有 e2e 通过 | 全绿 | 全绿（不回归） | `pnpm exec playwright test` |
| lint / typecheck | 全绿 | 全绿 | `pnpm lint` + `pnpm typecheck` |

## What Changes

**TypeWriterEffect 行为（流式增量累积）**
- From: useEffect 依赖 `[text, speed]`；text 每次变化时清空 `displayed` + 启动新一轮 RAF 动画从 i=0 累积到 `text.length`
- To: useEffect 依赖保持 `[text, speed]`；text 变化时从 `displayedRef.current.length` 累积到 `text.length`，**不**清空 `displayedRef`（除 text 变短/变空外）
- Reason: 修复"闪烁 + 全蹦" bug；保留打字机视觉效果
- Impact: 非破坏性，公共 API 不变（仅 `text` / `speed` / `className` 三个 props）

**TypeWriterEffect 边界处理（text 变短）**
- From: 旧实现未显式处理 text 变短场景（依赖 effect 反复重启动画）
- To: 新增显式分支 `displayedRef.current.length > text.length` 时直接同步 `displayedRef = text; setDisplayed(text)`，不做动画回退
- Reason: 避免数据漂移（陈旧 displayed 残留）；避免"打字机倒退"诡异动画
- Impact: 边界场景更健壮；既有用例无回归

**TypeWriterEffect 边界处理（text 变空）**
- From: 旧实现未显式处理（依赖 effect 反复重启动画）
- To: 新增显式分支 `text.length === 0` 时 `displayedRef.current = ''; setDisplayed(''); return`
- Reason: 明确"重置"信号；避免陈旧 displayed 残留
- Impact: 边界场景更健壮

**TypeWriterEffect 边界处理（text === displayedRef.current）**
- From: 旧实现仍会启动 RAF（虽然首帧 `i < text.length` 为 false 不递归）
- To: 显式 `if (displayedRef.current === text) return;` 跳过
- Reason: 避免无意义 RAF 调度；保证幂等
- Impact: 微小性能优化（无 op 时不调度）

**单元测试覆盖**
- From: 3 个测试（empty / progressively reveal / full text after RAF）
- To: 5 个测试（既有 3 + 新增 2：`text 增长不重启` + `text 变短同步`）
- Reason: 锁定 bug 修复行为；防止回归
- Impact: 覆盖率提升；测试运行时间略微增加（毫秒级）

## Capabilities

### New Capabilities

无。本次不引入新 capability，bug 修复点已落在既有 `streaming-chat` capability 的 `TypeWriterEffect 性能优化` Requirement 范围内。

### Modified Capabilities

- **`streaming-chat`**（修改 `TypeWriterEffect 性能优化` Requirement）：
  - **变更内容**：将"文本变化重置"行为（`props text` 从 `"Hello"` 变 `"World"` 时重新开始累积 `World`、不并发累积两者）改为"文本增长持续累积"（`text` 增长时从 `displayedRef.current.length` 继续累积到 `text.length`，不清空已显示部分）
  - **同步新增边界 Scenario**：
    - 文本变短同步（`text` 短于已显示部分时直接同步，不做动画回退）
    - 文本 === displayed 跳过（完全追上时跳过 RAF 调度，保证幂等）
  - **不修改**：`字符级 vs 块级累积`（CHUNK_SIZE=3 保持）、`空文本边界`、`长文本不阻塞` 等其他 Scenario
  - **delta 操作**：MODIFIED Requirements

## Impact

**受影响的代码**：
- `qwen-chatbot/components/TypeWriterEffect.tsx`（修改，约 10 行净改动）
- `qwen-chatbot/components/TypeWriterEffect.test.tsx`（修改，新增 2 个测试 case）

**API 影响**：无
- 公共 API（`text` / `speed` / `className` props）不变
- 不动后端 `/api/qwen` 端点
- 不动 ChatContext / ChatWindow / chat.tsx

**依赖影响**：无
- 不新增 npm 依赖
- 不修改 `package.json`

**数据库变更影响**：**无数据库变更**（纯前端组件内部状态机修复）

**用户影响**：无
- 无需用户操作
- 无需数据迁移
- 无 API Key / 配置变更
- 体验提升（修复 bug）

**文档影响**：无
- README.md / 用户手册无需更新
- TypeWriterEffect 文件顶部注释将更新以说明修复点（实施时一并完成）

**支持影响**：无
- 客服无需知道此次变更
- 错误码 / 错误信息不变

## 发布策略

**一次性上线**（单文件改动 + 单文件测试改动，无公共 API 变更）。

- **不**需要功能开关（feature flag）
- **不**需要灰度发布
- **不**需要数据迁移
- **不**需要配合其他发布
- **兼容性**：完全向后兼容（既有调用方式 `<TypeWriterEffect text={message.content} />` 不变）
- **建议发布时间**：任意（无业务高峰期依赖）
- **bundle 体积影响**：微乎其微（仅一个文件内函数重排）

## 回滚方案

**回滚操作**：
- 单文件 revert：`git revert <feat-commit-hash>` 即可恢复 `TypeWriterEffect.tsx` 旧实现
- 行为回滚：useEffect 恢复为原 `[text, speed]` 依赖 + `setDisplayed('')` 清空 + 启动 RAF；功能完整，仅 UX 退化到"闪烁 + 突然全蹦"原状态

**回滚影响**：
- 无数据丢失（无状态持久化变更）
- 无 API 变更
- 无需用户操作
- 旧实现已在 `git log` 中可追溯

**回滚后验证**：
- 单元测试：既有 3 个 TypeWriterEffect 测试仍通过
- e2e：既有 `e2e/01-send-message.spec.ts` 仍通过
- 手动：流式输出"闪烁 + 全蹦"行为复现（与本次修复前一致）

**回滚决策时机**：
- 如发现 `displayedRef` 与 `displayed` state 漂移导致渲染异常
- 如发现 RAF 调度异常导致性能问题
- 如发现边界场景（text 变短/变空）出现新 bug

## 待定事项

无。设计已收敛，关键决策（D1-D8）均有明确选择 + 理由 + 已考虑备选；用户已在前置 Q&A 确认方案 A；测试覆盖策略已规划；回滚策略已明确。

如后续发现新需求（如"重新生成历史消息时启用打字机"），可走单独 change 引入 `animated` prop 或新增 `history-replay-with-typewriter` capability。
