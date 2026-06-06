# LLM 项目指南

## 语言
所有对话、文档、思考过程必须使用简体中文。图表使用 mermaid 语法。

## 仓库结构

```
document-qa-system/   # RAG文档问答系统（主项目，最完整）
  backend/            # FastAPI 0.109 + PostgreSQL + pgvector + 阿里云百炼
  frontend/           # React 19 + Vite + TailwindCSS 4 + Zustand + TanStack Query
qwen-chatbot/         # Qwen聊天机器人（Next.js 16 + React 19 + TailwindCSS 3 + LangChain）
edu-ai-platform/      # 教育AI平台（Java Spring 项目框架，仅有 src 目录，开发中）
openspec/             # OpenSpec 配置 + superpowers-bridge schema
```

## 命令速查

### document-qa-system 后端
```bash
cd document-qa-system/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env.local     # 必填: DATABASE_URL, DASHSCOPE_API_KEY
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
**测试**: `pytest`（默认 --cov 覆盖, asyncio_mode=auto）
- 单文件: `pytest tests/unit/test_xxx.py -v`
- conftest 加载 `.env.local`，若无则降级 SQLite
- 测试数据库引擎和 session 由 conftest fixture 管理

### document-qa-system 前端
```bash
cd document-qa-system/frontend
pnpm install && pnpm run dev    # 端口 5173，proxy /api → :8000
```
**测试**: `pnpm test` (jest, 80% 覆盖率门槛), `pnpm test:coverage`, `pnpm lint`
- 测试文件: `src/__tests__/**/*.test.{ts,tsx}`
- e2e: Playwright (`tests` 目录)

### qwen-chatbot
```bash
cd qwen-chatbot
pnpm install && pnpm run dev    # 端口 3000
pnpm build && pnpm start
pnpm lint                       # next lint
```
**无测试配置**。需 `.env.local`：`OPENAI_API_KEY`, `OPENAI_API_BASE`, `MODEL_NAME`

### 根目录
无根 package.json。无 CI（无 `.github/`）。通过 `opencode.json` 配置 OpenCode。

## 技术栈明细

| 子项目 | 框架 | 数据库 | 包管理 |
|--------|------|--------|--------|
| document-qa-system/backend | FastAPI 0.109 + SQLAlchemy async | PostgreSQL 14+ / pgvector | pip |
| document-qa-system/frontend | React 19 + Vite 7 | - | pnpm |
| qwen-chatbot | Next.js 16 + LangChain | - | pnpm |
| edu-ai-platform | Spring (推测) | 待定 | 待定 |

## 重要约束
- 所有环境变量通过 `.env.local`（后端）/ `.env.local`（qwen-chatbot）加载，不提交到 git
- 后端 `.env.local` 必须含 `DATABASE_URL` 和 `DASHSCOPE_API_KEY`，否则测试降级 SQLite
- pgvector OID 问题：SQLAlchemy 无法识别 VECTOR 类型，向量操作使用原生 SQL
- qwen-chatbot 通过兼容 OpenAI 格式 API 调用通义千问，非直接 DashScope SDK

---

## 项目事实（OpenSpec 流程依赖）

> **本节是项目事实的唯一源**。SKILL.md / WORKFLOW.md / config.yaml 中如出现项目特定内容，请回退到本节维护。所有 OpenSpec 流程的 LLM 在执行 SKILL 前应读本节以获取项目特定值。

### 子项目结构（自动检测）

verify 阶段按下列规则判定当前 change 涉及哪个子项目：

| 子项目 | 检测文件 | 路径 |
|---|---|---|
| document-qa-system/backend | `requirements.txt` | `document-qa-system/backend/` |
| document-qa-system/frontend | `package.json` | `document-qa-system/frontend/` |
| qwen-chatbot | `package.json` | `qwen-chatbot/` |
| edu-ai-platform | (待框架) | `edu-ai-platform/` |

若多个子项目都被命中，按用户指定的聚焦子项目或依次跑全。

### 测试栈映射（verify 阶段用）

verify 阶段按子项目自动选择命令：

| 子项目 | lint | typecheck | 单元+覆盖率 | e2e |
|---|---|---|---|---|
| document-qa-system/backend | `ruff check app/` | `mypy app/` | `pytest --cov=app --cov-fail-under=60 --cov-report=term-missing` | (无) |
| document-qa-system/frontend | `pnpm lint` | `pnpm typecheck` 或 `pnpm exec tsc --noEmit` | `pnpm vitest run --coverage --coverage.thresholds.lines=60 --coverage.thresholds.branches=50 --coverage.thresholds.functions=60 --coverage.thresholds.statements=60` | `pnpm exec playwright test` |
| qwen-chatbot | `pnpm lint` | `pnpm typecheck` 或 `pnpm exec tsc --noEmit` | `pnpm vitest run --coverage --coverage.thresholds.lines=65 --coverage.thresholds.branches=75 --coverage.thresholds.functions=70 --coverage.thresholds.statements=65` | `pnpm exec playwright test` |
| edu-ai-platform | (待定) | (待定) | (待定) | (待定) |

> 流程机制（先 lint、再 typecheck、再 unit+coverage、最后 e2e；任一失败 → STOP）由 `openspec-verify-change` SKILL 定义。本节只提供具体命令。

### 覆盖率阈值

verify 阶段按子项目查下表，**不达标 = 阻塞 archive**：

| 子项目 | lines | branches | functions | statements |
|---|---|---|---|---|
| document-qa-system/backend | 60% | — | — | — |
| document-qa-system/frontend | 60% | 50% | 60% | 60% |
| qwen-chatbot | 65% | 75% | 70% | 65% |
| edu-ai-platform | (待定) | (待定) | (待定) | (待定) |

阈值来源：document-qa-system/backend 用 60%（默认），qwen-chatbot 65% 来自 `openspec/changes/archive/2026-06-06-qwen-chatbot-code-quality-refactor/retrospective.md` 实测基线（68.66% lines / 84% branches / 79.31% functions / 68.66% statements）下调一档。

### commit 规范

- **密度（机制）**：每 task ≥ 2 个 commit，由 `openspec-apply-change` SKILL 强制
- **前缀列表**：`test`, `feat`, `fix`, `refactor`, `chore`, `docs`, `style`
- **格式**：`<prefix>: <task-id> <description>`，例 `feat: 1.1 实现 useAISettings Hook`
- **TDD 顺序**（apply 阶段强制）：
  1. `test:` — 写失败测试，确认 RED
  2. `feat:` — 最小实现，测试 GREEN
  3. `refactor:` — 重构（可选第 3）
- **archive 提交形式**：`chore(archive): <change-name>`（archive 阶段使用）

### 命名约定

| 项 | 规则 | 示例 |
|---|---|---|
| change 名 | `<feature-name>-<timestamp>` | `api-key-rotation-20260606-1430` |
| 分支名 | = change 名（同名原则） | `api-key-rotation-20260606-1430` |
| worktree 路径 | `.worktrees/<change-name>/` | `.worktrees/api-key-rotation-20260606-1430/` |
| 时间戳格式 | `date +%Y%m%d-%H%M`（HHMM 精度） | `20260606-1430` |
| archive 目录 | `openspec/changes/archive/YYYY-MM-DD-<change-name>/` | `openspec/changes/archive/2026-06-06-api-key-rotation-20260606-1430/` |

> 强制：不允许无时间戳后缀的 change 名；不允许分支名与 change 名不一致。

---

## OpenSpec + Superpowers 工作流（5 阶段机制）

> 本节只描述流程机制（做什么、为什么、顺序如何）。**所有项目特定值（命令、阈值、前缀、命名格式）见上文"项目事实"章节**。

### 5 阶段命令链

```mermaid
flowchart LR
    N[/opsx:new<br/>创建 worktree] --> C[/opsx:continue ×5-6<br/>产出 artifact/]
    C --> A[/opsx:apply<br/>单元测试 + commit 粒度]
    A --> V[/opsx:verify<br/>4 类全面测试 + openspec]
    V --> AR[/opsx:archive<br/>archive + commit + push + 询问]

    classDef stage fill:#fff3e0,stroke:#e65100
    class N,C,A,V,AR stage
```

**v2.0 关键变化**（相对原版）：
- worktree 创建**提前到 NEW 阶段**（不是 APPLY）
- change 名强制 `name-YYYYMMDD-HHMM` 时间戳后缀（详见"命名约定"）
- 分支名 = change 名（同名原则）
- **APPLY 阶段只跑单元测试**，lint/typecheck/coverage/e2e 全归 VERIFY
- 强制 **commit 粒度**：每个 task 至少 2 个 commit（机制详见"commit 规范"）
- VERIFY 跑 **4 类全面测试** + OpenSpec 7 项
- ARCHIVE 严格顺序：archive → commit → push → 询问用户清理

### 各阶段职责（一句话）

| 阶段 | 职责 | 产物 |
|---|---|---|
| NEW | 创建隔离 worktree + 初始化 change 目录 | `.worktrees/<change>/` + `openspec/changes/<change>/` |
| CONTINUE | 产出 7 个 artifact（brainstorm/proposal/specs/design/tasks/plan） | `openspec/changes/<change>/*.md` |
| APPLY | 实施 + 单元测试 + 强制 commit 粒度 | commit 链 + `apply-summary.md` |
| VERIFY | 4 类全面测试 + OpenSpec 7 项 | `verify.md` |
| ARCHIVE | 同步 delta specs + 移动文件夹 + commit + push + 询问清理 | `openspec/changes/archive/<date>-<change>/` + 远端分支 |

### Pre-flight 拦载

- **NEW 阶段**启动前检测**遗留未 archive change**（`openspec/changes/<name>/` 不在 archive/ 下）
- 用 AskUserQuestion 询问用户：A 处理 / B 标记放弃（archive 空壳）/ C 继续新建

### archive 严格顺序

1. `openspec archive -y` — 同步 delta specs + 移动文件夹
2. `git add -A && git commit` — 提交 archive 移动（commit 形式见"commit 规范"）
3. `git push -u origin <branch>` — 推送分支
4. **询问用户**：A 删除本地分支? B 清理 worktree? C 立即开 PR?（不擅自处理）

**颠倒顺序会导致**：delta specs 未同步到 main specs 就被 commit（spec drift）。
