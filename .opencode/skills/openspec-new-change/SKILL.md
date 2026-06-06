---
name: openspec-new-change
description: Start a new OpenSpec change. **Immediately creates an isolated git worktree** to host the change branch. Use when the user wants to create a new feature, fix, or modification with a structured step-by-step approach.
license: MIT
compatibility: Requires openspec CLI + git worktree. 仓库根目录必须已 gitignore `.worktrees/`。
metadata:
  author: openspec + local-customization
  version: "3.0"
  generatedBy: "1.3.1"
---

# openspec-new-change

启动一个新 change，**关键区别**：在创建 change 目录之前就创建好隔离的 git worktree。所有后续 planning 在这个 worktree 内进行，避免污染 main。

> ⚠️ **本 skill 是流程通用版**。所有项目特定值（命名格式、时间戳格式、子项目结构）从 `AGENTS.md` "项目事实" 章节读取。本 skill 只描述流程机制。

## 输入

用户提供 change 名（kebab-case）**或**一段需求描述。若是描述，LLM 推导出 kebab-case 名（如 `add user auth` → `add-user-auth`）。

## 流程机制

### Step 0 — Pre-flight：检查遗留 change

```bash
# 通用命令：列未 archive 的 change 目录
find openspec/changes -mindepth 1 -maxdepth 1 -type d \
  -not -path 'openspec/changes/archive' 2>/dev/null
```

**若结果非空**（存在遗留未 archive change），**用 AskUserQuestion 询问用户**：

> ⚠️ 发现遗留 change 未 archive：<列出>
>
> 如何处理？
> - **A. 处理**：先 cd 到对应 worktree 走完 apply/verify/archive
> - **B. 标记放弃**：对遗留 change 直接 `openspec archive -y`（保留 proposal/design 等历史文档）
> - **C. 继续新建**：接受遗留，开始新 change（不推荐，可能产生 spec drift）

收到选择后执行对应分支。**A 分支**应回到 pre-flight 重新检测；**B 分支**运行 `openspec archive -y` 然后回 pre-flight；**C 分支**继续 Step 1。

### Step 1 — 拼名 + 冲突检测

**命名格式机制**：
- 模板：`<feature-name><separator><timestamp>`（具体模板从 `AGENTS.md "命名约定"` 读取）
- 命名约定的关键参数：时间戳命令、子项目结构等
- LLM 应先读 `AGENTS.md` 取得模板值，再拼接

**冲突检测**（通用机制）：
```bash
# 检测 worktree 冲突
git worktree list | grep -q "$WT_DIR" && echo "❌ worktree 存在"

# 检测分支冲突
git branch --list "$BRANCH_NAME" | grep -q . && echo "❌ 分支存在"
```

**冲突时**：用 AskUserQuestion 提示用户加 `--force`（删除同名 worktree + 分支并重建）或换名。

### Step 2 — 加载 using-git-worktrees skill

用 Skill tool 加载 `superpowers:using-git-worktrees`，传入上下文：
- 目标路径：`$WT_DIR`（按命名约定模板拼出）
- 目标分支：`$BRANCH_NAME`（已通过 Step 1 冲突检测）

该 skill 内部会：
- Step 0 自检是否已在 worktree（不会重复创建）
- 走 fallback `git worktree add "$WT_DIR" -b "$BRANCH_NAME"`
- 验证 `.worktrees/` 已在 .gitignore（项目根 AGENTS.md 应说明）

### Step 3 — 切换并初始化 change 目录

```bash
cd "$WT_DIR"
openspec new "$CHANGE_NAME" --schema superpowers-bridge
```

> `superpowers-bridge` 是本项目选择的 schema，定义在 `openspec/config.yaml`。

### Step 4 — 状态输出与后续指引

```bash
openspec status --change "$CHANGE_NAME"
```

获取第一个 ready artifact 的 instructions：

```bash
openspec instructions <first-artifact-id> --change "$CHANGE_NAME"
```

### Step 5 — STOP

向用户输出：

```
✅ change 已创建并进入隔离 worktree
  worktree: <按命名约定模板拼出>
  分支: <与 change 同名>
  schema: superpowers-bridge
  进度: 0/N artifacts

⚠️ 关键提醒：后续 /opsx:continue 必须在 worktree 内执行
  → cd <worktree 路径>
  → 继续 /opsx:continue 产出第一个 artifact
```

## Guardrails

- ❌ **不要**在主分支创建 change 目录（破坏 worktree 隔离的初衷）
- ❌ **不要**跳过 Step 0 pre-flight（遗留 change 会污染新 worktree 的 `openspec list` 输出）
- ❌ **不要**用 `git checkout -b` 而不通过 `git worktree add`（违背 worktree 隔离）
- ❌ **不要**接受无时间戳后缀的 change 名（保证全局唯一性 + 排序可读）
- ❌ **不要**在创建 worktree 后留在主分支执行后续步骤
- ❌ **不要**在 SKILL 中硬编码命名格式、时间戳格式、子项目路径（这些在 AGENTS.md）
- ✅ 若 `.worktrees/` 未在 .gitignore → STOP 提示用户先加
- ✅ 拼名前必读 `AGENTS.md "命名约定"`
- ✅ 若用户拒绝 worktree 工作流（要求在主分支直接操作）→ 询问后用 AskUserQuestion 记录显式豁免
