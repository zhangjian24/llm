// 定义对话历史记录的类型
export interface ConversationHistory {
  id: number;
  timestamp: string; // 使用字符串格式存储时间戳
  input: string;
  output: string;
  model: string;
  params: {
    temperature: number;
    top_p: number;
    max_tokens: number;
  };
  tokenUsage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  evaluation: string;
}

// 定义消息类型
export interface Message {
  role: string;
  content: string;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}