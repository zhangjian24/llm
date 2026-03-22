# Playwright 自动化测试指南

本目录包含使用 Playwright 通过 MCP 服务执行的前端自动化测试。

## 📋 测试范围

1. **页面加载和渲染** - 验证应用正常启动和显示
2. **用户交互功能** - 测试标签切换、消息输入和发送
3. **API 接口调用** - 验证前后端通信
4. **响应式布局** - 检查不同设备尺寸下的显示

## 🚀 快速开始

### 前置条件

确保已安装 Node.js 和 npm:

```bash
node --version
npm --version
```

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动前端开发服务器

```bash
# Windows PowerShell (需要绕过执行策略)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
npm run dev

# 或直接使用
npx vite
```

服务器将在 http://localhost:5173 启动（如果端口被占用会自动选择其他端口）

### 3. 运行自动化测试

测试通过 MCP Playwright 服务自动执行，无需手动运行命令。

测试会自动：
- 导航到前端页面
- 执行所有测试用例
- 截取屏幕截图
- 生成测试报告

## 📁 测试文件说明

| 文件 | 说明 |
|------|------|
| `playwright-tests.js` | 测试脚本源码 |
| `FRONTEND_AUTOMATED_TEST_REPORT.md` | 完整测试报告 |
| `TEST_EXECUTION_SUMMARY.md` | 测试执行摘要 |
| `README_TESTS.md` | 本文件 |

## 🧪 测试用例详情

### 测试 1: 页面加载验证
- 验证页面成功加载
- 检查主要 UI 元素存在
- 确认无控制台错误

### 测试 2: 标签页切换
- 切换到文档管理页面
- 验证上传界面显示
- 切换回对话页面

### 测试 3: 消息输入和发送
- 在输入框中输入文本
- 点击发送按钮
- 验证消息显示在聊天区域

### 测试 4: API 调用验证
- 监控网络请求
- 验证 API 端点响应
- 确认代理配置正确

### 测试 5-6: 响应式布局
- 测试平板尺寸 (1024x768)
- 测试手机尺寸 (390x844)

### 测试 7: 控制台错误检查
- 收集所有控制台消息
- 验证无严重错误

## 📊 测试结果

查看 `TEST_EXECUTION_SUMMARY.md` 获取测试结果摘要。

查看 `FRONTEND_AUTOMATED_TEST_REPORT.md` 获取详细分析报告。

## ️ 测试截图

测试过程中会生成以下截图：

1. `initial-page-load.png` - 初始页面加载
2. `document-upload-page.png` - 文档管理页面
3. `chat-with-input.png` - 输入测试消息
4. `chat-message-sent.png` - 消息发送成功
5. `responsive-tablet.png` - 平板布局测试
6. `responsive-mobile.png` - 手机布局测试

## 🔧 常见问题

### Q: 无法启动开发服务器？
A: 尝试设置 PowerShell 执行策略：
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Q: 端口 5173 被占用？
A: Vite 会自动选择其他端口（如 5174），注意查看终端输出。

### Q: Tailwind CSS 错误？
A: 确保已安装 `@tailwindcss/postcss`:
```bash
npm install -D @tailwindcss/postcss
```

### Q: 导入路径错误？
A: 检查组件中的相对路径是否正确（使用 `../../` 而不是 `../`）。

## 🛠️ 自定义测试

要修改或添加测试用例，编辑 `playwright-tests.js`:

```javascript
// 添加新的测试函数
async function testCustomFeature(page) {
  console.log('🧪 测试：自定义功能');
  
  // 你的测试代码...
  
  console.log('✅ 测试通过\n');
}

// 添加到主测试流程
async function runAllTests(page) {
  await testPageLoad(page);
  await testCustomFeature(page); // 添加这里
  // ...
}
```

## 📈 持续集成

可以将测试集成到 CI/CD 流程中：

```yaml
# GitHub Actions 示例
name: Frontend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd frontend && npm install
      - run: cd frontend && npm run build
```

##  最佳实践

1. **保持测试独立**: 每个测试用例应该独立运行
2. **使用有意义的选择器**: 使用 `getByRole`, `getByText` 等
3. **等待元素**: 使用适当的等待避免竞态条件
4. **清理状态**: 测试间清理浏览器状态
5. **定期运行**: 定期运行测试确保质量

## 📞 支持

如有问题，请查看详细报告或联系开发团队。

---

**最后更新**: 2026-03-11  
**维护者**: Development Team
