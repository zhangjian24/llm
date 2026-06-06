/**
 * lib/langchain 单元测试
 *
 * 覆盖关键纯函数：
 * - toStringContent：string 与 complex content 的转换
 * - createQwenChatModel：默认值与 overrides
 * - callQwenChat / streamQwenChat：content + usage 映射
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { HumanMessage, SystemMessage } from '@langchain/core/messages';
import { ChatOpenAI } from '@langchain/openai';

// 关键：先 mock @langchain/openai 避免拉真实 ChatOpenAI
vi.mock('@langchain/openai', () => ({
  ChatOpenAI: vi.fn(),
}));

import { createQwenChatModel, callQwenChat, streamQwenChat } from './index';

function setupInvokeMock(invokeResult: any) {
  vi.mocked(ChatOpenAI).mockImplementationOnce(
    () =>
      ({
        __opts: undefined,
        invoke: vi.fn().mockResolvedValue(invokeResult),
        stream: vi.fn(),
      }) as any,
  );
}

describe('toStringContent (private, 通过 callQwenChat 行为验证)', () => {
  it('字符串 content 原样返回', async () => {
    setupInvokeMock({ content: 'hello' });
    const result = await callQwenChat([new HumanMessage('hi')], { apiKey: 'test' });
    expect(result.content).toBe('hello');
  });

  it('complex content 提取所有 text 段', async () => {
    setupInvokeMock({
      content: [
        { type: 'text', text: '部分1' },
        { type: 'image', url: 'x' },
        { type: 'text', text: '部分2' },
      ],
    });
    const result = await callQwenChat([new HumanMessage('hi')], { apiKey: 'test' });
    expect(result.content).toBe('部分1部分2');
  });

  it('complex content 含 undefined text 时跳过', async () => {
    setupInvokeMock({
      content: [{ type: 'text', text: '正常' }, { type: 'text' }, { type: 'text', text: '尾段' }],
    });
    const result = await callQwenChat([new HumanMessage('hi')], { apiKey: 'test' });
    expect(result.content).toBe('正常尾段');
  });

  it('usage_metadata 缺失时 usage 为 undefined', async () => {
    setupInvokeMock({ content: 'no usage' });
    const result = await callQwenChat([new HumanMessage('hi')], { apiKey: 'test' });
    expect(result.usage).toBeUndefined();
  });

  it('usage_metadata 存在时正确映射', async () => {
    setupInvokeMock({
      content: 'has usage',
      usage_metadata: {
        input_tokens: 10,
        output_tokens: 20,
        total_tokens: 30,
      },
    });
    const result = await callQwenChat([new HumanMessage('hi')], { apiKey: 'test' });
    expect(result.usage).toEqual({
      prompt_tokens: 10,
      completion_tokens: 20,
      total_tokens: 30,
    });
  });
});

describe('createQwenChatModel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('使用默认值（无 options）', () => {
    createQwenChatModel();
    const opts = vi.mocked(ChatOpenAI).mock.calls[0][0]!;
    expect(opts).toMatchObject({
      modelName: process.env.MODEL_NAME || 'qwen-max',
      temperature: 0.7,
      topP: 0.9,
      maxTokens: 2048,
    });
    expect(opts.configuration!.baseURL).toContain('dashscope');
  });

  it('options 覆盖所有默认值', () => {
    createQwenChatModel({
      modelName: 'qwen-turbo',
      temperature: 0.5,
      topP: 0.8,
      maxTokens: 1024,
      apiKey: 'override-key',
    });
    const opts = vi.mocked(ChatOpenAI).mock.calls[0][0]!;
    expect(opts).toMatchObject({
      modelName: 'qwen-turbo',
      temperature: 0.5,
      topP: 0.8,
      maxTokens: 1024,
      apiKey: 'override-key',
    });
  });
});

describe('streamQwenChat', () => {
  it('流式调用逐块 yield content', async () => {
    const chunks = [{ content: '你' }, { content: '好' }, { content: '，世界' }];
    const asyncIter = (async function* () {
      for (const c of chunks) yield c;
    })();
    // mock ChatOpenAI 构造返回的 stream 函数
    const { ChatOpenAI } = await import('@langchain/openai');
    vi.mocked(ChatOpenAI).mockImplementationOnce(
      () =>
        ({
          stream: vi.fn().mockResolvedValue(asyncIter),
        }) as any,
    );
    const collected: string[] = [];
    for await (const chunk of streamQwenChat([new SystemMessage('助手')], { apiKey: 'test' })) {
      if (chunk.content) collected.push(chunk.content);
    }
    expect(collected).toEqual(['你', '好', '，世界']);
  });

  it('流式末尾 yield 含 usage', async () => {
    const chunks = [
      { content: 'a' },
      {
        content: '',
        usage_metadata: { input_tokens: 5, output_tokens: 1, total_tokens: 6 },
      },
    ];
    const asyncIter = (async function* () {
      for (const c of chunks) yield c;
    })();
    const { ChatOpenAI } = await import('@langchain/openai');
    vi.mocked(ChatOpenAI).mockImplementationOnce(
      () =>
        ({
          stream: vi.fn().mockResolvedValue(asyncIter),
        }) as any,
    );
    const collected: Array<{ content: string; usage?: any }> = [];
    for await (const chunk of streamQwenChat([new HumanMessage('hi')], { apiKey: 'test' })) {
      collected.push(chunk);
    }
    expect(collected[0]).toEqual({ content: 'a', usage: undefined });
    expect(collected[1].usage).toEqual({
      prompt_tokens: 5,
      completion_tokens: 1,
      total_tokens: 6,
    });
  });
});
