# TypeWriterEffect SSE 竞态修复 Implementation Plan

> **For agentic workers:** 已实施完成。持续 RAF 循环方案，修复 useEffect([text]) 在 SSE 快速 chunk 下的 RAF 竞态条件。
> 步骤使用 `- [x]` 标记完成状态。

**Goal:** 修复 qwen-chatbot `TypeWriterEffect` 在 SSE 流式输出场景下的"闪烁 + 突然全蹦"bug，保留打字机动画正向累积体验，单文件修改 + 新增单测。

**Architecture:** 使用持续 RAF 循环 + ref 读取最新 text，彻底解耦动画生命周期与 text 变化生命周期。

```mermaid
graph TD
    A[组件挂载] --> B[useEffect([]) 启动 RAF 循环]
    B --> C[tick 读取 textRef.current]
    C --> D{text.length > displayedRef.length?}
    D -->|是| E{now - lastUpdate >= speed?}
    E -->|是| F[累积 1 字符 + setDisplayed]
    F --> G[requestAnimationFrame(tick)]
    E -->|否| G
    D -->|否| G
    G --> C
```

**Tech Stack:**
- React 19 + Next.js 16 (qwen-chatbot)
- TypeScript 5.x
- Vitest + @testing-library/react（既有）

---

## 文件结构

| 路径 | 状态 | 职责 |
|------|------|------|
| `qwen-chatbot/components/TypeWriterEffect.tsx` | Modified | 持续 RAF 循环 + ref 读取最新 text |
| `qwen-chatbot/components/TypeWriterEffect.test.tsx` | Modified | 新增 3 个测试（含 SSE 竞态模拟） |

不动文件：`qwen-chatbot/pages/chat.tsx`、`qwen-chatbot/components/ChatWindow.tsx`、`qwen-chatbot/components/MarkdownRenderer.tsx`。

---

## Task 1: 写失败测试（RED）

- [x] 1.1 新增 `keeps displayed text growing without restart when text prop increases mid-stream`
- [x] 1.2 新增 `synchronizes displayed text when text prop becomes shorter than already-shown`
- [x] 1.3 新增 `handles rapid text updates without dropping animation frames (SSE race condition)`
  - 使用 `vi.useFakeTimers({ toFake: ['requestAnimationFrame', 'performance', ...] })`
  - SSE 模拟：20 chunks × 5ms 间隔，speed=50ms
  - 验证：最终完整文本 + 中间帧不丢
- [x] 1.4 跑测试确认 RED（旧实现：SSE 竞态测试 FAIL，显示 "aa" ≠ 20 a's）

## Task 2: 实施修复（GREEN）

- [x] 2.1 `textRef.current = text` 每次 render 同步更新
- [x] 2.2 `useEffect([text])` 处理 text 变空/变短（同步重置/同步）
- [x] 2.3 `useEffect([])` 挂载时启动持续 RAF 循环
- [x] 2.4 RAF tick 读取 `textRef.current`，`lastUpdateRef` 控制 50ms 速度
- [x] 2.5 RAF 永不停止（持续调度下一帧），支持 text 增长
- [x] 2.6 组件卸载 cleanup 取消 RAF
- [x] 2.7 跑测试确认 GREEN（6/6 全 PASS）

## Task 3: 重构 + 验证（REFACTOR）

- [x] 3.1 更新顶部注释说明持续 RAF 循环模式
- [x] 3.2 lint 0 警告
- [x] 3.3 typecheck 0 错误
- [x] 3.4 覆盖率单文件 100%

## Commit 总结

| 顺序 | 任务 | Commit 形式 | 提交内容 |
|------|------|-------------|----------|
| 1 | Task 1 RED | `test: 2.0 添加 SSE 竞态模拟测试 RED` | TypeWriterEffect.test.tsx |
| 2 | Task 2 GREEN | `feat: 2.1 实施持续 RAF 循环重构` | TypeWriterEffect.tsx |
| 3 | Task 3 REFACTOR | `refactor: 2.2 清理 + 更新注释` | TypeWriterEffect.tsx |

## 风险与回滚

- **风险 1**：RAF 循环无限运行。在空文本时仅空转（极低开销），无内存泄漏。
- **风险 2**：`textRef.current` 更新时机。同步更新在 render 阶段，早于 RAF tick，无竞态。
- **回滚**：`git revert <commits>` 单文件 revert。