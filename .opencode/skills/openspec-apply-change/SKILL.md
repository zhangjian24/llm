---
name: openspec-apply-change
description: Implement tasks from an OpenSpec change within its isolated worktree. **Enforces density** (each task produces ≥ 2 commits, with at least one test-related and one impl-related commit). **Apply phase focuses on unit tests only**; lint/typecheck/coverage/e2e run in the verify phase.
license: MIT
compatibility: Requires openspec CLI. 必须在 `/opsx:new` 创建的 worktree 内执行。
metadata:
  author: openspec + local-customization
  version: "3.0"
  generatedBy: "1.3.1"
---

# openspec-apply-change

在 worktree 内执行 change 的实现任务。本阶段的**核心职责**：

1. ✅ **单元测试**（每个 task 写失败测试 → 跑通）
2. ✅ **最小实现**（让单元测试通过）
3. ✅ **强制 commit 粒度**：每个 task 至少 2 个 commit（一红一绿）
4. ❌ **不在本阶段跑**：lint / typecheck / 覆盖率阈值 / e2e（这些归 verify 阶段）

> ⚠️ **本 skill 是流程通用版**。commit 前缀列表、具体格式、命令从 `AGENTS.md "项目事实" / "commit 规范" / "测试栈映射"` 读取。本 skill 只描述机制。

## 输入

可选 change 名。省略时按以下优先级推断：
- 对话上下文已提及
- 只有一个 active change 时自动选
- 否则运行 `openspec list --json` 并用 AskUserQuestion 让用户选

## 步骤

### Step 0 — 预检：worktree + plan.md 存在性

```bash
# 0.1 验证在 worktree 内（机制通用）
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
[ "$GIT_DIR" != "$GIT_COMMON" ] || { echo "❌ 不在 worktree 内"; exit 1; }

# 0.2 验证 plan.md 存在
[ -f openspec/changes/<name>/plan.md ] || \
  { echo "❌ plan.md 缺失，先 /opsx:continue"; exit 1; }

# 0.3 读取状态
openspec status --change "<name>" --json
```

输出当前进度和待办 task。

### Step 1 — 读取上下文

```bash
openspec instructions apply --change "<name>" --json
```

读取返回的 `contextFiles` 列表中的所有文件（proposal / specs / design / tasks / plan）。

### Step 2 — 显示当前进度

```
## 实施中: <change-name> (schema: superpowers-bridge)
worktree: <按 AGENTS.md 命名约定拼出>
当前进度: N/M tasks
剩余 task 概览:
  - 1.1 ...
  - 1.2 ...
```

### Step 3 — **强制 commit 粒度**（机制）

**密度机制**（由本 SKILL 强制）：

每个 plan.md task 必须产生 ≥ 2 个 commit：

1. **第 1 个 commit（RED）**：写失败测试，确认 RED
   - 前缀应使用"测试相关前缀"（具体列表从 `AGENTS.md "commit 规范"` 读取）
2. **第 2 个 commit（GREEN）**：最小实现让测试通过
   - 前缀应使用"实现相关前缀"
3. **第 3 个 commit（可选）**：重构
   - 前缀应使用"重构相关前缀"

**commit 格式**：`<prefix>: <task-id> <description>`（具体格式与前缀从 AGENTS.md 读取）。

**密度对账**（机制级检查，与前缀无关）：
```bash
TOTAL_TASKS=$(grep -c '^- \[' openspec/changes/<name>/tasks.md)
TOTAL_COMMITS=$(git log main..HEAD --oneline | wc -l)
[ "$TOTAL_COMMITS" -ge $((2 * TOTAL_TASKS)) ] || \
  echo "⚠️ 粒度不足: $TOTAL_COMMITS commits < 2*$TOTAL_TASKS"
```

> SKILL 不应硬编码前缀名 — 改 AGENTS.md 一处即可生效。

### Step 4 — 派发 subagent 逐 task 实施

加载 `superpowers:subagent-driven-development` skill（transitive: TDD + code-review）。

对每个 `- [ ]` task 派一个 subagent：
- subagent 读 plan.md 对应 task 段
- 实施 TDD 循环（按机制：先 RED 再 GREEN）
- 每个 task 完成 = 至少 2 个 commit

每个 subagent 完成一个 task 后，**主 agent**：
1. 在 worktree 内 `git log main..HEAD --oneline` 检查 commit
2. 在 `openspec/changes/<name>/tasks.md` 把对应项 `- [ ]` → `- [x]`
3. 增量 commit 该 tasks.md 更新（或与下一个 task 一起 commit）

### Step 5 — Apply 阶段结束自检

```bash
# 5.1 tasks 全勾？
PENDING=$(grep -c '^- \[ \]' openspec/changes/<name>/tasks.md)
[ "$PENDING" -eq 0 ] || echo "❌ 还有 $PENDING 个 task 未完成"

# 5.2 commit 粒度对账（与具体前缀无关，机制级）
TOTAL_TASKS=$(grep -c '^- \[' openspec/changes/<name>/tasks.md)
TOTAL_COMMITS=$(git log main..HEAD --oneline | wc -l)
MIN_REQUIRED=$((2 * TOTAL_TASKS))

echo "总 tasks: $TOTAL_TASKS"
echo "总 commits: $TOTAL_COMMITS (要求 ≥ $MIN_REQUIRED)"

[ "$TOTAL_COMMITS" -ge "$MIN_REQUIRED" ] || \
  echo "⚠️ commit 粒度不足，但允许 verify 阶段继续（仅警告）"
```

### Step 6 — 产出 apply-summary.md

在 `openspec/changes/<name>/` 写 `apply-summary.md`：

```markdown
# Apply Summary: <change-name>

**Worktree**: <按命名约定拼出>
**Branch**: <change-name>
**Date**: YYYY-MM-DD HH:MM

## Commit 列表

| # | Hash | 前缀 | Task ID | 描述 |
|---|------|------|---------|------|
| 1 | abc123 | <前缀> | 1.1 | <描述> |
| 2 | def456 | <前缀> | 1.1 | <描述> |
| ... | ... | ... | ... | ... |

## 单元测试结果

（粘贴 apply 阶段最后一次单元测试运行的关键输出；
具体命令从 AGENTS.md "测试栈映射" 读取）

## 粒度对账

- 总 tasks: N
- 总 commits: M (≥ 2N)

## 进入 verify 阶段

所有 task 完成 → 建议执行 `/opsx:verify`：
- 全面测试（lint + typecheck + coverage + e2e）
- openspec 7 项检查
- 产出 verify.md
```

### Step 7 — 暂停并提示

向用户输出：
```
## Apply 完成: <change-name>

Tasks: N/N 已勾 ✅
Commits: M ✅
Worktree: <worktree 路径> (未清理)
apply-summary.md: 已生成

→ 继续 /opsx:verify 跑全面测试
```

## Guardrails

- ❌ **不要**在 apply 阶段跑 lint / typecheck / 覆盖率检查 / e2e（归 verify）
- ❌ **不要**在主分支实施（必须 worktree 内）
- ❌ **不要**把多个 task 合成一个 commit（破坏粒度对账）
- ❌ **不要**跳过 RED 直接 GREEN（破坏 TDD 机制）
- ❌ **不要**硬编码 commit 前缀（从 AGENTS.md 读取）
- ❌ **不要**在 SKILL 中写具体测试命令（从 AGENTS.md 读取）
- ✅ 每个 task 至少 2 个 commit（具体前缀按 AGENTS.md 规范）
- ✅ `apply-summary.md` 必须包含 commit 列表（apply 阶段唯一证据）
- ✅ TDD 顺序：先 commit 失败测试，确认 RED，再写实现
- ✅ 若 worktree 内 git status 有未提交变更 → STOP 提示用户先 commit 或丢弃
