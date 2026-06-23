/**
 * E9: TypeWriterEffect 打字机动画专项 e2e 验证
 *
 * 通过覆写 window.fetch 模拟真实 SSE 流式场景（chunks 按时间间隔到达），
 * 验证打字机动画在流式响应中的行为。
 */
import { test, expect, gotoChat } from './fixtures';
import type { Page } from '@playwright/test';

test.describe('E9: TypeWriterEffect 打字机动画', () => {
  async function setupStreamingMock(page: Page, chunks: string[], delayMs = 80) {
    await page.addInitScript(`
      const chunks = ${JSON.stringify(chunks)};
      const delay = ${delayMs};
      const encoder = new TextEncoder();
      const origFetch = window.fetch.bind(window);
      window.fetch = async (input, init) => {
        const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;
        if (url.includes('/api/qwen')) {
          const stream = new ReadableStream({
            async start(controller) {
              for (const chunk of chunks) {
                await new Promise(r => setTimeout(r, delay));
                controller.enqueue(encoder.encode('data: ' + JSON.stringify({ content: chunk }) + '\\n\\n'));
              }
              controller.enqueue(encoder.encode('data: ' + JSON.stringify({ done: true, usage: { prompt_tokens: 5, completion_tokens: 10, total_tokens: 15 } }) + '\\n\\n'));
              controller.close();
            },
          });
          return new Response(stream, { status: 200, headers: { 'Content-Type': 'text/event-stream' } });
        }
        return origFetch(input, init);
      };
    `);
  }

  test('流式过程中气泡逐步增长', async ({ page }) => {
    const chunks = Array.from({ length: 12 }, (_, i) => String.fromCharCode(65 + i));
    await setupStreamingMock(page, chunks, 80);
    await gotoChat(page);

    await page.getByPlaceholder('在此输入您的消息...').fill('hello');
    await page.getByRole('button', { name: '发送' }).click();

    const assistant = page.getByTestId('assistant-message').first();
    await expect(assistant).toBeVisible({ timeout: 15_000 });

    await page.waitForTimeout(200);
    const s1 = (await assistant.textContent()) ?? '';
    expect(s1.length).toBeGreaterThan(0);

    await page.waitForTimeout(500);
    const s2 = (await assistant.textContent()) ?? '';
    expect(s2.length).toBeGreaterThan(s1.length);
  });

  test('多帧采样字符长度单调递增', async ({ page }) => {
    const chunks = Array.from({ length: 15 }, (_, i) => String.fromCharCode(65 + i));
    await setupStreamingMock(page, chunks, 60);
    await gotoChat(page);

    await page.getByPlaceholder('在此输入您的消息...').fill('test');
    await page.getByRole('button', { name: '发送' }).click();

    const assistant = page.getByTestId('assistant-message').first();
    await expect(assistant).toBeVisible({ timeout: 15_000 });

    await page.waitForTimeout(150);
    const samples: number[] = [];
    for (let i = 0; i < 5; i++) {
      await page.waitForTimeout(200);
      const content = (await assistant.textContent()) ?? '';
      samples.push(content.length);
    }

    for (let i = 1; i < samples.length; i++) {
      expect(samples[i]).toBeGreaterThanOrEqual(samples[i - 1]);
    }
    expect(Math.max(...samples)).toBeGreaterThan(0);
  });

  test('流结束后气泡内容 = 完整 chunk 拼接', async ({ page }) => {
    const chunks = ['Hello', ' ', 'World', '!'];
    await setupStreamingMock(page, chunks, 50);
    await gotoChat(page);

    await page.getByPlaceholder('在此输入您的消息...').fill('hi');
    await page.getByRole('button', { name: '发送' }).click();

    const assistant = page.getByTestId('assistant-message').first();
    await expect(assistant).toBeVisible({ timeout: 15_000 });
    await expect(assistant).toHaveText('Hello World!', { timeout: 10_000 });
  });

  test('流式期间 type-writer DOM 元素稳定存在', async ({ page }) => {
    const chunks = Array.from({ length: 8 }, (_, i) => String.fromCharCode(65 + i));
    await setupStreamingMock(page, chunks, 80);
    await gotoChat(page);

    await page.getByPlaceholder('在此输入您的消息...').fill('test');
    await page.getByRole('button', { name: '发送' }).click();

    const assistant = page.getByTestId('assistant-message').first();
    await expect(assistant).toBeVisible({ timeout: 15_000 });

    const typeWriter = assistant.getByTestId('type-writer');
    await expect(typeWriter).toBeVisible({ timeout: 5_000 });

    await page.waitForTimeout(1000);
    await expect(async () => {
      const text = (await assistant.textContent()) ?? '';
      expect(text.length).toBe(8);
    }).toPass({ timeout: 8_000 });
  });

  test('快 API（所有 chunk 同时到达）仍有打字机逐字效果', async ({ page }) => {
    // 模拟 fast API: 所有 chunk 在同一响应中一次性返回（delay=0）
    const chunks = Array.from({ length: 10 }, (_, i) => String.fromCharCode(65 + i));
    await setupStreamingMock(page, chunks, 0);
    await gotoChat(page);

    await page.getByPlaceholder('在此输入您的消息...').fill('fast');
    await page.getByRole('button', { name: '发送' }).click();

    const assistant = page.getByTestId('assistant-message').first();
    await expect(assistant).toBeVisible({ timeout: 15_000 });

    const typeWriter = assistant.getByTestId('type-writer');
    await expect(typeWriter).toBeVisible({ timeout: 5_000 });

    // 等待一小段时间让 TypeWriterEffect 开始动画
    await page.waitForTimeout(80);

    // 采样：字符应该从部分开始，逐渐增长到完整
    const s1 = (await assistant.textContent()) ?? '';
    expect(s1.length).toBeGreaterThan(0);

    // 再等一段，字符应该增长（证明是逐字动画而非瞬间全蹦）
    await page.waitForTimeout(200);
    const s2 = (await assistant.textContent()) ?? '';
    expect(s2.length).toBeGreaterThan(s1.length);

    // 最终完整内容
    await expect(assistant).toHaveText('ABCDEFGHIJ', { timeout: 10_000 });
  });
});
