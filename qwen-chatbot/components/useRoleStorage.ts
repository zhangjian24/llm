import { useState, useEffect } from 'react';
import { Role, DEFAULT_ROLES } from './RoleManager';

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

// 自定义 Hook 用于管理角色状态和持久化
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

  // 创建新角色
  const createRole = (roleData: Omit<Role, 'id'>): void => {
    const newRole: Role = {
      ...roleData,
      id: `role_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    };
    
    // 如果新角色被设为默认，则取消其他角色的默认状态
    if (newRole.isDefault) {
      const updatedRoles = roles.map(role => ({ ...role, isDefault: false }));
      const rolesWithNew = [...updatedRoles, newRole];
      setRoles(rolesWithNew);
      saveRolesToStorage(rolesWithNew);
      saveDefaultRoleId(newRole.id);
    } else {
      setRoles([...roles, newRole]);
      saveRolesToStorage([...roles, newRole]);
    }
  };

  // 更新角色
  const updateRole = (updatedRole: Role): void => {
    const updatedRoles = roles.map(role => 
      role.id === updatedRole.id ? updatedRole : role
    );
    
    // 如果更新的角色被设为默认，则取消其他角色的默认状态
    if (updatedRole.isDefault) {
      const rolesWithDefaultUpdated = updatedRoles.map(role => ({
        ...role,
        isDefault: role.id === updatedRole.id
      }));
      setRoles(rolesWithDefaultUpdated);
      saveRolesToStorage(rolesWithDefaultUpdated);
      saveDefaultRoleId(updatedRole.id);
    } else {
      setRoles(updatedRoles);
      saveRolesToStorage(updatedRoles);
      
      // 如果当前更新的角色是默认角色且被取消默认状态，则需要设置新的默认角色
      if (roles.find(r => r.id === updatedRole.id)?.isDefault) {
        const rolesWithoutDefault = updatedRoles.map(role => 
          role.id === updatedRole.id ? { ...role, isDefault: false } : role
        );
        setRoles(rolesWithoutDefault);
        saveRolesToStorage(rolesWithoutDefault);
        
        // 如果没有其他默认角色，则设置第一个角色为默认（如果存在）
        if (updatedRoles.length > 0) {
          const firstNonUpdatedRole = updatedRoles.find(r => r.id !== updatedRole.id);
          if (!firstNonUpdatedRole || !updatedRoles.some(r => r.isDefault)) {
            saveDefaultRoleId(null);
          }
        } else {
          saveDefaultRoleId(null);
        }
      }
    }
  };

  // 删除角色
  const deleteRole = (roleId: string): void => {
    if (roles.length <= 1) {
      console.warn('Cannot delete the last role');
      return;
    }

    const roleToDelete = roles.find(role => role.id === roleId);
    if (!roleToDelete) return;

    const updatedRoles = roles.filter(role => role.id !== roleId);
    
    // 如果删除的是默认角色，则需要设置新默认角色
    if (roleToDelete.isDefault && updatedRoles.length > 0) {
      // 设置第一个角色为默认角色
      const rolesWithNewDefault = updatedRoles.map((role, index) => ({
        ...role,
        isDefault: index === 0
      }));
      setRoles(rolesWithNewDefault);
      saveRolesToStorage(rolesWithNewDefault);
      saveDefaultRoleId(rolesWithNewDefault[0].id);
    } else {
      setRoles(updatedRoles);
      saveRolesToStorage(updatedRoles);
      
      // 如果删除的角色不是默认角色但当前没有默认角色，则设置第一个角色为默认
      if (!roles.some(r => r.isDefault) && updatedRoles.length > 0) {
        const rolesWithDefault = updatedRoles.map((role, index) => ({
          ...role,
          isDefault: index === 0
        }));
        setRoles(rolesWithDefault);
        saveRolesToStorage(rolesWithDefault);
        saveDefaultRoleId(rolesWithDefault[0].id);
      }
    }
  };

  // 获取默认角色
  const getDefaultRole = (): Role | undefined => {
    const defaultRoleId = getDefaultRoleId();
    if (defaultRoleId) {
      return roles.find(role => role.id === defaultRoleId);
    }
    // 如果没有明确的默认角色ID，则返回标记为默认的角色
    return roles.find(role => role.isDefault);
  };

  // 设置默认角色
  const setDefaultRole = (roleId: string): void => {
    const roleToSetAsDefault = roles.find(role => role.id === roleId);
    if (!roleToSetAsDefault) return;

    const updatedRoles = roles.map(role => ({
      ...role,
      isDefault: role.id === roleId
    }));

    setRoles(updatedRoles);
    saveRolesToStorage(updatedRoles);
    saveDefaultRoleId(roleId);
  };

  return {
    roles,
    loading,
    createRole,
    updateRole,
    deleteRole,
    getDefaultRole,
    setDefaultRole,
    saveRolesToStorage,
    loadRolesFromStorage
  };
};