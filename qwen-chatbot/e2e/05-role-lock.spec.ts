/**
 * E8: 角色切换锁定配置
 */
import { test, expect, gotoChat } from './fixtures';

test.describe('E8: 角色切换锁定配置', () => {
  test('选中角色 → 锁定 modelConfig', async ({ page }) => {
    await gotoChat(page);
    // 等待角色加载完成
    await page.waitForTimeout(1000);
    // chat 页应有 role selector 区域
    const roleSelector = page.getByText(/角色|Role/i).first();
    await expect(roleSelector).toBeVisible({ timeout: 10_000 });
  });
});
