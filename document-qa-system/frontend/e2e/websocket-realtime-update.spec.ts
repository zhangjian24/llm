/**
 * WebSocket 实时更新端到端测试
 * 
 * 测试场景:
 * 1. 上传文档后状态从"处理中"变为"就绪"
 * 2. 处理失败时状态变为"失败"
 * 3. 页面刷新后仍能正常接收实时更新
 */

import { test, expect } from '@playwright/test';

test.describe('WebSocket 实时更新 E2E 测试', () => {
  test.beforeEach(async ({ page }) => {
    // 访问文档管理页面
    await page.goto('/documents');
    
    // 等待页面加载完成
    await expect(page.getByTestId('document-list-table')).toBeVisible();
  });

  test('应该实时显示文档处理进度（processing → ready）', async ({ page }) => {
    console.log('=== Step 1: 上传文档 ===');
    
    // 1. 上传测试文档
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('test-documents/test.pdf');
    
    console.log('=== Step 2: 等待处理中状态 ===');
    
    // 2. 等待文档出现在列表中，状态为"处理中"
    await expect(page.getByText('⏳ 处理中')).toBeVisible({ timeout: 5000 });
    
    console.log('=== Step 3: 等待处理完成 ===');
    
    // 3. 等待状态变为"就绪"（通过 WebSocket 自动更新）
    await expect(page.getByText('✅ 就绪')).toBeVisible({ timeout: 30000 });
    
    console.log('=== Step 4: 验证块数显示 ===');
    
    // 4. 验证显示块数
    const chunksCell = page.locator('[data-testid="chunks-count"]').first();
    await expect(chunksCell).not.toHaveText('-');
    
    console.log('✅ 测试通过：文档处理流程正常');
  });

  test('应该实时显示文档处理失败', async ({ page }) => {
    console.log('=== Step 1: 上传会失败的文档 ===');
    
    // 1. 上传一个会导致处理失败的文档
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('test-documents/corrupted.pdf');
    
    console.log('=== Step 2: 等待处理中状态 ===');
    
    // 2. 等待文档出现在列表中，状态为"处理中"
    await expect(page.getByText('⏳ 处理中')).toBeVisible({ timeout: 5000 });
    
    console.log('=== Step 3: 等待失败状态 ===');
    
    // 3. 等待状态变为"失败"（通过 WebSocket 自动更新）
    await expect(page.getByText('❌ 失败')).toBeVisible({ timeout: 30000 });
    
    console.log('✅ 测试通过：失败状态实时更新');
  });

  test('应该在页面刷新后仍能接收实时更新', async ({ page }) => {
    console.log('=== Step 1: 上传文档 ===');
    
    // 1. 上传测试文档
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('test-documents/test.pdf');
    
    console.log('=== Step 2: 等待处理中状态 ===');
    
    // 2. 等待文档出现在列表中，状态为"处理中"
    await expect(page.getByText('⏳ 处理中')).toBeVisible({ timeout: 5000 });
    
    console.log('=== Step 3: 刷新页面 ===');
    
    // 3. 刷新页面
    await page.reload();
    
    // 等待页面重新加载
    await expect(page.getByTestId('document-list-table')).toBeVisible();
    
    console.log('=== Step 4: 等待处理完成（刷新后） ===');
    
    // 4. 等待状态变为"就绪"（刷新后仍能接收 WebSocket 更新）
    await expect(page.getByText('✅ 就绪')).toBeVisible({ timeout: 30000 });
    
    console.log('✅ 测试通过：页面刷新后 WebSocket 连接正常');
  });

  test('应该支持多个文档同时处理并实时更新', async ({ page }) => {
    console.log('=== Step 1: 上传多个文档 ===');
    
    // 1. 上传第一个文档
    let fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('test-documents/test1.pdf');
    
    // 2. 上传第二个文档
    fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('test-documents/test2.pdf');
    
    console.log('=== Step 2: 等待两个文档都显示为处理中 ===');
    
    // 3. 等待两个文档都显示为"处理中"
    const processingBadges = page.getByText('⏳ 处理中');
    await expect(processingBadges).toHaveCount(2, { timeout: 5000 });
    
    console.log('=== Step 3: 等待两个文档都处理完成 ===');
    
    // 4. 等待两个文档都变为"就绪"
    const readyBadges = page.getByText('✅ 就绪');
    await expect(readyBadges).toHaveCount(2, { timeout: 60000 });
    
    console.log('✅ 测试通过：多个文档并发处理正常');
  });

  test('应该正确显示 WebSocket 连接状态', async ({ page }) => {
    console.log('=== Step 1: 检查初始连接状态 ===');
    
    // 1. 打开开发者工具控制台
    const consoleMessages: string[] = [];
    page.on('console', msg => {
      const text = msg.text();
      if (text.includes('WebSocket')) {
        consoleMessages.push(text);
      }
    });
    
    // 2. 刷新页面触发 WebSocket 连接
    await page.reload();
    
    console.log('=== Step 2: 等待 WebSocket 连接成功 ===');
    
    // 3. 等待连接成功日志
    await expect.poll(() => 
      consoleMessages.some(msg => msg.includes('✅ WebSocket connected'))
    ).toBe(true);
    
    console.log('✅ 测试通过：WebSocket 连接状态正常显示');
  });

  test('应该在删除文档后立即更新列表', async ({ page }) => {
    console.log('=== Step 1: 上传文档 ===');
    
    // 1. 上传测试文档
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('test-documents/to-delete.pdf');
    
    // 2. 等待文档处理完成
    await expect(page.getByText('✅ 就绪')).toBeVisible({ timeout: 30000 });
    
    console.log('=== Step 2: 删除文档 ===');
    
    // 3. 点击删除按钮
    const deleteButton = page.getByTestId('delete-button').first();
    await deleteButton.click();
    
    // 4. 确认删除
    page.on('dialog', dialog => dialog.accept());
    
    console.log('=== Step 3: 验证文档已从列表中移除 ===');
    
    // 5. 验证文档已消失
    await expect(page.getByText('to-delete.pdf')).not.toBeVisible({ timeout: 5000 });
    
    console.log('✅ 测试通过：删除操作立即生效');
  });

  test('应该支持重新处理失败的文档', async ({ page }) => {
    console.log('=== Step 1: 创建失败文档 ===');
    
    // 1. 上传会失败的文档
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('test-documents/will-fail.pdf');
    
    // 2. 等待处理失败
    await expect(page.getByText('❌ 失败')).toBeVisible({ timeout: 30000 });
    
    console.log('=== Step 2: 点击重新处理 ===');
    
    // 3. 点击重新处理按钮
    const reprocessButton = page.getByTestId('reprocess-button').first();
    await reprocessButton.click();
    
    console.log('=== Step 3: 等待状态变回处理中 ===');
    
    // 4. 等待状态变为"处理中"
    await expect(page.getByText('⏳ 处理中')).toBeVisible({ timeout: 5000 });
    
    console.log('✅ 测试通过：重新处理功能正常');
  });
});
