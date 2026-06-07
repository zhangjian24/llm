# Brainstorm: fix-qwen-chatbot-streaming-typewriter-restart-20260606-2240

> Raw capture of brainstorming output (2026-06-06).
> Decision log: 背景 → 问题定义 → 方案链 → 设计权衡 → 范围与风险。
> design.md 阶段会从此档萃取并重组为结构化设计文件。

## 1. 用户分析

**目标用户画像**：
- 角色：qwen-chatbot 终端用户（开发者 / 学生 / 内部测试者）
- 技术背景：能配置 `.env.local`、理解 SSE / 流式 API 概念
- 使用场景：在浏览器中发送问题，期望逐字/逐块看到 AI 回复（类 ChatGPT 体验）

**用户痛点等级**：**阻碍使用**（流式输出是聊天产品的核心体感，闪烁 + 突然全蹦破坏"AI 在思考+回复"的心智模型）。

**用户规模**：qwen-chatbot 是 Next.js + LangChain + 通义千问的演示/内部项目，当前未上线生产。但该项目是 `document-qa-system` 主项目的附属，前端技术栈和工程化基线一致；bug 不修会影响后续接入新模型时的体验。

**竞品参考**：
- ChatGPT / Claude.ai：SSE 增量推送，用户看到的就是"AI 一个字一个字蹦出来"，**没有额外打字机动画**（因为 SSE 本身就是动画）
- 某些带"重新生成"的聊天产品：历史消息回放时才加打字机效果（流式生成场景不加）

**关键观察**：竞品在流式生成场景**不加额外打字机**。这强化了"打字机效果是冗余/干扰"的判断（方案 B 的核心理由）。

## 2. 问题定义

**用户故事**：
> As a qwen-chatbot 终端用户, I want AI 回复能平滑逐字呈现, so that 聊天体验类 ChatGPT、可观测 AI 思考节奏。

**当前现象**：
- 用户发送问题后，AI 回复气泡"先在一行闪烁几个字符"，然后"突然整个回复一次性蹦出"
- 不符合 SSE 流式输出的预期（应逐字/逐块持续累积）
- 用户感知："AI 思考 5 秒 → 一行字闪一下 → 5 秒后再整段蹦出"

**触发链**（已通过代码阅读定位）：
1. `pages/api/qwen.ts:104-122` 后端正常逐 chunk `res.write` SSE 数据 ✓
2. `pages/chat.tsx:173-201` 前端每收到 chunk → `chatDispatch SET_MESSAGES` 更新最后一条 assistant 消息 ✓
3. `components/ChatWindow.tsx:61` 当 `isLastAssistant=true` 时用 `<TypeWriterEffect text={message.content} />` 渲染
4. **`components/TypeWriterEffect.tsx:31-50` useEffect 依赖 `[text, speed]`**：
   - text 每次 SSE chunk 到达都变长 → useEffect 重新触发
   - 重新触发时执行 `setDisplayed('')` **清空**
   - 重新启动 RAF 动画从 i=0 累积
5. 用户看到循环：清空 → 显示 1-3 字符 → 清空 → ... → 流结束后 text 稳定 → 动画正常完成 → 整段一次性显示

**量化影响**：
- 闪烁频率 = SSE chunk 频率（典型 100ms-2s/次）
- 累积字符数 = `CHUNK_SIZE=3` × RAF 帧数（每 30ms 加 3 字符）
- 闪烁窗口 = text 变化间隔（30ms-2s）
- 用户感知就是"乱跳"

**根因**：`useEffect` 把 `text` 列入依赖 + 启动时 `setDisplayed('')` 双重导致每次 text 增长都"清空 + 重启"，破坏了"打字机应该是动画驱动 displayed 增长"的预期。

## 3. 方案探索

### 方案 A：修复 TypeWriterEffect（保留动画）✅ 采纳

**核心思路**：用 `displayedRef` 分离"渲染触发（state）"和"动画进度跟踪（ref）"；useEffect 启动的动画从 `displayedRef.current.length` 累积到 `text.length`，**不再清空 displayedRef**。

**实现骨架**：
```tsx
const displayedRef = useRef('');

useEffect(() => {
  if (text.length === 0) {
    displayedRef.current = '';
    setDisplayed('');
    return;
  }
  // text 变短：直接同步
  if (displayedRef.current.length > text.length) {
    displayedRef.current = text;
    setDisplayed(text);
    return;
  }
  // 已完全显示：跳过
  if (displayedRef.current === text) return;
  // 启动/继续动画
  let i = displayedRef.current.length;
  const tick = (timestamp) => {
    if (timestamp - lastUpdateRef.current >= speed) {
      i = Math.min(i + CHUNK_SIZE, text.length);
      const next = text.slice(0, i);
      displayedRef.current = next;
      setDisplayed(next);
      lastUpdateRef.current = timestamp;
    }
    if (i < text.length) rafRef.current = requestAnimationFrame(tick);
  };
  rafRef.current = requestAnimationFrame(tick);
  return () => { if (rafRef.current !== null) cancelAnimationFrame(rafRef.current); };
}, [text, speed]);
```

**优点**：
- 保留打字机视觉效果（产品设计意图）
- 修复精确：只动 TypeWriterEffect 一个文件 + 测试
- TDD 友好：能写测试覆盖"text 增长不重启"
- 边界处理完整（text 变短/变空/已完成）

**缺点**：
- 仍有少量 React anti-pattern（effect 内启动 RAF + cleanup cancel）
- 在某些慢速 SSE 场景下，动画可能"卡顿"（等下一个 chunk 几秒钟才出现下一个字符），但这其实更接近"打字机"语义

**实现成本**：小（TypeWriterEffect.tsx 约 10 行改动 + 1-2 个新测试）

### 方案 B：移除 TypeWriterEffect ❌ 否决

**核心思路**：ChatWindow 中 `isLastAssistant` 分支直接用 `<MarkdownRenderer>`，依赖 SSE 自带流式动画。

**优点**：
- 最简、零风险
- 符合"竞品做法"（ChatGPT/Claude 在流式生成场景不加额外动画）

**缺点**：
- 丢失"打字机"产品设计意图
- 若后续想给"重新生成历史消息"加打字机，需要重写组件

**实现成本**：极小（ChatWindow.tsx 1 处 + 可选删除 TypeWriterEffect.tsx）

**否决理由**：用户在前置 Q&A 中已明确选择保留动画（方案 A）。尊重用户选择。

### 方案 C：打字机改为可选 prop 🤔 备选

**核心思路**：TypeWriterEffect 加 `animated` prop，ChatWindow 传 `animated={false}`。

**优点**：
- 组件保留供历史重放等场景使用
- 灵活

**缺点**：
- 增加 API 复杂度
- 当前没有需要打字机的场景（YAGNI）

**否决理由**：当前不增加 prop，等真正需要时再加。YAGNI。

## 4. 设计决策

| 决策项 | 结论 | 理由 | 备选 | 决策人 |
|---|---|---|---|---|
| 修复方向 | 方案 A：修复 TypeWriterEffect | 保留产品设计意图，TDD 友好，改动小 | B 移除 / C prop 化 | 用户（前置 Q&A） |
| effect 依赖列表 | `[text, speed]` | displayed.length 进依赖会导致 effect 反复重启（循环） | 加 displayed.length | 当前 |
| 动画进度跟踪方式 | `displayedRef` (useRef) | ref 变化不触发 effect，可频繁更新 | state 同步 | 当前 |
| `CHUNK_SIZE` 常量 | 保持 3 不变 | 既有性能优化意图，本次只修 bug | 调整 | 不改 |
| `speed` 默认值 | 保持 30 不变 | 同上 | 调整 | 不改 |
| 是否新增 prop | 不加 | YAGNI | animated / enableRestart / 等 | 不加 |
| 是否动 ChatWindow | 不动 | bug 仅在 TypeWriterEffect 内 | 直接渲染 MarkdownRenderer | 不动 |
| 是否动后端 API | 不动 | 后端 SSE 正常 | 改 chunk 频率等 | 不动 |
| 是否动 chat.tsx | 不动 | 消息流处理正常 | 改 isStreaming 判定 | 不动 |
| 测试覆盖 | 至少 2 个新 vitest case | 覆盖"text 增长不重启" + "text 变短同步" | 仅 1 个 | 写 2 个 |

## 5. 成功指标

| 类别 | 指标 | 目标 | 可观测性 |
|---|---|---|---|
| 用户体验 | AI 回复从"闪烁 + 突然全蹦"改为"平滑逐字累积" | 100% 修复 | 浏览器手动 + Playwright 录屏（e2e 01-send-message） |
| 用户体验 | 流式过程中不出现 `displayed === ''` 中间状态 | 0 次 | 单元测试断言 |
| 技术 | TypeWriterEffect 单元测试通过 | 100% | `pnpm vitest run components/TypeWriterEffect.test.tsx` |
| 技术 | 覆盖率：TypeWriterEffect.tsx lines ≥ 90% | 维持 / 提升 | `pnpm vitest --coverage` |
| 技术 | qwen-chatbot 全量 lint / typecheck / 单元 / e2e 通过 | 全绿 | AGENTS.md "测试栈映射" |
| 回归 | 既有 e2e（01-send-message / 06-error-retry 等）通过 | 全绿 | `pnpm exec playwright test` |

## 6. 范围分层

**MVP（本次必须交付）**：
- 修复 `qwen-chatbot/components/TypeWriterEffect.tsx` 的 useEffect（用 `displayedRef` 重构）
- 新增 2 个 vitest 单元测试（text 增长不重启 + text 变短同步）
- 更新 `TypeWriterEffect.test.tsx` 已有测试确保不回归
- 文件顶部注释说明修复点

**第二期（明确不做）**：
- 不调整 `CHUNK_SIZE` / `speed` 默认值
- 不新增 `animated` / `enableRestart` 等 prop
- 不重构整个 useEffect 内部结构（除非本次为修复必要）
- 不重写后端 SSE chunk 频率
- 不改 chat.tsx 中 messages 数组的 dispatch 频率（如加节流）

**明确不做（防 scope creep）**：
- 不动 ChatWindow.tsx（除非验证发现新 bug）
- 不动后端 qwen.ts / lib/langchain
- 不动测试阈值（AGENTS.md 已固定 qwen-chatbot 65/75/70/65）
- 不做性能优化（除修复必要）

## 7. 依赖与风险

**前置依赖**：
- 无（纯前端组件内部修复）
- 不需要新的 npm 依赖
- 不需要数据库 / 后端变更

**关键假设**（错了会导致重做）：
- **H1**：SSE 推送的 chunk 频率不会快到让 RAF 跑不完（典型 100ms-2s/次，RAF 30ms 间隔，远快于 chunk 频率 → 假设成立）
- **H2**：displayedRef 和 displayed state 保持同步（RAF 内同时 setState + 写 ref → 假设成立）
- **H3**：用户期望"平滑累积"而非"完整显示"（前置 Q&A 已确认采纳方案 A → 假设成立）
- **H4**：既有 3 个 TypeWriterEffect 测试不会因本次重构失败（需用 `waitFor` + 大 speed 验证不回归）

**主要风险**：

| 风险 | 可能性 | 影响 | 缓解措施 |
|---|---|---|---|
| `displayedRef` 与 displayed 状态漂移 | 低 | 中 | RAF 内同时更新两者；测试覆盖同步 |
| effect 取消老 RAF 后未及时启动新 RAF | 中 | 中 | cleanup cancel + 新 effect 立即 schedule；test "text 增长不重启" 直接覆盖 |
| `speed` 改变时累积进度丢失 | 中 | 低 | 接受（speed 变化时重新累积符合"用户主动调速"语义）|
| Markdown 重新解析导致闪烁 | 中 | 低 | ReactMarkdown 有内部 memo；累积式 slice 不会整体重解析 |
| 测试中 RAF 不稳定导致 flaky | 高 | 中 | 用 `waitFor` + 大 `speed`（1000ms）+ `vi.useFakeTimers` 可选 |
| e2e 录屏断言复杂 | 中 | 低 | 维持现有 e2e（不做新视觉断言），靠单元测试 + 手动验证 |

**回滚方案**：
- 单文件改动：`qwen-chatbot/components/TypeWriterEffect.tsx`
- 旧实现可 `git revert <commit-hash>` 恢复（commit 粒度保证原子回滚）
- 行为回滚到原 useEffect（清空 + 重启动画），功能完整（仅 UX 退化）

## 8. 前端平台 / UI 设计参数

- **目标平台**：Web（Next.js 16 + React 19）
- **目标 viewport**：桌面 1200+（qwen-chatbot 当前未做移动端适配）
- **设计工具链**：无（不涉及新 UI 改动）
- **E2E 测试工具**：Playwright（项目已有 `playwright.config.ts` + `e2e/*.spec.ts`）
- 不需要写 `AGENTS.md` 的 `## 前端测试配置` 小节（既有信息已足够）

## 9. 决策链总结（Q1-Q5）

- Q1：要保留打字机还是依赖 SSE 自带动画？
  - A：保留打字机（用户偏好 → 采纳方案 A）
- Q2：effect 依赖列表是否包括 displayed？
  - A：否，否则循环重启（displayed 变化 → effect 跑 → setDisplayed → ...）
- Q3：动画进度跟踪用 state 还是 ref？
  - A：ref（useRef），不触发 effect
- Q4：text 变短时如何处理？
  - A：直接同步 displayed = text（不做动画回退）
- Q5：text === displayed 时如何处理？
  - A：跳过（避免重复启动 RAF）

## 10. 后续

- `design.md`（下一个 artifact）会把本档第 4 节（决策表）、第 6 节（范围）、第 7 节（风险）重组为结构化设计
- `proposal.md` 会基于本档第 2/3 节写"为什么做 + 做什么"
- `specs/*.md` 会基于第 5 节（成功指标）+ 第 6 节（范围）写 ADDED 增量规范
- `tasks.md` / `plan.md` 会基于本档产出 TDD 任务 + commit 粒度
