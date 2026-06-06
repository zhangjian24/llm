/**
 * 集中类型定义
 * 所有跨模块共享的类型在此声明；组件私有 props 类型保留在组件文件内。
 */

// ============ 角色（Role）============

/** 角色的模型配置 */
export interface ModelConfig {
  model: string;
  temperature: number;
  /** Top-P 采样参数 */
  top_p: number;
  /** 最大生成 token 数 */
  max_tokens: number;
}

/** AI 角色 */
export interface Role {
  id: string;
  name: string;
  description: string;
  systemPrompt: string;
  modelConfig: ModelConfig;
  isDefault: boolean;
}

// ============ 对话消息（Message）============

/** 单条对话消息 */
export interface Message {
  /** 可选唯一 ID（用于 React key 稳定 + React.memo 优化） */
  id?: string;
  role: string;
  content: string;
  usage?: TokenUsage;
}

// ============ 对话历史（ConversationHistory）============

/** 历史记录的模型参数快照（与 ModelConfig 解耦，避免 UI 配置变更污染历史） */
export interface ConversationHistoryParams {
  temperature: number;
  top_p: number;
  max_tokens: number;
}

/** 对话历史记录 */
export interface ConversationHistory {
  id: number;
  /** ISO 时间戳字符串 */
  timestamp: string;
  input: string;
  output: string;
  model: string;
  params: ConversationHistoryParams;
  tokenUsage?: TokenUsage;
  /** 用户评价：'good' | 'bad' | '' */
  evaluation: string;
}

// ============ LLM 集成（Qwen / LangChain）============

/** Qwen 聊天模型的配置选项 */
export interface QwenChatOptions {
  model?: string;
  temperature?: number;
  topP?: number;
  maxTokens?: number;
  apiKey?: string;
}

/** 令牌使用量统计 */
export interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

/** 聊天响应 */
export interface ChatResponse {
  content: string;
  usage?: TokenUsage;
}
