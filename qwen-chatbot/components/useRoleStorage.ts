import { useState, useEffect, useCallback } from 'react';
import { applyRoleCreate, applyRoleUpdate, applyRoleDelete } from '../lib/role-reducer';
import type { Role } from '../types';
import { DEFAULT_ROLES } from './RoleManager';

const ROLE_STORAGE_KEY = 'qwen_chatbot_roles';
const DEFAULT_ROLE_ID_KEY = 'qwen_chatbot_default_role_id';

// 从 localStorage 加载角色数据
export const loadRolesFromStorage = (): Role[] => {
  if (typeof window === 'undefined') return [];

  try {
    const storedRoles = localStorage.getItem(ROLE_STORAGE_KEY);
    if (storedRoles) {
      const parsedRoles = JSON.parse(storedRoles);
      // 确保所有角色都有完整的结构
      const rolesWithCompleteStructure = parsedRoles.map((role: any) => ({
        ...role,
        modelConfig: {
          model: role.modelConfig?.model || 'qwen-max',
          temperature: typeof role.modelConfig?.temperature === 'number' ? role.modelConfig.temperature : 0.7,
          top_p: typeof role.modelConfig?.top_p === 'number' ? role.modelConfig.top_p : 0.9,
          max_tokens: typeof role.modelConfig?.max_tokens === 'number' ? role.modelConfig.max_tokens : 2048,
        },
        isDefault: !!role.isDefault
      }));

      // 检查是否有预设角色需要更新
      let updatedRoles = [...rolesWithCompleteStructure];
      let hasUpdates = false;

      // 遍历默认角色，检查是否需要更新现有角色的systemPrompt
      DEFAULT_ROLES.forEach(defaultRole => {
        const existingRoleIndex = updatedRoles.findIndex(r => r.id === defaultRole.id);
        if (existingRoleIndex !== -1) {
          // 如果找到了匹配的角色ID，检查systemPrompt是否需要更新
          if (updatedRoles[existingRoleIndex].systemPrompt !== defaultRole.systemPrompt) {
            updatedRoles[existingRoleIndex] = {
              ...updatedRoles[existingRoleIndex],
              systemPrompt: defaultRole.systemPrompt // 更新为最新的systemPrompt
            };
            hasUpdates = true;
          }
        }
      });

      // 如果有更新，保存回存储
      if (hasUpdates) {
        saveRolesToStorage(updatedRoles);
      }

      return updatedRoles;
    }
  } catch (error) {
    console.error('Error loading roles from storage:', error);
  }

  return DEFAULT_ROLES;
};

// 保存角色数据到 localStorage
export const saveRolesToStorage = (roles: Role[]): void => {
  if (typeof window === 'undefined') return;

  try {
    localStorage.setItem(ROLE_STORAGE_KEY, JSON.stringify(roles));
  } catch (error) {
    console.error('Error saving roles to storage:', error);
  }
};

// 获取默认角色ID
export const getDefaultRoleId = (): string | null => {
  if (typeof window === 'undefined') return null;

  try {
    return localStorage.getItem(DEFAULT_ROLE_ID_KEY);
  } catch (error) {
    console.error('Error getting default role ID from storage:', error);
    return null;
  }
};

// 保存默认角色ID
export const saveDefaultRoleId = (roleId: string | null): void => {
  if (typeof window === 'undefined') return;

  try {
    if (roleId) {
      localStorage.setItem(DEFAULT_ROLE_ID_KEY, roleId);
    } else {
      localStorage.removeItem(DEFAULT_ROLE_ID_KEY);
    }
  } catch (error) {
    console.error('Error saving default role ID to storage:', error);
  }
};

/**
 * 自定义 Hook 用于管理角色状态和持久化
 *
 * 重构要点：
 * 1. 所有 setter 函数改用纯函数 callback 形式（setRoles(prev => applyX(prev, ...))）
 *    修复 updateRole 中多次 setState 导致的 stale closure 问题
 * 2. 所有返回函数用 useCallback 包装，依赖数组为 []，引用稳定
 * 3. 默认角色初始化提取为内部函数，避免与 useEffect 重复
 */
export const useRoleStorage = () => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);

  // 初始化加载角色数据
  useEffect(() => {
    const loadedRoles = loadRolesFromStorage();
    setRoles(loadedRoles);
    setLoading(false);

    // 监听 storage 事件，以便在其他标签页中更改角色时同步更新
    const handleStorageChange = () => {
      const updatedRoles = loadRolesFromStorage();
      setRoles(updatedRoles);
    };

    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  // 创建新角色（稳定引用，纯函数式更新）
  const createRole = useCallback((roleData: Omit<Role, 'id'>): void => {
    const newRole: Role = {
      ...roleData,
      id: `role_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    };

    setRoles((prev) => {
      // 用纯函数处理默认角色互斥逻辑
      const withNew = applyRoleCreate(prev, newRole);
      if (newRole.isDefault) {
        const result = withNew.map((r) => (r.id === newRole.id ? r : { ...r, isDefault: false }));
        // 异步保存以避免在 render 期间同步写 storage
        queueMicrotask(() => {
          saveRolesToStorage(result);
          saveDefaultRoleId(newRole.id);
        });
        return result;
      }
      queueMicrotask(() => saveRolesToStorage(withNew));
      return withNew;
    });
  }, []);

  // 更新角色（纯函数式更新，修复多次 setState bug）
  const updateRole = useCallback((updatedRole: Role): void => {
    setRoles((prev) => {
      const result = applyRoleUpdate(prev, updatedRole);
      // 之前默认切换的二次 setRoles 已合并到一次纯函数调用
      queueMicrotask(() => {
        saveRolesToStorage(result);
        if (updatedRole.isDefault) {
          saveDefaultRoleId(updatedRole.id);
        }
      });
      return result;
    });
  }, []);

  // 删除角色（纯函数式更新）
  const deleteRole = useCallback((roleId: string): void => {
    setRoles((prev) => {
      try {
        const result = applyRoleDelete(prev, roleId);
        queueMicrotask(() => {
          saveRolesToStorage(result);
          // 如果删除的是默认角色，applyRoleDelete 已迁移默认，更新 default id
          const newDefault = result.find((r) => r.isDefault);
          if (newDefault) {
            saveDefaultRoleId(newDefault.id);
          }
        });
        return result;
      } catch (e) {
        // 拒绝删最后一个角色时保持原状态
        console.warn('Cannot delete the last role');
        return prev;
      }
    });
  }, []);

  // 获取默认角色（稳定引用）
  const getDefaultRole = useCallback((): Role | undefined => {
    const defaultRoleId = getDefaultRoleId();
    if (defaultRoleId) {
      return roles.find((role) => role.id === defaultRoleId);
    }
    // 如果没有明确的默认角色ID，则返回标记为默认的角色
    return roles.find((role) => role.isDefault);
  }, [roles]);

  // 设置默认角色（纯函数式更新，互斥）
  const setDefaultRole = useCallback((roleId: string): void => {
    setRoles((prev) => {
      const target = prev.find((r) => r.id === roleId);
      if (!target) return prev;
      const updated = { ...target, isDefault: true };
      const result = applyRoleUpdate(prev, updated);
      queueMicrotask(() => {
        saveRolesToStorage(result);
        saveDefaultRoleId(roleId);
      });
      return result;
    });
  }, []);

  return {
    roles,
    loading,
    createRole,
    updateRole,
    deleteRole,
    getDefaultRole,
    setDefaultRole,
    saveRolesToStorage,
    loadRolesFromStorage,
  };
};
