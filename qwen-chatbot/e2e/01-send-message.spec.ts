/**
 * E1: 发送消息 + 流式响应
 */
import { test, expect, gotoChat } from './fixtures';

test.describe('E1: 发送消息 + 流式响应', () => {
  test('用户输入 → 助手流式回复 → 至少 1 条助手气泡', async ({ page, mockQwenAPI }) => {
    await mockQwenAPI(['你好', '，', '我是', 'AI']);
    await gotoChat(page);

    const textarea = page.getByPlaceholder('在此输入您的消息...');
    await textarea.fill('hello');
    await page.getByRole('button', { name: '发送' }).click();

    // 等待助手消息气泡出现
    const assistant = page.getByTestId('assistant-message').first();
    await expect(assistant).toBeVisible({ timeout: 15_000 });
    // 流式结束后气泡内容应非空
    await expect(assistant).not.toBeEmpty();
  });

  test('流式过程中 DOM 仅 1 条助手消息气泡', async ({ page, mockQwenAPI }) => {
    await mockQwenAPI(['A', 'B', 'C', 'D', 'E']);
    await gotoChat(page);

    await page.getByPlaceholder('在此输入您的消息...').fill('hi');
    await page.getByRole('button', { name: '发送' }).click();

    // 等至少 1 个 chunk 到达
    await expect(page.getByTestId('assistant-message').first()).toBeVisible({ timeout: 10_000 });
    // 助手消息条数应为 1（流式去重 currentResponse 验证）
    const count = await page.getByTestId('assistant-message').count();
    expect(count).toBeLessThanOrEqual(1);
  });
});
