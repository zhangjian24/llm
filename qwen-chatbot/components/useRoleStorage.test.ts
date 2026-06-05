/**
 * useRoleStorage Hook 单元测试
 * 任务 7.5 / 任务 17 阶段跑（任务 16 安装 vitest + @testing-library/react）
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useRoleStorage } from './useRoleStorage';

describe('useRoleStorage', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.useRealTimers();
  });

  it('返回函数引用稳定（多次 re-render 不变）', () => {
    const { result, rerender } = renderHook(() => useRoleStorage());
    const firstRefs = {
      createRole: result.current.createRole,
      updateRole: result.current.updateRole,
      deleteRole: result.current.deleteRole,
      setDefaultRole: result.current.setDefaultRole,
      getDefaultRole: result.current.getDefaultRole,
    };
    rerender();
    expect(result.current.createRole).toBe(firstRefs.createRole);
    expect(result.current.updateRole).toBe(firstRefs.updateRole);
    expect(result.current.deleteRole).toBe(firstRefs.deleteRole);
    expect(result.current.setDefaultRole).toBe(firstRefs.setDefaultRole);
    expect(result.current.getDefaultRole).toBe(firstRefs.getDefaultRole);
  });

  it('createRole 追加到列表', async () => {
    const { result } = renderHook(() => useRoleStorage());
    // 等待初始化 useEffect 完成
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });
    const initialLen = result.current.roles.length;
    act(() => {
      result.current.createRole({
        name: 'New',
        description: 'd',
        systemPrompt: '',
        modelConfig: { model: 'qwen-max', temperature: 0.7, top_p: 0.9, max_tokens: 2048 },
        isDefault: false,
      });
    });
    expect(result.current.roles.length).toBe(initialLen + 1);
  });

  it('createRole 设置默认时取消其他默认', async () => {
    const { result } = renderHook(() => useRoleStorage());
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });
    // 找到当前默认
    const currentDefault = result.current.roles.find((r) => r.isDefault);
    expect(currentDefault).toBeDefined();
    act(() => {
      result.current.createRole({
        name: 'NewDefault',
        description: 'd',
        systemPrompt: '',
        modelConfig: { model: 'qwen-max', temperature: 0.7, top_p: 0.9, max_tokens: 2048 },
        isDefault: true,
      });
    });
    const defaults = result.current.roles.filter((r) => r.isDefault);
    expect(defaults).toHaveLength(1);
    expect(defaults[0].name).toBe('NewDefault');
  });

  it('updateRole 不会导致多次 setState 引起的 bug', async () => {
    const { result } = renderHook(() => useRoleStorage());
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });
    const firstRole = { ...result.current.roles[0] };
    act(() => {
      result.current.updateRole({ ...firstRole, name: '更新后' });
    });
    // 验证单次更新后，列表中只有一条 name 为 '更新后' 的角色
    const matched = result.current.roles.filter((r) => r.name === '更新后');
    expect(matched).toHaveLength(1);
  });

  it('deleteRole 拒绝删除最后一个角色', async () => {
    const { result } = renderHook(() => useRoleStorage());
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });
    // 删到只剩一个
    while (result.current.roles.length > 1) {
      const last = result.current.roles[result.current.roles.length - 1];
      act(() => result.current.deleteRole(last.id));
    }
    const lastId = result.current.roles[0].id;
    const before = result.current.roles.length;
    act(() => result.current.deleteRole(lastId));
    expect(result.current.roles.length).toBe(before); // 保持不变
  });
});
