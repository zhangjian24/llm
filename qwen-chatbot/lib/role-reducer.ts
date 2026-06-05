/**
 * 角色状态管理的纯函数 reducer
 *
 * 抽取目的：
 * 1. 业务逻辑（创建 / 更新 / 删除 + 默认角色迁移）与 React 状态解耦
 * 2. 单元测试可达 100% 覆盖
 * 3. useRoleStorage 等 hook 通过调用这些纯函数更新状态
 */
import type { Role } from '../types';

export type RoleUpdater = (prev: Role[]) => Role[];

/**
 * 创建角色
 * - 追加到列表末尾
 * - 不修改原数组（不可变性）
 */
export function applyRoleCreate(prev: Role[], newRole: Role): Role[] {
  return [...prev, newRole];
}

/**
 * 更新角色
 * - 按 id 匹配替换
 * - 如果更新后 isDefault=true：其他角色全部取消默认（互斥）
 * - 不修改原数组
 */
export function applyRoleUpdate(prev: Role[], updated: Role): Role[] {
  const next = prev.map((r) => (r.id === updated.id ? updated : r));
  if (updated.isDefault) {
    return next.map((r) => (r.id === updated.id ? r : { ...r, isDefault: false }));
  }
  return next;
}

/**
 * 删除角色
 * - 按 id 过滤
 * - 最后一个角色拒绝删除（业务约束）
 * - 如果删除的是默认角色：第一个剩余角色自动成为新默认（迁移）
 * - 不修改原数组
 */
export function applyRoleDelete(prev: Role[], id: string): Role[] {
  if (prev.length <= 1) {
    throw new Error('Cannot delete the last role');
  }
  const filtered = prev.filter((r) => r.id !== id);
  const wasDefault = prev.find((r) => r.id === id)?.isDefault === true;
  if (wasDefault && filtered.length > 0) {
    return [{ ...filtered[0], isDefault: true }, ...filtered.slice(1)];
  }
  return filtered;
}
