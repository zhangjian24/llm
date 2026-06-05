/**
 * 角色 reducer 纯函数单元测试
 * 任务 6 的 TDD 测试文件；任务 16 安装 vitest 后跑测试
 */
import { describe, it, expect } from 'vitest';
import { applyRoleCreate, applyRoleUpdate, applyRoleDelete } from './role-reducer';
import type { Role } from '../types';

const baseRole = (overrides: Partial<Role> = {}): Role => ({
  id: 'r1',
  name: '测试角色',
  description: 'desc',
  systemPrompt: '',
  modelConfig: { model: 'qwen-max', temperature: 0.7, top_p: 0.9, max_tokens: 2048 },
  isDefault: true,
  ...overrides,
});

describe('applyRoleCreate', () => {
  it('追加到列表末尾', () => {
    const r1 = baseRole();
    const r2 = baseRole({ id: 'r2', isDefault: false });
    const result = applyRoleCreate([r1], r2);
    expect(result).toHaveLength(2);
    expect(result[1]).toEqual(r2);
  });

  it('不修改原数组（不可变性）', () => {
    const r1 = baseRole();
    const r2 = baseRole({ id: 'r2' });
    const original = [r1];
    applyRoleCreate(original, r2);
    expect(original).toHaveLength(1);
  });
});

describe('applyRoleUpdate', () => {
  it('按 id 匹配替换', () => {
    const r1 = baseRole();
    const r2 = baseRole({ id: 'r2' });
    const updated = { ...r1, name: '新名称' };
    const result = applyRoleUpdate([r1, r2], updated);
    expect(result[0].name).toBe('新名称');
    expect(result[1]).toEqual(r2);
  });

  it('更新为默认时取消其他默认（互斥）', () => {
    const r1 = baseRole({ isDefault: true });
    const r2 = baseRole({ id: 'r2', isDefault: false });
    const updated = { ...r2, isDefault: true };
    const result = applyRoleUpdate([r1, r2], updated);
    expect(result[0].isDefault).toBe(false);
    expect(result[1].isDefault).toBe(true);
  });

  it('更新为非默认时不影响其他默认', () => {
    const r1 = baseRole({ isDefault: true });
    const r2 = baseRole({ id: 'r2', isDefault: false });
    const updated = { ...r2, name: '改名' };
    const result = applyRoleUpdate([r1, r2], updated);
    expect(result[0].isDefault).toBe(true);
    expect(result[1].isDefault).toBe(false);
  });
});

describe('applyRoleDelete', () => {
  it('按 id 过滤', () => {
    const r1 = baseRole();
    const r2 = baseRole({ id: 'r2' });
    const result = applyRoleDelete([r1, r2], 'r1');
    expect(result).toEqual([r2]);
  });

  it('拒绝删除最后一个角色', () => {
    const r1 = baseRole();
    expect(() => applyRoleDelete([r1], 'r1')).toThrow('Cannot delete the last role');
  });

  it('删除默认角色时迁移到第一个剩余角色', () => {
    const r1 = baseRole({ isDefault: true });
    const r2 = baseRole({ id: 'r2', isDefault: false });
    const r3 = baseRole({ id: 'r3', isDefault: false });
    const result = applyRoleDelete([r1, r2, r3], 'r1');
    expect(result[0].isDefault).toBe(true);
    expect(result[0].id).toBe('r2');
  });

  it('删除非默认角色不影响其他默认', () => {
    const r1 = baseRole({ isDefault: true });
    const r2 = baseRole({ id: 'r2', isDefault: false });
    const result = applyRoleDelete([r1, r2], 'r2');
    expect(result[0].isDefault).toBe(true);
    expect(result).toHaveLength(1);
  });
});
