# ui-component-library Specification

## Purpose
TBD - created by archiving change qwen-chatbot-code-quality-refactor. Update Purpose after archive.
## Requirements
### Requirement: 共享 LoadingState 组件

**User Story**: As a 用户，I want 看到一致的加载占位符 so that 不同页面切换时不会感觉割裂。

**Priority**: P1

**Acceptance**: 该 spec MUST: 替换 `pages/chat.tsx` 和 `pages/roles.tsx` 中的内联"加载中"为共享 `<LoadingState />`。

**Non-functional**: N/A

`<LoadingState />` 组件 MUST 满足：

1. 接受 `message?: string` props（默认"加载中..."）
2. 渲染居中、灰色文字、padding
3. 在 `components/LoadingState.tsx` 中实现
4. 替换 `pages/chat.tsx:273` 和 `pages/roles.tsx:36` 的内联实现

#### Scenario: 默认消息
- **WHEN** 渲染 `<LoadingState />`
- **THEN** MUST 显示"加载中..."居中文字
- **AND** MUST 占据合理空间（py-8）

#### Scenario: 自定义消息
- **WHEN** 渲染 `<LoadingState message="角色加载中..." />`
- **THEN** MUST 显示"角色加载中..."居中文字

#### Scenario: 重复实现消除
- **WHEN** 执行 `grep -rn "加载中" pages/ components/`
- **THEN** MUST 仅 `components/LoadingState.tsx` 含此字符串
- **AND** `pages/*.tsx` MUST NOT 含内联"加载中"div

---

### Requirement: 共享 ModelOptions 常量

**User Story**: As a 开发者，I want Qwen 模型选项集中定义 so that 新增模型时只需修改一处。

**Priority**: P1

**Acceptance**: 该 spec MUST: `lib/model-options.ts` 导出 `MODEL_OPTIONS` 常量；`ModelConfigPanel` 和 `RoleManager` 均从该常量读取。

**Non-functional**: N/A

`MODEL_OPTIONS` MUST 满足：

1. 导出位置：`lib/model-options.ts`（或 `components/ModelOptions.tsx` 中作为常量导出）
2. 类型：`{ value: string; label: string }[]`
3. 当前 MUST 包含：`qwen-turbo`（Fast & Cheap）、`qwen-plus`（Balance）、`qwen-max`（Most Capable）
4. `ModelConfigPanel.tsx` 和 `RoleManager.tsx` MUST 从该常量导入
5. MUST NOT 在两处分别硬编码

#### Scenario: 单一来源
- **WHEN** 执行 `grep -rn "qwen-turbo" components/`
- **THEN** MUST 仅在 `lib/model-options.ts` 中出现
- **AND** `ModelConfigPanel` 和 `RoleManager` MUST 通过 `import { MODEL_OPTIONS } from '@/lib/model-options'` 引用

#### Scenario: 新增模型自动同步
- **GIVEN** 在 `lib/model-options.ts` 添加 `{ value: 'qwen-long', label: 'Qwen-Long (1M context)' }`
- **WHEN** 渲染 `<ModelConfigPanel />`
- **THEN** 下拉框 MUST 自动包含该选项
- **AND** `<RoleManager>` 的模型选择下拉框 MUST 同样包含

---

### Requirement: 共享 HistoryTable 组件

**User Story**: As a 开发者，I want 对话历史表格集中实现 so that 模态框与未来内联展示使用同一组件。

**Priority**: P1

**Acceptance**: 该 spec MUST: `<HistoryTable history={...} onEvaluationChange={...} />` 组件存在；`<HistoryModal>` 使用它；旧的 `ConversationHistoryTable` 被删除。

**Non-functional**: N/A

`<HistoryTable>` 组件 MUST 满足：

1. 接收 props：
   - `history: ConversationHistory[]`
   - `onEvaluationChange: (id: number, evaluation: string) => void`
2. 渲染列：时间、输入、输出、模型、参数、Token 明细、效果评估
3. 输入列截断 30 字符，输出列截断 60 字符
4. 效果评估列含可编辑 input，placeholder 为 `autoEvaluate(item.output)` 结果
5. `autoEvaluate` MUST 用中文字符数（而非 `split(/\s+/)`）判断
6. `HistoryModal` MUST 使用 `<HistoryTable>` 替换其内联表格
7. `components/ConversationHistoryTable.tsx` MUST 被删除

#### Scenario: 模态框使用共享组件
- **WHEN** `<HistoryModal isOpen={true} history={[...]}` 渲染
- **THEN** 内部 MUST 渲染 `<HistoryTable history={...} onEvaluationChange={...} />`
- **AND** MUST NOT 包含内联 `<table>` 元素

#### Scenario: autoEvaluate 中文分词
- **GIVEN** `item.output = "你好世界"`
- **WHEN** 调用 `autoEvaluate(item.output)`
- **THEN** MUST 返回"响应适中"（5 个中文字符 > 5 但 < 100）
- **AND** MUST NOT 返回"响应过短"（错误按空格分词判定为 1 词）

#### Scenario: 截断显示
- **GIVEN** `item.input` 长度为 100
- **WHEN** 渲染表格
- **THEN** 输入列 MUST 显示前 30 字符 + `...`
- **AND** 完整内容可通过 hover title 或详情展开查看

#### Scenario: 评价输入同步
- **GIVEN** 渲染 `<HistoryTable history={[{id: 1, evaluation: ''}]} onEvaluationChange={fn} />`
- **WHEN** 用户在 evaluation input 中输入"好"
- **THEN** `onEvaluationChange(1, '好')` MUST 被调用

---

### Requirement: 共享 MarkdownRenderer 组件

**User Story**: As a 开发者，I want Markdown 渲染配置集中 so that 添加新插件（如数学公式）只需修改一处。

**Priority**: P1

**Acceptance**: 该 spec MUST: `<MarkdownRenderer>{text}</MarkdownRenderer>` 组件存在；替换 3 处内联 `ReactMarkdown`。

**Non-functional**: N/A

`<MarkdownRenderer>` 组件 MUST 满足：

1. 接受 props：
   - `children: string`（Markdown 文本）
   - `className?: string`
2. 内部使用 `<ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]}>`
3. 替换位置：
   - `components/ChatWindow.tsx:58-63`
   - `components/TypeWriterEffect.tsx:66-69`
   - 任何未来新增的 Markdown 渲染点
4. `remark-gfm` 和 `rehype-highlight` 的插件配置 MUST 仅在此处声明

#### Scenario: 单一配置源
- **WHEN** 执行 `grep -rn "remarkGfm\|rehypeHighlight" components/ pages/`
- **THEN** MUST 仅在 `components/MarkdownRenderer.tsx` 出现
- **AND** 其他文件 MUST 通过 `<MarkdownRenderer>` 使用

#### Scenario: 流式 markdown 渲染
- **GIVEN** `<TypeWriterEffect text="# Hello" />`
- **WHEN** 打字机完成
- **THEN** MUST 渲染为 `<h1>Hello</h1>`
- **AND** 内部 MUST 使用 `<MarkdownRenderer>`

#### Scenario: 代码高亮
- **GIVEN** `<MarkdownRenderer>{\`\`\`js\nconst x = 1;\n\`\`\`}</MarkdownRenderer>`
- **WHEN** 渲染
- **THEN** MUST 包含 `<pre><code class="hljs language-js">` 元素
- **AND** 关键字 MUST 有高亮 class

