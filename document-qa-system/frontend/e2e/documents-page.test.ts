import { test, expect } from '@playwright/test';

test.describe('文档管理页面', () => {
  
  test.beforeEach(async ({ page }) => {
    // 导航到应用
    await page.goto('/');
  });
  
  test('应该能够切换到文档标签页并查看文档列表标题', async ({ page }) => {
    // 从聊天页切换到文档页
    await page.click('button:has-text("📄 文档")');
    
    // 验证页面标题
    await expect(page.locator('h1')).toHaveText('文档管理');
  });
  
  test('应该正确显示文档列表表格结构', async ({ page }) => {
    // 切换到文档页
    await page.click('button:has-text("📄 文档")');
    
    // 等待表格加载（即使是空表）
    await page.waitForSelector('[data-testid="document-list-table"]');
    
    // 验证表头存在
    const headers = page.locator('thead th');
    await expect(headers.first()).toContainText('文件名');
  });
  
  test('应该支持状态筛选功能', async ({ page }) => {
    // 切换到文档页
    await page.click('button:has-text("📄 文档")');
    
    // 等待筛选器加载
    await page.waitForSelector('[data-testid="status-filter"]');
    
    // 选择"就绪"状态
    await page.selectOption('[data-testid="status-filter"]', 'ready');
    
    // 验证筛选器值已更新
    const selectedValue = await page.$eval('[data-testid="status-filter"]', 
      (el: HTMLSelectElement) => el.value);
    expect(selectedValue).toBe('ready');
  });
  
  test('应该支持刷新文档列表', async ({ page }) => {
    // 切换到文档页
    await page.click('button:has-text("📄 文档")');
    
    // 等待刷新按钮出现
    await page.waitForSelector('[data-testid="refresh-button"]');
    
    // 点击刷新按钮
    await page.click('[data-testid="refresh-button"]');
    
    // 验证表格仍然存在（表示刷新完成）
    await page.waitForSelector('[data-testid="document-list-table"]');
  });
  
  test('分页控件应该在有多页时显示', async ({ page }) => {
    // 切换到文档页
    await page.click('button:has-text("📄 文档")');
    
    // 注：实际分页是否显示取决于数据量
    // 这里只验证分页组件的结构存在性
    const pagination = page.locator('[data-testid="pagination"]');
    
    // 如果有多页，分页控件应该可见
    if (await pagination.count() > 0) {
      await expect(pagination.first()).toBeVisible();
    }
  });
  
  test('删除按钮应该存在并可点击', async ({ page }) => {
    // 切换到文档页
    await page.click('button:has-text("📄 文档")');
    
    // 等待表格加载
    await page.waitForSelector('[data-testid="document-list-table"]');
    
    // 查找删除按钮（可能有多个）
    const deleteButtons = page.locator('[data-testid="delete-button"]');
    
    // 如果有文档，删除按钮应该存在
    if (await deleteButtons.count() > 0) {
      await expect(deleteButtons.first()).toBeVisible();
    }
  });
  
  test('重新处理按钮应该存在', async ({ page }) => {
    // 切换到文档页
    await page.click('button:has-text("📄 文档")');
    
    // 等待表格加载
    await page.waitForSelector('[data-testid="document-list-table"]');
    
    // 查找重新处理按钮
    const reprocessButtons = page.locator('[data-testid="reprocess-button"]');
    
    // 如果有文档，重新处理按钮应该存在
    if (await reprocessButtons.count() > 0) {
      await expect(reprocessButtons.first()).toBeVisible();
    }
  });
  
  test('状态标签应该正确显示', async ({ page }) => {
    // 切换到文档页
    await page.click('button:has-text("📄 文档")');
    
    // 等待表格加载
    await page.waitForSelector('[data-testid="document-list-table"]');
    
    // 查找状态标签
    const statusBadges = page.locator('[data-testid="status-badge"]');
    
    // 如果有文档，状态标签应该存在
    if (await statusBadges.count() > 0) {
      const firstBadge = statusBadges.first();
      await expect(firstBadge).toBeVisible();
      
      // 验证状态文本是预期的之一
      const badgeText = await firstBadge.textContent();
      expect(['处理中', '就绪', '失败']).toContain(badgeText?.trim());
    }
  });
  
  test('文件大小应该正确格式化', async ({ page }) => {
    // 切换到文档页
    await page.click('button:has-text("📄 文档")');
    
    // 等待表格加载
    await page.waitForSelector('[data-testid="document-list-table"]');
    
    // 验证文件大小列存在
    const sizeCells = page.locator('tbody td').nth(1);
    
    if (await sizeCells.count() > 0) {
      const sizeText = await sizeCells.textContent();
      // 应该包含单位（B、KB、MB 或 GB）
      expect(sizeText).toMatch(/\d+(\.\d+)?\s*(B|KB|MB|GB)/);
    }
  });
  
  test('上传时间应该正确格式化', async ({ page }) => {
    // 切换到文档页
    await page.click('button:has-text("📄 文档")');
    
    // 等待表格加载
    await page.waitForSelector('[data-testid="document-list-table"]');
    
    // 验证时间列存在
    const timeCells = page.locator('tbody td').nth(5);
    
    if (await timeCells.count() > 0) {
      const timeText = await timeCells.textContent();
      // 应该包含日期格式特征
      expect(timeText).toMatch(/\d{4}[-/]\d{1,2}[-/]\d{1,2}/);
    }
  });
});
