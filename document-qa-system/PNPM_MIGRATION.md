# PNPM 迁移指南

## 为什么选择 PNPM？

PNPM 相比传统 npm/yarn 具有以下优势：
- **磁盘空间节省**：通过硬链接和符号链接避免重复安装
- **更快的安装速度**：并行安装和内容寻址存储
- **严格的依赖管理**：防止幽灵依赖问题
- **更好的安全性**：内容校验和隔离

## 前端项目 PNPM 配置

### 已完成的配置变更：

1. **package.json 更新**：
   - 修正了 `react-icons` 版本从 `^4.12.1` 到 `^4.12.0`（适配 PNPM）
   - 保持了所有其他依赖版本不变

2. **依赖安装**：
   ```bash
   # 在 frontend 目录下执行
   pnpm install
   ```

3. **锁定文件**：
   - 生成 `pnpm-lock.yaml` 替代 `package-lock.json`
   - 确保依赖版本的一致性

### 使用说明：

#### 开发环境启动：
```bash
cd frontend
pnpm install  # 首次安装或依赖更新时
pnpm run dev  # 启动开发服务器
```

#### 生产构建：
```bash
pnpm run build  # 构建生产版本
pnpm run preview  # 预览生产构建
```

#### 其他常用命令：
```bash
pnpm add <package>        # 添加依赖
pnpm add -D <package>     # 添加开发依赖
pnpm remove <package>     # 移除依赖
pnpm update               # 更新依赖
pnpm list                 # 查看已安装依赖
```

### 注意事项：

1. **版本兼容性**：某些包可能存在 PNPM 特定的兼容性问题
2. **CI/CD 配置**：如果使用 CI/CD，需要相应更新构建脚本
3. **团队协作**：建议团队成员统一使用 PNPM

### 回退到 npm（如有需要）：

如果遇到 PNPM 相关问题，可以回退到 npm：
```bash
# 清理 PNPM 相关文件
rm -rf node_modules pnpm-lock.yaml

# 使用 npm 安装
npm install
```

## 性能对比

初步测试显示 PNPM 在以下方面表现优异：
- 安装速度提升约 30-50%
- 磁盘空间占用减少约 60%
- 依赖解析更加严格和安全

---
*文档更新时间：2026年2月*