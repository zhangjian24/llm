/**
 * 模型选项常量
 * 集中管理支持的 Qwen 模型列表，UI 选择器统一引用
 */
export const MODEL_OPTIONS = [
  { value: 'qwen-turbo', label: 'Qwen-Turbo (Fast & Cheap)' },
  { value: 'qwen-plus', label: 'Qwen-Plus (Balance)' },
  { value: 'qwen-max', label: 'Qwen-Max (Most Capable)' },
] as const;

export type ModelId = (typeof MODEL_OPTIONS)[number]['value'];
