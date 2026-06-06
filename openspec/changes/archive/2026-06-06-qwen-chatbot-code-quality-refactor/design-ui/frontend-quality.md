# UI 设计稿: qwen-chatbot-code-quality-refactor

## 概述

> ⚠️ **无 UI 变更**

本期变更为**纯代码质量改造**（行为 100% 不变，UI 100% 不变），依据 `design-ui` 阶段 PRECHECK 规则跳过 .op 设计稿生成。本目录仅保留设计令牌参考，供未来其他变更复用。

## 关联 Capabilities

| Capability | 设计文件 | 说明 |
|------------|----------|------|
| type-system | — | 无 UI 变更 |
| chat-state-management | — | 无 UI 变更（内部 Context 拆分） |
| role-state-management | — | 无 UI 变更（CRUD 行为不变） |
| ui-component-library | — | 无 UI 变更（抽取共享组件，视觉一致） |
| streaming-chat | — | 无 UI 变更（数据流统一，视觉一致） |
| engineering-tooling | — | 无 UI 变更（仅工具链） |
| frontend-quality | — | UI 体验**增强**（可访问性、React.memo、虚拟列表）但视觉外观不变 |

**注意**：`frontend-quality` 涉及可访问性（aria 属性、focus trap、ESC 关闭）但**不改变视觉外观**；react-virtuoso 启用阈值 `> 100` 条，不影响 < 100 条场景；React.memo 仅优化重渲染，不改变 DOM 结构。

## 设计规范

完整设计令牌见 `../design.md` §UI Design Tokens，此处摘要：

### 配色方案（Tailwind 类，现状保留）

- **主色**：`bg-blue-600` / `hover:bg-blue-700`（主按钮、链接、激活态）
- **辅助**：`bg-blue-100` / `text-blue-800`（默认角色 badge）
- **成功**：`bg-green-500` / `text-green-600`（用户头像、✓ 提示）
- **错误**：`text-red-600` / `bg-red-100`（错误提示、删除按钮）
- **警告**：`text-yellow-600`（警告态）
- **中性**：`bg-gray-50/100/200`（背景）/ `text-gray-500/600/700/800`（文字层级）
- **边框**：`border-gray-200/300`（卡片、表单）

### 字体

- 主字体栈：`-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, ...`
- 代码字体：`Monaco, Consolas, monospace`
- 字号：H1 `text-3xl` (30px) / H2 `text-2xl` (24px) / H3 `text-lg/xl` / Body `text-base` (16px) / Caption `text-sm/xs`

### 间距

- 页面内边距：`p-4 sm:p-6 md:p-8`
- 卡片内边距：`p-4 sm:p-6`
- 组件间距：`space-y-4/6`
- 模态框：`p-4 sm:p-6`
- 表单字段：`space-y-2`

### 圆角

- 按钮/卡片/输入框：`rounded-lg` (8px)
- Badge / 头像：`rounded-full`
- 消息气泡：`rounded-2xl` (16px)

### 阴影

- 卡片：`shadow-md` / `hover:shadow-md`
- 模态框：`shadow-lg`
- 按钮：`shadow-sm/md`

### 断点（Tailwind 默认）

| 断点 | 宽度 | 用途 |
|------|------|------|
| 默认 | < 640px | 移动端 |
| `sm` | ≥ 640px | 大屏手机 |
| `md` | ≥ 768px | 平板 |
| `lg` | ≥ 1024px | 桌面端（侧边栏常驻） |
| `xl` | ≥ 1280px | 大屏 |

## 组件清单（仅前端可访问性相关）

> 本期 `frontend-quality` 涉及的可访问性增强（MUST 但不改变视觉）：

| 组件 | ARIA 增强 | 焦点管理 | 视觉变化 |
|------|----------|---------|---------|
| `<HistoryModal>` | `role="dialog"` `aria-modal="true"` `aria-labelledby` | ESC 关闭、focus trap、focus 恢复 | ❌ 无 |
| `<RoleManager>` 编辑模态框 | 同上 | 同上 | ❌ 无 |
| `<ChatWindow>` 消息 | `aria-label` 区分用户/助手 | — | ❌ 无 |
| 关闭按钮（×） | `aria-label="关闭"` | — | ❌ 无 |

## 目标平台

依据 design.md §Frontend Architecture：

- **平台类型**：响应式 Web（桌面优先 + 移动端适配）
- **画布尺寸**：
  - 桌面：1200px（侧边栏常驻）
  - 移动端：375px（抽屉式侧边栏）
- **布局模式**：
  - 桌面：固定侧边栏（256-288px）+ 流式主区
  - 移动：抽屉式侧边栏 + 全屏主区
- **断点策略**：Tailwind 默认（`sm/md/lg/xl`）

## 使用说明

1. 本期无新 UI 设计稿实现需求
2. `tasks.md` 中如需实现 UI 增强（可访问性 / 性能），直接参考 design.md §UI Design Tokens
3. 不需要 .op 文件支持
4. 后续如需重新设计 UI（如新功能、新页面），应开新 OpenSpec change 并重新走 design-ui 阶段

---

**结论**：本 change 不产出 .op 文件，跳过 design-ui 主体，进入 tasks 阶段。
