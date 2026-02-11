# Qwen Chatbot

一个基于 Next.js 和通义千问（Qwen）大模型的 AI 聊天机器人，通过兼容 OpenAI 格式的 Chat API 接口调用 Qwen 模型。

![](https://img.jianzhang.cc/2026/01/7179c34f282c33d4c06655d215b0eef7.png)


![](https://img.jianzhang.cc/2026/01/6928ea31bb39ace945b15a9646e4406c.png)


![](https://img.jianzhang.cc/2026/02/0758cb218c03dfce5e1b489cae158139.png)

## 功能特性

- 基于 Next.js 的现代化前端界面
- 实时流式响应，提供流畅的对话体验
- 完整的错误处理机制
- 环境变量配置，确保安全性与可移植性
- 响应式设计，支持多种设备
- Token使用量统计，实时显示输入/输出/总token数
- 对话历史记录管理，方便回顾过往交流内容
- AI角色管理系统，支持创建和切换不同功能角色
- LangChain框架集成，提供模块化的AI调用能力
- 多模型支持，可灵活配置Qwen系列不同能力等级模型

## 技术栈

- **前端框架**: Next.js 16, React 19, TypeScript
- **状态管理**: React Context API
- **图标库**: react-icons (Ant Design Icons)
- **后端架构**: Next.js API Routes
- **AI框架**: LangChain Core v1.1.18
- **AI模型**: 通义千问（Qwen）通过 OpenAI 兼容 API
- **样式框架**: Tailwind CSS v3.4.19
- **Markdown渲染**: react-markdown, remark-gfm, rehype-highlight
- **UI组件**: 自定义React组件库

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
├── components/            # React 组件
│   ├── ChatInput.tsx      # 聊天输入框组件
│   ├── ChatWindow.tsx     # 聊天窗口显示组件
│   ├── ConversationHistoryTable.tsx # 对话历史表格组件
│   ├── HistoryModal.tsx   # 历史记录模态框组件
│   ├── Layout.tsx         # 页面布局组件
│   ├── ModelConfigPanel.tsx # 模型参数配置面板
│   ├── RoleManager.tsx    # AI角色管理组件
│   ├── RoleSelector.tsx   # 角色选择器组件
│   ├── Sidebar.tsx        # 侧边栏导航组件
│   ├── ThinkingIndicator.tsx # AI思考状态指示器
│   ├── TypeWriterEffect.tsx # 打字机效果组件
│   └── useRoleStorage.ts  # 角色存储Hook
├── contexts/              # React Context
│   └── AppContext.tsx     # 全局应用状态管理
├── lib/langchain/         # LangChain集成层
│   ├── index.ts           # 核心LangChain封装
│   └── tools.ts           # 工具函数定义
├── pages/                 # Next.js 页面
│   ├── api/qwen.ts        # 通义千问 API 路由
│   ├── _app.tsx           # 应用入口文件
│   ├── chat.tsx           # 主聊天页面
│   ├── index.tsx          # 首页重定向
│   └── roles.tsx          # AI角色管理页面
├── styles/                # 样式文件
│   └── globals.css        # 全局样式文件
├── types/                 # TypeScript 类型定义
│   └── index.ts           # 共享类型接口
├── .env.local             # 环境变量配置（本地）
├── .env.example           # 环境变量模板
├── next.config.js         # Next.js 配置文件
├── package.json           # 项目依赖和脚本
├── tailwind.config.js     # Tailwind CSS 配置
├── tsconfig.json          # TypeScript 配置
└── README.md              # 项目说明文档
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

### 基础对话
1. 在输入框中输入您的问题或指令
2. 点击 "Send" 按钮或按 Enter 键提交
3. 机器人将以流式方式返回回答
4. 对话历史将显示在聊天窗口中
5. 每条助手回复下方将显示本次对话的token使用详情
6. 在右侧面板中可以查看本次会话的累计token消耗统计

### AI角色管理
1. 点击左侧导航栏的"AI角色管理"
2. 可以查看现有角色或创建新角色
3. 每个角色可以配置：
   - 角色名称和描述
   - 系统提示词（定义AI行为）
   - 模型参数（temperature、top_p、max_tokens）
   - 绑定的Qwen模型类型
4. 创建后可在聊天页面选择对应角色

### 模型配置
1. 在聊天页面可以调整LLM参数
2. 当选择特定角色时，参数配置会被锁定
3. 支持三种Qwen模型：
   - Qwen-Turbo：快速且经济
   - Qwen-Plus：平衡性能
   - Qwen-Max：最强能力

### 历史记录查看
1. 点击"查看历史"按钮打开对话历史
2. 可以查看：
   - 时间戳和对话内容
   - 使用的模型和参数
   - Token消耗详情
   - 对话效果评价
3. 支持对历史对话进行评价和备注

## 自定义配置

### 环境变量配置
- 更换模型：在 `.env.local` 中更改 `MODEL_NAME`
- API 地址：在 `.env.local` 中更改 `OPENAI_API_BASE`
- 密钥管理：在 `.env.local` 中配置 `OPENAI_API_KEY`

### 界面样式定制
- 使用 Tailwind CSS 类名进行样式设计
- 参考 [Tailwind CSS 文档](https://tailwindcss.com/docs) 进行高级定制
- 通过修改组件中的 react-icons 导入语句更换图标
- Token显示样式可通过Tailwind CSS类名调整

### AI角色扩展
- 在`components/RoleManager.tsx`中添加新的预设角色
- 修改`lib/langchain/tools.ts`添加新的工具函数
- 扩展`types/index.ts`中的角色接口定义

### 模型参数调优
- temperature：控制输出随机性（0-2）
- top_p：控制核采样参数（0-1）
- max_tokens：限制最大输出长度
- 根据具体应用场景调整这些参数获得最佳效果

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
4. **角色切换失效**: 清除浏览器缓存或重启开发服务器
5. **历史记录丢失**: 检查浏览器localStorage存储权限

### 错误信息

- `Authentication failed`: API 密钥无效，请检查 `.env.local` 配置
- `Rate limit exceeded`: API 请求频率超限，请稍后再试
- `Network error`: 无法连接到 API 服务，请检查网络连接
- `Model not found`: 指定的模型不可用，请检查`MODEL_NAME`配置
- `Context length exceeded`: 输入内容过长，请缩短输入或增加max_tokens

### 开发调试

1. 查看浏览器控制台错误信息
2. 检查Node.js开发服务器日志
3. 验证环境变量是否正确加载
4. 确认依赖包版本兼容性
5. 使用`pnpm run lint`检查代码质量

## 许可证

MIT License