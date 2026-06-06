/**
 * E6: API Key 配置 + 测试连接
 */
import { test, expect } from './fixtures';

test.describe('E6: API Key 配置 + 测试连接', () => {
  test('输入 Key + 测试连接 → 成功提示', async ({ page }) => {
    // mock verify-key
    await page.route('**/api/verify-key', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true }),
      });
    });

    await page.goto('/settings');
    const input = page.locator('input[type="password"], input[type="text"]').first();
    await input.fill('mock-key-12345');
    await page.getByRole('button', { name: '测试连接' }).click();
    await expect(page.getByText('连接成功')).toBeVisible({ timeout: 5_000 });
  });

  test('错误 Key → 错误提示', async ({ page }) => {
    await page.route('**/api/verify-key', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ success: false, error: '无效的 API Key' }),
      });
    });

    await page.goto('/settings');
    const input = page.locator('input[type="password"], input[type="text"]').first();
    await input.fill('bad-key');
    await page.getByRole('button', { name: '测试连接' }).click();
    await expect(page.getByText(/失败|无效/)).toBeVisible({ timeout: 5_000 });
  });

  test('保存 Key → localStorage 写入', async ({ page }) => {
    await page.goto('/settings');
    const input = page.locator('input[type="password"], input[type="text"]').first();
    await input.fill('saved-key-xyz');
    await page.getByRole('button', { name: '保存配置' }).click();
    const stored = await page.evaluate(() => localStorage.getItem('qwen_chatbot_api_key'));
    expect(stored).toBe('saved-key-xyz');
  });
});
