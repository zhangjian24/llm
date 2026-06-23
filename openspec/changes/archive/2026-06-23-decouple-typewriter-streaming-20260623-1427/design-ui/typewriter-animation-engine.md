# UI 设计稿

## 概述
本目录包含变更相关的 UI 设计稿，使用 OpenPencil 格式（.op 文件）。

## 关联 Capabilities

| Capability | 设计文件 | 说明 |
|------------|----------|------|
| typewriter-animation-engine | typewriter-animation-engine.md | 无 UI 视觉结构变更，仅动画逻辑优化 |

## 设计规范

从 design.md 提取的样式要求：

### 配色方案
- 主色：N/A（无视觉样式变更）

### 组件规范
- TypeWriterEffect：动画渲染组件，逻辑重构（Hook 抽取），UI 展示层不变。

## 设计状态
本次变更为纯行为变更（behavioral change），不涉及视觉 UI 结构调整或新增界面元素。打字机效果的所有视觉呈现逻辑（Markdown 渲染、样式类、布局）均保持不变。

变更范围：
1. 动画逻辑从 TypeWriterEffect 组件抽离为 useTypewriter Hook
2. ChatWindow 组件不再直接控制 TypeWriterEffect 的 instant/streaming 逻辑

## 组件清单
- TypeWriterEffect：展示组件，接收 displayedText 并渲染
- useTypewriter（新）：动画逻辑 Hook
- ChatWindow：集成新 Hook

## 使用说明
1. 无需 UI 设计稿预览，视觉层未变更
2. 最终效果：流式内容平滑显示，不闪烁
