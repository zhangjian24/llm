// Next.js API路由 - 通义千问模型调用接口
// 提供流式和非流式两种响应模式，支持token使用量统计

import type { NextApiRequest, NextApiResponse } from 'next';
import { HumanMessage, SystemMessage, AIMessage } from '@langchain/core/messages';
import { callQwenChat, streamQwenChat, callQwenChatWithTools, streamQwenChatWithTools, QwenChatOptions } from '../../lib/langchain';

/**
 * 通义千问API路由处理函数
 * 支持流式和非流式响应，提供token使用量统计
 * 
 * @param req - Next.js API请求对象
 * @param res - Next.js API响应对象
 * @returns API响应结果
 */
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // 仅接受POST请求
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // 解构请求体中的参数
  const { 
    messages,           // 消息数组，包含对话历史
    stream = false,     // 是否启用流式响应
    model,              // 模型名称
    temperature = 0.7,  // 生成温度
    top_p = 0.9,      // Top-p采样参数
    max_tokens = 2048   // 最大生成token数
  } = req.body;

  // 验证messages参数是否存在且为数组
  if (!messages || !Array.isArray(messages)) {
    return res.status(400).json({ error: 'Messages are required and must be an array' });
  }

  try {
    // 将消息数组转换为LangChain兼容的格式
    // 根据消息角色创建相应的LangChain消息对象
    const langchainMessages = messages.map((msg: any) => {
      if (msg.role === 'system') {
        // 系统消息 - 用于设定助手的行为和上下文
        return new SystemMessage(msg.content);
      } else if (msg.role === 'user') {
        // 用户消息 - 包含用户的输入
        return new HumanMessage(msg.content);
      } else if (msg.role === 'assistant') {
        // 助手消息 - 包含AI助手的回复
        return new AIMessage(msg.content);
      } else {
        // 默认为用户消息，保证类型安全
        return new HumanMessage(msg.content);
      }
    });

    // 构建模型调用选项
    // 使用传入的参数或环境变量中的默认值
    const options = {
      model: model || process.env.MODEL_NAME || 'qwen-max',  // 模型名称
      temperature,                                        // 生成温度
      topP: top_p,                                       // Top-p采样参数
      maxTokens: max_tokens,                             // 最大生成token数
    };

    // 检查是否需要使用工具调用
    const needsTools = messages.some((msg: any) => 
      msg.content && 
      (typeof msg.content === 'string') && 
      (msg.content.toLowerCase().includes('天气') || 
       msg.content.toLowerCase().includes('weather'))
    );
    
    // 根据stream参数决定使用流式或非流式响应
    if (stream) {
      try {
        // 设置SSE (Server-Sent Events)响应头
        // 允许客户端建立长连接以接收实时数据流
        res.writeHead(200, {
          'Content-Type': 'text/event-stream',  // SSE内容类型
          'Cache-Control': 'no-cache',         // 禁用缓存
          'Connection': 'keep-alive',         // 保持连接
          'Access-Control-Allow-Origin': '*',  // 允许跨域请求
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',  // 允许的HTTP方法
          'Access-Control-Allow-Headers': 'Content-Type',        // 允许的请求头
        });

        // 使用LangChain进行流式处理
        // 选择是否使用工具调用的流式处理函数
        const streamResult = needsTools 
          ? streamQwenChatWithTools(langchainMessages, options)
          : streamQwenChat(langchainMessages, options);
        
        // 遍历流式结果并逐块发送给客户端
        for await (const chunk of streamResult) {
          if (chunk.content) {
            // 发送内容块
            const data = `data: ${JSON.stringify({ content: chunk.content })}\n\n`;
            res.write(data);
          }
          
          if (chunk.usage) {
            // 发送token使用量信息
            const tokenData = {
              usage: {
                prompt_tokens: chunk.usage.prompt_tokens,      // 输入token数
                completion_tokens: chunk.usage.completion_tokens, // 输出token数
                total_tokens: chunk.usage.total_tokens,           // 总token数
              }
            };
            const data = `data: ${JSON.stringify(tokenData)}\n\n`;
            res.write(data);
          }
        }
        
        // 发送流结束信号
        res.write('data: [DONE]\n\n');
        res.end();
        return;
      } catch (error: any) {
        // 记录错误并发送错误信息给客户端
        console.error('Stream processing error:', error);
        const errorMessage = `data: ${JSON.stringify({ error: error.message || 'AI service error' })}\n\n`;
        res.write(errorMessage);
        res.end();
        return;
      }
    } else {
      // 非流式响应 - 等待完整结果后一次性返回
      const result = needsTools
        ? await callQwenChatWithTools(langchainMessages, options)
        : await callQwenChat(langchainMessages, options);
      
      // 返回JSON格式的响应
      res.status(200).json({ 
        content: result.content,  // AI生成的内容
        usage: result.usage       // token使用量统计
      });
    }
  } catch (error: any) {
    // 记录错误信息
    console.error('Error calling Qwen API with LangChain:', error);
    
    // 初始化错误信息和状态码
    let errorMessage = 'An error occurred while calling the API';
    let statusCode = 500;
    
    // 根据错误状态码设置具体的错误信息
    if (error.status === 401) {
      // 认证失败
      errorMessage = 'Authentication failed. Please check your API key.';
      statusCode = 401;
    } else if (error.status === 403) {
      // 访问被拒绝
      errorMessage = 'Access forbidden. Please check your API permissions.';
      statusCode = 403;
    } else if (error.status === 429) {
      // 请求频率超限
      errorMessage = 'Rate limit exceeded. Please try again later.';
      statusCode = 429;
    } else if (error.status === 404 && error.message.includes('model')) {
      // 模型未找到
      errorMessage = 'Model not found or access denied. Please check the model name and your API permissions. Try using "qwen-max" instead of "qwen-max-0102".';
      statusCode = 404;
    } else if (error.message) {
      // 其他错误
      errorMessage = error.message;
    }
    
    // 返回错误响应
    res.status(statusCode).json({ 
      error: errorMessage,  // 错误信息
      // 在开发环境中返回详细的错误信息
      details: process.env.NODE_ENV === 'development' ? error.toString() : undefined
    });
  }
}