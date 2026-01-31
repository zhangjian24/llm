import type { NextApiRequest, NextApiResponse } from 'next';
import OpenAI from 'openai';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { messages, stream = false } = req.body;

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
      // 流式响应
      const stream = await client.chat.completions.create({
        model: process.env.MODEL_NAME || 'qwen-max',
        messages,
        stream: true,
      });

      // 设置 SSE 响应头
      res.setHeader('Content-Type', 'text/event-stream');
      res.setHeader('Cache-Control', 'no-cache');
      res.setHeader('Connection', 'keep-alive');
      res.setHeader('Transfer-Encoding', 'chunked');

      for await (const chunk of stream) {
        const content = chunk.choices[0]?.delta?.content;
        if (content) {
          res.write(`data: ${JSON.stringify({ content })}\n\n`);
        }
      }

      // 发送结束信号
      res.write('data: [DONE]\n\n');
      res.end();
    } else {
      // 非流式响应
      const response = await client.chat.completions.create({
        model: process.env.MODEL_NAME || 'qwen-max',
        messages,
      });

      const content = response.choices[0]?.message?.content || '';
      res.status(200).json({ content });
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
    } else if (error.message) {
      errorMessage = error.message;
    }

    res.status(statusCode).json({ 
      error: errorMessage,
      details: process.env.NODE_ENV === 'development' ? error.toString() : undefined
    });
  }
}