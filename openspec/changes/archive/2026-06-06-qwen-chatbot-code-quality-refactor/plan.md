# Qwen-Chatbot 代码质量改造实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在保持 UI 与 100% 行为不变的前提下，将 qwen-chatbot 从"能跑"提升到"工业级"：类型安全 / 状态可维护 / 测试覆盖 / 工具链完整 / 性能可访问性达标。

**Architecture:** 单 worktree、单 PR、按 P0→P1→P2 顺序渐进改造。每任务独立 commit，TDD 严格（先红再绿再重构），所有 13 个 spec 的 Scenario 必须有对应测试。

**Tech Stack:** Next.js 16 + React 19 + TypeScript 5 + TailwindCSS 3 + LangChain + Vitest 1 + React Testing Library + Playwright + axe-core + ESLint 9 + Prettier 3

---

## 文件结构

### 改造后新增/修改/删除

| 操作 | 路径 | 用途 |
|------|------|------|
| 改 | `types/index.ts` | 集中类型（7 个） |
| 改 | `lib/langchain/index.ts` | 移除 6 处 `as string` |
| 改 | `lib/role-reducer.ts`（新）| 纯函数 reducer |
| 改 | `lib/model-options.ts`（新）| 模型选项常量 |
| 改 | `lib/logger.ts`（新）| 统一日志 |
| 改 | `contexts/ChatContext.tsx`（新）| 持久化状态 |
| 改 | `contexts/UIContext.tsx`（新）| 输入框状态 |
| 改 | `contexts/RoleContext.tsx`（新）| 角色 Hook 包装 |
| 删 | `contexts/AppContext.tsx` | 改用三个拆分 Context |
| 改 | `components/LoadingState.tsx`（新）| 共享 Loading |
| 改 | `components/HistoryTable.tsx`（新）| 共享历史表格 |
| 改 | `components/MarkdownRenderer.tsx`（新）| 共享 Markdown |
| 删 | `components/ConversationHistoryTable.tsx` | 旧冗余副本 |
| 改 | `components/useRoleStorage.ts` | 纯函数化 + 稳定引用 |
| 改 | `components/RoleManager.tsx` | 用 `MODEL_OPTIONS` |
| 改 | `components/ModelConfigPanel.tsx` | 用 `MODEL_OPTIONS` |
| 改 | `components/ChatWindow.tsx` | 去重 + 移除 console |
| 改 | `components/TypeWriterEffect.tsx` | RAF 优化 |
| 改 | `components/HistoryModal.tsx` | ARIA + HistoryTable |
| 改 | `pages/_app.tsx` | 三个 Provider 嵌套 |
| 改 | `pages/chat.tsx` | 改用新 Context |
| 改 | `pages/roles.tsx` | 改用新 Context |
| 改 | `pages/api/verify-key.ts` | 修正 HTTP 状态码 |
| 改 | `tsconfig.json` | 删除错误别名 |
| 改 | `package.json` | 加 scripts + devDeps |
| 改 | `.eslintrc.json`（新）| 规则 |
| 改 | `.prettierrc`（新）| 格式 |
| 改 | `vitest.config.ts`（新）| 配置 |
| 改 | `vitest.setup.ts`（新）| setup |
| 改 | `playwright.config.ts`（新）| E2E |
| 改 | `e2e/01-07-*.spec.ts`（新）| 7 个 E2E |
| 改 | `tests/**/*.test.{ts,tsx}` | 单元 + 组件测试 |

### 文件责任单一性

- **types/**: 纯类型，无运行时
- **lib/**: 纯逻辑（无 React 依赖），易测试
- **contexts/**: React Context + Provider
- **components/**: 单一职责 UI 组件
- **hooks/**: 自定义 Hook（稳定引用）

---

## Task 1: 统一类型到 types/index.ts

**Files:**
- Modify: `qwen-chatbot/types/index.ts`
- Modify: `qwen-chatbot/components/ChatWindow.tsx`
- Modify: `qwen-chatbot/components/ConversationHistoryTable.tsx`
- Modify: `qwen-chatbot/components/ModelConfigPanel.tsx`

- [ ] **Step 1.1: 写 types/index.ts 集中 7 个类型**

```typescript
// qwen-chatbot/types/index.ts
export interface Role {
  id: string;
  name: string;
  avatar: string;
  systemPrompt: string;
  modelConfig: ModelConfig;
  createdAt: number;
  isDefault?: boolean;
}

export interface ModelConfig {
  model: string;
  temperature: number;
  topP: number;
  maxTokens: number;
  presencePenalty: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
  usage?: TokenUsage;
}

export interface ConversationHistory {
  id: string;
  title: string;
  createdAt: number;
  updatedAt: number;
  roleId: string;
  messages: Message[];
  evaluation?: 'good' | 'bad' | null;
}

export interface QwenChatOptions {
  apiKey: string;
  baseUrl?: string;
}

export interface TokenUsage {
  promptTokens: number;
  completionTokens: number;
  totalTokens: number;
}

export interface ChatResponse {
  content: string;
  usage?: TokenUsage;
}
```

- [ ] **Step 1.2: 删除 ChatWindow.tsx 中的本地接口（行 5-30）**

```typescript
// 替换为
import type { Message } from '../types';
```

- [ ] **Step 1.3: 删除 ConversationHistoryTable.tsx 中的本地接口**

```typescript
import type { ConversationHistory } from '../types';
```

- [ ] **Step 1.4: 删除 ModelConfigPanel.tsx 中的本地接口**

```typescript
import type { ModelConfig } from '../types';
```

- [ ] **Step 1.5: 校验**

```bash
cd qwen-chatbot && npx tsc --noEmit
```

Expected: 0 errors

- [ ] **Step 1.6: 校验无重复接口**

```bash
cd qwen-chatbot && grep -r "^interface" components/ lib/ types/ | awk -F: '{print $3}' | sort | uniq -c | awk '$1 > 1'
```

Expected: 无输出

- [ ] **Step 1.7: 提交**

```bash
git add types/index.ts components/ChatWindow.tsx components/ConversationHistoryTable.tsx components/ModelConfigPanel.tsx
git commit -m "refactor(types): 统一 7 个类型到 types/index.ts，删除本地副本"
```

---

## Task 2: 修复 LangChain 强制类型断言

**Files:**
- Modify: `qwen-chatbot/lib/langchain/index.ts`
- Create: `qwen-chatbot/lib/langchain/index.test.ts`（仅 1 个守卫测试，完整测试在 Task 17）

- [ ] **Step 2.1: 添加类型守卫函数**

```typescript
// qwen-chatbot/lib/langchain/index.ts 顶部
function toStringContent(
  content: string | Array<{ type: string; text?: string }>
): string {
  if (typeof content === 'string') return content;
  return content
    .filter((c) => c.type === 'text' && typeof c.text === 'string')
    .map((c) => c.text as string)
    .join('');
}
```

- [ ] **Step 2.2: 替换 6 处 `as string`**

查找模式 `content as string`，6 处全部改为 `toStringContent(content)`。

- [ ] **Step 2.3: 写守卫单元测试**

```typescript
// qwen-chatbot/lib/langchain/index.test.ts
import { describe, it, expect } from 'vitest';

describe('toStringContent', () => {
  it('returns string as-is', () => {
    expect(toStringContent('hello')).toBe('hello');
  });

  it('joins text parts from array', () => {
    const result = toStringContent([
      { type: 'text', text: 'Hello ' },
      { type: 'text', text: 'world' },
    ]);
    expect(result).toBe('Hello world');
  });

  it('filters non-text parts', () => {
    const result = toStringContent([
      { type: 'text', text: 'keep' },
      { type: 'image', text: undefined },
    ]);
    expect(result).toBe('keep');
  });
});
```

> 注：toStringContent 不导出。完整测试在 Task 17 引入导出后进行。此处只验证函数存在。

- [ ] **Step 2.4: 校验**

```bash
cd qwen-chatbot && npx tsc --noEmit
```

Expected: 0 errors

- [ ] **Step 2.5: 提交**

```bash
git add lib/langchain/index.ts
git commit -m "refactor(langchain): 替换 6 处 as string 为类型守卫 toStringContent"
```

---

## Task 3: 修复 tsconfig 路径别名

**Files:**
- Modify: `qwen-chatbot/tsconfig.json`

- [ ] **Step 3.1: 删除错误别名**

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

> 保留 `"@/*": ["./*"]`（指向项目根而非不存在的 src/）。如未使用则全删。

- [ ] **Step 3.2: 校验**

```bash
cd qwen-chatbot && npx tsc --noEmit
```

Expected: 0 errors

- [ ] **Step 3.3: 提交**

```bash
git add tsconfig.json
git commit -m "chore(tsconfig): 修复 @/* 路径别名指向项目根"
```

---

## Task 4: 清理调试代码与统一 Logger

**Files:**
- Create: `qwen-chatbot/lib/logger.ts`
- Modify: `qwen-chatbot/components/ChatWindow.tsx`（移除 line 32 console.log）
- Modify: 任何含 console.log 的文件

- [ ] **Step 4.1: 列出全部 console.log**

```bash
cd qwen-chatbot && grep -rn "console\." --include="*.ts" --include="*.tsx" components/ lib/ pages/ contexts/
```

- [ ] **Step 4.2: 创建统一 logger**

```typescript
// qwen-chatbot/lib/logger.ts
const isDev = process.env.NODE_ENV !== 'production';

export const log = {
  debug: (...args: unknown[]) => {
    if (isDev) console.log('[DEBUG]', ...args);
  },
  info: (...args: unknown[]) => {
    if (isDev) console.info('[INFO]', ...args);
  },
  warn: (...args: unknown[]) => console.warn('[WARN]', ...args),
  error: (...args: unknown[]) => console.error('[ERROR]', ...args),
};
```

- [ ] **Step 4.3: 替换所有纯调试 console.log**

```typescript
// 替换前
console.log('currentResponse', currentResponse);

// 替换后
import { log } from '../lib/logger';
log.debug('currentResponse', currentResponse);
```

> 保留 console.error 和 console.warn（生产中仍需）；仅移除 console.log / console.info。

- [ ] **Step 4.4: 校验生产构建无 console.log**

```bash
cd qwen-chatbot && pnpm build && grep -r "console.log" .next/static/ || echo "OK: 0 matches"
```

Expected: `OK: 0 matches`

- [ ] **Step 4.5: 提交**

```bash
git add lib/logger.ts components/ pages/ contexts/
git commit -m "refactor: 引入统一 logger，移除生产调试 console.log"
```

---

## Task 5: 修正 verify-key HTTP 语义

**Files:**
- Modify: `qwen-chatbot/pages/api/verify-key.ts`
- Create: `qwen-chatbot/pages/api/verify-key.test.ts`

- [ ] **Step 5.1: 写失败测试**

```typescript
// qwen-chatbot/pages/api/verify-key.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import handler from './verify-key';
import type { NextApiRequest, NextApiResponse } from 'next';

function mockRes() {
  const res: Partial<NextApiResponse> = {
    status: vi.fn().mockReturnThis(),
    json: vi.fn().mockReturnThis(),
  };
  return res as NextApiResponse;
}

describe('POST /api/verify-key', () => {
  beforeEach(() => vi.clearAllMocks());

  it('returns 401 when API returns authentication error', async () => {
    const req = { method: 'POST', body: { apiKey: 'invalid' } } as NextApiRequest;
    const res = mockRes();
    await handler(req, res);
    expect(res.status).toHaveBeenCalledWith(401);
  });

  it('returns 200 on success', async () => {
    const req = { method: 'POST', body: { apiKey: 'valid-key' } } as NextApiRequest;
    const res = mockRes();
    await handler(req, res);
    expect(res.status).toHaveBeenCalledWith(200);
  });
});
```

- [ ] **Step 5.2: 跑测试确认红**

```bash
cd qwen-chatbot && pnpm test pages/api/verify-key.test.ts
```

Expected: 401 测试失败（当前返回 200）

- [ ] **Step 5.3: 修复 verify-key.ts:36**

```typescript
// 替换前（第 30-40 行附近的 catch 或错误处理）
res.status(200).json({ valid: false, error: errorMsg });

// 替换后
const status = errorMsg.includes('Invalid') || errorMsg.includes('401') ? 401 : 400;
res.status(status).json({ valid: false, error: errorMsg });
```

- [ ] **Step 5.4: 跑测试确认绿**

```bash
cd qwen-chatbot && pnpm test pages/api/verify-key.test.ts
```

Expected: PASS

- [ ] **Step 5.5: 提交**

```bash
git add pages/api/verify-key.ts pages/api/verify-key.test.ts
git commit -m "fix(api): verify-key 错误时返回正确 HTTP 状态码（401/400）"
```

---

## Task 6: 抽取纯函数 reducer

**Files:**
- Create: `qwen-chatbot/lib/role-reducer.ts`
- Create: `qwen-chatbot/lib/role-reducer.test.ts`

- [ ] **Step 6.1: TDD 写 create 测试**

```typescript
// qwen-chatbot/lib/role-reducer.test.ts
import { describe, it, expect } from 'vitest';
import { applyRoleCreate, applyRoleUpdate, applyRoleDelete } from './role-reducer';
import type { Role } from '../types';

const baseRole: Role = {
  id: 'r1', name: 'R1', avatar: '🤖', systemPrompt: '',
  modelConfig: { model: 'qwen-turbo', temperature: 0.7, topP: 0.8, maxTokens: 2048, presencePenalty: 0 },
  createdAt: 1, isDefault: true,
};

describe('applyRoleCreate', () => {
  it('appends new role to list', () => {
    const newRole = { ...baseRole, id: 'r2' };
    const result = applyRoleCreate([baseRole], newRole);
    expect(result).toEqual([baseRole, newRole]);
  });
});
```

- [ ] **Step 6.2: 跑测试确认红**

```bash
cd qwen-chatbot && pnpm test lib/role-reducer.test.ts
```

Expected: FAIL（模块不存在）

- [ ] **Step 6.3: 实现 create 函数**

```typescript
// qwen-chatbot/lib/role-reducer.ts
import type { Role } from '../types';

export type RoleUpdater = (prev: Role[]) => Role[];

export function applyRoleCreate(prev: Role[], newRole: Role): Role[] {
  return [...prev, newRole];
}
```

- [ ] **Step 6.4: 跑测试确认绿**

```bash
cd qwen-chatbot && pnpm test lib/role-reducer.test.ts
```

Expected: PASS

- [ ] **Step 6.5: TDD 写 update 测试**

```typescript
describe('applyRoleUpdate', () => {
  it('replaces role by id', () => {
    const updated = { ...baseRole, name: 'R1-Updated' };
    const result = applyRoleUpdate([baseRole], updated);
    expect(result[0].name).toBe('R1-Updated');
  });

  it('does not mutate input', () => {
    applyRoleUpdate([baseRole], { ...baseRole, name: 'X' });
    expect(baseRole.name).toBe('R1');
  });
});
```

- [ ] **Step 6.6: 实现 update 函数**

```typescript
export function applyRoleUpdate(prev: Role[], updated: Role): Role[] {
  return prev.map((r) => (r.id === updated.id ? updated : r));
}
```

- [ ] **Step 6.7: TDD 写 delete 测试**

```typescript
describe('applyRoleDelete', () => {
  it('removes role by id', () => {
    const r2 = { ...baseRole, id: 'r2' };
    const result = applyRoleDelete([baseRole, r2], 'r1');
    expect(result).toEqual([r2]);
  });

  it('refuses to delete last role', () => {
    expect(() => applyRoleDelete([baseRole], 'r1')).toThrow();
  });

  it('migrates default when default is deleted', () => {
    const r2 = { ...baseRole, id: 'r2', isDefault: false };
    const result = applyRoleDelete([baseRole, r2], 'r1');
    expect(result[0].isDefault).toBe(true);
  });
});
```

- [ ] **Step 6.8: 实现 delete 函数**

```typescript
export function applyRoleDelete(prev: Role[], id: string): Role[] {
  if (prev.length === 1) {
    throw new Error('Cannot delete the last role');
  }
  const filtered = prev.filter((r) => r.id !== id);
  // 如果删的是默认角色，把第一个迁移为默认
  if (prev.find((r) => r.id === id)?.isDefault && filtered.length > 0) {
    filtered[0] = { ...filtered[0], isDefault: true };
  }
  return filtered;
}
```

- [ ] **Step 6.9: 校验 100% 覆盖**

```bash
cd qwen-chatbot && pnpm test lib/role-reducer.test.ts --coverage
```

Expected: 100% lines, branches, functions

- [ ] **Step 6.10: 提交**

```bash
git add lib/role-reducer.ts lib/role-reducer.test.ts
git commit -m "feat(reducer): 抽取纯函数 applyRoleCreate/Update/Delete + 100% 覆盖"
```

---

## Task 7: 重构 useRoleStorage

**Files:**
- Modify: `qwen-chatbot/components/useRoleStorage.ts`
- Create: `qwen-chatbot/components/useRoleStorage.test.ts`

- [ ] **Step 7.1: 写 Hook 稳定引用测试**

```typescript
// qwen-chatbot/components/useRoleStorage.test.ts
import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useRoleStorage } from './useRoleStorage';

describe('useRoleStorage', () => {
  it('returns stable function references across re-renders', () => {
    const { result, rerender } = renderHook(() => useRoleStorage());
    const first = {
      addRole: result.current.addRole,
      updateRole: result.current.updateRole,
      deleteRole: result.current.deleteRole,
    };
    rerender();
    expect(result.current.addRole).toBe(first.addRole);
    expect(result.current.updateRole).toBe(first.updateRole);
    expect(result.current.deleteRole).toBe(first.deleteRole);
  });

  it('addRole appends to roles list', () => {
    const { result } = renderHook(() => useRoleStorage());
    const initialLen = result.current.roles.length;
    act(() => {
      result.current.addRole({
        id: 'new', name: 'New', avatar: '🆕', systemPrompt: '',
        modelConfig: { model: 'qwen-turbo', temperature: 0.7, topP: 0.8, maxTokens: 2048, presencePenalty: 0 },
        createdAt: Date.now(),
      });
    });
    expect(result.current.roles.length).toBe(initialLen + 1);
  });
});
```

- [ ] **Step 7.2: 跑测试确认部分红**

```bash
cd qwen-chatbot && pnpm test useRoleStorage.test.ts
```

Expected: 引用稳定性测试可能红（当前未 useCallback 包装）

- [ ] **Step 7.3: 替换内联 setState 为纯函数调用**

```typescript
// qwen-chatbot/components/useRoleStorage.ts
import { useCallback, useEffect, useState } from 'react';
import { applyRoleCreate, applyRoleUpdate, applyRoleDelete } from '../lib/role-reducer';
import type { Role } from '../types';

export function useRoleStorage() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [defaultRoleId, setDefaultRoleId] = useState<string | null>(null);

  // 初始化（从 localStorage 读取 + 首次创建默认）
  useEffect(() => {
    try {
      const stored = localStorage.getItem('qwen_chatbot_roles');
      const storedDefault = localStorage.getItem('qwen_chatbot_default_role_id');
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setRoles(parsed);
          setDefaultRoleId(storedDefault ?? parsed[0].id);
          return;
        }
      }
    } catch { /* 降级到默认 */ }
    // 首次创建默认角色
    const defaultRole = createDefaultRole();
    setRoles([defaultRole]);
    setDefaultRoleId(defaultRole.id);
  }, []);

  // 持久化
  useEffect(() => {
    if (roles.length > 0) {
      localStorage.setItem('qwen_chatbot_roles', JSON.stringify(roles));
    }
  }, [roles]);

  useEffect(() => {
    if (defaultRoleId) {
      localStorage.setItem('qwen_chatbot_default_role_id', defaultRoleId);
    }
  }, [defaultRoleId]);

  // 稳定引用
  const addRole = useCallback((role: Role) => {
    setRoles((prev) => applyRoleCreate(prev, role));
  }, []);

  const updateRole = useCallback((role: Role) => {
    setRoles((prev) => applyRoleUpdate(prev, role));
    if (role.isDefault) {
      setDefaultRoleId(role.id);
    }
  }, []);

  const deleteRole = useCallback((id: string) => {
    setRoles((prev) => applyRoleDelete(prev, id));
  }, []);

  return { roles, defaultRoleId, addRole, updateRole, deleteRole, setDefaultRoleId };
}
```

- [ ] **Step 7.4: 跑测试确认绿**

```bash
cd qwen-chatbot && pnpm test useRoleStorage.test.ts
```

Expected: PASS

- [ ] **Step 7.5: 提交**

```bash
git add components/useRoleStorage.ts components/useRoleStorage.test.ts
git commit -m "refactor(hook): useRoleStorage 改用纯函数 reducer + useCallback 稳定引用"
```

---

## Task 8: 拆分 AppContext

**Files:**
- Create: `qwen-chatbot/contexts/ChatContext.tsx`
- Create: `qwen-chatbot/contexts/UIContext.tsx`
- Create: `qwen-chatbot/contexts/RoleContext.tsx`
- Modify: `qwen-chatbot/contexts/AppContext.tsx`（保留为 deprecated 兼容层）
- Modify: `qwen-chatbot/pages/_app.tsx`
- Modify: `qwen-chatbot/pages/chat.tsx`
- Modify: `qwen-chatbot/pages/roles.tsx`

- [ ] **Step 8.1: 安装 use-debounce**

```bash
cd qwen-chatbot && pnpm add use-debounce
```

- [ ] **Step 8.2: 创建 ChatContext**

```typescript
// qwen-chatbot/contexts/ChatContext.tsx
import { createContext, useContext, useReducer, useEffect, useRef, type ReactNode } from 'react';
import { useDebouncedCallback } from 'use-debounce';
import type { Message, ConversationHistory } from '../types';

const STORAGE_KEY = 'appState';
const SCHEMA_VERSION = 1;

interface ChatState {
  messages: Message[];
  conversationHistory: ConversationHistory[];
  selectedRoleId: string | null;
  schemaVersion: number;
}

type ChatAction =
  | { type: 'SET_MESSAGES'; payload: Message[] }
  | { type: 'SET_HISTORY'; payload: ConversationHistory[] }
  | { type: 'SET_SELECTED_ROLE'; payload: string | null }
  | { type: 'LOAD_STATE'; payload: ChatState };

function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case 'SET_MESSAGES': return { ...state, messages: action.payload };
    case 'SET_HISTORY': return { ...state, conversationHistory: action.payload };
    case 'SET_SELECTED_ROLE': return { ...state, selectedRoleId: action.payload };
    case 'LOAD_STATE': return action.payload;
    default: return state;
  }
}

function getInitialState(): ChatState {
  if (typeof window === 'undefined') {
    return { messages: [], conversationHistory: [], selectedRoleId: null, schemaVersion: SCHEMA_VERSION };
  }
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      if (parsed && typeof parsed === 'object' && Array.isArray(parsed.messages)) {
        return {
          messages: parsed.messages,
          conversationHistory: Array.isArray(parsed.conversationHistory) ? parsed.conversationHistory : [],
          selectedRoleId: typeof parsed.selectedRoleId === 'string' ? parsed.selectedRoleId : null,
          schemaVersion: SCHEMA_VERSION,
        };
      }
    }
  } catch { /* 降级 */ }
  return { messages: [], conversationHistory: [], selectedRoleId: null, schemaVersion: SCHEMA_VERSION };
}

const ChatContext = createContext<{
  state: ChatState;
  dispatch: React.Dispatch<ChatAction>;
} | null>(null);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(chatReducer, undefined, getInitialState);

  const debouncedSave = useDebouncedCallback((s: ChatState) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
    } catch (e) {
      console.error('Failed to persist chat state', e);
    }
  }, 500);

  useEffect(() => {
    debouncedSave(state);
  }, [state, debouncedSave]);

  // beforeunload 强制 flush
  useEffect(() => {
    const handler = () => {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
      } catch { /* ignore */ }
    };
    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
  }, [state]);

  return (
    <ChatContext.Provider value={{ state, dispatch }}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChatContext() {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error('useChatContext must be used within ChatProvider');
  return ctx;
}
```

- [ ] **Step 8.3: 创建 UIContext**

```typescript
// qwen-chatbot/contexts/UIContext.tsx
import { createContext, useContext, useState, type ReactNode } from 'react';

interface UIState {
  inputMessage: string;
  isGenerating: boolean;
  isThinking: boolean;
  currentResponse: string;
}

type UIDispatch = {
  setInputMessage: (s: string) => void;
  setIsGenerating: (b: boolean) => void;
  setIsThinking: (b: boolean) => void;
  setCurrentResponse: (s: string) => void;
};

const UIContext = createContext<(UIState & UIDispatch) | null>(null);

export function UIProvider({ children }: { children: ReactNode }) {
  const [inputMessage, setInputMessage] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [currentResponse, setCurrentResponse] = useState('');

  return (
    <UIContext.Provider value={{
      inputMessage, setInputMessage,
      isGenerating, setIsGenerating,
      isThinking, setIsThinking,
      currentResponse, setCurrentResponse,
    }}>
      {children}
    </UIContext.Provider>
  );
}

export function useUIContext() {
  const ctx = useContext(UIContext);
  if (!ctx) throw new Error('useUIContext must be used within UIProvider');
  return ctx;
}
```

- [ ] **Step 8.4: 创建 RoleContext**

```typescript
// qwen-chatbot/contexts/RoleContext.tsx
import { createContext, useContext, type ReactNode } from 'react';
import { useRoleStorage } from '../components/useRoleStorage';

const RoleContext = createContext<ReturnType<typeof useRoleStorage> | null>(null);

export function RoleProvider({ children }: { children: ReactNode }) {
  const roleStorage = useRoleStorage();
  return <RoleContext.Provider value={roleStorage}>{children}</RoleContext.Provider>;
}

export function useRoleContext() {
  const ctx = useContext(RoleContext);
  if (!ctx) throw new Error('useRoleContext must be used within RoleProvider');
  return ctx;
}
```

- [ ] **Step 8.5: 标记 AppContext 为 deprecated**

```typescript
// qwen-chatbot/contexts/AppContext.tsx 顶部
/**
 * @deprecated 自 2026-Q1 拆分。改用 ChatProvider + UIProvider + RoleProvider。
 * 保留此文件仅为兼容旧版本，本版本后将删除。
 */
```

- [ ] **Step 8.6: 改写 _app.tsx**

```typescript
// qwen-chatbot/pages/_app.tsx
import type { AppProps } from 'next/app';
import { ChatProvider } from '../contexts/ChatContext';
import { UIProvider } from '../contexts/UIContext';
import { RoleProvider } from '../contexts/RoleContext';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <RoleProvider>
      <ChatProvider>
        <UIProvider>
          <Component {...pageProps} />
        </UIProvider>
      </ChatProvider>
    </RoleProvider>
  );
}
```

- [ ] **Step 8.7: 改写 chat.tsx（关键改 useChat/useUI/useRole）**

```typescript
// qwen-chatbot/pages/chat.tsx 顶部
import { useChatContext } from '../contexts/ChatContext';
import { useUIContext } from '../contexts/UIContext';
import { useRoleContext } from '../contexts/RoleContext';

export default function ChatPage() {
  const { state: chatState, dispatch: chatDispatch } = useChatContext();
  const ui = useUIContext();
  const { roles, defaultRoleId } = useRoleContext();
  // ... 其余代码
}
```

- [ ] **Step 8.8: 改写 roles.tsx（同样）**

```typescript
// qwen-chatbot/pages/roles.tsx 顶部
import { useRoleContext } from '../contexts/RoleContext';
```

- [ ] **Step 8.9: 校验**

```bash
cd qwen-chatbot && npx tsc --noEmit
```

Expected: 0 errors

- [ ] **Step 8.10: 提交**

```bash
git add contexts/ pages/_app.tsx pages/chat.tsx pages/roles.tsx package.json
git commit -m "refactor(contexts): 拆分 AppContext 为 Chat/UI/Role + debounce 持久化 + schemaVersion"
```

---

## Task 9: 抽取共享 LoadingState

**Files:**
- Create: `qwen-chatbot/components/LoadingState.tsx`
- Modify: `qwen-chatbot/pages/chat.tsx`
- Modify: `qwen-chatbot/pages/roles.tsx`

- [ ] **Step 9.1: 创建组件**

```typescript
// qwen-chatbot/components/LoadingState.tsx
export function LoadingState({ message = '加载中...' }: { message?: string }) {
  return (
    <div className="flex items-center justify-center p-8" role="status" aria-live="polite">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" aria-hidden="true" />
      <span className="ml-3 text-gray-600">{message}</span>
    </div>
  );
}
```

- [ ] **Step 9.2: 替换 chat.tsx 内联 Loading**

```typescript
// 替换前
<div className="p-4">加载中...</div>

// 替换后
import { LoadingState } from '../components/LoadingState';
<LoadingState />
```

- [ ] **Step 9.3: 替换 roles.tsx 内联 Loading**

同上。

- [ ] **Step 9.4: 校验唯一来源**

```bash
cd qwen-chatbot && grep -rn "加载中" pages/ | grep -v LoadingState
```

Expected: 无输出

- [ ] **Step 9.5: 提交**

```bash
git add components/LoadingState.tsx pages/chat.tsx pages/roles.tsx
git commit -m "refactor: 抽取共享 LoadingState 组件"
```

---

## Task 10: 抽取共享 ModelOptions

**Files:**
- Create: `qwen-chatbot/lib/model-options.ts`
- Modify: `qwen-chatbot/components/ModelConfigPanel.tsx`
- Modify: `qwen-chatbot/components/RoleManager.tsx`

- [ ] **Step 10.1: 创建常量**

```typescript
// qwen-chatbot/lib/model-options.ts
export const MODEL_OPTIONS = [
  { value: 'qwen-turbo', label: '通义千问 Turbo（快速）' },
  { value: 'qwen-plus', label: '通义千问 Plus（平衡）' },
  { value: 'qwen-max', label: '通义千问 Max（高质量）' },
  { value: 'qwen-long', label: '通义千问 Long（长文本）' },
] as const;

export type ModelId = (typeof MODEL_OPTIONS)[number]['value'];
```

- [ ] **Step 10.2: 替换 ModelConfigPanel 内联**

```typescript
import { MODEL_OPTIONS } from '../lib/model-options';
// 替换原 <option value="qwen-turbo"> 等等
{MODEL_OPTIONS.map((opt) => (
  <option key={opt.value} value={opt.value}>{opt.label}</option>
))}
```

- [ ] **Step 10.3: 替换 RoleManager 内联**

同上。

- [ ] **Step 10.4: 校验唯一来源**

```bash
cd qwen-chatbot && grep -rn "qwen-turbo" components/ pages/ | grep -v model-options
```

Expected: 无输出

- [ ] **Step 10.5: 提交**

```bash
git add lib/model-options.ts components/ModelConfigPanel.tsx components/RoleManager.tsx
git commit -m "refactor: 抽取共享 MODEL_OPTIONS 常量"
```

---

## Task 11: 抽取共享 HistoryTable

**Files:**
- Create: `qwen-chatbot/components/HistoryTable.tsx`
- Create: `qwen-chatbot/components/HistoryTable.test.tsx`
- Modify: `qwen-chatbot/components/HistoryModal.tsx`
- Delete: `qwen-chatbot/components/ConversationHistoryTable.tsx`

- [ ] **Step 11.1: TDD 写测试**

```typescript
// qwen-chatbot/components/HistoryTable.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HistoryTable } from './HistoryTable';
import type { ConversationHistory } from '../types';

const sample: ConversationHistory = {
  id: 'h1', title: '测试会话', createdAt: 1, updatedAt: 2, roleId: 'r1',
  messages: [{
    id: 'm1', role: 'user', content: '这是一个很长的用户输入内容用于测试截断显示'.repeat(5), timestamp: 1,
  }, {
    id: 'm2', role: 'assistant', content: 'AI响应内容也比较长，同样需要测试截断。'.repeat(5), timestamp: 2,
  }],
};

describe('HistoryTable', () => {
  it('truncates long content with ellipsis', () => {
    render(<HistoryTable history={[sample]} onEvaluationChange={() => {}} />);
    expect(screen.getAllByText(/\.\.\./).length).toBeGreaterThan(0);
  });

  it('counts auto-evaluate by characters not bytes', () => {
    const cn: ConversationHistory = { ...sample, messages: [{
      id: 'm3', role: 'assistant', content: '中文'.repeat(50), timestamp: 1,
    }]};
    render(<HistoryTable history={[cn]} onEvaluationChange={() => {}} />);
    // 100 中文字符应触发 autoEvaluate 显示
    expect(screen.getByText('自动评价')).toBeInTheDocument();
  });
});
```

- [ ] **Step 11.2: 跑测试确认红**

```bash
cd qwen-chatbot && pnpm test HistoryTable.test.tsx
```

Expected: FAIL（组件不存在）

- [ ] **Step 11.3: 创建 HistoryTable**

```typescript
// qwen-chatbot/components/HistoryTable.tsx
import { useState } from 'react';
import type { ConversationHistory } from '../types';

const AUTO_EVALUATE_THRESHOLD = 100;
const TRUNCATE_INPUT = 30;
const TRUNCATE_OUTPUT = 60;

function shouldAutoEvaluate(content: string): boolean {
  return [...content].length > AUTO_EVALUATE_THRESHOLD;
}

function truncate(s: string, n: number): string {
  const chars = [...s];
  return chars.length > n ? chars.slice(0, n).join('') + '...' : s;
}

interface Props {
  history: ConversationHistory[];
  onEvaluationChange: (id: string, evaluation: 'good' | 'bad' | null) => void;
}

export function HistoryTable({ history, onEvaluationChange }: Props) {
  return (
    <table className="w-full text-sm">
      <thead>
        <tr>
          <th>时间</th>
          <th>输入</th>
          <th>输出</th>
          <th>评价</th>
        </tr>
      </thead>
      <tbody>
        {history.map((h) => {
          const userMsg = h.messages.find((m) => m.role === 'user')?.content ?? '';
          const assistantMsg = h.messages.find((m) => m.role === 'assistant')?.content ?? '';
          const autoEval = shouldAutoEvaluate(assistantMsg) ? 'good' : null;
          return (
            <tr key={h.id}>
              <td>{new Date(h.createdAt).toLocaleString()}</td>
              <td title={userMsg}>{truncate(userMsg, TRUNCATE_INPUT)}</td>
              <td title={assistantMsg}>{truncate(assistantMsg, TRUNCATE_OUTPUT)}</td>
              <td>
                <EvaluationControl
                  id={h.id}
                  initial={h.evaluation ?? autoEval}
                  onChange={onEvaluationChange}
                />
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

function EvaluationControl({ id, initial, onChange }: {
  id: string; initial: 'good' | 'bad' | null;
  onChange: (id: string, e: 'good' | 'bad' | null) => void;
}) {
  const [val, setVal] = useState(initial);
  return (
    <div>
      {val === 'good' && <span>自动评价:好</span>}
      <button onClick={() => { setVal('good'); onChange(id, 'good'); }}>👍</button>
      <button onClick={() => { setVal('bad'); onChange(id, 'bad'); }}>👎</button>
    </div>
  );
}
```

- [ ] **Step 11.4: 跑测试确认绿**

```bash
cd qwen-chatbot && pnpm test HistoryTable.test.tsx
```

Expected: PASS

- [ ] **Step 11.5: 替换 HistoryModal 内联表格**

```typescript
import { HistoryTable } from './HistoryTable';
// 替换原内联 <table> 元素
<HistoryTable history={history} onEvaluationChange={onEval} />
```

- [ ] **Step 11.6: 删除 ConversationHistoryTable.tsx**

```bash
cd qwen-chatbot && git rm components/ConversationHistoryTable.tsx
```

- [ ] **Step 11.7: 校验 tsc**

```bash
cd qwen-chatbot && npx tsc --noEmit
```

Expected: 0 errors

- [ ] **Step 11.8: 提交**

```bash
git add components/HistoryTable.tsx components/HistoryTable.test.tsx components/HistoryModal.tsx
git commit -m "refactor: 抽取共享 HistoryTable + 修复 autoEvaluate 中文分词 + 删除旧副本"
```

---

## Task 12: 抽取共享 MarkdownRenderer

**Files:**
- Create: `qwen-chatbot/components/MarkdownRenderer.tsx`
- Modify: `qwen-chatbot/components/ChatWindow.tsx`
- Modify: `qwen-chatbot/components/TypeWriterEffect.tsx`

- [ ] **Step 12.1: 创建组件**

```typescript
// qwen-chatbot/components/MarkdownRenderer.tsx
import { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';

interface Props {
  children: string;
  className?: string;
}

export function MarkdownRenderer({ children, className }: Props) {
  const components = useMemo(() => ({
    a: ({ ...props }) => <a {...props} target="_blank" rel="noopener noreferrer" />,
  }), []);
  return (
    <div className={className}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]} components={components}>
        {children}
      </ReactMarkdown>
    </div>
  );
}
```

- [ ] **Step 12.2: 替换 ChatWindow.tsx**

```typescript
import { MarkdownRenderer } from './MarkdownRenderer';
// 替换 ReactMarkdown + remarkGfm + rehypeHighlight 三件套
<MarkdownRenderer className="prose prose-sm max-w-none">{msg.content}</MarkdownRenderer>
```

- [ ] **Step 12.3: 替换 TypeWriterEffect.tsx**

同上。

- [ ] **Step 12.4: 校验唯一来源**

```bash
cd qwen-chatbot && grep -rn "remarkGfm\|rehypeHighlight" components/ | grep -v MarkdownRenderer
```

Expected: 无输出

- [ ] **Step 12.5: 提交**

```bash
git add components/MarkdownRenderer.tsx components/ChatWindow.tsx components/TypeWriterEffect.tsx
git commit -m "refactor: 抽取共享 MarkdownRenderer 组件"
```

---

## Task 13: 流式响应去重

**Files:**
- Modify: `qwen-chatbot/pages/chat.tsx`

- [ ] **Step 13.1: 移除 currentResponse 本地 state**

```typescript
// 删除 const [currentResponse, setCurrentResponse] = useState(''); 改用 messages
import { useMemo } from 'react';

const lastMessage = useMemo(
  () => chatState.messages[chatState.messages.length - 1],
  [chatState.messages]
);
const isStreaming = ui.isGenerating && lastMessage?.role === 'assistant';
```

- [ ] **Step 13.2: 改写 TypeWriterEffect 调用**

```typescript
// 替换前
<TypeWriterEffect text={currentResponse} />

// 替换后
{isStreaming && <TypeWriterEffect text={lastMessage.content} />}
```

- [ ] **Step 13.3: 添加 E2E 测试断言**

```typescript
// e2e/03-streaming.spec.ts（新建）
test('流式响应 DOM 仅 1 条助手消息气泡', async ({ page }) => {
  await page.goto('/chat');
  await page.fill('textarea', '你好');
  await page.click('button[type="submit"]');
  await page.waitForSelector('[data-testid="assistant-message"]');
  // 等流式 500ms 后断言数量仍为 1
  await page.waitForTimeout(500);
  const count = await page.locator('[data-testid="assistant-message"]').count();
  expect(count).toBe(1);
});
```

- [ ] **Step 13.4: 提交**

```bash
git add pages/chat.tsx e2e/03-streaming.spec.ts
git commit -m "refactor: 流式响应去重 currentResponse state，直接订阅 messages"
```

---

## Task 14: TypeWriterEffect 性能优化

**Files:**
- Modify: `qwen-chatbot/components/TypeWriterEffect.tsx`
- Create: `qwen-chatbot/components/TypeWriterEffect.test.tsx`

- [ ] **Step 14.1: TDD 写测试**

```typescript
// qwen-chatbot/components/TypeWriterEffect.test.tsx
import { describe, it, expect } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { TypeWriterEffect } from './TypeWriterEffect';

describe('TypeWriterEffect', () => {
  it('renders text progressively', async () => {
    jest.useFakeTimers();
    const { rerender } = render(<TypeWriterEffect text="Hello" speed={10} />);
    act(() => { jest.advanceTimersByTime(20); });
    rerender(<TypeWriterEffect text="Hello World" speed={10} />);
    expect(screen.getByText(/Hello/)).toBeInTheDocument();
  });
});
```

- [ ] **Step 14.2: 实现 RAF 优化版**

```typescript
// qwen-chatbot/components/TypeWriterEffect.tsx
import { useEffect, useRef, useState, useMemo } from 'react';
import { MarkdownRenderer } from './MarkdownRenderer';

const CHUNK_SIZE = 3;
const FRAME_INTERVAL = 16; // ms, ~60fps

export function TypeWriterEffect({ text, speed = 30 }: { text: string; speed?: number }) {
  const [displayed, setDisplayed] = useState('');
  const rafRef = useRef<number | null>(null);
  const lastUpdateRef = useRef(0);

  useEffect(() => {
    setDisplayed('');
    let i = 0;
    const tick = (timestamp: number) => {
      if (timestamp - lastUpdateRef.current >= speed) {
        i = Math.min(i + CHUNK_SIZE, text.length);
        setDisplayed(text.slice(0, i));
        lastUpdateRef.current = timestamp;
      }
      if (i < text.length) {
        rafRef.current = requestAnimationFrame(tick);
      }
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [text, speed]);

  const memoMarkdown = useMemo(() => displayed, [displayed]);

  return <MarkdownRenderer>{memoMarkdown}</MarkdownRenderer>;
}
```

- [ ] **Step 14.3: 跑测试**

```bash
cd qwen-chatbot && pnpm test TypeWriterEffect.test.tsx
```

Expected: PASS

- [ ] **Step 14.4: 提交**

```bash
git add components/TypeWriterEffect.tsx components/TypeWriterEffect.test.tsx
git commit -m "perf(TypeWriter): 改用 requestAnimationFrame + 3 字符累积 + useMemo 缓存"
```

---

## Task 15: 错误处理使用本地变量

**Files:**
- Modify: `qwen-chatbot/pages/chat.tsx`
- Create: `qwen-chatbot/pages/chat.test.tsx`

- [ ] **Step 15.1: TDD 写错误路径测试**

```typescript
// qwen-chatbot/pages/chat.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ChatPage from './chat';

vi.mock('../contexts/ChatContext', () => ({
  useChatContext: () => ({
    state: { messages: [], conversationHistory: [], selectedRoleId: null, schemaVersion: 1 },
    dispatch: vi.fn(),
  }),
}));

describe('ChatPage error path', () => {
  it('records user input in history when API errors', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('Network'));
    render(<ChatPage />);
    const textarea = screen.getByRole('textbox');
    fireEvent.change(textarea, { target: { value: 'test input' } });
    fireEvent.click(screen.getByRole('button', { name: /发送/ }));
    await waitFor(() => {
      expect(screen.getByText('test input')).toBeInTheDocument();
    });
  });
});
```

- [ ] **Step 15.2: 修复 use local variable**

```typescript
// qwen-chatbot/pages/chat.tsx handleSend 函数
const handleSend = async () => {
  const userInput = ui.inputMessage; // 关键：本地变量
  if (!userInput.trim() || ui.isGenerating) return;

  const userMessage: Message = {
    id: crypto.randomUUID(),
    role: 'user',
    content: userInput,
    timestamp: Date.now(),
  };

  chatDispatch({ type: 'SET_MESSAGES', payload: [...chatState.messages, userMessage] });
  ui.setInputMessage('');
  ui.setIsGenerating(true);
  ui.setIsThinking(true);

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: [...chatState.messages, { role: 'user', content: userInput }],
        // ...其他参数
      }),
    });
    // ...
  } catch (error) {
    // 用 userInput 而非 ui.inputMessage（已被清空）
    const errorRecord: ConversationHistory = {
      id: crypto.randomUUID(),
      title: userInput.slice(0, 30),
      createdAt: Date.now(),
      updatedAt: Date.now(),
      roleId: chatState.selectedRoleId ?? '',
      messages: [userMessage],
    };
    chatDispatch({
      type: 'SET_HISTORY',
      payload: [errorRecord, ...chatState.conversationHistory],
    });
  } finally {
    ui.setIsGenerating(false);
    ui.setIsThinking(false);
  }
};
```

- [ ] **Step 15.3: 跑测试**

```bash
cd qwen-chatbot && pnpm test pages/chat.test.tsx
```

Expected: PASS

- [ ] **Step 15.4: 提交**

```bash
git add pages/chat.tsx pages/chat.test.tsx
git commit -m "fix(chat): 错误处理使用本地变量 userInput 而非已清空的 inputMessage"
```

---

## Task 16: ESLint + Prettier + Vitest 工具链

**Files:**
- Modify: `qwen-chatbot/package.json`
- Create: `qwen-chatbot/.eslintrc.json`
- Create: `qwen-chatbot/.prettierrc`
- Create: `qwen-chatbot/.prettierignore`
- Create: `qwen-chatbot/vitest.config.ts`
- Create: `qwen-chatbot/vitest.setup.ts`

- [ ] **Step 16.1: 安装依赖**

```bash
cd qwen-chatbot && pnpm add -D \
  eslint@^9 \
  eslint-config-next \
  prettier@^3 \
  vitest@^1 \
  @vitest/ui \
  @testing-library/react \
  @testing-library/jest-dom \
  @testing-library/user-event \
  jsdom \
  @playwright/test \
  happy-dom
```

- [ ] **Step 16.2: 创建 .eslintrc.json**

```json
{
  "extends": ["next/core-web-vitals"],
  "rules": {
    "no-console": ["error", { "allow": ["error", "warn"] }],
    "react-hooks/exhaustive-deps": "warn"
  }
}
```

- [ ] **Step 16.3: 创建 .prettierrc**

```json
{
  "singleQuote": true,
  "semi": true,
  "trailingComma": "all",
  "printWidth": 100,
  "tabWidth": 2
}
```

- [ ] **Step 16.4: 创建 .prettierignore**

```
node_modules/
.next/
coverage/
playwright-report/
test-results/
*.log
.env.local
```

- [ ] **Step 16.5: 创建 vitest.config.ts**

```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
    globals: true,
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

- [ ] **Step 16.6: 创建 vitest.setup.ts**

```typescript
import '@testing-library/jest-dom';
```

- [ ] **Step 16.7: 更新 package.json scripts**

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "format": "prettier --write \"**/*.{ts,tsx,json,md}\"",
    "format:check": "prettier --check \"**/*.{ts,tsx,json,md}\"",
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "test:ui": "vitest --ui",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui"
  }
}
```

- [ ] **Step 16.8: 跑 lint 与 format:check**

```bash
cd qwen-chatbot && pnpm run lint && pnpm run format:check
```

Expected: 通过（可能需要先跑 format 修复格式）

- [ ] **Step 16.9: 提交**

```bash
git add package.json .eslintrc.json .prettierrc .prettierignore vitest.config.ts vitest.setup.ts
git commit -m "chore(tooling): 集成 ESLint + Prettier + Vitest + Playwright + 覆盖率门槛"
```

---

## Task 17: 单元 + 组件测试补齐

**Files:**
- Create: `qwen-chatbot/lib/langchain/index.test.ts`
- Create: `qwen-chatbot/lib/langchain/tools.test.ts`
- Create: `qwen-chatbot/components/useAISettings.test.ts`
- Create: `qwen-chatbot/components/RoleManager.test.tsx`
- Create: `qwen-chatbot/components/ChatInput.test.tsx`
- Create: `qwen-chatbot/components/ModelConfigPanel.test.tsx`

- [ ] **Step 17.1: 写 createQwenChatModel 测试**

```typescript
// qwen-chatbot/lib/langchain/index.test.ts
import { describe, it, expect, vi } from 'vitest';

vi.mock('@langchain/community/chat_models/tongyi', () => ({
  ChatTongyi: vi.fn().mockImplementation((opts) => ({ opts })),
}));

import { createQwenChatModel } from './index';

describe('createQwenChatModel', () => {
  it('passes config to ChatTongyi', () => {
    const model = createQwenChatModel({
      apiKey: 'k',
      model: 'qwen-plus',
      temperature: 0.5,
      maxTokens: 1024,
    });
    expect(model.opts.model).toBe('qwen-plus');
    expect(model.opts.temperature).toBe(0.5);
  });
});
```

- [ ] **Step 17.2: 写天气工具测试**

```typescript
// qwen-chatbot/lib/langchain/tools.test.ts
import { describe, it, expect, vi } from 'vitest';

global.fetch = vi.fn();
import { getWeatherData } from './tools';

describe('getWeatherData', () => {
  it('maps weather codes to descriptions', async () => {
    (fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({ current: { weather_code: 0, temperature_2m: 20 } }),
    });
    const result = await getWeatherData('北京');
    expect(result).toContain('晴');
  });

  it('throws on city not found', async () => {
    (fetch as any).mockResolvedValue({ ok: false, status: 404 });
    await expect(getWeatherData('不存在城市xyz')).rejects.toThrow();
  });
});
```

- [ ] **Step 17.3: 写 useAISettings 测试**

```typescript
// qwen-chatbot/components/useAISettings.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useAISettings } from './useAISettings';

describe('useAISettings', () => {
  beforeEach(() => localStorage.clear());

  it('saves api key to localStorage', () => {
    const { result } = renderHook(() => useAISettings());
    act(() => result.current.saveApiKey('test-key'));
    expect(localStorage.getItem('qwen_chatbot_api_key')).toBe('test-key');
  });

  it('clears api key', () => {
    localStorage.setItem('qwen_chatbot_api_key', 'old');
    const { result } = renderHook(() => useAISettings());
    act(() => result.current.clearApiKey());
    expect(localStorage.getItem('qwen_chatbot_api_key')).toBeNull();
  });
});
```

- [ ] **Step 17.4: 写 RoleManager 测试**

```typescript
// qwen-chatbot/components/RoleManager.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { RoleManager } from './RoleManager';

describe('RoleManager', () => {
  it('submits form with role data', async () => {
    const onSubmit = vi.fn();
    render(<RoleManager onSubmit={onSubmit} />);
    await userEvent.type(screen.getByLabelText('角色名'), '助手');
    fireEvent.click(screen.getByRole('button', { name: /保存/ }));
    expect(onSubmit).toHaveBeenCalledWith(expect.objectContaining({ name: '助手' }));
  });
});
```

- [ ] **Step 17.5: 写 ChatInput 测试**

```typescript
// qwen-chatbot/components/ChatInput.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ChatInput } from './ChatInput';

describe('ChatInput', () => {
  it('disables when generating', () => {
    render(<ChatInput onSend={() => {}} isGenerating={true} value="" onChange={() => {}} />);
    expect(screen.getByRole('textbox')).toBeDisabled();
  });

  it('calls onSend on submit', () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} isGenerating={false} value="hi" onChange={() => {}} />);
    fireEvent.click(screen.getByRole('button', { name: /发送/ }));
    expect(onSend).toHaveBeenCalledWith('hi');
  });
});
```

- [ ] **Step 17.6: 写 ModelConfigPanel 测试**

```typescript
// qwen-chatbot/components/ModelConfigPanel.test.tsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ModelConfigPanel } from './ModelConfigPanel';

describe('ModelConfigPanel', () => {
  it('locks inputs when disabled', () => {
    render(<ModelConfigPanel value={{ ... }} onChange={() => {}} disabled={true} />);
    expect(screen.getByLabelText('Temperature')).toBeDisabled();
  });
});
```

- [ ] **Step 17.7: 跑全量覆盖率**

```bash
cd qwen-chatbot && pnpm test:coverage
```

Expected: ≥ 80% 全局

- [ ] **Step 17.8: 提交**

```bash
git add lib/langchain/index.test.ts lib/langchain/tools.test.ts \
        components/useAISettings.test.ts components/RoleManager.test.tsx \
        components/ChatInput.test.tsx components/ModelConfigPanel.test.tsx
git commit -m "test: 补齐单元+组件测试，覆盖率 ≥ 80%"
```

---

## Task 18: Playwright E2E 测试

**Files:**
- Create: `qwen-chatbot/playwright.config.ts`
- Create: `qwen-chatbot/e2e/01-send-message.spec.ts`
- Create: `qwen-chatbot/e2e/02-role-crud.spec.ts`
- Create: `qwen-chatbot/e2e/03-api-key.spec.ts`
- Create: `qwen-chatbot/e2e/04-history.spec.ts`
- Create: `qwen-chatbot/e2e/05-role-lock.spec.ts`
- Create: `qwen-chatbot/e2e/06-error-retry.spec.ts`
- Create: `qwen-chatbot/e2e/07-persistence.spec.ts`

- [ ] **Step 18.1: 安装 Playwright 浏览器**

```bash
cd qwen-chatbot && pnpm exec playwright install --with-deps chromium
```

- [ ] **Step 18.2: 创建 playwright.config.ts**

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    command: 'pnpm dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
```

- [ ] **Step 18.3: 写 01-send-message**

```typescript
// e2e/01-send-message.spec.ts
import { test, expect } from '@playwright/test';

test('E1 用户能发送消息并接收流式响应', async ({ page }) => {
  await page.goto('/chat');
  await page.fill('textarea', '你好');
  await page.click('button[type="submit"]');
  await expect(page.locator('[data-testid="user-message"]')).toContainText('你好');
  await expect(page.locator('[data-testid="assistant-message"]')).toBeVisible({ timeout: 10000 });
});
```

- [ ] **Step 18.4-18.9: 写其余 6 个 E2E（CRUD、API Key、History、Lock、Error、Persistence）**

按 spec/frontend-quality/spec.md 与 spec/role-state-management/spec.md 的 Scenario 实现。

- [ ] **Step 18.10: 跑全量 E2E**

```bash
cd qwen-chatbot && pnpm test:e2e
```

Expected: 7+ specs 全绿

- [ ] **Step 18.11: 提交**

```bash
git add playwright.config.ts e2e/
git commit -m "test(e2e): 7 个关键路径 Playwright 覆盖（CRUD/对话/历史/错误/持久化）"
```

---

## Task 19: 性能优化

**Files:**
- Modify: `qwen-chatbot/types/index.ts`（添加 id 字段）
- Modify: `qwen-chatbot/components/ChatWindow.tsx`
- Modify: `qwen-chatbot/components/RoleSelector.tsx`
- Modify: `qwen-chatbot/components/ModelConfigPanel.tsx`
- Modify: `qwen-chatbot/pages/chat.tsx`
- Modify: `qwen-chatbot/pages/roles.tsx`

- [ ] **Step 19.1: 添加 id 字段到 Message**

```typescript
// types/index.ts Message 接口添加
export interface Message {
  id: string; // 新增
  role: 'user' | 'assistant' | 'system';
  // ...
}
```

- [ ] **Step 19.2: ChatWindow 消息 key + memo**

```typescript
import { memo } from 'react';
const MessageBubble = memo(function MessageBubble({ message }: { message: Message }) {
  return <div data-testid={`${message.role}-message`}>{message.content}</div>;
});

// 渲染列表
{messages.map((m) => <MessageBubble key={m.id} message={m} />)}
```

- [ ] **Step 19.3-19.4: RoleSelector 与 ModelConfigPanel 加 memo**

```typescript
export const RoleSelector = memo(function RoleSelector(props: Props) { ... });
export const ModelConfigPanel = memo(function ModelConfigPanel(props: Props) { ... });
```

- [ ] **Step 19.5-19.6: chat.tsx 懒加载**

```typescript
import dynamic from 'next/dynamic';
const HistoryModal = dynamic(() => import('../components/HistoryModal').then(m => m.HistoryModal), { ssr: false });
const RoleManager = dynamic(() => import('../components/RoleManager').then(m => m.RoleManager), { ssr: false });
```

- [ ] **Step 19.7: roles.tsx 同上**

- [ ] **Step 19.8: 条件性虚拟列表**

```typescript
import { useState, useEffect } from 'react';
const Virtuoso = useState(() => dynamic(() => import('react-virtuoso').then(m => m.Virtuoso)))[0];

function HistoryList({ items }: { items: ConversationHistory[] }) {
  if (items.length < 100) {
    return <>{items.map((i) => <Item key={i.id} item={i} />)}</>;
  }
  const V = Virtuoso;
  return <V data={items} itemContent={(_, item) => <Item item={item} />} />;
}
```

- [ ] **Step 19.9: 校验**

```bash
cd qwen-chatbot && pnpm build
```

Expected: build 成功

- [ ] **Step 19.10: 提交**

```bash
git add types/index.ts components/ pages/chat.tsx pages/roles.tsx
git commit -m "perf: 稳定 key + React.memo + 懒加载 + 虚拟列表（条件性）"
```

---

## Task 20: 可访问性补齐

**Files:**
- Modify: `qwen-chatbot/components/HistoryModal.tsx`
- Modify: `qwen-chatbot/components/RoleManager.tsx`

- [ ] **Step 20.1: HistoryModal ARIA**

```typescript
<div role="dialog" aria-modal="true" aria-labelledby="history-modal-title">
  <h2 id="history-modal-title">历史记录</h2>
  <button aria-label="关闭" onClick={onClose}>×</button>
  ...
</div>
```

- [ ] **Step 20.2: ESC 关闭 + focus trap**

```typescript
useEffect(() => {
  const handler = (e: KeyboardEvent) => {
    if (e.key === 'Escape') onClose();
  };
  document.addEventListener('keydown', handler);
  return () => document.removeEventListener('keydown', handler);
}, [onClose]);
```

- [ ] **Step 20.3-20.4: RoleManager 编辑模态框同上**

- [ ] **Step 20.5: 颜色对比修复**

```bash
cd qwen-chatbot && grep -rn "text-gray-400" components/ pages/
# 替换为 text-gray-600 或 text-gray-700
```

- [ ] **Step 20.6: 安装 axe-core**

```bash
cd qwen-chatbot && pnpm add -D @axe-core/playwright
```

- [ ] **Step 20.7: 添加 E2E a11y 检查**

```typescript
// e2e/08-a11y.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('模态框无 a11y critical 违规', async ({ page }) => {
  await page.goto('/chat');
  await page.click('[data-testid="open-history"]');
  const results = await new AxeBuilder({ page }).analyze();
  const critical = results.violations.filter((v) => v.impact === 'critical');
  expect(critical).toEqual([]);
});
```

- [ ] **Step 20.8: 跑 E2E**

```bash
cd qwen-chatbot && pnpm test:e2e e2e/08-a11y.spec.ts
```

Expected: 0 critical violations

- [ ] **Step 20.9: 提交**

```bash
git add components/HistoryModal.tsx components/RoleManager.tsx e2e/08-a11y.spec.ts package.json
git commit -m "a11y: 模态框 ARIA + ESC + focus trap + 颜色对比 + axe-core 验证"
```

---

## Task 21: 最终验收

**Files:**（仅运行命令，不修改文件）

- [ ] **Step 21.1: tsc 0 错误**

```bash
cd qwen-chatbot && pnpm typecheck
```

Expected: 0 errors

- [ ] **Step 21.2: lint 0 警告**

```bash
cd qwen-chatbot && pnpm lint
```

Expected: 0 warnings

- [ ] **Step 21.3: 覆盖率 ≥ 80%**

```bash
cd qwen-chatbot && pnpm test:coverage
```

Expected: ≥ 80% lines / functions / statements

- [ ] **Step 21.4: E2E 全绿**

```bash
cd qwen-chatbot && pnpm test:e2e
```

Expected: 8+ specs 全 PASS

- [ ] **Step 21.5: 生产构建成功**

```bash
cd qwen-chatbot && pnpm build
```

Expected: build 完成无错误

- [ ] **Step 21.6: 启动并 Lighthouse ≥ 90**

```bash
cd qwen-chatbot && pnpm start &
# 用 Chrome DevTools Lighthouse 审计 /chat 与 /roles
# 目标：Performance / Accessibility / Best Practices / SEO 均 ≥ 90
```

- [ ] **Step 21.7: 生产构建无 console.log**

```bash
cd qwen-chatbot && grep -r "console.log" .next/static/ || echo "OK"
```

Expected: `OK`

- [ ] **Step 21.8: 手动验证多角色渲染**

```bash
# 在 /roles 创建 5+ 角色，切换聊天无渲染循环
# 验证：用 React DevTools Profiler，切换时无 re-render 整个消息列表
```

- [ ] **Step 21.9: 推送 PR**

```bash
git push -u origin feature/qwen-chatbot-code-quality
gh pr create --title "refactor(qwen-chatbot): P0+P1+P2 全套代码质量改造" \
  --body "见 openspec/changes/qwen-chatbot-code-quality-refactor/ 设计文档"
```

---

## 执行方式选择

Plan 完成并已保存到 `openspec/changes/qwen-chatbot-code-quality-refactor/plan.md`。两种执行方式：

**1. Subagent-Driven (推荐)** - 我为每个任务派发新的子代理，任务之间审查，快速迭代
**2. Inline Execution** - 在本会话中用 executing-plans 批量执行，含审查检查点

请告知选择哪种执行方式，或继续生成 verify.md + retrospective.md 完成 OpenSpec 流程。
