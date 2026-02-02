import React, { useState, useEffect } from 'react';
import styles from '../styles/RoleManager.module.css';

// 定义角色数据结构
export interface Role {
  id: string;
  name: string;
  description: string;
  systemPrompt: string;
  modelConfig: {
    model: string;
    temperature: number;
    top_p: number;
    max_tokens: number;
  };
  isDefault: boolean;
}

// 默认角色数据
export const DEFAULT_ROLES: Role[] = [
  {
    id: 'customer-service',
    name: '客服助手',
    description: '专业的客户服务助手，友好耐心地解答用户问题',
    systemPrompt: `# 角色定位
你是一位经验丰富、专业友好的客户服务代表，拥有5年以上客户支持经验，擅长解决各类客户问题。

# 核心任务
- 解答客户的疑问和问题
- 处理投诉和不满情绪
- 提供产品使用指导
- 记录客户需求和反馈

# 行为准则
1. 保持友好、耐心、专业的语气
2. 始终尊重客户，无论他们的情绪状态如何
3. 用积极的语言表达，避免负面措辞
4. 确保回应准确，如不确定答案则引导至人工客服
5. 提供具体可行的解决方案

# 输出格式
- 开头致意：表示问候和愿意提供帮助
- 核心解答：清晰解决问题
- 结尾确认：确认问题是否得到解决

# 能力边界
✓ 提供产品相关信息和支持
✓ 一般性咨询和故障排除

✗ 访问客户账户或个人数据
✗ 处理退款或财务事务
✗ 承诺无法兑现的服务条款

# 特殊情况处理
- 遇到技术问题：提供基本排查步骤，必要时转接技术支持
- 客户情绪激动：保持冷静，表达理解，寻求双赢解决方案
- 无法解决的问题：礼貌说明原因，提供转接人工服务的选项`,
    modelConfig: {
      model: 'qwen-turbo',
      temperature: 0.5,
      top_p: 0.8,
      max_tokens: 2048,
    },
    isDefault: true
  },
  {
    id: 'programming-tutor',
    name: '编程导师',
    description: '专业的编程指导助手，帮助解决编程问题和学习困难',
    systemPrompt: `# 角色定位
你是一位资深软件工程师和编程导师，拥有8年以上多语言开发经验，精通教学方法，善于将复杂概念简化。

# 核心任务
- 解释代码逻辑和编程概念
- 提供最佳实践建议
- 调试和修复代码问题
- 指导编程学习路径

# 行为准则
1. 详细解释代码的工作原理，不仅给出答案
2. 区分新手和有经验的开发者，调整解释深度
3. 提供可运行、经过验证的代码示例
4. 指出潜在的改进点和最佳实践
5. 鼓励提问并提供进一步学习资源

# 输出格式
- 问题分析：简述问题所在
- 解决方案：提供代码和解释
- 原理说明：解释背后的逻辑
- 扩展建议：相关的最佳实践或进阶知识

# 能力边界
✓ 提供编程指导和技术解释
✓ 代码审查和优化建议
✓ 算法和数据结构解释

✗ 执行真实代码或访问外部系统
✗ 提供商业级安全代码保证
✗ 替代正式的代码测试和审核

# 特殊情况处理
- 用户是初学者：使用简单语言，提供基础概念解释，给出简单的例子
- 用户是高级开发者：提供深入的技术细节，讨论性能和架构考虑
- 代码安全问题：强调安全性，提供安全编码实践`,
    modelConfig: {
      model: 'qwen-plus',
      temperature: 0.7,
      top_p: 0.9,
      max_tokens: 4096,
    },
    isDefault: false
  },
  {
    id: 'copywriter',
    name: '文案写手',
    description: '创意文案助手，帮助撰写各种类型的文案内容',
    systemPrompt: `# 角色定位
你是一位资深文案策划师和内容创作者，拥有6年以上品牌营销和内容创作经验，擅长不同风格的文案写作。

# 核心任务
- 撰写吸引人的广告文案
- 创作社交媒体内容
- 编写营销邮件和推广材料
- 优化现有文案的转化率

# 行为准则
1. 根据目标受众调整语言风格和语调
2. 突出产品/服务的独特卖点和价值
3. 使用强有力的行动号召(CTA)
4. 确保文案简洁有力，避免冗余
5. 融入情感元素以建立共鸣

# 输出格式
- 标题/引言：抓住注意力
- 主体内容：传达核心信息
- 行动号召：引导用户采取行动

# 能力边界
✓ 创作原创、有吸引力的文案内容
✓ 提供不同风格的文案选项
✓ 优化文案以提高转化率

✗ 代替法律审核合同或声明类文案
✗ 保证文案一定会产生特定商业结果
✗ 生成可能违反广告法规的内容

# 特殊情况处理
- 缺乏产品信息：询问关键卖点、目标受众、品牌调性
- 需要SEO优化：融入相关关键词，保持自然流畅
- 多种风格需求：提供2-3种不同风格的文案供选择
- 篇幅限制：在限定字数内最大化效果`,
    modelConfig: {
      model: 'qwen-max',
      temperature: 0.8,
      top_p: 0.9,
      max_tokens: 2048,
    },
    isDefault: false
  }
];

// 角色管理器组件
interface RoleManagerProps {
  roles: Role[];
  onSelectRole: (roleId: string) => void;
  onCreateRole: (role: Omit<Role, 'id'>) => void;
  onUpdateRole: (role: Role) => void;
  onDeleteRole: (roleId: string) => void;
  setDefaultRole: (roleId: string) => void;
  selectedRoleId: string | null;
}

const RoleManager: React.FC<RoleManagerProps> = ({
  roles,
  onSelectRole,
  onCreateRole,
  onUpdateRole,
  onDeleteRole,
  setDefaultRole,
  selectedRoleId
}) => {
  const [showForm, setShowForm] = useState(false);
  const [currentRole, setCurrentRole] = useState<Omit<Role, 'id'> | Role | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  // 设置为默认角色
  const handleSetDefault = (roleId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setDefaultRole(roleId);
  };

  // 初始化默认角色
  useEffect(() => {
    if (roles.length === 0) {
      DEFAULT_ROLES.forEach(role => {
        onCreateRole({
          name: role.name,
          description: role.description,
          systemPrompt: role.systemPrompt,
          modelConfig: { ...role.modelConfig },
          isDefault: role.isDefault
        });
      });
    }
  }, [roles, onCreateRole]);

  const handleCreateNew = () => {
    setCurrentRole({
      name: '',
      description: '',
      systemPrompt: '',
      modelConfig: {
        model: 'qwen-max',
        temperature: 0.7,
        top_p: 0.9,
        max_tokens: 2048,
      },
      isDefault: false
    });
    setIsEditing(false);
    setShowForm(true);
  };

  const handleEdit = (role: Role) => {
    setCurrentRole(role);
    setIsEditing(true);
    setShowForm(true);
  };

  const handleDelete = (roleId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm('确定要删除这个角色吗？此操作不可撤销。')) {
      onDeleteRole(roleId);
    }
  };

  const handleSave = () => {
    if (!currentRole) return;
    
    if (isEditing && 'id' in currentRole) {
      onUpdateRole(currentRole as Role);
    } else {
      onCreateRole(currentRole as Omit<Role, 'id'>);
    }
    
    setShowForm(false);
    setCurrentRole(null);
  };

  const handleCancel = () => {
    setShowForm(false);
    setCurrentRole(null);
  };

  const handleInputChange = (field: string, value: any) => {
    if (!currentRole) return;
    
    setCurrentRole(prev => {
      if (!prev) return null;
      
      // 处理嵌套的 modelConfig
      if (field.startsWith('modelConfig.')) {
        const configField = field.split('.')[1];
        return {
          ...prev,
          modelConfig: {
            ...prev.modelConfig,
            [configField]: value
          }
        };
      }
      
      return {
        ...prev,
        [field]: value
      };
    });
  };

  return (
    <div className={styles.roleManager}>
      <div className={styles.roleHeader}>
        <h3>AI角色管理</h3>
        <button onClick={handleCreateNew} className={styles.addButton}>+ 新建角色</button>
      </div>
      
      <div className={styles.roleList}>
        {roles.map(role => (
          <div 
            key={role.id} 
            className={`${styles.roleItem} ${selectedRoleId === role.id ? styles.selected : ''}`}
            onClick={() => onSelectRole(role.id)}
          >
            <div className={styles.roleInfo}>
              <h4>{role.name} {role.isDefault && <span className={styles.defaultBadge}>默认</span>}</h4>
              <p>{role.description}</p>
            </div>
            <div className={styles.roleActions}>
              {!role.isDefault && (
                <button 
                  onClick={(e) => handleSetDefault(role.id, e)} 
                  className={styles.defaultButton}
                >
                  设为默认
                </button>
              )}
              <button 
                onClick={(e) => handleEdit(role)} 
                className={styles.editButton}
              >
                编辑
              </button>
              <button 
                onClick={(e) => handleDelete(role.id, e)} 
                className={styles.deleteButton}
              >
                删除
              </button>
            </div>
          </div>
        ))}
      </div>
      
      {showForm && currentRole && (
        <div className={styles.roleFormOverlay}>
          <div className={styles.roleForm}>
            <h3>{isEditing ? '编辑角色' : '新建角色'}</h3>
            
            <div className={styles.formGroup}>
              <label>角色名称:</label>
              <input
                type="text"
                value={currentRole.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                placeholder="输入角色名称"
              />
            </div>
            
            <div className={styles.formGroup}>
              <label>角色描述:</label>
              <textarea
                value={currentRole.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="描述角色的功能和特点"
                rows={2}
              />
            </div>
            
            <div className={styles.formGroup}>
              <label>系统指令 (System Prompt):</label>
              <textarea
                value={currentRole.systemPrompt}
                onChange={(e) => handleInputChange('systemPrompt', e.target.value)}
                placeholder="定义AI助手的行为和上下文"
                rows={4}
              />
            </div>
            
            <div className={styles.formGroup}>
              <label>模型配置:</label>
              <div className={styles.modelConfig}>
                <div className={styles.configRow}>
                  <label>模型:</label>
                  <select
                    value={currentRole.modelConfig.model}
                    onChange={(e) => handleInputChange('modelConfig.model', e.target.value)}
                  >
                    <option value="qwen-turbo">Qwen-Turbo (Fast & Cheap)</option>
                    <option value="qwen-plus">Qwen-Plus (Balance)</option>
                    <option value="qwen-max">Qwen-Max (Most Capable)</option>
                  </select>
                </div>
                
                <div className={styles.configRow}>
                  <label>Temperature: {currentRole.modelConfig.temperature.toFixed(2)}</label>
                  <input
                    type="range"
                    min="0"
                    max="2"
                    step="0.01"
                    value={currentRole.modelConfig.temperature}
                    onChange={(e) => handleInputChange('modelConfig.temperature', parseFloat(e.target.value))}
                  />
                  <span>{currentRole.modelConfig.temperature.toFixed(2)}</span>
                </div>
                
                <div className={styles.configRow}>
                  <label>Top-P: {currentRole.modelConfig.top_p.toFixed(2)}</label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={currentRole.modelConfig.top_p}
                    onChange={(e) => handleInputChange('modelConfig.top_p', parseFloat(e.target.value))}
                  />
                  <span>{currentRole.modelConfig.top_p.toFixed(2)}</span>
                </div>
                
                <div className={styles.configRow}>
                  <label>Max Tokens: {currentRole.modelConfig.max_tokens}</label>
                  <input
                    type="range"
                    min="1"
                    max="8192"
                    step="1"
                    value={currentRole.modelConfig.max_tokens}
                    onChange={(e) => handleInputChange('modelConfig.max_tokens', parseInt(e.target.value))}
                  />
                  <span>{currentRole.modelConfig.max_tokens}</span>
                </div>
              </div>
            </div>
            
            <div className={styles.formGroup}>
              <label>
                <input
                  type="checkbox"
                  checked={currentRole.isDefault}
                  onChange={(e) => handleInputChange('isDefault', e.target.checked)}
                />
                设为默认角色
              </label>
            </div>
            
            <div className={styles.formActions}>
              <button onClick={handleSave} className={styles.saveButton}>保存</button>
              <button onClick={handleCancel} className={styles.cancelButton}>取消</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RoleManager;