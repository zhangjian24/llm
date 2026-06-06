/**
 * E2E 公共 Fixture
 *
 * 提供 mock SSE 流式响应 + 登录态注入
 */
import { test as base, expect, Page } from '@playwright/test';

export const test = base.extend<{
  mockQwenAPI: (chunks: string[]) => Promise<void>;
  seedApiKey: () => Promise<void>;
}>({
  mockQwenAPI: async ({ page }, use) => {
    await use(async (chunks: string[]) => {
      await page.route('**/api/qwen', async (route) => {
        const sse = chunks.map((c) => `data: ${JSON.stringify({ content: c })}\n\n`).join('') +
          `data: ${JSON.stringify({ done: true, usage: { prompt_tokens: 10, completion_tokens: 5, total_tokens: 15 } })}\n\n`;
        await route.fulfill({
          status: 200,
          contentType: 'text/event-stream',
          body: sse,
        });
      });
    });
  },
  seedApiKey: async ({ page }, use) => {
    await use(async () => {
      await page.addInitScript(() => {
        localStorage.setItem('qwen_chatbot_api_key', 'mock-test-key-for-e2e');
      });
    });
  },
});

export { expect };

/**
 * 通用登录流程：注入 localStorage 角色 + 跳转到 /chat
 */
export async function gotoChat(page: Page) {
  await page.addInitScript(() => {
    localStorage.setItem('qwen_chatbot_api_key', 'mock-test-key-for-e2e');
  });
  await page.goto('/chat');
}
