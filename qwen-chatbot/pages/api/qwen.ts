import type { NextApiRequest, NextApiResponse } from 'next';
import OpenAI from 'openai';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { messages, stream = false, model, temperature = 0.7, top_p = 0.9, max_tokens = 2048 } = req.body;

  // 验证必需字段
  if (!messages || !Array.isArray(messages)) {
    return res.status(400).json({ error: 'Messages are required and must be an array' });
  }

  try {
    // 创建 OpenAI 兼容的客户端，适配通义千问
    const client = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY || '',
      baseURL: process.env.OPENAI_API_BASE || 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    });

    if (stream) {
      // 使用 TransformStream 实现流式响应
      const encoder = new TextEncoder();
      const stream = new TransformStream();
      const writer = stream.writable.getWriter();

      // 异步处理函数
      (async () => {
        try {
          // 通义千问API支持system message，直接使用原始消息
          const response = await client.chat.completions.create({
            model: model || process.env.MODEL_NAME || 'qwen-max',
            messages,
            stream: true,
            temperature,
            top_p,
            max_tokens,
            stream_options: { include_usage: true }, // 包含使用量信息
          });

          // 逐块发送数据
          for await (const chunk of response) {
            const content = chunk.choices[0]?.delta?.content;
            
            // 如果有内容，发送内容数据
            if (content) {
              const data = `data: ${JSON.stringify({ content })}\n\n`;
              await writer.write(encoder.encode(data));
            }
            
            // 如果有usage信息，发送token使用数据
            if (chunk.usage) {
              const tokenData = {
                usage: {
                  prompt_tokens: chunk.usage.prompt_tokens,
                  completion_tokens: chunk.usage.completion_tokens,
                  total_tokens: chunk.usage.total_tokens,
                }
              };
              const data = `data: ${JSON.stringify(tokenData)}\n\n`;
              await writer.write(encoder.encode(data));
            }
          }
          
          // 发送结束信号
          await writer.write(encoder.encode('data: [DONE]\n\n'));
        } catch (error: any) {
          // 发送错误信息
          await writer.write(
            encoder.encode(`data: ${JSON.stringify({ error: error.message || 'AI service error' })}\n\n`)
          );
        } finally {
          await writer.close();
        }
      })();

      // 返回 SSE 响应
      res.setHeader('Content-Type', 'text/event-stream');
      res.setHeader('Cache-Control', 'no-cache');
      res.setHeader('Connection', 'keep-alive');
      return new Response(stream.readable, {
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
      });
    } else {
      // 非流式响应
      // 通义千问API支持system message，直接使用原始消息
      const response = await client.chat.completions.create({
        model: model || process.env.MODEL_NAME || 'qwen-max',
        messages,
        temperature,
        top_p,
        max_tokens,
      });

      const content = response.choices[0]?.message?.content || '';
      const usage = response.usage;
      
      res.status(200).json({ 
        content, 
        usage: usage ? {
          prompt_tokens: usage.prompt_tokens,
          completion_tokens: usage.completion_tokens,
          total_tokens: usage.total_tokens,
        } : undefined
      });
    }
  } catch (error: any) {
    console.error('Error calling Qwen API:', error);
    
    let errorMessage = 'An error occurred while calling the API';
    let statusCode = 500;
    
    if (error.status === 401) {
      errorMessage = 'Authentication failed. Please check your API key.';
      statusCode = 401;
    } else if (error.status === 403) {
      errorMessage = 'Access forbidden. Please check your API permissions.';
      statusCode = 403;
    } else if (error.status === 429) {
      errorMessage = 'Rate limit exceeded. Please try again later.';
      statusCode = 429;
    } else if (error.status === 404 && error.message.includes('model')) {
      errorMessage = 'Model not found or access denied. Please check the model name and your API permissions. Try using "qwen-max" instead of "qwen-max-0102".';
      statusCode = 404;
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    res.status(statusCode).json({ 
      error: errorMessage,
      details: process.env.NODE_ENV === 'development' ? error.toString() : undefined
    });
  }
}