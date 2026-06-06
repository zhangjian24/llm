---
name: openspec-archive-change
description: Archive a completed change. **Strict 4-step order**: (1) openspec archive -y → (2) git add + commit archive move → (3) git push branch → (4) ASK user about branch delete / worktree cleanup / PR creation. **No silent cleanup.**
license: MIT
compatibility: Requires openspec CLI + gh CLI（可选）.
metadata:
  author: openspec + local-customization
  version: "3.0"
  generatedBy: "1.3.1"
---

# openspec-archive-change

归档一个已完成的 change。**严格 4 步顺序**：

1. `openspec archive -y`（同步 delta specs + 移动文件夹到 archive/）
2. `git add -A && git commit`（提交归档内容）
3. `git push -u origin <branch>`
4. **询问用户**清理选项（分支 / worktree / PR）—— 不擅自处理

> ⚠️ **本 skill 是流程通用版**。archive 提交形式（如 `chore(archive):`）从 `AGENTS.md "commit 规范"` 读取。本 skill 只描述顺序与机制。

## 输入

可选 change 名。省略时按 openspec-* 通用规则推断/询问。

## 前置条件（机制级自检）

- ✅ `verify.md` 存在且无 ❌ 阻塞项
- ✅ `apply-summary.md` 存在
- ✅ 当前在 worktree 内
- ✅ git status 干净

## 步骤

### Step 0 — 预检

```bash
# 0.1 验证在 worktree 内
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
[ "$GIT_DIR" != "$GIT_COMMON" ] || { echo "❌ 不在 worktree 内"; exit 1; }

# 0.2 验证 verify.md 存在且无 FAIL
[ -f openspec/changes/<name>/verify.md ] || \
  { echo "❌ verify.md 缺失，先 /opsx:verify"; exit 1; }
grep -q '^- \[x\] ❌ FAIL' openspec/changes/<name>/verify.md && \
  { echo "❌ verify.md 含 FAIL 项，先修复"; exit 1; } || true

# 0.3 git status 干净
git diff --quiet || \
  { echo "❌ 有未提交变更，先 commit"; git status --short; exit 1; }

# 0.4 列出未 archive change 供选择（若 name 未指定）
[ -n "$NAME" ] || {
  echo "可用未 archive change:"
  find openspec/changes -mindepth 1 -maxdepth 1 -type d \
    -not -path 'openspec/changes/archive' -printf '  - %f\n'
  exit 0
}
```

### Step 1 — 检查 artifact / task 完成状态

```bash
openspec status --change "<name>" --json
```

- 若有 artifact 非 `done` → 用 AskUserQuestion 询问是否强制 archive
- 若 tasks.md 有 `- [ ]` → 同上

### Step 2 — **执行 archive（关键 Step 1/4）**

```bash
openspec archive -y
```

**这一步会**：
- 同步 delta specs（`openspec/changes/<name>/specs/` → `openspec/specs/<capability>/spec.md`）
- 移动 `openspec/changes/<name>/` → `openspec/changes/archive/YYYY-MM-DD-<name>/`

> archive 目录命名格式见 `AGENTS.md "命名约定"`。

**注意**：此时 git working tree 是 dirty 的（archive 移动了大量文件 + 修改了 main specs），**必须**走 Step 3 commit。

### Step 3 — **commit 归档内容（关键 Step 2/4）**

**commit 形式从 `AGENTS.md "commit 规范" / "archive 提交形式"` 读取**（项目可能为 `chore(archive): <name>` 或其他）。

```bash
git add -A
git commit -m "<按 AGENTS.md 规范的 archive 形式>"
```

commit 后 worktree 内的分支已包含完整 cycle 状态。

### Step 4 — **push 分支（关键 Step 3/4）**

```bash
git push -u origin "<branch-name>"
```

> 分支名 = change 名（与 openspec-new-change 的命名约定一致）。

若远端不存在该分支 → `-u` 会建立追踪。若远端已存在且有冲突 → 询问用户。

### Step 5 — **询问用户清理选项（关键 Step 4/4，必问，不擅自）**

**用 AskUserQuestion 询问 3 个独立选项**（避免一锅端）：

```
✅ archive + commit + push 已完成
  - change: <name>
  - 分支已 push: origin/<name>
  - archive 位置: openspec/changes/archive/YYYY-MM-DD-<name>/

请选择清理操作（可多选）：
```

| 选项 | 描述 | 执行命令 |
|---|---|---|
| **A. 删除本地分支** | 合并 PR 后或确认无需保留时 | `git branch -d <name>` |
| **B. 清理 worktree** | 合并 PR 后或确定本地不再需要 | `git worktree remove <worktree 路径>` |
| **C. 立即开 PR** | 用 gh CLI 创建 PR，base=main | `gh pr create --base main --head <name> --body-file <archive 路径>/proposal.md` |

**每项独立询问**（默认 No）：

```
Q1: 是否删除本地分支 <name>? (默认 No)
Q2: 是否清理 worktree? (默认 No)
Q3: 是否立即开 PR? (默认 No)
```

### Step 6 — 按回答执行

```bash
# 6.1 记录用户回答
DELETE_BRANCH=<A 的答案>
CLEAN_WT=<B 的答案>
OPEN_PR=<C 的答案>

# 6.2 条件执行
[ "$DELETE_BRANCH" = "yes" ] && git branch -d "<name>"
[ "$CLEAN_WT" = "yes" ]      && git worktree remove "<worktree 路径>"
[ "$OPEN_PR" = "yes" ]       && gh pr create \
  --base main \
  --head "<name>" \
  --title "<name>" \
  --body-file "openspec/changes/archive/<archive 目录>/proposal.md"
```

**安全约束**：
- `git branch -d` 而非 `-D`（未合并时拒绝删除，强制用户决策）
- `git worktree remove` 加 `--force` 仅在用户显式同意时
- `gh pr create` 失败（如无 gh CLI）→ 提示用户手动开 PR，给出 URL

### Step 7 — 输出总结

```
## Archive Complete: <name>

| Step | 状态 | 说明 |
|------|------|------|
| 1. openspec archive -y | ✅ | delta specs 已同步 + 文件夹已移动 |
| 2. git commit | ✅ | 提交 archive 移动 |
| 3. git push | ✅ | 分支已推送到 origin |
| 4. 清理选项 | <A/B/C 实际执行情况> | |

最终状态:
- worktree: <保留/已清理>
- 本地分支: <保留/已删除>
- PR: <已开/手动开>
- archive 位置: openspec/changes/archive/YYYY-MM-DD-<name>/

后续可在新 change (/opsx:new) 中引用 archive 案例。
```

## Guardrails

- ❌ **不要**颠倒 Step 2/3/4/5 顺序（先 archive 再 commit 再 push 再询问）
  - 颠倒会导致：delta specs 未同步到 main specs 就被 commit（spec drift）
- ❌ **不要**在 archive 后跳过 commit（archive 移动会污染 working tree）
- ❌ **不要**擅自删除分支或清理 worktree（必须 AskUserQuestion）
- ❌ **不要**用 `git branch -D`（用 `-d`，未合入时强制用户决策）
- ❌ **不要**自动 `gh pr create`（必须用户明确选择 C）
- ❌ **不要**在 verify.md 含 ❌ 时继续 archive
- ❌ **不要**硬编码 archive commit 形式（从 AGENTS.md 读取）
- ✅ archive 命令本身是幂等的（重复 archive 会报错但不会损坏）
- ✅ push 失败（如无网络）→ 允许用户先 commit 暂存，事后补 push
- ✅ 分支冲突 → 询问用户是 force push 还是 rebase
