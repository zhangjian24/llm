// lib/langchain/index.ts
// LangChain集成层 - 提供对通义千问模型的统一访问接口
// 包含同步和流式调用的封装，以及token使用量统计功能

import { ChatOpenAI } from "@langchain/openai";
import { BaseMessage, HumanMessage, SystemMessage, AIMessage } from "@langchain/core/messages";
import { tools } from "./tools";
import { ToolMessage } from "@langchain/core/messages";
import { RunnableWithMessageHistory } from "@langchain/core/runnables";
import { JsonOutputParser } from "@langchain/core/output_parsers";
/**
 * 创建Qwen聊天模型实例
 * 使用DashScope API兼容OpenAI格式
 * 
 * @param options - 模型配置选项
 * @param options.modelName - 模型名称，默认使用环境变量中的MODEL_NAME或'qwen-max'
 * @param options.temperature - 温度参数，控制生成的随机性，默认0.7
 * @param options.topP - Top-p采样参数，默认0.9
 * @param options.maxTokens - 最大生成token数，默认2048
 * @returns 配置好的ChatOpenAI实例
 */
export const createQwenChatModel = (options?: {
  modelName?: string;
  temperature?: number;
  topP?: number;
  maxTokens?: number;
}) => {
  const {
    modelName = process.env.MODEL_NAME || 'qwen-max',
    temperature = 0.7,
    topP = 0.9,
    maxTokens = 2048
  } = options || {};

  return new ChatOpenAI({
    modelName,
    temperature,
    topP,
    maxTokens,
    configuration: {
      baseURL: process.env.OPENAI_API_BASE || 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    },
    apiKey: process.env.OPENAI_API_KEY,
  });
};

/**
 * Qwen聊天模型的配置选项接口
 */
export interface QwenChatOptions {
  /** 模型名称，如qwen-max, qwen-plus等 */
  model?: string;
  /** 生成温度，控制随机性，值越高越随机，默认0.7 */
  temperature?: number;
  /** Top-P采样参数，控制生成多样性，默认0.9 */
  topP?: number;
  /** 最大生成token数，默认2048 */
  maxTokens?: number;
}

/**
 * 令牌使用量统计接口
 * 记录API调用过程中输入、输出和总计的token数量
 */
export interface TokenUsage {
  /** 输入提示的token数量 */
  prompt_tokens: number;
  /** 生成回复的token数量 */
  completion_tokens: number;
  /** 总共使用的token数量 */
  total_tokens: number;
}

/**
 * 聊天响应接口
 * 定义API调用返回的数据结构
 */
export interface ChatResponse {
  /** AI生成的内容 */
  content: string;
  /** 令牌使用量统计（可选） */
  usage?: TokenUsage;
}

/**
 * 使用LangChain同步调用Qwen模型
 * 
 * @param messages - 消息数组，包含系统消息、用户消息和助手消息
 * @param options - 模型调用选项
 * @returns 包含内容和使用量信息的响应对象
 * @throws 调用API时可能出现的错误
 */
export const callQwenChat = async (
  messages: BaseMessage[],
  options?: QwenChatOptions
): Promise<ChatResponse> => {
  const model = createQwenChatModel({
    modelName: options?.model,
    temperature: options?.temperature,
    topP: options?.topP,
    maxTokens: options?.maxTokens,
  });

  const result = await model.invoke(messages);
  
  return {
    content: result.content as string,
    usage: result.usage_metadata
      ? {
          prompt_tokens: result.usage_metadata.input_tokens,
          completion_tokens: result.usage_metadata.output_tokens,
          total_tokens: result.usage_metadata.total_tokens,
        }
      : undefined,
  };
};

/**
 * 使用LangChain以流式方式调用Qwen模型
 * 逐块返回生成的内容，提供实时响应体验
 * 
 * @param messages - 消息数组，包含系统消息、用户消息和助手消息
 * @param options - 模型调用选项
 * @yields 包含内容片段和使用量信息的对象
 * @throws 调用API时可能出现的错误
 */
export async function* streamQwenChat(
  messages: BaseMessage[],
  options?: QwenChatOptions
) {
  const model = createQwenChatModel({
    modelName: options?.model,
    temperature: options?.temperature,
    topP: options?.topP,
    maxTokens: options?.maxTokens,
  });

  const stream = await model.stream(messages);

  for await (const chunk of stream) {
    yield {
      content: chunk.content as string,
      usage: chunk.usage_metadata
        ? {
            prompt_tokens: chunk.usage_metadata.input_tokens,
            completion_tokens: chunk.usage_metadata.output_tokens,
            total_tokens: chunk.usage_metadata.total_tokens,
          }
        : undefined,
    };
  }
}

/**
 * 使用LangChain同步调用Qwen模型并支持工具调用
 * 
 * @param messages - 消息数组，包含系统消息、用户消息和助手消息
 * @param options - 模型调用选项
 * @returns 包含内容和使用量信息的响应对象
 */
export const callQwenChatWithTools = async (
  messages: BaseMessage[],
  options?: QwenChatOptions
): Promise<ChatResponse> => {
  const model = createQwenChatModel({
    modelName: options?.model,
    temperature: options?.temperature,
    topP: options?.topP,
    maxTokens: options?.maxTokens,
  });

  // 绑定工具到模型
  const modelWithTools = model.bindTools(tools);

  const result = await modelWithTools.invoke(messages);

  // 如果模型调用了工具，我们需要处理工具调用结果
  if (result.tool_calls && result.tool_calls.length > 0) {
    // 为每个工具调用执行相应的工具
    const toolMessages = [];
    for (const toolCall of result.tool_calls) {
      const { name, args, id } = toolCall;
      
      // 查找对应的工具
      const tool = tools.find(t => t.name === name);
      if (tool) {
        try {
          const toolResult = await tool.invoke(args);
          const content = typeof toolResult === 'string' ? toolResult : JSON.stringify(toolResult);
          toolMessages.push(new ToolMessage({
            content: content || '工具调用未返回结果',
            tool_call_id: id || '',
          }));
        } catch (error) {
          const errorMessage = `工具调用失败: ${(error as Error)?.message || '未知错误'}`;
          toolMessages.push(new ToolMessage({
            content: errorMessage,
            tool_call_id: id || '',
          }));
        }
      }
    }

    // 使用工具结果再次调用模型以获得最终响应
    const finalResult = await model.invoke([...messages, result, ...toolMessages]);
    
    return {
      content: finalResult.content as string,
      usage: finalResult.usage_metadata
        ? {
            prompt_tokens: finalResult.usage_metadata.input_tokens,
            completion_tokens: finalResult.usage_metadata.output_tokens,
            total_tokens: finalResult.usage_metadata.total_tokens,
          }
        : undefined,
    };
  }

  return {
    content: result.content as string,
    usage: result.usage_metadata
      ? {
          prompt_tokens: result.usage_metadata.input_tokens,
          completion_tokens: result.usage_metadata.output_tokens,
          total_tokens: result.usage_metadata.total_tokens,
        }
      : undefined,
  };
};

/**
 * 使用LangChain以流式方式调用Qwen模型并支持工具调用
 * 
 * @param messages - 消息数组，包含系统消息、用户消息和助手消息
 * @param options - 模型调用选项
 * @yields 包含内容片段和使用量信息的对象
 */
export async function* streamQwenChatWithTools(
  messages: BaseMessage[],
  options?: QwenChatOptions
) {
  const model = createQwenChatModel({
    modelName: options?.model,
    temperature: options?.temperature,
    topP: options?.topP,
    maxTokens: options?.maxTokens,
  });

  // 绑定工具到模型
  const modelWithTools = model.bindTools(tools);

  const stream = await modelWithTools.stream(messages);

  for await (const chunk of stream) {
    // 如果是工具调用，处理工具调用
    if (chunk.tool_calls && chunk.tool_calls.length > 0) {
      // 收集所有工具调用结果
      const toolMessages = [];
      for (const toolCall of chunk.tool_calls) {
        const { name, args, id } = toolCall;
        
        // 查找对应的工具
        const tool = tools.find(t => t.name === name);
        if (tool) {
          try {
            const toolResult = await tool.invoke(args);
            const content = typeof toolResult === 'string' ? toolResult : JSON.stringify(toolResult);
            toolMessages.push(new ToolMessage({
              content: content || '工具调用未返回结果',
              tool_call_id: id || '',
            }));
          } catch (error) {
            const errorMessage = `工具调用失败: ${(error as Error)?.message || '未知错误'}`;
            toolMessages.push(new ToolMessage({
              content: errorMessage,
              tool_call_id: id || '',
            }));
          }
        }
      }

      // 使用工具结果再次调用模型以获得最终响应
      const finalResult = await model.invoke([...messages, chunk, ...toolMessages]);
      
      yield {
        content: finalResult.content as string,
        usage: finalResult.usage_metadata
          ? {
              prompt_tokens: finalResult.usage_metadata.input_tokens,
              completion_tokens: finalResult.usage_metadata.output_tokens,
              total_tokens: finalResult.usage_metadata.total_tokens,
            }
          : undefined,
      };
    } else {
      yield {
        content: chunk.content as string,
        usage: chunk.usage_metadata
          ? {
              prompt_tokens: chunk.usage_metadata.input_tokens,
              completion_tokens: chunk.usage_metadata.output_tokens,
              total_tokens: chunk.usage_metadata.total_tokens,
            }
          : undefined,
      };
    }
  }
}