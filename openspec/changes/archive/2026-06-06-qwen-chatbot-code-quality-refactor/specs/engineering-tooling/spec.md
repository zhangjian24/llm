# Spec: engineering-tooling

> 工程质量工具链；ESLint + Prettier + Vitest + Playwright + npm scripts 编排。

## ADDED Requirements

### Requirement: ESLint 配置

**User Story**: As a 开发者，I want `pnpm run lint` 实际可用 so that 提交前能自动检测代码问题。

**Priority**: P0

**Acceptance**: 该 spec MUST: `pnpm run lint` 报告 0 警告；包含 React Hooks 规则。

**Non-functional**: N/A

ESLint 配置 MUST 满足：

1. 安装 `eslint@^9` 与 `eslint-config-next` 为 devDependencies
2. 根目录新增 `.eslintrc.json`（或 `eslint.config.js`）继承 `next/core-web-vitals`
3. 额外启用 `react-hooks/recommended` 与 `react-hooks/exhaustive-deps`
4. 规则 `no-console: ["error", { allow: ["error", "warn"] }]` 阻止 `console.log` 提交
5. `package.json` 中 `lint` script 升级为 `next lint`（已存在）但配置可用

#### Scenario: 基础 lint 通过
- **WHEN** 执行 `pnpm run lint`
- **THEN** MUST 报告 0 errors / 0 warnings
- **AND** MUST 退出码为 0

#### Scenario: console.log 违规检测
- **GIVEN** 任意源文件含 `console.log('debug')`
- **WHEN** 执行 `pnpm run lint`
- **THEN** MUST 报告该行违规
- **AND** MUST NOT 仅在生产构建中失败

#### Scenario: Hook 依赖检查
- **GIVEN** `useEffect(() => { fetchData() }, [])` 但 `fetchData` 引用未声明在依赖中
- **WHEN** 执行 `pnpm run lint`
- **THEN** MUST 报告 `react-hooks/exhaustive-deps` 违规

#### Scenario: 自动修复
- **WHEN** 执行 `pnpm run lint --fix`
- **THEN** MUST 自动修复可修复问题（缩进、引号等）
- **AND** 不可修复问题仍报告

---

### Requirement: Prettier 格式化

**User Story**: As a 开发者，I want 代码格式自动统一 so that 团队协作时无格式争议。

**Priority**: P1

**Acceptance**: 该 spec MUST: `pnpm run format` 成功执行且无文件需修改（即代码已格式化）。

**Non-functional**: N/A

Prettier 配置 MUST 满足：

1. 安装 `prettier@^3` 为 devDependency
2. 根目录新增 `.prettierrc`：
   ```json
   {
     "semi": true,
     "singleQuote": true,
     "trailingComma": "all",
     "printWidth": 100,
     "tabWidth": 2
   }
   ```
3. 新增 `.prettierignore` 排除 `node_modules/`、`.next/`、`coverage/`、`dist/`
4. `package.json` 新增 scripts：
   - `"format": "prettier --write \"**/*.{ts,tsx,css,md,json}\""`
   - `"format:check": "prettier --check \"**/*.{ts,tsx,css,md,json}\""`

#### Scenario: 自动格式化
- **WHEN** 执行 `pnpm run format`
- **THEN** 所有匹配文件 MUST 被格式化
- **AND** 退出码为 0

#### Scenario: 格式检查
- **WHEN** 执行 `pnpm run format:check`
- **THEN** 若有文件未格式化 MUST 报告并退出码非 0
- **AND** 若全部已格式化 MUST 退出码 0

#### Scenario: 排除 node_modules
- **WHEN** 执行 `pnpm run format`
- **THEN** MUST NOT 修改 `node_modules/` 下任何文件
- **AND** MUST NOT 修改 `.next/` 下任何文件

---

### Requirement: Vitest 单元 + 组件测试

**User Story**: As a 开发者，I want 关键函数有单元测试 so that 重构时不会被静默破坏。

**Priority**: P0

**Acceptance**: 该 spec MUST: 单元 + 组件测试覆盖率 ≥ 80%；关键纯函数 100% 覆盖。

**Non-functional**: N/A

Vitest 配置 MUST 满足：

1. 安装 devDependencies：`vitest@^1` `@vitest/ui` `@testing-library/react` `@testing-library/jest-dom` `jsdom` `@testing-library/user-event`
2. 根目录新增 `vitest.config.ts`：
   ```typescript
   import { defineConfig } from 'vitest/config';
   import react from '@vitejs/plugin-react';
   export default defineConfig({
     plugins: [react()],
     test: {
       environment: 'jsdom',
       globals: true,
       setupFiles: ['./vitest.setup.ts'],
       coverage: {
         provider: 'v8',
         reporter: ['text', 'html'],
         thresholds: {
           lines: 80,
           functions: 80,
           branches: 75,
           statements: 80,
         },
       },
     },
   });
   ```
3. 根目录新增 `vitest.setup.ts` 导入 `@testing-library/jest-dom`
4. `package.json` 新增 scripts：
   - `"test": "vitest run"`
   - `"test:watch": "vitest"`
   - `"test:coverage": "vitest run --coverage"`
   - `"test:ui": "vitest --ui"`

#### Scenario: 单元测试运行
- **WHEN** 执行 `pnpm test`
- **THEN** MUST 运行所有 `**/*.test.ts` 和 `**/*.test.tsx` 文件
- **AND** 报告通过/失败/跳过统计
- **AND** 退出码反映测试结果（0 全过）

#### Scenario: 覆盖率门槛
- **WHEN** 执行 `pnpm test:coverage`
- **THEN** MUST 报告 lines/branches/functions/statistics 覆盖率
- **AND** 若任一指标 < 阈值 MUST 退出码非 0
- **AND** HTML 报告 MUST 生成于 `coverage/`

#### Scenario: 关键函数 100% 覆盖
- **GIVEN** `lib/role-reducer.ts` 含 `applyRoleUpdate` / `applyRoleCreate` / `applyRoleDelete`
- **WHEN** 执行 `pnpm test:coverage`
- **THEN** `lib/role-reducer.ts` 覆盖率 MUST 为 100%
- **AND** 每个分支（如"isDefault 切换"）MUST 有对应测试

#### Scenario: 组件测试
- **GIVEN** 测试文件 `components/RoleManager.test.tsx` 包含 5 个 `it()`
- **WHEN** 执行 `pnpm test`
- **THEN** MUST 运行并报告 5 个测试结果
- **AND** jsdom 环境 MUST 支持 React 渲染

---

### Requirement: Playwright E2E 测试

**User Story**: As a 开发者，I want 关键用户路径有 E2E 测试 so that 端到端回归被自动化捕获。

**Priority**: P0

**Acceptance**: 该 spec MUST: 10 条 E2E 关键路径全绿（详见 `design.md` §Testing Strategy）。

**Non-functional**: N/A

Playwright 配置 MUST 满足：

1. 安装 devDependencies：`@playwright/test`
2. 安装浏览器：`pnpm exec playwright install --with-deps chromium`
3. 根目录新增 `playwright.config.ts`：
   ```typescript
   import { defineConfig } from '@playwright/test';
   export default defineConfig({
     testDir: './e2e',
     timeout: 30_000,
     use: {
       baseURL: 'http://localhost:3000',
       trace: 'on-first-retry',
     },
     webServer: {
       command: 'pnpm dev',
       port: 3000,
       timeout: 60_000,
     },
   });
   ```
4. 新增目录 `e2e/` 含 10 个测试文件
5. `package.json` 新增 scripts：
   - `"test:e2e": "playwright test"`
   - `"test:e2e:ui": "playwright test --ui"`

#### Scenario: E2E 套件运行
- **WHEN** 执行 `pnpm test:e2e`
- **THEN** MUST 自动启动 dev server（如未运行）
- **THEN** MUST 运行所有 `e2e/**/*.spec.ts` 文件
- **AND** 报告通过/失败统计
- **AND** 失败时 MUST 保存 trace 视频

#### Scenario: 关键路径覆盖
- **WHEN** 执行 `pnpm test:e2e`
- **THEN** MUST 至少覆盖：
  1. 发送消息并收到流式响应
  2. 创建/编辑/删除角色
  3. 配置 API Key 并测试连接
  4. 打开历史模态框并编辑评价
  5. 切换角色锁定 ModelConfigPanel
  6. 错误重试流程
  7. 持久化往返（关闭重开状态恢复）
- **AND** 全部 MUST 通过

#### Scenario: 失败时 trace
- **GIVEN** E2E 测试失败
- **WHEN** 查看 `test-results/`
- **THEN** MUST 包含 `.zip` trace 文件
- **AND** trace 可用 `playwright show-trace` 打开

#### Scenario: 浏览器依赖完整
- **WHEN** 在 CI 环境执行 `pnpm test:e2e`
- **THEN** Chromium 浏览器 MUST 可启动
- **AND** MUST NOT 报"Missing dependencies"错误

---

### Requirement: 覆盖率门槛与豁免

**User Story**: As a 开发者，I want 覆盖率门槛清晰、可豁免 so that 测试目标明确且不被形式化拖累。

**Priority**: P1

**Acceptance**: 该 spec MUST: 关键纯函数 100% 覆盖；其他模块 ≥ 80% 覆盖；豁免有明确注释。

**Non-functional**: N/A

覆盖率规则 MUST 满足：

1. 关键纯函数 100% 覆盖（强制）：
   - `lib/role-reducer.ts` 所有导出
   - `lib/langchain/index.ts:createQwenChatModel`
   - `lib/langchain/tools.ts:getWeatherData` / `getCoordinatesByCity`
   - `components/useAISettings.ts:saveApiKey` / `clearApiKey`
2. 其他模块 ≥ 80% 覆盖（全局阈值）
3. 豁免 MUST 使用 `/* c8 ignore next */` 注释 + 注释说明豁免原因
4. 豁免比例 MUST ≤ 5%

#### Scenario: 关键函数 100% 覆盖
- **WHEN** 执行 `pnpm test:coverage --reporter=text`
- **THEN** `lib/role-reducer.ts` MUST 100% lines/branches/functions
- **AND** 任何未覆盖分支 MUST 阻塞 PR 合并

#### Scenario: 豁免注释格式
- **GIVEN** 某段代码 `/* c8 ignore next */ // 错误处理路径，依赖 fetch 网络失败`
- **WHEN** 执行 `pnpm test:coverage`
- **THEN** 该段 MUST NOT 计入分母
- **AND** 注释 MUST 解释豁免原因（人工审查）

#### Scenario: 豁免比例超限
- **GIVEN** 豁免代码行 > 5%
- **WHEN** 人工审查
- **THEN** MUST 重新设计为可测试（如抽函数 / mock）
