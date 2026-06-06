# type-system Specification

## Purpose
TBD - created by archiving change qwen-chatbot-code-quality-refactor. Update Purpose after archive.
## Requirements
### Requirement: 统一类型定义入口

**User Story**: As a 项目维护者，I want 所有共享类型集中在单一文件 so that 任何类型演进只需修改一处。

**Priority**: P0

**Acceptance**: 该 spec MUST: 跨组件 / 页面 / 库的同名接口数量 ≤ 1（仅 `types/index.ts` 内）。

**Non-functional**: N/A

项目 MUST 在 `types/index.ts` 内集中声明以下类型，任何其他文件 MUST NOT 重复定义：

- `Role`：AI 角色数据结构（id、name、description、systemPrompt、modelConfig、isDefault）
- `ModelConfig`：模型配置（model、temperature、top_p、max_tokens）
- `Message`：对话消息（role、content、usage?）
- `ConversationHistory`：对话历史记录（id、timestamp、input、output、model、params、tokenUsage?、evaluation）
- `QwenChatOptions`：Qwen 调用选项（model、temperature、topP、maxTokens、apiKey）
- `TokenUsage`：token 用量（prompt_tokens、completion_tokens、total_tokens）
- `ChatResponse`：聊天响应（content、usage?）

#### Scenario: 类型定义集中
- **WHEN** 开发者需要在组件中使用 `Role` 类型
- **THEN** MUST 通过 `import type { Role } from '../types'` 引用
- **AND** MUST NOT 在组件文件内重新声明 `interface Role`

#### Scenario: 重复定义检测
- **GIVEN** 项目代码已合并
- **WHEN** 执行 `grep -r "^interface" components/ pages/ lib/ contexts/ --include="*.ts*" | awk -F: '{print $3}' | sort | uniq -c | awk '$1 > 1'`
- **THEN** 输出 MUST 为空（或仅 `types/index.ts` 中的定义）

#### Scenario: 类型演进一致
- **WHEN** 在 `types/index.ts` 中给 `Message` 添加新字段（如 `id: string`）
- **THEN** 所有引用 `Message` 的组件 MUST 自动获得新字段（无需逐个修改）
- **AND** `tsc --noEmit` MUST 报告 0 类型错误

---

### Requirement: 禁止使用 `as string` 强制断言

**User Story**: As a 项目维护者，I want 消除 LangChain 集成层的不安全类型断言 so that 运行时非字符串内容不会被错误展示。

**Priority**: P0

**Acceptance**: 该 spec MUST: `lib/langchain/index.ts` 中 0 处 `as string`；改用 `String()` 包装或类型守卫。

**Non-functional**: N/A

`lib/langchain/index.ts` 内对 LangChain 响应内容的处理 MUST 满足：

1. `result.content` 转换 MUST 使用 `String(result.content)` 或类型守卫 `typeof content === 'string' ? content : content.map(c => c.text).join('')`
2. MUST NOT 使用 `as string` 强制类型断言
3. 类型签名 SHOULD 显式标注返回类型 `Promise<ChatResponse>`

#### Scenario: 内容为字符串
- **WHEN** LangChain 返回 `AIMessage`，其 `content` 为字符串
- **THEN** `callQwenChat` MUST 返回 `{ content: <string>, usage?: TokenUsage }`
- **AND** TypeScript 编译时 MUST 不报类型错误

#### Scenario: 内容为复杂类型
- **WHEN** LangChain 返回 `AIMessageChunk`，其 `content` 为 `MessageContentComplex[]`（含 `text` 字段）
- **THEN** `callQwenChat` MUST 将其转换为字符串
- **AND** MUST NOT 抛出 `TypeError: content is not iterable`
- **AND** MUST NOT 使用 `as string` 绕过类型检查

#### Scenario: 类型守卫覆盖工具调用场景
- **WHEN** `callQwenChatWithTools` 处理工具调用结果
- **THEN** 最终 `content` MUST 为字符串
- **AND** `usage` MUST 从 `usage_metadata` 正确映射（如有）

---

### Requirement: 类型导入使用 `import type`

**User Story**: As a 项目维护者，I want 类型导入与值导入清晰分离 so that 编译产物不包含未使用的运行时导入。

**Priority**: P1

**Acceptance**: 该 spec MUST: 100% 的纯类型导入使用 `import type` 语法。

**Non-functional**: N/A

项目中所有纯类型导入 MUST 使用 `import type` 语法：

```typescript
// ✓ 正确
import type { Role, Message } from '../types';
import type { NextApiRequest, NextApiResponse } from 'next';

// ✗ 错误（值导入但仅用作类型）
import { Role, Message } from '../types';
```

例外：枚举、命名空间、运行时需要的 const（如 `DEFAULT_ROLES`）使用普通 import。

#### Scenario: 类型导入检测
- **WHEN** 执行 `tsc --noEmit` 并启用 `verbatimModuleSyntax: true`
- **THEN** MUST 报告 0 个 TS1259 / TS1272 错误
- **AND** 项目 MUST 通过此校验不需修改源代码

#### Scenario: 运行时值导入保持普通语法
- **WHEN** 导入 `DEFAULT_ROLES` 常量数组用于渲染预设角色
- **THEN** MUST 使用 `import { DEFAULT_ROLES } from '../components/RoleManager'`
- **AND** MUST NOT 使用 `import type`

---

### Requirement: 修复 `tsconfig.json` 路径别名

**User Story**: As a 项目维护者，I want `tsconfig.json` 路径别名指向真实目录 so that 后续引入别名导入时不会指向不存在的路径。

**Priority**: P1

**Acceptance**: 该 spec MUST: `@/*` 别名指向 `pages/*` 或删除该别名（保持现状但消除误导）。

**Non-functional**: N/A

`tsconfig.json` 的 `paths` 配置 MUST 满足以下条件之一：

1. 删除 `"@/*": ["./src/*"]`（因项目使用 Pages Router 而非 `src/` 结构）
2. 或改为 `"@/*": ["./*"]`（允许 `@/types/index` 等导入）

MUST NOT 保留指向不存在目录的别名。

#### Scenario: 删除误导性别名
- **GIVEN** `tsconfig.json` 含 `"@/*": ["./src/*"]`
- **WHEN** 删除该 paths 字段
- **THEN** `tsc --noEmit` MUST 仍报告 0 错误（无任何代码使用 `@/` 导入）
- **AND** IDE 自动补全 MUST 不再显示 `@/src/*` 路径

#### Scenario: 启用真实别名
- **GIVEN** `tsconfig.json` 含 `"@/*": ["./*"]`
- **WHEN** 任意文件中使用 `import { Role } from '@/types'`
- **THEN** TypeScript MUST 正确解析
- **AND** Next.js 构建 MUST 不报"模块未找到"错误

