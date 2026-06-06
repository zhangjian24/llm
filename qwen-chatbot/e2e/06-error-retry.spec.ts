/**
 * E9: 错误处理
 */
import { test, expect, gotoChat } from './fixtures';

test.describe('E9: API 错误处理', () => {
  test('网络错误 → 助手消息包含错误提示', async ({ page }) => {
    // mock 失败
    await page.route('**/api/qwen', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' }),
      });
    });
    await gotoChat(page);

    await page.getByPlaceholder('在此输入您的消息...').fill('hi');
    await page.getByRole('button', { name: '发送' }).click();

    // 等待错误信息
    await expect(page.getByText(/Error|错误|失败/).first()).toBeVisible({ timeout: 10_000 });
  });

  test('API Key 缺失 → 重定向到 /settings 或显示提示', async ({ page }) => {
    // 不注入 API Key
    await page.goto('/chat');
    await page.evaluate(() => localStorage.removeItem('qwen_chatbot_api_key'));
    await page.reload();

    await page.getByPlaceholder('在此输入您的消息...').fill('hi');
    await page.getByRole('button', { name: '发送' }).click();

    // 应有 API Key 提示或跳转到 /settings
    await expect(async () => {
      const url = page.url();
      const text = await page.textContent('body');
      const hasRedirect = url.includes('/settings');
      const hasWarning = text?.includes('API Key') || text?.includes('请先');
      expect(hasRedirect || hasWarning).toBeTruthy();
    }).toPass({ timeout: 10_000 });
  });
});
