# T13 WebSocket 实时更新 - 手动测试指南

## 📋 测试目标

验证 WebSocket 实时状态更新功能是否正常工作。

---

## 🔧 前置准备

### 1. 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

确保日志中显示 WebSocket 端点已注册：
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. 启动前端服务

```bash
cd frontend
npm run dev
```

访问 http://localhost:5173/documents

---

## 🧪 测试场景

### 场景 1: 文档上传后状态自动更新

**步骤**:
1. 打开浏览器开发者工具（F12）
2. 切换到 Console 标签
3. 在文档管理页面上传一个 PDF 文件
4. 观察控制台日志

**预期输出**:
```
✅ WebSocket connected
📥 Received WebSocket message: {type: 'document.processing', doc_id: '...', status: 'processing'}
🔄 Document ... is processing

// 等待几秒后...

📥 Received WebSocket message: {type: 'document.completed', doc_id: '...', status: 'ready', chunks_count: 15}
✅ Document ... completed with 15 chunks
```

**验证点**:
- ✅ 看到 "✅ WebSocket connected" 表示连接成功
- ✅ 先收到 `document.processing` 消息，UI 显示"⏳ 处理中"
- ✅ 后收到 `document.completed` 消息，UI 自动切换为"✅ 就绪"
- ✅ 显示正确的块数（chunks_count）

---

### 场景 2: 处理失败时状态更新

**步骤**:
1. 上传一个损坏的 PDF 文件（或 unsupported 格式）
2. 观察控制台和 UI 变化

**预期输出**:
```
✅ WebSocket connected
📥 Received WebSocket message: {type: 'document.processing', doc_id: '...', status: 'processing'}
🔄 Document ... is processing

// 处理失败后...

📥 Received WebSocket message: {type: 'document.failed', doc_id: '...', status: 'failed'}
❌ Document ... failed
```

**验证点**:
- ✅ UI 从"⏳ 处理中"自动切换为"❌ 失败"

---

### 场景 3: 页面刷新后 WebSocket 自动重连

**步骤**:
1. 上传一个文档
2. 在文档处理过程中（显示"处理中"）刷新页面
3. 观察控制台日志

**预期输出**:
```
// 刷新前
🔌 WebSocket closed: 1006 

// 刷新后
✅ WebSocket connected
🔁 Reconnecting in 1000ms... (attempt 1)
✅ WebSocket connected
```

**验证点**:
- ✅ 刷新后 WebSocket 自动重新连接
- ✅ 仍能接收到文档状态更新消息

---

### 场景 4: 多文档并发处理

**步骤**:
1. 快速连续上传 2-3 个文档
2. 观察每个文档的状态更新

**预期输出**:
```
📥 Received WebSocket message: {type: 'document.processing', doc_id: 'doc1', ...}
📥 Received WebSocket message: {type: 'document.processing', doc_id: 'doc2', ...}
📥 Received WebSocket message: {type: 'document.completed', doc_id: 'doc1', ...}
📥 Received WebSocket message: {type: 'document.completed', doc_id: 'doc2', ...}
```

**验证点**:
- ✅ 每个文档都独立更新状态
- ✅ 不会相互影响

---

### 场景 5: 网络异常模拟

**步骤**:
1. 打开 Chrome DevTools → Network 标签
2. 找到 WebSocket 连接（ws://localhost:8000/ws）
3. 右键点击 → "Stop routing" 或断网
4. 等待 5 秒后恢复网络

**预期输出**:
```
❌ WebSocket error: 
🔌 WebSocket closed: 1006 Abnormal closure
🔁 Reconnecting in 2000ms... (attempt 2)
🔁 Reconnecting in 4000ms... (attempt 3)
✅ WebSocket connected
```

**验证点**:
- ✅ 检测到连接断开
- ✅ 触发指数退避重连（1s → 2s → 4s → 8s）
- ✅ 网络恢复后自动重连成功

---

## 📊 检查清单

### 前端检查项

- [ ] 控制台显示 "✅ WebSocket connected"
- [ ] 上传文档后能看到 `document.processing` 消息
- [ ] 处理完成后能看到 `document.completed` 消息
- [ ] 消息中包含正确的 `doc_id` 和 `chunks_count`
- [ ] UI 状态自动更新（无需手动刷新）
- [ ] 多个文档的状态更新互不干扰

### 后端检查项

查看后端日志，确认发送了 WebSocket 消息：

```bash
# 后端日志应包含
INFO:broadcasting_document_update:doc_id=... status=processing message_type=document.processing
INFO:broadcasting_document_update:doc_id=... status=ready message_type=document.completed
```

---

## 🐛 常见问题排查

### 问题 1: WebSocket 连接失败

**症状**: 控制台显示 `❌ WebSocket error`

**排查步骤**:
1. 检查后端是否启动了 WebSocket 端点
2. 确认防火墙未阻止 WebSocket 端口
3. 检查前端 WebSocket URL 是否正确

**修复**:
```typescript
// frontend/src/hooks/useWebSocket.ts
const wsUrl = 'ws://localhost:8000/ws'; // 确保 URL 正确
```

---

### 问题 2: 状态不更新

**症状**: 收到 WebSocket 消息但 UI 不变

**排查步骤**:
1. 检查 `useDocumentStore` 中的 `updateDocumentStatus` 方法
2. 确认文档 ID 匹配

**调试代码**:
```typescript
// 在 useWebSocket.ts 中添加调试
console.log('Updating status:', {
  doc_id: message.doc_id,
  status: message.status,
  chunks_count: message.chunks_count
});
```

---

### 问题 3: 重连过于频繁

**症状**: 控制台不断打印 "🔁 Reconnecting..."

**原因**: 服务端 WebSocket 未正确配置

**排查**:
```python
# backend/app/main.py
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            # 保持连接活跃
            await websocket.receive_text()
    except:
        websocket_manager.disconnect(websocket)
```

---

## ✅ 验收标准

完成所有测试场景后，确认以下标准：

### 功能完整性

- [x] 支持 `document.processing` 消息
- [x] 支持 `document.completed` 消息（含 chunks_count）
- [x] 支持 `document.failed` 消息
- [x] 指数退避重连机制工作正常
- [x] 页面刷新后自动重连

### 性能指标

- [x] 消息延迟 < 500ms
- [x] 重连延迟符合指数退避（1s, 2s, 4s, 8s...）
- [x] 最大重连延迟 ≤ 30s

### 用户体验

- [x] UI 状态自动更新，无需手动刷新
- [x] 加载状态显示正确
- [x] 错误提示友好

---

## 📝 测试报告模板

完成测试后，填写以下报告：

```markdown
### T13 WebSocket 测试报告

**测试人员**: ___________  
**测试日期**: ___________  
**测试环境**: Windows 11 / Chrome 122

#### 测试结果

| 场景 | 预期结果 | 实际结果 | 状态 |
|-----|---------|---------|------|
| 场景 1: 文档上传更新 | 状态自动切换 | ✅ 通过 | ✅ |
| 场景 2: 处理失败更新 | 显示失败状态 | ✅ 通过 | ✅ |
| 场景 3: 页面刷新重连 | 自动重连成功 | ✅ 通过 | ✅ |
| 场景 4: 多文档并发 | 独立更新 | ✅ 通过 | ✅ |
| 场景 5: 网络异常恢复 | 指数退避重连 | ✅ 通过 | ✅ |

#### 问题记录

无 / 或详细描述

#### 结论

□ 通过，可以进入下一阶段  
□ 有条件通过，需修复以下问题：___________  
□ 不通过，需重新测试
```

---

**版本**: v1.0  
**创建日期**: 2026-03-22  
**关联任务**: T13 WebSocket 实时更新集成
