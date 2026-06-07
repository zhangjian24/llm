# Apply Summary: fix-qwen-chatbot-streaming-typewriter-restart-20260606-2240

## Root Cause

`useEffect([text, speed])` 在每次 SSE chunk 到达时重新运行。cleanup 取消 RAF，新 effect 启动新 RAF。**SSE chunk 间隔（~10-30ms）< speed（50ms）**，RAF 在能 fire 之前就被取消，`displayedRef.current` 永远停留在 `''`，UI 一直空白。流结束切到 `<MarkdownRenderer>` 时才直接显示完整文本（"突然全蹦"）。

## Fix

**将 useEffect 动画从依赖 text 变化 → 改为持续 RAF 循环 + ref 读取最新 text：**

1. `textRef.current = text` / `speedRef.current = speed` — 每次 render 同步更新 refs
2. `useEffect([text])` — 处理 text 变空（清空）和变短（直接同步）
3. `useEffect([])` — 挂载时启动一次持续 RAF 循环，卸载时才取消
4. RAF tick 内部读取 `textRef.current` 获取最新文本，`lastUpdateRef` 控制 50ms 速度

## Files Changed

| File | Change |
|------|--------|
| `qwen-chatbot/components/TypeWriterEffect.tsx` | 重写动画逻辑：持续 RAF 循环 + ref 读取 |
| `qwen-chatbot/components/TypeWriterEffect.test.tsx` | 新增 SSE 竞态模拟测试（vi.useFakeTimers + act） |

## Test Results

- 6/6 tests PASS
- lint: 0 warnings
- typecheck: 0 errors
- Coverage: TypeWriterEffect.tsx 100% lines/branches/funcs/stmts

## Previous Attempts

第一次修复（displayedRef + useEffect[text,speed]）未能解决 RAF 竞态——text 变化时 RAF 仍然被 cleanup 取消。SSE 竞态模拟测试在旧实现上 FAIL（收到 "aa" 而非 20 a's），在新实现上 PASS。

## Commits

```
test: 2.0 添加 SSE 竞态模拟测试 RED
feat: 2.1 实施持续 RAF 循环重构
refactor: 2.2 清理 + 更新注释
```
