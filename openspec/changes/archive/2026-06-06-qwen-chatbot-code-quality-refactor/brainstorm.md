# Brainstorm: qwen-chatbot-code-quality-refactor

> Raw capture from superpowers:brainstorming.
> 设计决策通过对话式问答收敛后记录于此。
> 后续 `design.md` 从本档重组为 Context / Goals / Decisions / Risks / Migration。

## 1. 用户分析

| 维度 | 描述 |
|------|------|
| 主要影响者 | 项目的开发者 / 维护者（单人项目，本次"自己改自己审"） |
| 间接受益 | 后续接手者、AI 协作方（可读性提升） |
| 用户画像 | TypeScript 熟练，了解 React/Next.js，关注工程质量 |
| 痛点等级 | 阻碍级（debug 残留 / 类型不一致 → 长期维护成本上升） |
| 影响规模 | 13 个文件、~1500 行代码；单 PR；不涉及外部用户行为变化 |
| 行业参考 | 成熟 Next.js 项目普遍采用：单一类型源、Hook 引用稳定、ESLint+Prettier+测试三件套 |

## 2. 问题定义

### 用户故事

```
As a qwen-chatbot 项目的开发者兼维护者
I want 对项目进行系统性代码质量改造（消除类型重复、稳定 Hook 引用、抽取共享组件、补齐 Lint/测试）
so that 后续维护、二次开发与团队协作时不会因"散弹式修改"反复踩坑
```

### 现状局限

通过对 22 个源文件的全面审查（详见代码质量评估报告），发现：
- 类型重复定义 4 处（`Role`、`Message`、`ConversationHistory`、`ModelConfig`）
- 生产残留 `console.log` 调试代码
- `useRoleStorage.updateRole` 多次 setState 引发状态不一致
- 流式响应双重渲染（messages 末尾 + TypeWriterEffect currentResponse）
- AppContext 全量序列化触发每次输入按键
- 12 个 `as string` 强制断言
- 零测试 + ESLint 配置缺失
- Hook 函数未用 useCallback 包装导致引用不稳定

### 量化指标

- 静态问题：严重 6 / 重要 14 / 次要 22 / 建议 8
- 测试覆盖率：0%
- TypeScript 严格模式：开启但被 `any` 绕过
- 构建产物：无 `console.log` 检查

## 3. 方案探索

### 方案 A：一气贯成全套重构（✅ 采纳）

**概要**：在单 worktree / 单 PR 内完成 P0+P1+P2 全套 13 个有效任务。

| 维度 | 评估 |
|------|------|
| 优点 | 决策一致、上下文连贯、避免半途状态 |
| 缺点 | PR 体积大（~1500 行），评审难度高；中途合并冲突风险 |
| 成本 | 大（2-3 周） |
| 推荐理由 | 用户明确选择 |

### 方案 B：分阶段 PR（❌ 否决）

**概要**：P0 一批 / P1 一批 / P2 一批，3 个 PR 顺序合并。

| 维度 | 评估 |
|------|------|
| 优点 | PR 体积小、易评审 |
| 缺点 | 跨 PR 状态依赖（Context 拆分后需要后续 PR 配合）；用户明确选择不采纳 |
| 否决理由 | 用户选择"一气贯成" |

### 方案 C：仅 P0（❌ 否决）

**概要**：只做最紧急的 4 个修复。

| 维度 | 评估 |
|------|------|
| 优点 | 1-2 天可完成 |
| 否决理由 | 范围过窄，无法满足"质量门禁达标"的成功标准 |

## 4. 设计决策

| 决策项 | 结论 | 理由 | 备选 | 决策人 |
|--------|------|------|------|--------|
| D1 改造范围 | 全套 P0+P1+P2 | 用户明确选择 | 仅 P0 / 分阶段 | 用户 |
| D2 产品行为 | 100% 不变 | 用户明确选择 | 可接受 UX 变动 | 用户 |
| D3 测试策略 | 单元+组件+E2E | 用户明确选择 | 仅单元 | 用户 |
| D4 实施节奏 | 单 worktree / 单 PR | 用户明确选择 | 分 PR | 用户 |
| D5 成功标准 | 质量门禁（tsc/lint/覆盖/E2E/console/Lighthouse） | 用户明确选择 | 可达即可 | 用户 |
| D6 架构 | 保持 Pages Router | 避免范围蔓延 + Pages Router 仍受 Next 16 支持 | 迁移 App Router | 用户 |
| D7 API Key 加固 | 本期不做 | D2 约束 UX 变更 | 加固存储 | 隐含决策 |
| D8 API 限流 | 本期不做 | D2 约束行为变更 | 加限流 | 隐含决策 |
| D9 任务编号 | 移除 T8/T12 | D7/D8 决策 | 保留可选项 | 隐含决策 |
| D10 任务总数 | 13 个（T1-T7, T9-T11, T13-T15） | 上述调整 | 15 个 | 隐含决策 |

## 5. 成功指标

| 类别 | 指标 | 目标值 | 测量方法 |
|------|------|--------|----------|
| 类型安全 | tsc 错误数 | 0 | `tsc --noEmit` |
| 代码规范 | ESLint 警告 | 0 | `pnpm run lint` |
| 测试覆盖 | 单元+组件覆盖率 | ≥ 80% | `vitest run --coverage` |
| E2E | 关键路径通过率 | 100% | Playwright |
| 生产净化 | 生产构建中 `console.log` 数 | 0 | grep dist/ |
| 性能 | Lighthouse Performance | ≥ 90 | `lighthouse http://localhost:3000` |
| 类型重复 | 跨文件同名 interface 数 | ≤ 1（types/index.ts） | `grep -r "^interface"` |
| Hook 稳定性 | useEffect 依赖中函数引用数 | 0（除原生 setState） | 人工审查 |

## 6. 范围分层

### MVP（本次必交付，13 任务）

**P0 — 立即修复**
- T1 统一类型定义（types/index.ts 单一源）
- T2 清理调试代码（移除 console.log）
- T3 修复 useRoleStorage.updateRole 状态不一致
- T4 修正 verify-key.ts HTTP 语义

**P1 — 一周内**
- T5 拆分 AppContext（临时态 / 持久化态 / Role 三 Context）
- T6 Hook 引用稳定化（useRoleStorage + useAISettings 用 useCallback）
- T7 抽取共享组件（LoadingState / ModelOptions / HistoryTable / MarkdownRenderer）
- T8 流式响应去重（消除 messages 末尾 + currentResponse 重复）
- T9 TypeWriterEffect 性能优化（RAF 批量 + 词分块）
- T10 错误处理加固（缓存 inputMessage、String() 替代 as 断言）

**P2 — 持续改进**
- T11 ESLint + Prettier 工具链
- T13 性能优化（React.memo + react-virtuoso + next/dynamic）
- T14 可访问性（dialog role + focus trap + ESC 关闭 + 颜色对比）
- T15 单元 + 组件 + E2E 测试

### 明确不做（防止 scope creep）

- ❌ API Key 存储加固（涉及 UX 变更，违反 D2）
- ❌ API 路由限流（涉及行为变更，违反 D2）
- ❌ 迁移到 App Router（违反 D6）
- ❌ 引入 i18n / react-hook-form / swr 等大型依赖（保持最小变更）
- ❌ 移除 Tailwind 或更换样式方案（违反 D2）
- ❌ 升级到 React 20 或 Next.js 17（如有）（超出"代码质量"范畴）

## 7. 依赖与风险

### 前置依赖

- Node.js ≥ 18（项目要求）
- pnpm ≥ 8
- Next.js 16 + Pages Router（已就绪）
- TypeScript 5.9（已就绪）
- React 19（已就绪）
- PostgreSQL/pgvector — **不涉及**（无后端数据库）
- LangChain + @langchain/openai — **不重写**（仅修类型断言）
- 阿里云百炼 API Key — 用户自配，**不在后端**

### 关键假设（错了会导致重做）

| 假设 | 验证方式 |
|------|----------|
| Pages Router 在 Next 16 仍完整支持 | `next dev` 启动正常 + 关键路径 E2E 通过 |
| 现有功能行为可被 E2E 完整捕获 | 至少覆盖：发消息 / 角色创建 / 历史查看 / 主题切换 |
| localStorage 5MB 容量在用户场景下不爆 | 假设历史记录 < 1000 条（个人使用） |
| React 19 兼容 React Testing Library 最新版 | RTL ≥ 16 已支持 React 19 |
| Vitest 与 Next.js 16 SWC 编译不冲突 | 引入后跑通 `vitest run` |

### 风险矩阵

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| 类型重构引发级联错误 | 高 | 中 | T1 后立即 tsc；分批 commit；保留旧类型为 alias 过渡 |
| 单 PR 体积过大 | 高 | 中 | 13 任务 = 13 个独立 commit；提供 PR 描述 checklist |
| 行为回归 | 中 | 高 | T15 在 T1-T14 之前先建 E2E 基线，迭代中持续回归 |
| TDD 强制与"大重构"模式冲突 | 中 | 中 | 测试代码可与生产代码同 PR；不强求"测试先于功能"覆盖到每行 |
| Next.js 16 Pages Router 长尾 bug | 低 | 高 | 关键路径 E2E 全绿即视为安全 |
| 虚拟列表 react-virtuoso 与现有滚动冲突 | 中 | 中 | T13 中评估；如不兼容则降级为简单 memo 优化 |
| Markdown 解析性能瓶颈 | 中 | 中 | T9 / T13 中引入 memo；如不达标则降级 |
| Hook 重构引发渲染循环 | 中 | 高 | T6 后跑全套 E2E + 手动验证 5+ 角色场景 |
| 拆分 Context 时遗漏局部依赖 | 中 | 中 | T5 提供兼容层；功能 1:1 复现 |
| 抽取组件时 props 接口错位 | 中 | 中 | T7 配套组件测试 |

## 8. 与 OpenSpec 后续 artifact 的衔接

本 brainstorm 为后续产物提供素材：
- **proposal.md**：直接引用 D1-D10 决策表 + 范围分层
- **design.md**：重组为 Context / Goals / Decisions / Risks / Migration
- **specs.md**：从 §5 成功指标抽取可测试的需求（含正常/异常 Scenario）
- **tasks.md**：直接映射 13 个任务为 T1.x ~ T15.x 编号
- **plan.md**：依据 §7 依赖关系排序、风险矩阵调度

## 9. 备注

- 本次不引入新功能，不改变产品行为
- 所有决策已通过对话收敛，不再追问
- 如需调整任一决策，应在 proposal 阶段提出（开新 OpenSpec change）
