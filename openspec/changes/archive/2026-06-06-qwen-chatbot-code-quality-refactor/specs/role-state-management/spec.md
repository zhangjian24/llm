# Spec: role-state-management

> AI 角色管理；CRUD、默认角色迁移、localStorage 持久化、Hook 引用稳定。

## ADDED Requirements

### Requirement: 纯函数化角色 reducer

**User Story**: As a 项目维护者，I want 角色 CRUD 抽取为纯函数 so that 状态变更可预测、可测试、避免多次 setState 引发不一致。

**Priority**: P0

**Acceptance**: 该 spec MUST: `applyRoleCreate`、`applyRoleUpdate`、`applyRoleDelete` 为纯函数，单元测试覆盖率 100%。

**Non-functional**: N/A

`useRoleStorage` MUST 抽取以下纯函数（建议放在 `lib/role-reducer.ts` 或同文件顶部）：

```typescript
type RoleUpdater = (prev: Role[]) => Role[];

const applyRoleCreate: RoleUpdater = (prev, newRole) => { ... };
const applyRoleUpdate: RoleUpdater = (prev, updatedRole) => { ... };
const applyRoleDelete: RoleUpdater = (prev, roleId) => { ... };
```

调用约定：

1. MUST 使用 `setRoles(prev => applyRoleCreate(prev, newRole))` 模式
2. MUST NOT 在 reducer 内部直接访问闭包外的 `roles` 变量
3. `applyRoleUpdate` MUST 在一次调用内完成所有相关状态变更（含默认角色迁移）
4. MUST NOT 出现同一逻辑的多次 `setRoles` 调用

#### Scenario: 创建默认角色迁移
- **GIVEN** 现有角色列表 `[{id: 'a', isDefault: true}, {id: 'b', isDefault: false}]`
- **WHEN** 调用 `applyRoleCreate(prev, {id: 'c', isDefault: true, ...})`
- **THEN** 返回 MUST 为 `[{id: 'a', isDefault: false}, {id: 'b', isDefault: false}, {id: 'c', isDefault: true}]`
- **AND** 调用次数 MUST 为 1（而非 2 次 setState）

#### Scenario: 更新非默认角色
- **GIVEN** 现有角色列表 `[{id: 'a', name: 'old'}]`
- **WHEN** 调用 `applyRoleUpdate(prev, {id: 'a', name: 'new', isDefault: false, ...})`
- **THEN** 返回 MUST 为 `[{id: 'a', name: 'new', isDefault: false}]`
- **AND** 其他属性（如 modelConfig）MUST 保留

#### Scenario: 取消默认角色
- **GIVEN** 现有角色列表 `[{id: 'a', isDefault: true}, {id: 'b', isDefault: false}]`
- **WHEN** 调用 `applyRoleUpdate(prev, {id: 'a', isDefault: false, ...})`
- **THEN** 返回 MUST 为 `[{id: 'a', isDefault: false}, {id: 'b', isDefault: false}]`
- **AND** 角色列表中 MUST NOT 有 `isDefault: true` 的角色（允许无默认）

#### Scenario: 删除非默认角色
- **GIVEN** 现有角色列表 `[{id: 'a', isDefault: true}, {id: 'b', isDefault: false}]`
- **WHEN** 调用 `applyRoleDelete(prev, 'b')`
- **THEN** 返回 MUST 为 `[{id: 'a', isDefault: true}]`
- **AND** 默认角色 MUST 保持不变

#### Scenario: 删除默认角色自动迁移
- **GIVEN** 现有角色列表 `[{id: 'a', isDefault: true}, {id: 'b', isDefault: false}, {id: 'c', isDefault: false}]`
- **WHEN** 调用 `applyRoleDelete(prev, 'a')`
- **THEN** 返回 MUST 为 `[{id: 'b', isDefault: true}, {id: 'c', isDefault: false}]`
- **AND** 第一个剩余角色 MUST 自动成为默认

#### Scenario: 拒绝删除最后一个角色
- **GIVEN** 现有角色列表 `[{id: 'a', isDefault: true}]`
- **WHEN** 调用 `applyRoleDelete(prev, 'a')`
- **THEN** MUST 返回原列表不变（或抛出明确错误）
- **AND** MUST NOT 让角色列表变为空

---

### Requirement: Hook 函数引用稳定

**User Story**: As a 项目维护者，I want `useRoleStorage` 返回的所有函数引用稳定 so that 下游 useEffect 不因引用变化而误触发。

**Priority**: P0

**Acceptance**: 该 spec MUST: `useRoleStorage` 返回的所有函数在相同 state 下引用一致（`useCallback` 包装）。

**Non-functional**: 性能：依赖 Hook 返回函数的 useEffect 不应在 state 未变时重复执行

`useRoleStorage` MUST 满足：

1. 所有返回函数（`createRole`、`updateRole`、`deleteRole`、`setDefaultRole`、`getDefaultRole`、`saveRolesToStorage`、`loadRolesFromStorage`）MUST 用 `useCallback` 包装
2. 内部访问 state 时 MUST 通过 setter 回调 `setRoles(prev => ...)`
3. 不得在函数体内直接引用闭包中的 `roles` 变量
4. 依赖数组 MUST 为空（`[]`）或不包含非稳定引用

#### Scenario: 引用稳定
- **GIVEN** `useRoleStorage()` 在组件 A 中调用
- **WHEN** 组件 A 重新渲染（但 state 未变）
- **THEN** 返回的 `createRole` 函数引用 MUST 与上次一致
- **AND** React DevTools Profiler MUST 显示下游 useEffect 未执行

#### Scenario: 引用随 state 更新
- **GIVEN** `useRoleStorage()` 第一次调用返回 `createRole: fn1`
- **WHEN** 内部 state 更新（如新增角色）
- **THEN** 返回的 `createRole` 函数引用 MUST 仍稳定（如 fn1 === fn2）
- **AND** 仅 state 数据变化，不引起引用变化

#### Scenario: 单元测试可重复
- **GIVEN** 单元测试 `applyRoleUpdate` 函数
- **WHEN** 相同输入调用两次
- **THEN** MUST 返回相同的输出
- **AND** MUST NOT 产生副作用（如 localStorage 写入）

---

### Requirement: 默认角色 ID 持久化同步

**User Story**: As a 项目维护者，I want 默认角色 ID 单独持久化 so that 重启应用后默认角色选择立即恢复。

**Priority**: P0

**Acceptance**: 该 spec MUST: 设置默认角色后，刷新页面默认角色仍被选中。

**Non-functional**: N/A

`useRoleStorage` MUST 满足：

1. `setDefaultRole(roleId)` MUST 同时更新 `roles` 数组（isDefault 标记）和 `defaultRoleId`（localStorage 键）
2. `getDefaultRole()` MUST 优先按 `defaultRoleId` 查找，找不到时回退到 `roles.find(r => r.isDefault)`
3. `defaultRoleId` 与 `roles` 中标记的 `isDefault` MUST 保持一致（任一变更需同步另一）

#### Scenario: 设置默认角色
- **GIVEN** 当前默认角色为 `a`
- **WHEN** 调用 `setDefaultRole('b')`
- **THEN** `roles` 数组中 `b` 的 `isDefault` MUST 为 `true`
- **AND** `a` 的 `isDefault` MUST 为 `false`
- **AND** `localStorage.getItem('qwen_chatbot_default_role_id')` MUST 为 `'b'`

#### Scenario: 通过 defaultRoleId 查找
- **GIVEN** `defaultRoleId = 'b'`
- **WHEN** 调用 `getDefaultRole()`
- **THEN** MUST 返回 `roles.find(r => r.id === 'b')`
- **AND** 即使该角色的 `isDefault === false`，仍优先按 ID 返回

#### Scenario: defaultRoleId 失效
- **GIVEN** `defaultRoleId = 'deleted_role'`，但 `'deleted_role'` 已不在 roles 中
- **WHEN** 调用 `getDefaultRole()`
- **THEN** MUST 回退到 `roles.find(r => r.isDefault)`
- **AND** 若无 isDefault 角色则返回 `undefined`

#### Scenario: 持久化往返
- **GIVEN** 设置 `defaultRoleId = 'b'`
- **WHEN** 刷新页面
- **THEN** 初始化时 `defaultRoleId` MUST 为 `'b'`
- **AND** `getDefaultRole()` MUST 返回 `b` 角色

---

### Requirement: 初始化默认角色下放到 Hook

**User Story**: As a 项目维护者，I want 默认角色创建逻辑下沉到 `useRoleStorage` 内部 so that 各页面不再重复"首次空列表时创建默认"的副作用。

**Priority**: P1

**Acceptance**: 该 spec MUST: 页面组件不再持有"首次创建默认角色" useEffect；`useRoleStorage` 自管理。

**Non-functional**: N/A

`useRoleStorage` MUST 满足：

1. 内部 `useEffect` MUST 在 `roles` 为空时初始化 `DEFAULT_ROLES`（从 `RoleManager` 导入）
2. 该初始化 MUST 仅在 `useRoleStorage` 首次挂载时执行一次
3. 页面组件（如 `pages/chat.tsx`、`pages/roles.tsx`）MUST 移除对应的初始化 useEffect
4. 初始化 MUST 通过纯函数 `applyRoleCreate` 串行触发

#### Scenario: 首次访问自动初始化
- **GIVEN** localStorage 中无 `qwen_chatbot_roles` 键
- **WHEN** 任意页面挂载并调用 `useRoleStorage()`
- **THEN** 内部 MUST 自动创建 `DEFAULT_ROLES`（3 个预设角色）
- **AND** `roles` 状态 MUST 包含 3 个角色
- **AND** localStorage MUST 立即持久化

#### Scenario: 已有数据不重复初始化
- **GIVEN** localStorage 中已有 5 个自定义角色
- **WHEN** 调用 `useRoleStorage()`
- **THEN** MUST NOT 追加 `DEFAULT_ROLES`
- **AND** roles 状态 MUST 为已有的 5 个角色

#### Scenario: 页面组件无初始化 useEffect
- **WHEN** 检查 `pages/chat.tsx` 和 `pages/roles.tsx`
- **THEN** MUST NOT 包含"如果 roles 为空就 onCreateRole"的 useEffect
- **AND** 仅保留消费方逻辑（如选中默认角色用于 modelConfig）
