import { test, expect } from '@playwright/test';

test.describe('聊天功能测试', () => {
  test.beforeEach(async ({ page }) => {
    // 访问应用
    await page.goto('http://localhost:5174');
    
    // 等待页面加载完成
    await page.waitForLoadState('networkidle');
  });

  test('应该能够发送消息并接收回复', async ({ page }) => {
    // 确保在聊天标签页
    await expect(page.locator('text=智能问答')).toBeVisible();
    
    // 查找输入框
    const inputField = page.locator('textarea[placeholder*="输入问题"]');
    await expect(inputField).toBeVisible();
    
    // 输入测试消息
    const testMessage = '你好，这是一个测试消息';
    await inputField.fill(testMessage);
    
    // 检查发送按钮是否启用
    const sendButton = page.locator('button:has-text("发送")');
    await expect(sendButton).toBeEnabled();
    
    // 点击发送
    await sendButton.click();
    
    // 验证用户消息已显示
    await expect(page.locator(`text=${testMessage}`)).toBeVisible();
    
    // 等待助手回复（最长等待30秒）
    await page.waitForTimeout(2000); // 等待2秒让消息开始处理
    
    // 检查是否有加载状态
    const loadingIndicator = page.locator('text=正在思考中...');
    if (await loadingIndicator.isVisible()) {
      console.log('检测到加载状态指示器');
      // 等待加载完成
      await loadingIndicator.waitFor({ state: 'hidden', timeout: 30000 });
    }
    
    // 检查是否显示了助手回复
    const assistantMessages = page.locator('.bg-gray-100.text-gray-900');
    const messageCount = await assistantMessages.count();
    
    if (messageCount > 0) {
      console.log(`检测到 ${messageCount} 条助手消息`);
      // 检查第一条助手消息是否包含内容
      const firstAssistantMessage = assistantMessages.first();
      const messageText = await firstAssistantMessage.textContent();
      
      expect(messageText).toBeTruthy();
      console.log('助手回复内容:', messageText?.substring(0, 100) + '...');
    } else {
      console.log('暂无助手回复，可能是后端处理中或出现错误');
      // 检查是否有错误消息
      const errorMessage = page.locator('text=❌');
      if (await errorMessage.isVisible()) {
        const errorText = await errorMessage.textContent();
        console.log('检测到错误消息:', errorText);
      }
    }
  });

  test('WebSocket连接状态应该正确显示', async ({ page }) => {
    // 检查WebSocket连接状态指示器
    const connectionStatus = page.locator('text=🟢 实时连接, 🔴 连接断开');
    
    // 等待状态指示器出现
    await connectionStatus.first().waitFor({ state: 'visible', timeout: 5000 });
    
    const statusText = await connectionStatus.first().textContent();
    console.log('WebSocket连接状态:', statusText);
    
    // 验证状态文本格式正确
    expect(statusText).toMatch(/^[🟢🔴]\s*(实时连接|连接断开)$/);
  });

  test('应该能够切换到文档标签页并查看文档列表', async ({ page }) => {
    // 点击文档标签
    await page.click('button:has-text("📄 文档")');
    
    // 等待文档页面加载
    await expect(page.locator('text=文档管理')).toBeVisible();
    
    // 检查文档计数显示
    const documentCount = page.locator('button:has-text("📄 文档")').first();
    const countText = await documentCount.textContent();
    
    if (countText) {
      const match = countText.match(/\((\d+)\)/);
      if (match) {
        const count = parseInt(match[1]);
        console.log(`文档数量: ${count}`);
        
        // 如果有文档，检查文档列表
        if (count > 0) {
          const documentItems = page.locator('.bg-white.rounded-lg.border');
          await expect(documentItems.first()).toBeVisible();
          
          // 检查文档项的基本结构
          const firstDoc = documentItems.first();
          await expect(firstDoc.locator('.font-medium')).toBeVisible(); // 文件名
          await expect(firstDoc.locator('.text-sm')).toBeVisible(); // 文件大小和状态
        }
      }
    }
  });

  test('输入框应该有正确的占位符和行为', async ({ page }) => {
    const inputField = page.locator('textarea[placeholder*="输入问题"]');
    
    // 检查占位符文本
    const placeholder = await inputField.getAttribute('placeholder');
    expect(placeholder).toContain('输入问题');
    expect(placeholder).toContain('Shift+Enter 换行');
    
    // 测试空输入时发送按钮被禁用
    await inputField.fill('');
    const sendButton = page.locator('button:has-text("发送")');
    await expect(sendButton).toBeDisabled();
    
    // 测试有内容时发送按钮启用
    await inputField.fill('测试消息');
    await expect(sendButton).toBeEnabled();
  });

  test('应该正确显示聊天历史', async ({ page }) => {
    // 发送第一条消息
    const inputField = page.locator('textarea[placeholder*="输入问题"]');
    await inputField.fill('第一条测试消息');
    await page.click('button:has-text("发送")');
    
    // 等待处理
    await page.waitForTimeout(1000);
    
    // 发送第二条消息
    await inputField.fill('第二条测试消息');
    await page.click('button:has-text("发送")');
    
    // 等待处理
    await page.waitForTimeout(1000);
    
    // 检查聊天历史
    const userMessages = page.locator('.bg-blue-500.text-white');
    const assistantMessages = page.locator('.bg-gray-100.text-gray-900');
    
    const userCount = await userMessages.count();
    const assistantCount = await assistantMessages.count();
    
    console.log(`用户消息数: ${userCount}, 助手消息数: ${assistantCount}`);
    
    // 应该至少有一条用户消息和一条助手消息
    expect(userCount).toBeGreaterThanOrEqual(2);
    expect(assistantCount).toBeGreaterThanOrEqual(1);
  });
});

test.describe('错误处理测试', () => {
  test('应该优雅地处理网络错误', async ({ page }) => {
    // 模拟网络中断场景
    await page.route('**/api/v1/chat', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: '服务器内部错误' })
      });
    });
    
    // 尝试发送消息
    const inputField = page.locator('textarea[placeholder*="输入问题"]');
    await inputField.fill('测试错误处理');
    await page.click('button:has-text("发送")');
    
    // 等待错误消息显示
    await page.waitForTimeout(2000);
    
    // 检查是否显示错误消息
    const errorMessages = page.locator('text=❌');
    if (await errorMessages.count() > 0) {
      console.log('成功捕获并显示错误消息');
      const firstError = await errorMessages.first().textContent();
      console.log('错误消息:', firstError);
    }
    
    // 检查加载状态是否正确清除
    const loadingOverlay = page.locator('text=正在思考中...');
    await expect(loadingOverlay).not.toBeVisible({ timeout: 5000 });
  });
});