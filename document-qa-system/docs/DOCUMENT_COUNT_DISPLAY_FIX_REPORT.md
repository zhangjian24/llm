# 文档计数显示修复报告

## 问题描述

**问题现象**：访问网站时，左侧边栏的文档标签显示"文档 (0)"，但实际应该显示正确的文档数量。只有当用户手动切换到"文档"标签页时，文档数量才会正确显示。

**影响范围**：用户体验不佳，用户需要额外操作才能看到正确的文档统计信息。

## 根本原因分析

### 原始代码问题

在 `frontend/src/App.tsx` 中的文档加载逻辑存在设计缺陷：

```typescript
// ❌ 原始有问题的代码
useEffect(() => {
  const loadDocuments = async () => {
    try {
      const response = await documentAPI.getList(1, 100);
      setDocuments(response.data.items, response.data.total);
    } catch (error) {
      console.error('Failed to load documents:', error);
      setError(error instanceof Error ? error.message : '加载文档失败');
    }
  };
  
  if (activeTab === 'documents') {
    loadDocuments();
  }
}, [activeTab, setDocuments, setError]);
```

**问题点**：
1. 文档加载被条件限制在 `activeTab === 'documents'` 时才执行
2. 应用启动时默认显示"对话"标签页 (`activeTab = 'chat'`)
3. 因此文档数据不会在应用初始化时加载
4. 用户必须手动切换到文档标签页才能触发数据加载

## 修复方案

### 设计思路

采用双阶段加载策略：
1. **初始化加载**：应用启动时立即加载文档数据
2. **按需刷新**：切换到文档标签页时重新加载以保持数据新鲜度

### 实现代码

```typescript
// ✅ 修复后的代码
// 提取文档加载逻辑为独立函数
const loadDocuments = async () => {
  try {
    const response = await documentAPI.getList(1, 100);
    setDocuments(response.data.items, response.data.total);
  } catch (error) {
    console.error('Failed to load documents:', error);
    setError(error instanceof Error ? error.message : '加载文档失败');
  }
};

// 应用启动时加载文档数据
useEffect(() => {
  loadDocuments();
}, []); // 空依赖数组，只在组件挂载时执行一次

// 当切换到文档标签页时重新加载（保持数据新鲜度）
useEffect(() => {
  if (activeTab === 'documents') {
    loadDocuments();
  }
}, [activeTab]); // 依赖activeTab变化
```

### 修复要点

1. **分离关注点**：将文档加载逻辑提取为独立函数避免重复
2. **初始化加载**：使用空依赖数组的useEffect确保应用启动时加载数据
3. **保持刷新机制**：保留原有的标签页切换刷新功能
4. **性能优化**：避免不必要的重复加载

## 验证测试

### 测试场景

1. **页面初始加载测试**
   - 期望：应用启动后左侧边栏立即显示正确文档数量
   - 验证：无需手动切换标签页即可看到准确计数

2. **标签页切换测试**
   - 期望：切换到文档标签页时能获取最新数据
   - 验证：文档列表显示最新的状态和数量

3. **数据一致性测试**
   - 期望：侧边栏计数与主内容区域计数保持一致
   - 验证：两个位置显示相同的文档数量

### 部署验证

- 后端服务：http://localhost:8000 ✅ 运行正常
- 前端服务：http://localhost:5174 ✅ 运行正常
- WebSocket连接：已建立 ✅ 实时更新功能正常

## 技术细节

### 修改文件
- `frontend/src/App.tsx` - 核心修复文件

### 关键变更
1. 提取 `loadDocuments` 函数避免代码重复
2. 添加初始化加载的 useEffect hook
3. 优化依赖数组配置
4. 保持原有刷新机制

### 性能考虑
- 初始化加载只执行一次
- 标签页切换时的加载有明确触发条件
- 避免了无限循环或过度请求

## 总结

本次修复解决了文档计数显示的核心问题，通过合理的React Hooks使用模式，确保了：
- 数据在应用启动时就可用
- 用户体验得到显著改善
- 代码结构更加清晰和可维护
- 保持了原有的数据新鲜度机制

修复后，用户访问网站时就能立即看到准确的文档统计信息，无需额外操作。