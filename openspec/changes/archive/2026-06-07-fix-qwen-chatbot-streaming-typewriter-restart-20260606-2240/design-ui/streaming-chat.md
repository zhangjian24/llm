# UI 设计稿：streaming-chat（TypeWriterEffect 性能优化 修改）

## 状态：N/A — 无 UI 变更

本次变更（`fix-qwen-chatbot-streaming-typewriter-restart-20260606-2240`）为 `components/TypeWriterEffect.tsx` 内部状态机修复，**不涉及前端 UI 变更**：

- `design.md` §Frontend Architecture：`N/A — 无前端架构变更`
- `design.md` §UI Design Tokens：`N/A — 无 UI 设计令牌变更`
- `specs/streaming-chat/spec.md` 修改的 `TypeWriterEffect 性能优化` Requirement 范围仅限内部 RAF 调度逻辑
- 变更前后 TypeWriterEffect 在组件树中的位置不变（`ChatWindow → TypeWriterEffect → MarkdownRenderer`）
- 视觉输出不变（仍为 `<MarkdownRenderer>` 渲染，受 Tailwind / MarkdownRenderer 既有规则控制）
- 不需要 OpenPencil `.op` 设计稿

按 schema 的 PRECHECK 规则跳过 UI 设计稿生成。

## 关联 Capabilities

| Capability | 设计文件 | 说明 |
|------------|----------|------|
| `streaming-chat`（修改 `TypeWriterEffect 性能优化` Requirement） | N/A | 仅修复内部状态机，视觉输出不变 |

## 设计规范

N/A — 沿用既有 `components/MarkdownRenderer.tsx` + Tailwind 既有规则。

## 组件清单

N/A — 无新组件、无组件层级变化。TypeWriterEffect 在组件树中的位置不变。
