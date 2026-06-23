## 摘要

通过将 `TypeWriterEffect` 组件中的打字机渲染逻辑抽离为 `useTypewriter` Hook，实现渲染引擎与流式数据接口的解耦，从而解决高速流式数据到达时组件重渲染导致的动画失效与显示闪烁问题。

## Why

目前 `TypeWriterEffect` 依赖 `text` prop 的瞬时全量更新，由于 React 重渲染机制，在流式数据的高频 `chunk` 到达时，组件内部的 `useEffect` 和计时器被反复重置，导致动画逻辑无法衔接，直接表现为全量文本跳跃显示。解耦渲染逻辑是提升聊天交互体验的核心瓶颈。

## 用户价值

- **目标用户**: 所有使用聊天界面的用户。
- **可感知变化**: 流式生成的文字将平滑地逐字或逐 chunk 展现，无论后端 API 响应速度如何，体验一致流畅，避免闪烁。

## 成功标准

- **流畅度**: 在高速流式下 (如 100token/s) 依然保持打字机效果。
- **一致性**: `TypeWriterEffect` 不再受重渲染影响。

## What Changes

**流式动画逻辑重构**
- From: `TypeWriterEffect` 组件内耦合计时器与流式状态，受组件 props 重渲染影响。
- To: 引入 `useTypewriter` Hook，将动画状态保存在 `useRef` 中，仅依据全量内容自动推进动画，与流式数据接收解耦。

## Capabilities

### New Capabilities

- `typewriter-animation-engine`: 独立的打字机渲染 Hook，支持平滑追赶机制。

### Modified Capabilities

- N/A

## Impact

- 涉及 `qwen-chatbot/components/TypeWriterEffect.tsx` 重构。
- 涉及 `qwen-chatbot/components/ChatWindow.tsx` 集成 Hook。

## 发布策略

一次性上线。

## 回滚方案

回滚 `TypeWriterEffect` 和 `ChatWindow` 的相关提交，恢复之前的耦合组件实现。

## 待定事项

- 无。
