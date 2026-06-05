import type { NextApiRequest, NextApiResponse } from 'next';
import { ChatOpenAI } from '@langchain/openai';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ success: false, error: 'Method not allowed' });
  }

  const { apiKey } = req.body;

  if (!apiKey) {
    return res.status(400).json({ success: false, error: 'API Key is required' });
  }

  try {
    const model = new ChatOpenAI({
      modelName: 'qwen-max',
      temperature: 0,
      maxTokens: 1,
      configuration: {
        baseURL: process.env.OPENAI_API_BASE || 'https://dashscope.aliyuncs.com/compatible-mode/v1',
      },
      apiKey,
    });

    await model.invoke([{ role: 'user', content: 'ping' }]);

    return res.status(200).json({ success: true });
  } catch (error: any) {
    const message = error.status === 401
      ? 'API Key 无效，请检查后重试'
      : error.status === 429
        ? '请求频率超限，请稍后重试'
        : error.message || '连接失败';

    // 按 HTTP 语义返回正确的状态码（错误时 200 是不对的）
    const httpStatus = error.status === 401
      ? 401
      : error.status === 429
        ? 429
        : 400;

    return res.status(httpStatus).json({ success: false, error: message });
  }
}
