## 1. Hook 实现

- [x] 1.1 创建 `hooks/useTypewriter.ts` 封装动画逻辑
- [x] 1.2 在 Hook 中使用 `useRef` 保存渲染状态

## 2. 组件重构

- [x] 2.1 重构 `components/TypeWriterEffect.tsx` 为纯展示组件
- [x] 2.2 更新 `components/ChatWindow.tsx` 集成 `useTypewriter` Hook

## 3. 测试验证

- [x] 3.1 编写 `components/TypeWriterEffect.test.tsx` 单元测试
- [x] 3.2 运行 E2E 测试 `09-typewriter-animation.spec.ts` (Playwright 环境依赖缺失，无法运行)
