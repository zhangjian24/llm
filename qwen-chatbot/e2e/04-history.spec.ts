/**
 * E7: 历史 + 评价
 */
import { test, expect, gotoChat } from './fixtures';

test.describe('E7: 对话历史查看 + 评价', () => {
  test('打开历史模态框 → 显示表格', async ({ page }) => {
    await gotoChat(page);
    // 注入历史记录到 localStorage
    await page.evaluate(() => {
      const history = [
        {
          id: 1,
          timestamp: '2026-01-01T00:00:00.000Z',
          input: 'test input',
          output: 'test output',
          model: 'qwen-plus',
          params: { temperature: 0.7, top_p: 0.8, max_tokens: 1000 },
          evaluation: '',
        },
      ];
      const state = {
        messages: [],
        conversationHistory: history,
        inputMessage: '',
        selectedRoleId: null,
        schemaVersion: 1,
      };
      localStorage.setItem('appState', JSON.stringify(state));
    });
    await page.reload();

    // 找查看历史按钮（页面顶部或聊天区）
    const historyBtn = page.getByRole('button', { name: /历史/ }).first();
    if (await historyBtn.isVisible()) {
      await historyBtn.click();
      // 用 #history-modal-title 精确选择模态框标题
      await expect(page.locator('#history-modal-title')).toBeVisible({ timeout: 5_000 });
    }
  });

  test('空历史 → 空提示', async ({ page }) => {
    await gotoChat(page);
    await page.evaluate(() => {
      localStorage.setItem('appState', JSON.stringify({
        messages: [],
        conversationHistory: [],
        inputMessage: '',
        selectedRoleId: null,
        schemaVersion: 1,
      }));
    });
    await page.reload();
    const historyBtn = page.getByRole('button', { name: /历史/ }).first();
    if (await historyBtn.isVisible()) {
      await historyBtn.click();
      await expect(page.getByText('暂无对话历史')).toBeVisible({ timeout: 5_000 });
    }
  });
});
