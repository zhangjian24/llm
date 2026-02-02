import React from 'react';
import { Role } from './RoleManager';
import styles from '../styles/RoleSelector.module.css';

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
    <div className={styles.roleSelector}>
      <label htmlFor="roleSelect">AI角色:</label>
      <select
        id="roleSelect"
        value={selectedRoleId || ''}
        onChange={(e) => onSelectRole(e.target.value)}
        className={styles.roleSelect}
        disabled={disabled}
      >
        <option value="">请选择角色...</option>
        {roles.map(role => (
          <option key={role.id} value={role.id}>
            {role.name} {role.isDefault ? '(默认)' : ''}
          </option>
        ))}
      </select>
      
      {selectedRole && (
        <div className={styles.roleInfo}>
          <h4>{selectedRole.name} {selectedRole.isDefault && <span className={styles.defaultBadge}>默认</span>}</h4>
          <p>{selectedRole.description}</p>
          <div className={styles.roleDetails}>
            <div className={styles.detailItem}>
              <strong>模型:</strong> {selectedRole.modelConfig.model}
            </div>
            <div className={styles.detailItem}>
              <strong>温度:</strong> {selectedRole.modelConfig.temperature.toFixed(2)}
            </div>
            <div className={styles.detailItem}>
              <strong>Top-P:</strong> {selectedRole.modelConfig.top_p.toFixed(2)}
            </div>
            <div className={styles.detailItem}>
              <strong>最大Tokens:</strong> {selectedRole.modelConfig.max_tokens}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RoleSelector;