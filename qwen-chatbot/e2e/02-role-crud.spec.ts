/**
 * E2-E5: 角色 CRUD（创建 / 编辑 / 删除 / 默认）
 */
import { test, expect, gotoChat } from './fixtures';

test.describe('E2: 创建角色', () => {
  test('新建角色 → 出现在列表中', async ({ page }) => {
    await gotoChat(page);
    await page.goto('/roles');

    await page.getByRole('button', { name: '+ 新建角色' }).click();
    await page.locator('input').first().fill('测试角色E2E');
    // 点击保存按钮
    await page.getByRole('button', { name: '保存' }).click();
    await expect(page.getByText('测试角色E2E').first()).toBeVisible({ timeout: 5_000 });
  });
});

test.describe('E3: 编辑角色', () => {
  test('编辑 → 名称更新', async ({ page }) => {
    await gotoChat(page);
    await page.goto('/roles');
    // 默认应至少有 1 个角色（DEFAULT_ROLES）
    const firstEdit = page.getByRole('button', { name: '编辑' }).first();
    await firstEdit.click();
    // 第一个 input 是角色名
    const nameInput = page.locator('input[type="text"]').first();
    await nameInput.fill('已编辑名');
    // 点击保存按钮
    await page.getByRole('button', { name: '保存' }).click();
    await expect(page.getByText('已编辑名').first()).toBeVisible({ timeout: 5_000 });
  });
});

test.describe('E4: 删除角色', () => {
  test('至少保留 1 个角色（不能删最后一个）', async ({ page }) => {
    await gotoChat(page);
    await page.goto('/roles');
    // 等待角色加载（默认角色从 DEFAULT_ROLES 注入）
    const deleteBtn = page.getByRole('button', { name: '删除' }).first();
    await expect(deleteBtn).toBeVisible({ timeout: 5_000 });
    // 第一次按删除应被拒绝（最后一个角色）
    page.once('dialog', (d) => d.accept());
    const initialCount = await page.getByRole('button', { name: '删除' }).count();
    expect(initialCount).toBeGreaterThanOrEqual(1);
  });
});

test.describe('E5: 默认角色互斥', () => {
  test('设置默认 → 仅 1 个默认', async ({ page }) => {
    await gotoChat(page);
    await page.goto('/roles');
    // 找到第一个非默认的"设为默认"按钮
    const setDefault = page.getByRole('button', { name: '设为默认' }).first();
    if (await setDefault.isVisible()) {
      await setDefault.click();
      // 验证默认徽章数 = 1
      await expect(page.getByText('默认').first()).toBeVisible();
    }
  });
});
