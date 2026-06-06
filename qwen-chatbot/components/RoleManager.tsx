import React, { useState, useEffect } from 'react';
import type { Role } from '../types';
import { MODEL_OPTIONS } from '../lib/model-options';

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
    isDefault: true,
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
    isDefault: false,
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
    isDefault: false,
  },
  {
    id: 'data-analyst',
    name: '数据分析师',
    description: '专业的数据分析助手，擅长解读数据并提供洞察',
    systemPrompt: `# 角色定位
你是一位资深数据分析师，拥有统计学、数据可视化和商业智能背景，擅长从数据中提炼可执行的洞察。

# 核心任务
- 解读统计指标和趋势
- 协助设计实验和 A/B 测试
- 提供数据可视化建议
- 解释模型输出和不确定性

# 行为准则
1. 用通俗语言解释复杂统计概念
2. 强调数据质量与样本偏差
3. 避免过度推断，明确相关性不等于因果
4. 提供可重复的分析步骤

# 输出格式
- 关键发现：列点
- 数据支持：图表或表格描述
- 行动建议：可执行下一步

# 能力边界
✓ 解释常见统计方法和图表
✓ 提供抽样、显著性检验建议
✗ 替代正式统计建模或合规审计
✗ 处理个人隐私或敏感数据`,
    modelConfig: {
      model: 'qwen-plus',
      temperature: 0.3,
      top_p: 0.8,
      max_tokens: 2048,
    },
    isDefault: false,
  },
  {
    id: 'language-tutor',
    name: '英语私教',
    description: '耐心的英语教师，提供语法、词汇、口语全方位指导',
    systemPrompt: `# 角色定位
你是一位经验丰富的英语教师，擅长根据学习者水平调整教学节奏，兼顾语法准确性和表达流畅性。

# 核心任务
- 解释语法点和用法差异
- 改写并润色英文句子
- 设计词汇和口语练习
- 提供文化背景与表达习惯

# 行为准则
1. 用学习者母语（中文）解释难点，但例句保持英文
2. 鼓励试错并给出正向反馈
3. 标注常用搭配和近义词差异
4. 保持简洁、对话式语调

# 输出格式
- 例句：英文 + 中文翻译
- 讲解：核心语法 / 词汇要点
- 练习：1-2 个跟读或造句任务

# 能力边界
✓ 通用英语 / 商务英语指导
✓ 雅思、托福备考建议
✗ 替代正式语言课程或考试报名`,
    modelConfig: {
      model: 'qwen-turbo',
      temperature: 0.6,
      top_p: 0.9,
      max_tokens: 2048,
    },
    isDefault: false,
  },
  {
    id: 'tech-writer',
    name: '技术文档作者',
    description: '严谨的技术写作助手，擅长撰写 API 文档、设计说明与用户手册',
    systemPrompt: `# 角色定位
你是一位资深技术作者，专注于把复杂技术内容写成清晰、可检索、可测试的文档。

# 核心任务
- 撰写 API 参考、教程、概念文档
- 整理需求到设计说明
- 校对现有文档的准确性与一致性
- 生成可复用的 Markdown / OpenAPI 片段

# 行为准则
1. 简洁、明确、无歧义
2. 主动标注前置条件和边界情况
3. 关键步骤提供可执行示例
4. 避免营销化措辞

# 输出格式
- 概述：一句话目标
- 前置条件：依赖、环境
- 步骤：编号列表
- 示例：代码块 + 期望输出
- 排错：常见问题与解法

# 能力边界
✓ 通用技术写作（REST、SDK、CLI）
✓ Markdown / reStructuredText 结构
✗ 替代专业法律或安全合规审查`,
    modelConfig: {
      model: 'qwen-max',
      temperature: 0.4,
      top_p: 0.8,
      max_tokens: 4096,
    },
    isDefault: false,
  },
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
  selectedRoleId,
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
      DEFAULT_ROLES.forEach((role) => {
        onCreateRole({
          name: role.name,
          description: role.description,
          systemPrompt: role.systemPrompt,
          modelConfig: { ...role.modelConfig },
          isDefault: role.isDefault,
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
      isDefault: false,
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

  const handleInputChange = (field: string, value: string | number | boolean) => {
    if (!currentRole) return;

    setCurrentRole((prev) => {
      if (!prev) return null;

      // 处理嵌套的 modelConfig
      if (field.startsWith('modelConfig.')) {
        const configField = field.split('.')[1];
        return {
          ...prev,
          modelConfig: {
            ...prev.modelConfig,
            [configField]: value,
          },
        };
      }

      return {
        ...prev,
        [field]: value,
      };
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-bold text-gray-800">AI角色管理</h3>
        <button
          onClick={handleCreateNew}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          + 新建角色
        </button>
      </div>

      <div className="grid gap-4">
        {roles.map((role) => (
          <div
            key={role.id}
            className={`bg-white rounded-lg border p-4 cursor-pointer transition-all hover:shadow-md ${selectedRoleId === role.id ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200'}`}
            onClick={() => onSelectRole(role.id)}
          >
            <div className="flex justify-between items-start mb-3">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="font-semibold text-gray-800">{role.name}</h4>
                  {role.isDefault && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      默认
                    </span>
                  )}
                </div>
                <p className="text-gray-600 text-sm">{role.description}</p>
              </div>
              <div className="flex gap-2">
                {!role.isDefault && (
                  <button
                    onClick={(e) => handleSetDefault(role.id, e)}
                    className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                  >
                    设为默认
                  </button>
                )}
                <button
                  onClick={() => handleEdit(role)}
                  className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
                >
                  编辑
                </button>
                <button
                  onClick={(e) => handleDelete(role.id, e)}
                  className="px-3 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
                >
                  删除
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {showForm && currentRole && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={handleCancel}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="role-form-title"
            className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6"
            onClick={(e) => e.stopPropagation()}
            onKeyDown={(e) => {
              if (e.key === 'Escape') {
                e.preventDefault();
                handleCancel();
              }
            }}
          >
            <h3
              id="role-form-title"
              className="text-xl font-bold text-gray-800 mb-6 border-b pb-3"
            >
              {isEditing ? '编辑角色' : '新建角色'}
            </h3>

            <div className="space-y-4 mb-6">
              <div>
                <label htmlFor="role-form-name" className="block text-sm font-medium text-gray-700 mb-2">角色名称:</label>
                <input
                  id="role-form-name"
                  type="text"
                  value={currentRole.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  placeholder="输入角色名称"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label htmlFor="role-form-description" className="block text-sm font-medium text-gray-700 mb-2">角色描述:</label>
                <textarea
                  id="role-form-description"
                  value={currentRole.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="描述角色的功能和特点"
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label htmlFor="role-form-system-prompt" className="block text-sm font-medium text-gray-700 mb-2">
                  系统指令 (System Prompt):
                </label>
                <textarea
                  id="role-form-system-prompt"
                  value={currentRole.systemPrompt}
                  onChange={(e) => handleInputChange('systemPrompt', e.target.value)}
                  placeholder="定义AI助手的行为和上下文"
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">模型配置:</label>
                <div className="space-y-4 bg-gray-50 p-4 rounded-lg">
                  <div>
                    <label htmlFor="role-form-model" className="block text-sm font-medium text-gray-700 mb-2">模型:</label>
                    <select
                      id="role-form-model"
                      value={currentRole.modelConfig.model}
                      onChange={(e) => handleInputChange('modelConfig.model', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      {MODEL_OPTIONS.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <label htmlFor="role-form-temperature" className="text-sm font-medium text-gray-700">
                        Temperature: {currentRole.modelConfig.temperature.toFixed(2)}
                      </label>
                      <span className="text-sm font-medium text-gray-800 bg-gray-100 px-2 py-1 rounded">
                        {currentRole.modelConfig.temperature.toFixed(2)}
                      </span>
                    </div>
                    <input
                      id="role-form-temperature"
                      type="range"
                      min="0"
                      max="2"
                      step="0.01"
                      value={currentRole.modelConfig.temperature}
                      onChange={(e) =>
                        handleInputChange('modelConfig.temperature', parseFloat(e.target.value))
                      }
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>

                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <label htmlFor="role-form-top-p" className="text-sm font-medium text-gray-700">
                        Top-P: {currentRole.modelConfig.top_p.toFixed(2)}
                      </label>
                      <span className="text-sm font-medium text-gray-800 bg-gray-100 px-2 py-1 rounded">
                        {currentRole.modelConfig.top_p.toFixed(2)}
                      </span>
                    </div>
                    <input
                      id="role-form-top-p"
                      type="range"
                      min="0"
                      max="1"
                      step="0.01"
                      value={currentRole.modelConfig.top_p}
                      onChange={(e) =>
                        handleInputChange('modelConfig.top_p', parseFloat(e.target.value))
                      }
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>

                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <label htmlFor="role-form-max-tokens" className="text-sm font-medium text-gray-700">
                        Max Tokens: {currentRole.modelConfig.max_tokens}
                      </label>
                      <span className="text-sm font-medium text-gray-800 bg-gray-100 px-2 py-1 rounded">
                        {currentRole.modelConfig.max_tokens}
                      </span>
                    </div>
                    <input
                      id="role-form-max-tokens"
                      type="range"
                      min="1"
                      max="8192"
                      step="1"
                      value={currentRole.modelConfig.max_tokens}
                      onChange={(e) =>
                        handleInputChange('modelConfig.max_tokens', parseInt(e.target.value))
                      }
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>
                </div>
              </div>

              <div className="flex items-center">
                <input
                  id="role-form-is-default"
                  type="checkbox"
                  checked={currentRole.isDefault}
                  onChange={(e) => handleInputChange('isDefault', e.target.checked)}
                  className="mr-2 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="role-form-is-default" className="text-sm text-gray-700">设为默认角色</label>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t">
              <button
                onClick={handleCancel}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleSave}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                保存
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RoleManager;
