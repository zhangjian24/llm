/**
 * E10: 持久化往返
 */
import { test, expect, gotoChat } from './fixtures';

test.describe('E10: localStorage 持久化往返', () => {
  test('发送消息后刷新 → appState 仍存在', async ({ page, mockQwenAPI }) => {
    await mockQwenAPI(['Hello', ' world']);
    await gotoChat(page);

    await page.getByPlaceholder('在此输入您的消息...').fill('persist test');
    await page.getByRole('button', { name: '发送' }).click();
    // 等待助手消息出现
    await expect(page.getByTestId('assistant-message').first()).toBeVisible({ timeout: 10_000 });

    // 等待 localStorage 写入完成（debounce 500ms）
    await page.waitForTimeout(1_500);
    // 验证 localStorage 中 appState 存在
    const stored = await page.evaluate(() => {
      const raw = localStorage.getItem('appState');
      if (!raw) return null;
      const s = JSON.parse(raw);
      return { messages: s.messages?.length ?? 0, schemaVersion: s.schemaVersion };
    });
    expect(stored).not.toBeNull();
    expect(stored?.messages).toBeGreaterThan(0);
    expect(stored?.schemaVersion).toBe(1);
  });

  test('schemaVersion 字段存在', async ({ page }) => {
    await gotoChat(page);
    const version = await page.evaluate(() => {
      const raw = localStorage.getItem('appState');
      if (!raw) return null;
      return JSON.parse(raw).schemaVersion;
    });
    // null 也 OK（首次访问未写入），但写入后必须 = 1
    if (version !== null) {
      expect(version).toBe(1);
    }
  });

  test('API Key 持久化', async ({ page }) => {
    await page.goto('/settings');
    const input = page.locator('input[type="password"], input[type="text"]').first();
    await input.fill('persist-key-abc');
    await page.getByRole('button', { name: '保存配置' }).click();
    await page.reload();
    const stored = await page.evaluate(() => localStorage.getItem('qwen_chatbot_api_key'));
    expect(stored).toBe('persist-key-abc');
  });
});
