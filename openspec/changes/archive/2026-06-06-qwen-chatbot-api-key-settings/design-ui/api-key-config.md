# UI 设计稿: API Key 配置页

## 概述

设置页面 `/settings`，用于配置 API Key。设计为移动端布局（375×812）。

## 布局结构

```
┌─────────────────────────────────────┐
│  ← 设置                              │  Header
├─────────────────────────────────────┤
│                                     │
│  API Key                            │
│  ┌───────────────────────────────┐  │
│  │ sk-xxxxxxxxxxxxxxxxxxxxxxxx  │  │  输入框
│  └───────────────────────────────┘  │
│  从阿里云百炼控制台获取 API Key     │  Form
│                                     │
│  ┌───────────────────────────────┐  │
│  │          保存配置              │  │  主按钮（蓝色）
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │          测试连接              │  │  次按钮（灰色描边）
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ ✓ 配置已保存                  │  │  绿色成功
│  ├───────────────────────────────┤  │
│  │ ✓ 连接成功                    │  │  绿色成功
│  ├───────────────────────────────┤  │  Status
│  │ ✗ 连接失败：Invalid API key    │  │  红色错误
│  ├───────────────────────────────┤  │
│  │ ✗ 请先填写 API Key            │  │  红色校验
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

## 节点结构

```
API Key Settings (frame, 375×812, vertical)
├── Header (frame, fill, 64px)
│   ├── BackButton (icon-button 40×40)
│   │   └── ArrowLeftIcon (path)
│   └── PageTitle (text "设置")
├── Form (frame, vertical, gap=20)
│   ├── ApiKeyLabel (text "API Key")
│   ├── ApiKeyInput (form-input, fill, 48px)
│   │   └── InputPlaceholder (text)
│   ├── HintText (caption "从阿里云百炼控制台获取 API Key")
│   ├── SaveButton (button, fill, 48px, #2563EB)
│   │   └── SaveLabel (text "保存配置")
│   └── TestButton (button, fill, 48px, #FFF, stroke)
│       └── TestLabel (text "测试连接")
└── Status (frame, vertical, gap=8)
    ├── SuccessSave (card, #F0FDF4) — "✓ 配置已保存"
    ├── SuccessTest (card, #F0FDF4) — "✓ 连接成功"
    ├── ErrorTest (card, #FEF2F2) — "✗ 连接失败：Invalid API key"
    └── ValidationError (card, #FEF2F2) — "✗ 请先填写 API Key"
```

## UI 状态（对应 specs Scenario 覆盖）

| # | 状态 | 触发条件（specs Scenario） | 显示内容 | 对应节点 |
|---|------|---------------------------|---------|---------|
| 1 | 初始态 | 首次访问 / Key 未配置 | 输入框空，占位符显示 "sk-xxx..." | InputPlaceholder 可见，Status 隐藏 |
| 2 | 已填写 | 用户输入 Key | 输入框显示用户输入内容 | InputPlaceholder 替换为用户文字 |
| 3 | 保存成功 | Scenario: 正常填写并保存 | 绿色卡片 "✓ 配置已保存" | SuccessSave 显示 |
| 4 | 清空保存 | Scenario: 清空 API Key 并保存 | localStorage 清空，输入框为空 | InputPlaceholder 恢复 |
| 5 | 连接成功 | Scenario: 有效 Key 测试连接 | 绿色卡片 "✓ 连接成功" | SuccessTest 显示 |
| 6 | 连接失败 | Scenario: 无效 Key 测试连接 | 红色卡片 "✗ 连接失败：..." | ErrorTest 显示 |
| 7 | 空值校验 | Scenario: Key 为空时点击测试连接 | 红色卡片 "✗ 请先填写 API Key" | ValidationError 显示，不发起请求 |

## 样式令牌

| 令牌 | 值 | 用途 |
|------|-----|------|
| 页面背景 | `#F8FAFC` | 整体背景 |
| 表面 | `#FFFFFF` | 输入框、按钮背景 |
| 主色 | `#2563EB` | 保存按钮 |
| 成功背景 | `#F0FDF4` | 成功提示卡片 |
| 成功文字 | `#16A34A` / `#15803D` | 成功提示 icon / 文案 |
| 错误背景 | `#FEF2F2` | 错误提示卡片 |
| 错误文字 | `#DC2626` / `#991B1B` | 错误提示 icon / 文案 |
| 描边 | `#E2E8F0` | 输入框、次按钮描边 |
| 占位符 | `#94A3B8` | 输入框占位文字 |
| 提示文字 | `#64748B` | 说明文案 |

## 交互说明

- Status 区域的状态卡片**互斥显示**，同一时间只显示一个
- 输入框无密码模式，Key 明文显示（design.md D1 决策）
- "测试连接"按钮发起 `POST /api/verify-key`（design.md D4 决策）
- Key 缺失时 handleSubmit 拦截跳转（design.md D3 决策），不在本页处理

## 设计文件

- `api-key-config.op` — OpenPencil 可编辑设计稿
