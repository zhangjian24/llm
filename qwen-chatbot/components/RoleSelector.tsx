import React from 'react';
import { Role } from './RoleManager';

interface RoleSelectorProps {
  roles: Role[];
  selectedRoleId: string | null;
  onSelectRole: (roleId: string) => void;
  disabled?: boolean;
}

const RoleSelector: React.FC<RoleSelectorProps> = ({ 
  roles, 
  selectedRoleId, 
  onSelectRole,
  disabled = false
}) => {
  const selectedRole = roles.find(role => role.id === selectedRoleId);

  return (
    <div className="space-y-4">
      <div>
        <label htmlFor="roleSelect" className="block text-sm font-medium text-gray-700 mb-2">AI角色:</label>
        <select
          id="roleSelect"
          value={selectedRoleId || ''}
          onChange={(e) => onSelectRole(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          disabled={disabled}
        >
          <option value="">请选择角色...</option>
          {roles.map(role => (
            <option key={role.id} value={role.id}>
              {role.name} {role.isDefault ? '(默认)' : ''}
            </option>
          ))}
        </select>
      </div>
      
      {selectedRole && (
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            <h4 className="font-semibold text-gray-800">{selectedRole.name}</h4>
            {selectedRole.isDefault && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                默认
              </span>
            )}
          </div>
          <p className="text-gray-600 text-sm mb-3">{selectedRole.description}</p>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="flex justify-between">
              <strong className="text-gray-700">模型:</strong>
              <span className="text-gray-600">{selectedRole.modelConfig.model}</span>
            </div>
            <div className="flex justify-between">
              <strong className="text-gray-700">温度:</strong>
              <span className="text-gray-600">{selectedRole.modelConfig.temperature.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <strong className="text-gray-700">Top-P:</strong>
              <span className="text-gray-600">{selectedRole.modelConfig.top_p.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <strong className="text-gray-700">最大Tokens:</strong>
              <span className="text-gray-600">{selectedRole.modelConfig.max_tokens}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RoleSelector;