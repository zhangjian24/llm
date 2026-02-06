# Qwen Chatbot

一个基于 Next.js 和通义千问（Qwen）大模型的 AI 聊天机器人，通过兼容 OpenAI 格式的 Chat API 接口调用 Qwen 模型。

![](https://img.jianzhang.cc/2026/01/7179c34f282c33d4c06655d215b0eef7.png)


![](https://img.jianzhang.cc/2026/01/6928ea31bb39ace945b15a9646e4406c.png)

## 功能特性

- 基于 Next.js 的现代化前端界面
- 实时流式响应，提供流畅的对话体验
- 完整的错误处理机制
- 环境变量配置，确保安全性与可移植性
- 响应式设计，支持多种设备
- Token使用量统计，实时显示输入/输出/总token数
- 对话历史记录管理，方便回顾过往交流内容

## 技术栈

- **前端**: Next.js, React, TypeScript
- **图标库**: react-icons (Ant Design Icons)
- **后端**: Next.js API Routes
- **AI 模型**: 通义千问（Qwen）通过 OpenAI 兼容 API
- **样式**: Tailwind CSS

## 样式规范

- **优先使用 Tailwind CSS**: 项目中应尽量使用 Tailwind CSS 类名进行样式设计，而不是编写自定义 CSS 样式
- **样式一致性**: 所有组件的样式应遵循统一的设计规范，通过 Tailwind 的实用优先方法实现
- **响应式设计**: 利用 Tailwind CSS 的响应式类名实现不同屏幕尺寸下的适配

## 环境要求

- Node.js 18 或更高版本
- 有效的通义千问 API 密钥

## 安装与启动

### 1. 克隆项目

```bash
git clone <repository-url>
cd qwen-chatbot
```

### 2. 安装依赖

```bash
pnpm install
```

### 3. 配置环境变量

复制 `.env.example` 文件为 `.env.local` 并填入您的 API 密钥：

```bash
cp .env.example .env.local
```

编辑 `.env.local` 文件：

```env
OPENAI_API_KEY=your_actual_qwen_api_key_here
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL_NAME=qwen-max
```

### 4. 启动开发服务器

```bash
pnpm run dev
```

应用程序将在 `http://localhost:3000` 上运行。

## 项目结构

```
qwen-chatbot/
├── pages/                 # Next.js 页面组件
│   ├── index.tsx          # 主聊天界面
│   └── api/               # API 路由
│       └── qwen.ts        # 通义千问 API 调用接口
├── components/            # React 组件
│   ├── ChatWindow.tsx     # 聊天窗口组件
│   └── ChatInput.tsx      # 输入框组件
├── styles/                # 样式文件
│   ├── globals.css        # Tailwind CSS 全局样式
│   ├── tailwind.config.js # Tailwind 配置
│   └── postcss.config.js  # PostCSS 配置
├── .env.local             # 环境变量配置（本地）
├── .env.example           # 环境变量示例
├── next.config.js         # Next.js 配置
├── package.json           # 项目依赖和脚本
└── README.md              # 项目说明
```

## API 配置

项目使用以下环境变量：

- `OPENAI_API_KEY`: 通义千问 API 密钥
- `OPENAI_API_BASE`: API 基础 URL，默认为 `https://dashscope.aliyuncs.com/compatible-mode/v1`
- `MODEL_NAME`: 使用的模型名称，默认为 `qwen-max`

API 支持 token 使用量统计功能，可在响应中获取详细的 token 消耗信息用于成本控制和性能优化：
- `prompt_tokens`: 输入消息的 token 数量
- `completion_tokens`: 模型回复的 token 数量
- `total_tokens`: 总 token 数量（输入 + 输出）
- `cached_tokens_details`: 包含缓存命中情况的详细信息（如适用）

## 使用说明

1. 在输入框中输入您的问题或指令
2. 点击 "Send" 按钮或按 Enter 键提交
3. 机器人将以流式方式返回回答
4. 对话历史将显示在聊天窗口中
5. 每条助手回复下方将显示本次对话的token使用详情
6. 在右侧面板中可以查看本次会话的累计token消耗统计

## 自定义配置

您可以根据需要修改以下配置：

- 更换模型：在 `.env.local` 中更改 `MODEL_NAME`
- API 地址：在 `.env.local` 中更改 `OPENAI_API_BASE`
- 界面样式：使用 Tailwind CSS 类名进行样式定制（参考 [Tailwind CSS 文档](https://tailwindcss.com/docs)）
- 图标：通过修改组件中的 react-icons 导入语句更换图标（如 `AiOutlineMessage`, `AiOutlineRobot` 等 Ant Design Icons）
- Token显示样式：通过 Tailwind CSS 类名调整样式

## 部署

### 构建生产版本

```bash
pnpm run build
```

### 启动生产服务器

```bash
pnpm start
```

## 故障排除

### 常见问题

1. **API 密钥错误**: 确保 `.env.local` 中的 `OPENAI_API_KEY` 正确无误
2. **网络连接问题**: 检查网络连接并确认 API 服务可用
3. **跨域问题**: Next.js 已自动处理 CORS，通常不会出现此问题

### 错误信息

- `Authentication failed`: API 密钥无效，请检查 `.env.local` 配置
- `Rate limit exceeded`: API 请求频率超限，请稍后再试
- `Network error`: 无法连接到 API 服务，请检查网络连接

## 许可证

MIT License