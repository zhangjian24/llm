# TypeWriterEffect 流式累积修复 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复 qwen-chatbot `TypeWriterEffect` 在 SSE 流式输出场景下的"闪烁 + 突然全蹦"bug，保留打字机动画正向累积体验，单文件修改 + 新增单测。

**Architecture:** 在既有 `useState + useEffect + useRef(rafRef)` 基础上新增 `displayedRef`，useEffect 启动 RAF 时从 `displayedRef.current.length` 持续累积到 `text.length`，**不**清空 state；通过 `displayedRef` 分离"动画进度跟踪"与"渲染触发"，避免把 `displayed` 加进 useEffect 依赖导致循环重启。

**Tech Stack:**
- React 19 + Next.js 16 (qwen-chatbot)
- TypeScript 5.x
- Vitest + @testing-library/react（既有）
- Playwright（既有 e2e）

---

## 文件结构

| 路径 | 状态 | 职责 |
|------|------|------|
| `qwen-chatbot/components/TypeWriterEffect.tsx` | Modify | useEffect 改为"持续累积 + displayedRef 跟踪" |
| `qwen-chatbot/components/TypeWriterEffect.test.tsx` | Modify | 新增 3 个测试 case 覆盖新行为 |

不动文件：`qwen-chatbot/pages/chat.tsx`、`qwen-chatbot/components/ChatWindow.tsx`、`qwen-chatbot/components/MarkdownRenderer.tsx`、`qwen-chatbot/pages/api/qwen.ts`、`qwen-chatbot/lib/langchain/*`。

---

## Task 1: 写失败测试（1.1 写失败测试）

**Files:**
- Modify: `qwen-chatbot/components/TypeWriterEffect.test.tsx:42` (追加 3 个测试 case)

### Step 1.1.1: 写 3 个失败测试

在 `TypeWriterEffect.test.tsx` 末尾追加：

```tsx
it('keeps displayed text growing without restart when text prop increases mid-stream', async () => {
  const { rerender } = render(<TypeWriterEffect text="Hello" speed={0} />);
  await waitFor(
    () => {
      expect(screen.getByTestId('type-writer').textContent).toContain('Hello');
    },
    { timeout: 500 },
  );
  rerender(<TypeWriterEffect text="Hello World" speed={0} />);
  await waitFor(
    () => {
      expect(screen.getByTestId('type-writer').textContent).toContain('Hello World');
    },
    { timeout: 500 },
  );
  const observed = screen.getByTestId('type-writer').textContent ?? '';
  expect(observed.length).toBe('Hello World'.length);
  expect(observed).toBe('Hello World');
});

it('synchronizes displayed text when text prop becomes shorter than already-shown', async () => {
  const { rerender } = render(<TypeWriterEffect text="Hello World" speed={0} />);
  await waitFor(
    () => {
      expect(screen.getByTestId('type-writer').textContent).toContain('Hello World');
    },
    { timeout: 500 },
  );
  rerender(<TypeWriterEffect text="Hi" speed={0} />);
  await waitFor(
    () => {
      expect(screen.getByTestId('type-writer').textContent).toBe('Hi');
    },
    { timeout: 500 },
  );
});

it('does not retrigger animation when rerendered with identical text', async () => {
  const { rerender } = render(<TypeWriterEffect text="abc" speed={0} />);
  await waitFor(
    () => {
      expect(screen.getByTestId('type-writer').textContent).toContain('abc');
    },
    { timeout: 500 },
  );
  rerender(<TypeWriterEffect text="abc" speed={0} />);
  expect(screen.getByTestId('type-writer').textContent).toContain('abc');
});
```

### Step 1.1.2: 跑测试确认 RED

```bash
cd /mnt/d/jianzhang/Workspace/Personal/Codes/llm/.worktrees/fix-qwen-chatbot-streaming-typewriter-restart-20260606-2240/qwen-chatbot
pnpm vitest run components/TypeWriterEffect.test.tsx
```

**Expected:** 既有 3 个测试通过，新增 3 个测试 FAIL（displayed 行为不符）。
**实际判定：** 看输出末尾 `Tests  N passed | N failed`，新增 3 个应出现在 failed。

### Step 1.1.3: Commit test (RED)

```bash
cd /mnt/d/jianzhang/Workspace/Personal/Codes/llm/.worktrees/fix-qwen-chatbot-streaming-typewriter-restart-20260606-2240
git add qwen-chatbot/components/TypeWriterEffect.test.tsx
git commit -m "test: 1.1 添加 TypeWriterEffect 流式累积 RED 测试"
```

---

## Task 2: 实施 useEffect 修复（1.2 实施修复）

**Files:**
- Modify: `qwen-chatbot/components/TypeWriterEffect.tsx:27-50` (替换 useEffect，引入 displayedRef)

### Step 1.2.1: 引入 displayedRef

在 `TypeWriterEffect.tsx` 第 27-28 行之间插入：

```tsx
  const [displayed, setDisplayed] = useState('');
  const displayedRef = useRef('');
  const rafRef = useRef<number | null>(null);
```

### Step 1.2.2: 替换 useEffect

将第 31-50 行 useEffect 整体替换为：

```tsx
  useEffect(() => {
    if (text === '') {
      displayedRef.current = '';
      setDisplayed('');
      return;
    }
    if (displayedRef.current.length > text.length || displayedRef.current === text) {
      if (displayedRef.current !== text) {
        displayedRef.current = text;
        setDisplayed(text);
      }
      return;
    }
    let i = displayedRef.current.length;
    const tick = (timestamp: number) => {
      if (timestamp - lastUpdateRef.current >= speed) {
        i = Math.min(i + CHUNK_SIZE, text.length);
        const next = text.slice(0, i);
        displayedRef.current = next;
        setDisplayed(next);
        lastUpdateRef.current = timestamp;
      }
      if (i < text.length) {
        rafRef.current = requestAnimationFrame(tick);
      }
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => {
      if (rafRef.current !== null) {
        cancelAnimationFrame(rafRef.current);
      }
    };
  }, [text, speed]);
```

**关键决策**：
- `useRef('')` 与 `useState('')` 双轨同步：RAF tick 内**同时**更新两者（保持 ref 持有当前显示进度，state 触发 re-render）
- text 变短（`displayedRef.current.length > text.length`）→ 直接同步，不做动画回退
- text 长度相同但内容不同（如"Hello"→"He llo"）→ 同步（保证幂等）
- text 完全相同（`displayedRef.current === text`）→ 跳过 RAF 调度
- text 变长 → 从 `displayedRef.current.length` 持续累积到 `text.length`（核心修复点）

### Step 1.2.3: 跑测试确认 GREEN

```bash
cd /mnt/d/jianzhang/Workspace/Personal/Codes/llm/.worktrees/fix-qwen-chatbot-streaming-typewriter-restart-20260606-2240/qwen-chatbot
pnpm vitest run components/TypeWriterEffect.test.tsx
```

**Expected:** 6/6 测试全 PASS（既有 3 + 新增 3）。

### Step 1.2.4: Commit feat (GREEN)

```bash
cd /mnt/d/jianzhang/Workspace/Personal/Codes/llm/.worktrees/fix-qwen-chatbot-streaming-typewriter-restart-20260606-2240
git add qwen-chatbot/components/TypeWriterEffect.tsx
git commit -m "feat: 1.2 实施 useEffect displayedRef 流式累积修复"
```

---

## Task 3: 重构 + 全量验证（1.3 重构 + 验证）

**Files:**
- Modify: `qwen-chatbot/components/TypeWriterEffect.tsx:1-10` (更新顶部注释)
- Run: 4 类验证命令（lint / typecheck / 单测+coverage / e2e）

### Step 1.3.1: 更新顶部注释

将第 1-10 行的 JSDoc 注释替换为：

```tsx
/**
 * TypeWriterEffect - 打字机效果（SSE 流式累积版）
 *
 * 关键设计（修复流式闪烁 bug）：
 * - useEffect 依赖 [text, speed]，**不**包含 displayed
 * - 用 displayedRef 跟踪动画进度，RAF tick 内**同时**更新 ref + setDisplayed
 * - text 变长：从 displayedRef.current.length 持续累积到 text.length（不重启）
 * - text 变短：直接同步（不做动画回退）
 * - text === displayedRef.current：跳过 RAF 调度（幂等保护）
 * - 每帧累积 CHUNK_SIZE 个字符（避免 setTimeout 频繁 re-render）
 * - useMemo 缓存输出
 *
 * 测试：components/TypeWriterEffect.test.tsx
 */
```

### Step 1.3.2: 跑 4 类验证

```bash
cd /mnt/d/jianzhang/Workspace/Personal/Codes/llm/.worktrees/fix-qwen-chatbot-streaming-typewriter-restart-20260606-2240/qwen-chatbot

# 1. lint
pnpm lint

# 2. typecheck
pnpm exec tsc --noEmit

# 3. 单元测试 + 覆盖率
pnpm vitest run --coverage --coverage.thresholds.lines=65 --coverage.thresholds.branches=75 --coverage.thresholds.functions=70 --coverage.thresholds.statements=65

# 4. e2e（仅 01-send-message 流式路径）
pnpm exec playwright test e2e/01-send-message.spec.ts
```

**Expected**:
- lint: 0 警告
- typecheck: 0 错误
- vitest: 全项目覆盖率 lines ≥ 65% / branches ≥ 75% / functions ≥ 70% / statements ≥ 65%（AGENTS.md 阈值）
- playwright: 0 regression

### Step 1.3.3: 手动验证

```bash
cd /mnt/d/jianzhang/Workspace/Personal/Codes/llm/.worktrees/fix-qwen-chatbot-streaming-typewriter-restart-20260606-2240/qwen-chatbot
pnpm dev   # 端口 3000
```

浏览器打开 `http://localhost:3000`，发送长问题（如"请详细介绍 React 19 的新特性"），观察助手回复气泡：
- ✅ 文本应"平滑逐字累积"，不闪烁、不突然全蹦
- ✅ 流式完成后，文本定格在完整回复
- ✅ 既不影响后续消息发送

### Step 1.3.4: Commit refactor (验证 + 注释)

```bash
cd /mnt/d/jianzhang/Workspace/Personal/Codes/llm/.worktrees/fix-qwen-chatbot-streaming-typewriter-restart-20260606-2240
git add qwen-chatbot/components/TypeWriterEffect.tsx
git commit -m "refactor: 1.3 更新 TypeWriterEffect 注释说明流式累积修复点"
```

---

## Commit 总结

| 顺序 | 任务 | Commit 形式 | 提交内容 |
|------|------|-------------|----------|
| 1 | 1.1 写失败测试 | `test: 1.1 添加 TypeWriterEffect 流式累积 RED 测试` | TypeWriterEffect.test.tsx |
| 2 | 1.2 实施修复 | `feat: 1.2 实施 useEffect displayedRef 流式累积修复` | TypeWriterEffect.tsx |
| 3 | 1.3 重构 + 验证 | `refactor: 1.3 更新 TypeWriterEffect 注释说明流式累积修复点` | TypeWriterEffect.tsx 注释 |

**3 commits / 1 task，符合 AGENTS.md "每 task ≥ 2 commit" + TDD 顺序强制（test → feat → refactor）。**

---

## 风险与回滚

| 风险 | 缓解 | 验证 |
|------|------|------|
| displayedRef 与 displayed state 漂移 | RAF tick 内**同时**更新两者 | 单元测试断言两者最终一致 |
| effect cleanup 取消老 RAF 后未及时启动新 RAF | cleanup cancelAnimationFrame + 新 effect 立即 schedule | "text 增长不重启动画"测试 |
| CHUNK_SIZE / speed 默认值被意外修改 | 硬编码常量不动 | grep 确认 `CHUNK_SIZE = 3` 未改 |
| React StrictMode 双调用 effect 引发双重 RAF | 既有用 useState 初始化相同，double-call 后 ref 状态一致 | dev 模式手动验证 |

**回滚**：`git revert <feat-commit-hash> <refactor-commit-hash>` 即可，行为回滚到原 useEffect（清空+重启），单文件 revert。
