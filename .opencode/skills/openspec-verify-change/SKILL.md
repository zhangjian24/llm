---
name: openspec-verify-change
description: Run **full test suite** (4 classes: lint, typecheck, unit+coverage threshold, e2e) within the worktree, then run OpenSpec's 7 structural checks. Produces verify.md. Must run AFTER apply-summary.md exists.
license: MIT
compatibility: Requires openspec CLI + 子项目对应测试栈。
metadata:
  author: openspec + local-customization
  version: "3.0"
  generatedBy: "1.3.1"
---

# openspec-verify-change

在 worktree 内**先跑 4 类全面测试**（机制），**再处理 OpenSpec 7 项**结构化检查，产出 `verify.md`。**注意**：`apply-summary.md` 必须存在，否则 STOP。

> ⚠️ **本 skill 是流程通用版**。具体子项目命令、覆盖率阈值从 `AGENTS.md "项目事实" / "测试栈映射" / "覆盖率阈值"` 读取。本 skill 只描述机制。

## 4 类测试机制（顺序敏感）

按下列顺序跑，**任一失败立即 STOP**（不继续后续类）：

1. **Lint** — 静态代码风格/语法
2. **Type check** — 类型系统
3. **Unit test + 覆盖率阈值** — 单元测试 + 覆盖率不达阈值即阻塞
4. **E2E** — 端到端（项目可能不支持，按 AGENTS.md "测试栈映射" 标记的 SKIP 项跳过）

## 步骤

### Step 0 — 预检

```bash
# 0.1 验证在 worktree 内（机制通用）
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
[ "$GIT_DIR" != "$GIT_COMMON" ] || { echo "❌ 不在 worktree 内"; exit 1; }

# 0.2 验证 apply-summary.md 存在（apply 阶段产物）
[ -f openspec/changes/<name>/apply-summary.md ] || \
  { echo "❌ apply-summary.md 缺失，先 /opsx:apply"; exit 1; }

# 0.3 git status 干净？
git diff --quiet || \
  { echo "❌ 有未提交变更，先 commit"; git status --short; exit 1; }
```

### Step 1 — 选择 change 并加载上下文

```bash
openspec status --change "<name>" --json
openspec instructions apply --change "<name>" --json
```

读取 `contextFiles` 列表中的所有 artifact（proposal / specs / design / tasks / plan / apply-summary）。

### Step 2 — 判定子项目（机制）

**从 `AGENTS.md "子项目结构"` 读取检测规则**（如 `requirements.txt` → backend；特定 `package.json` 内容 → 前端/qwen-chatbot）。

按 AGENTS.md 规则逐项检测。若多个子项目都存在 → 询问用户聚焦哪个，或依次跑全。

### Step 3 — 跑 4 类全面测试

**具体命令从 `AGENTS.md "测试栈映射"` 读取**，按子项目查表执行。

**机制级规则**（与具体命令无关）：
- 每类失败 → **立即 STOP**，不进入下一类
- 覆盖率不达 `AGENTS.md "覆盖率阈值"` 对应子项目的值 → **立即 STOP**
- E2E 标记为 SKIP 的子项目 → 跳过但记录
- 测试输出尾部 5-10 行粘贴到 verify.md

### Step 4 — 跑 OpenSpec 7 项检查

按 superpowers-bridge schema 的 verify 检查清单（**与具体项目无关的通用机制**）：

| # | 检查项 | 命令模式 | 阻塞性 |
|---|---|---|---|
| 1 | 结构校验 | `openspec validate --all --json` | **阻塞** |
| 2 | Task 完成度 | 检查 `- [x]` 计数 | **阻塞** |
| 3 | delta spec 同步状态 | 检查 archive 目录对应 spec 已合并 | 警告 |
| 4 | design/specs 一致性 | 人工核验 | 警告 |
| 5 | 实现信号 | `git log main..HEAD | wc -l > 0` | **阻塞** |
| 6 | front-door routing 泄漏 | 检查无 `docs/superpowers/specs/` 残留 | 警告 |
| 7 | deferred-dogfood 等价性 | `plan.md [~]` 项必须有等价段 | **条件阻塞** |

### Step 5 — 产出 verify.md

在 `openspec/changes/<name>/verify.md` 写：

```markdown
# Verify Report: <change-name>

**Worktree**: <按 AGENTS.md 命名约定>
**Branch**: <change-name>
**Date**: YYYY-MM-DD HH:MM
**子项目**: <detected>

---

## 1. 全面测试结果（4 类）

### 1.1 Lint
- 命令: <从 AGENTS.md "测试栈映射" 读取>
- 结果: ✅ PASS / ❌ FAIL
- 关键输出: <粘贴 1-3 行>

### 1.2 Type Check
- 命令: <从 AGENTS.md "测试栈映射" 读取>
- 结果: ✅ PASS / ❌ FAIL
- 关键输出: <粘贴 1-3 行>

### 1.3 单元测试 + 覆盖率
- 命令: <从 AGENTS.md "测试栈映射" 读取>
- 结果: ✅ PASS / ❌ FAIL
- 覆盖率（实测）: lines X% / branches Y% / functions Z% / statements W%
- 阈值（AGENTS.md）: <对应子项目行>
- 关键输出: <粘贴 summary 行>

### 1.4 E2E
- 命令: <从 AGENTS.md "测试栈映射" 读取>
- 结果: ✅ PASS / ❌ FAIL / ⏭️ SKIP
- 测试数: N 套
- 关键输出: <粘贴 1-3 行>

---

## 2. OpenSpec 7 项检查

| # | 检查 | 结果 | 说明 |
|---|------|------|------|
| 1 | 结构校验 (validate --all) | ✅/❌ | <说明> |
| 2 | Task 完成度 | ✅/❌ | <N>/<M> 已勾 |
| 3 | delta spec 同步 | ✅/⚠️ | <说明> |
| 4 | design/specs 一致性 | ✅/⚠️ | <说明> |
| 5 | 实现信号 (commits > 0) | ✅/❌ | <N> commits |
| 6 | front-door 泄漏 | ✅/⚠️ | <说明> |
| 7 | deferred-dogfood 等价 | ✅/❌/N/A | <说明> |

---

## 3. Summary

| 维度 | 状态 |
|------|------|
| 全面测试 | ✅/❌ |
| OpenSpec 结构 | ✅/❌ |
| 进入 archive | ✅ Ready / ❌ Blocked |

### 阻塞项（如有）

- <列出所有 ❌ 项，每项含修复指引>

### 最终结论

- **Ready for archive**: 所有阻塞项通过
- **Blocked**: 列出需修复的项
```

### Step 6 — 暂停

向用户输出：
```
## Verify 完成: <change-name>

全面测试:
  - Lint: ✅/❌
  - Type: ✅/❌
  - Unit + Coverage: ✅/❌ (lines X% / 阈值见 AGENTS.md)
  - E2E: ✅/❌/⏭️

OpenSpec 7 项:
  - 阻塞项: 0 / N
  - 警告项: 0 / M

verify.md: 已生成

→ 通过 → 继续 /opsx:archive
→ 阻塞 → 修复后重新 /opsx:verify
```

## Guardrails

- ❌ **不要**跳过任何一类测试就标 PASS（4 类必须全跑）
- ❌ **不要**把覆盖率阈值降低以绕过失败（应回 apply 补单测）
- ❌ **不要**在 verify 阶段修改实现代码（若发现 bug → 回 apply 处理）
- ❌ **不要**在主分支跑 verify
- ❌ **不要**在 SKILL 中硬编码具体测试命令（从 AGENTS.md 读取）
- ❌ **不要**在 SKILL 中硬编码具体阈值数字（从 AGENTS.md 读取）
- ✅ 覆盖率未达阈值 → 立即 STOP，列出未覆盖文件
- ✅ 任何 lint / typecheck / e2e 失败 → 立即 STOP
- ✅ verify.md 是 archive 阶段的输入（archive 会要求 verify.md 存在）
