# frontend-quality Specification

## Purpose
TBD - created by archiving change qwen-chatbot-code-quality-refactor. Update Purpose after archive.
## Requirements
### Requirement: 消息列表稳定 key

**User Story**: As a 开发者，I want 消息组件使用稳定 key so that 流式更新时不会重渲染全部历史消息。

**Priority**: P1

**Acceptance**: 该 spec MUST: `<ChatWindow>` 消息项 `key` MUST 为 message 自有 ID（而非 index）。

**Non-functional**: 性能：100 条历史消息下，新增一条耗时 ≤ 16ms（1 帧）

`<ChatWindow>` MUST 满足：

1. 每条消息 MUST 有稳定唯一 ID（建议 `crypto.randomUUID()` 或基于 timestamp + content hash）
2. 消息列表渲染 MUST 使用 `key={message.id}`，MUST NOT 使用 `key={index}`
3. 消息项组件 SHOULD 用 `React.memo` 包装，未变化的 props MUST 跳过重渲染
4. `Message` 类型 MUST 包含 `id: string` 字段（已在 `types/index.ts` 增补）

#### Scenario: 稳定 key
- **GIVEN** 已有 3 条消息
- **WHEN** 流式追加第 4 条
- **THEN** React DevTools Profiler MUST 显示前 3 条未重渲染
- **AND** 仅第 4 条组件重渲染

#### Scenario: 消息 ID 唯一性
- **WHEN** 创建新消息
- **THEN** `message.id` MUST 与现有所有 ID 不同
- **AND** 建议使用 `crypto.randomUUID()`（浏览器原生）或 `Date.now() + Math.random()`

#### Scenario: 历史加载稳定
- **GIVEN** 从 localStorage 恢复 50 条历史
- **WHEN** 渲染 `<ChatWindow>`
- **THEN** 每条 MUST 有 ID
- **AND** 即使 localStorage 数据无 ID 字段，初始化 MUST 补全

---

### Requirement: 重型组件懒加载

**User Story**: As a 用户，I want 首屏加载更快 so that 进入聊天页时不必下载历史模态框等非首屏组件。

**Priority**: P2

**Acceptance**: 该 spec MUST: `<HistoryModal>` 与 `<RoleManager>` 通过 `next/dynamic` 懒加载；首屏 JS bundle 减少 ≥ 10%。

**Non-functional**: 性能：首屏 Lighthouse Performance ≥ 90

`pages/chat.tsx` 与 `pages/roles.tsx` MUST 满足：

1. `<HistoryModal>` MUST 通过 `dynamic(() => import('../components/HistoryModal'), { ssr: false })` 导入
2. `<RoleManager>` MUST 通过 `dynamic(() => import('../components/RoleManager'), { ssr: false })` 导入
3. 动态加载 MUST 提供占位 UI（loading: <LoadingState />）
4. 懒加载组件 MUST 不影响功能

#### Scenario: 首屏 bundle 减小
- **WHEN** 执行 `pnpm build`
- **THEN** 首屏 chunks（与 `/chat` 相关） MUST NOT 包含 HistoryModal 完整代码
- **AND** 懒加载组件 MUST 出现在独立 chunk 中

#### Scenario: 运行时按需加载
- **GIVEN** 用户停留在 /chat，未打开历史模态框
- **WHEN** 检查 network
- **THEN** HistoryModal chunk MUST NOT 被请求
- **AND** 打开模态框时 MUST 触发按需加载

#### Scenario: 占位 UI
- **GIVEN** 用户点击"查看历史"按钮
- **WHEN** HistoryModal chunk 加载中
- **THEN** MUST 显示占位（loading prop）
- **AND** 加载完成后 MUST 替换为真实模态框

---

### Requirement: 模态框可访问性

**User Story**: As a 键盘 / 屏幕阅读器用户，I want 模态框可被辅助技术正确识别并可通过键盘操作 so that 无障碍使用。

**Priority**: P1

**Acceptance**: 该 spec MUST: `<HistoryModal>` 与 `<RoleManager>` 编辑模态框符合 WAI-ARIA Dialog 规范。

**Non-functional**: 可访问性：通过 axe-core 0 关键违规

模态框 MUST 满足：

1. 根元素 MUST 含 `role="dialog"` `aria-modal="true"` `aria-labelledby="<title-id>"`
2. 标题元素 MUST 含 `id` 属性供 `aria-labelledby` 引用
3. 关闭按钮 MUST 含 `aria-label="关闭"`（中文 OK，但建议双语）
4. ESC 键 MUST 关闭模态框
5. Tab 键 MUST 在模态框内循环（focus trap），不离开到背景
6. 打开时焦点 MUST 移至模态框内（建议关闭按钮或第一个交互元素）
7. 关闭后焦点 MUST 恢复到打开前的元素

#### Scenario: ARIA 属性齐全
- **GIVEN** `<HistoryModal isOpen={true}>` 渲染
- **WHEN** 检查 DOM
- **THEN** 根元素 MUST 含 `role="dialog"` `aria-modal="true"`
- **AND** `aria-labelledby` MUST 引用标题 id

#### Scenario: ESC 关闭
- **GIVEN** 模态框打开
- **WHEN** 用户按 ESC 键
- **THEN** `onClose` MUST 被调用
- **AND** 模态框 MUST 消失

#### Scenario: Focus trap
- **GIVEN** 模态框打开，焦点在第一个可聚焦元素
- **WHEN** 用户按 Tab 键
- **THEN** 焦点 MUST 移至下一个模态框内可聚焦元素
- **AND** 当到达最后一个时，Tab MUST 循环到第一个
- **AND** 焦点 MUST NOT 移出模态框

#### Scenario: 焦点恢复
- **GIVEN** 用户从"查看历史"按钮打开模态框
- **WHEN** 关闭模态框
- **THEN** 焦点 MUST 恢复到"查看历史"按钮

#### Scenario: axe-core 检测
- **WHEN** 执行 axe-core 扫描
- **THEN** 模态框区域 MUST 0 个 critical 违规
- **AND** MUST 0 个 serious 违规

---

### Requirement: 颜色对比达标

**User Story**: As a 弱视用户，I want 文字与背景对比度达到 WCAG AA 标准 so that 文字清晰可读。

**Priority**: P2

**Acceptance**: 该 spec MUST: 全部正文字体（size ≥ 18px 或 bold ≥ 14px）对比度 ≥ 4.5:1；大字体（≥ 18px）对比度 ≥ 3:1。

**Non-functional**: 可访问性：通过 WCAG AA

颜色使用 MUST 满足：

1. MUST NOT 使用 `text-gray-400` 作为正文（对比度 < 4.5:1）
2. `text-gray-500` 仅可用于 caption 文字（< 14px 时避免）
3. 错误信息 `text-red-600` 对白底对比度 MUST ≥ 4.5:1（验证：#dc2626 vs #fff = 4.83:1 ✓）
4. 成功信息 `text-green-600` 对白底对比度 MUST ≥ 4.5:1
5. 提示文字 SHOULD 使用 `text-gray-600` 或更深

#### Scenario: gray-400 不作正文
- **GIVEN** 任意 `<p className="text-gray-400">` 作为正文段落
- **WHEN** 人工审查 / axe-core 扫描
- **THEN** MUST 改为 `text-gray-600` 或更深

#### Scenario: 对比度计算
- **GIVEN** `text-red-600` on white background
- **WHEN** 计算 WCAG 对比度
- **THEN** MUST ≥ 4.5:1（实际 4.83）
- **AND** 通过 WCAG AA

#### Scenario: 按钮文字可读
- **GIVEN** `bg-gray-300` 按钮配 `text-gray-500` 文字（禁用态）
- **WHEN** 检查对比度
- **THEN** 该组合仅用于 disabled 状态可接受
- **AND** 启用态 MUST 用 `bg-blue-600 text-white`（高对比）

---

### Requirement: React.memo 优化重组件

**User Story**: As a 用户，I want 切换角色时仅必要组件重渲染 so that 交互流畅。

**Priority**: P2

**Acceptance**: 该 spec MUST: `<RoleSelector>`、`<ModelConfigPanel>`、`<ChatWindow>` 项用 React.memo 包装，Profiler 验证重渲染范围收敛。

**Non-functional**: 性能：切换角色时重渲染组件数 ≤ 3

组件优化 MUST 满足：

1. `<RoleSelector>` MUST 用 `React.memo` 包装，比较 props 浅相等
2. `<ModelConfigPanel>` MUST 用 `React.memo` 包装
3. `<MessageBubble>`（如抽取）MUST 用 `React.memo` 包装
4. 父组件传 props MUST 保持引用稳定（必要时用 useMemo / useCallback）
5. 不应过度 memo（props 频繁变化时反而增加开销）

#### Scenario: 切换角色不重渲染无关组件
- **GIVEN** 当前选中角色 A
- **WHEN** 用户切换为角色 B
- **THEN** `<RoleSelector>` MUST 重渲染（props 变化）
- **AND** `<ModelConfigPanel>` MUST 重渲染（modelConfig 变化）
- **AND** 已显示的消息 MUST 不重渲染

#### Scenario: 流式更新仅末条重渲染
- **GIVEN** 100 条历史消息
- **WHEN** 流式追加第 101 条
- **THEN** Profiler MUST 显示前 100 条 skipped
- **AND** 仅第 101 条 rendered

#### Scenario: 过度 memo 警示
- **GIVEN** 某组件 props 含内联对象 `{ x: 1 }`
- **WHEN** 父组件每次渲染都创建新对象
- **THEN** memo 失效（props 浅比较 false）
- **AND** 应改用 useMemo 稳定引用

---

### Requirement: 虚拟列表（可选）

**User Story**: As a 用户，I want 长历史记录流畅滚动 so that 1000+ 条历史仍可用。

**Priority**: P2

**Acceptance**: 该 spec MUST: 当历史 > 100 条时启用 `react-virtuoso`；否则使用简单列表。

**Non-functional**: 性能：1000 条历史下滚动 FPS ≥ 50

虚拟列表 MUST 满足（条件性启用）：

1. 仅在 `conversationHistory.length > 100` 时启用
2. 使用 `react-virtuoso` 替代普通 `<div className="overflow-y-auto">` 渲染
3. 行高 MUST 预估并传递 `itemSize` 或用 `Virtuoso` 自适应
4. 滚动到顶部 MUST 仍能加载更早历史（如有）

#### Scenario: 启用阈值
- **GIVEN** `conversationHistory.length = 50`
- **WHEN** 渲染历史
- **THEN** MUST 使用普通滚动列表
- **AND** MUST NOT 引入 react-virtuoso 依赖

#### Scenario: 虚拟化滚动
- **GIVEN** `conversationHistory.length = 500`
- **WHEN** 渲染历史
- **THEN** MUST 使用 `<Virtuoso>` 渲染
- **AND** DOM 中实际渲染行数 MUST ≤ 20

#### Scenario: 与现有样式兼容
- **WHEN** 启用虚拟列表
- **THEN** 视觉上 MUST 与原表格一致（行高、颜色、padding）
- **AND** 编辑 evaluation input MUST 仍可用

#### Scenario: 性能不达标则降级
- **GIVEN** 启用 react-virtuoso 后 FPS < 50
- **WHEN** 人工评估
- **THEN** 改为 React.memo + 不启用虚拟化
- **AND** 记录决策到 design.md

