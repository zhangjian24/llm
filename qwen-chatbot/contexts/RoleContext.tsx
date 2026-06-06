/**
 * RoleContext - 角色管理的 React Context 包装
 *
 * 直接复用 useRoleStorage Hook（已具备稳定引用 + 纯函数 reducer）。
 * 通过 Context 暴露给子树，避免逐层传递 props。
 */
import { createContext, useContext, type ReactNode } from 'react';
import { useRoleStorage } from '../components/useRoleStorage';

const RoleContext = createContext<ReturnType<typeof useRoleStorage> | null>(null);

export function RoleProvider({ children }: { children: ReactNode }) {
  const roleStorage = useRoleStorage();
  return <RoleContext.Provider value={roleStorage}>{children}</RoleContext.Provider>;
}

export function useRoleContext() {
  const ctx = useContext(RoleContext);
  if (!ctx) {
    throw new Error('useRoleContext must be used within RoleProvider');
  }
  return ctx;
}
