# streaming-chat Delta Spec

> Delta spec for change `fix-qwen-chatbot-streaming-typewriter-restart-20260606-2240`.
> 修改 `streaming-chat` capability 中的 `TypeWriterEffect 性能优化` Requirement。
> Archive 阶段 apply 后，openspec/specs/streaming-chat/spec.md 中该 Requirement 内容将被本档完整替换。

## Purpose

N/A — Purpose 段不修改，archive 时保持 openspec/specs/streaming-chat/spec.md 现有 Purpose（TBD - created by archiving change qwen-chatbot-code-quality-refactor. Update Purpose after archive.）。

## MODIFIED Requirements

### Requirement: TypeWriterEffect 性能优化

**User Story**: As a 用户，I want 流式响应流畅不卡顿 so that 长时间对话体验良好。

**Priority**: P1

**Acceptance**: 该 spec MUST: 1000 字符文本打字机期间，主线程长任务 ≤ 50ms。

**Non-functional**: 性能：单次 RAF 周期内 `setDisplayedText` 调用 ≤ 1 次

`<TypeWriterEffect>` MUST 满足：

1. 使用 `requestAnimationFrame` 替代 `setTimeout` 触发字符累积
2. 每次 RAF 内累积 `CHUNK_SIZE = 3` 字符（非单字符）
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
- **AND** 视觉上每帧推进 3 字符
