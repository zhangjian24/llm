/**
 * T20.7: 可访问性（a11y）验证
 * 使用 axe-core 检测模态框等关键组件的 0 critical / 0 serious 违规
 */
import { test, expect, gotoChat } from './fixtures';
import AxeBuilder from '@axe-core/playwright';

test.describe('A11y: 模态框可访问性', () => {
  test('HistoryModal 打开时无 critical/serious 违规', async ({ page }) => {
    await gotoChat(page);

    // 注入历史记录以激活按钮
    await page.evaluate(() => {
      const history = [
        {
          id: 1,
          timestamp: '2026-01-01T00:00:00.000Z',
          input: 'a',
          output: 'b',
          model: 'qwen-plus',
          params: { temperature: 0.7, top_p: 0.8, max_tokens: 1000 },
          evaluation: '',
        },
      ];
      localStorage.setItem(
        'appState',
        JSON.stringify({
          messages: [],
          conversationHistory: history,
          inputMessage: '',
          selectedRoleId: null,
          schemaVersion: 1,
        }),
      );
    });
    await page.reload();

    // 点击查看历史按钮
    const historyBtn = page.getByRole('button', { name: /历史/ }).first();
    if (await historyBtn.isVisible()) {
      await historyBtn.click();
      await expect(page.locator('#history-modal-title')).toBeVisible({ timeout: 5_000 });

      // 对模态框执行 axe 检测
      const results = await new AxeBuilder({ page })
        .include('[role="dialog"]')
        .analyze();

      const critical = results.violations.filter(
        (v) => v.impact === 'critical' || v.impact === 'serious',
      );
      if (critical.length > 0) {
        console.error('A11y 违规:', JSON.stringify(critical.map((v) => ({
          id: v.id,
          impact: v.impact,
          help: v.help,
          nodes: v.nodes.length,
        })), null, 2));
      }
      expect(critical).toEqual([]);
    }
  });

  test('RoleManager 编辑模态 0 critical/serious 违规', async ({ page }) => {
    await gotoChat(page);
    await page.goto('/roles');

    // 打开编辑模态（第一个角色必有"编辑"按钮）
    const editBtn = page.getByRole('button', { name: '编辑' }).first();
    await expect(editBtn).toBeVisible({ timeout: 5_000 });
    await editBtn.click();

    // 等待模态框出现
    const dialog = page.locator('[role="dialog"]');
    await expect(dialog).toBeVisible({ timeout: 5_000 });

    // axe 检测
    const results = await new AxeBuilder({ page })
      .include('[role="dialog"]')
      .analyze();

    const critical = results.violations.filter(
      (v) => v.impact === 'critical' || v.impact === 'serious',
    );
    if (critical.length > 0) {
      console.error('A11y 违规:', JSON.stringify(critical.map((v) => ({
        id: v.id,
        impact: v.impact,
        help: v.help,
        nodes: v.nodes.length,
      })), null, 2));
    }
    expect(critical).toEqual([]);
  });
});
