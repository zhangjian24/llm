# Windows 环境下脚本运行指南

## 问题说明

在 Windows PowerShell 环境下直接运行 Python 脚本时，可能会遇到 `ModuleNotFoundError: No module named 'app'` 错误。这是因为 Python 无法正确找到项目模块。

## 解决方案

### 方案一：使用修复后的脚本（推荐）

所有脚本都已经添加了路径修复代码，可以直接运行：

```bash
# 环境检查
python scripts/check_pgvector_env.py

# 数据库迁移
python scripts/migrate_vectors.py

# 文档向量化
python scripts/revectorize_documents.py

# 数据迁移
python scripts/migrate_vector_data.py
```

### 方案二：使用批处理包装器

使用 `run_script.bat` 包装器来运行脚本：

```cmd
# 在 CMD 中运行
run_script.bat scripts/check_pgvector_env.py
run_script.bat scripts/migrate_vectors.py
```

### 方案三：手动设置环境变量

在运行脚本前手动设置 PYTHONPATH：

```cmd
set PYTHONPATH=D:\jianzhang\Codes\llm\document-qa-system\backend;D:\jianzhang\Codes\llm\document-qa-system
python scripts/check_pgvector_env.py
```

## 常见问题

### Q: 仍然出现 ModuleNotFoundError
A: 确保：
1. 在 `backend` 目录下运行命令
2. `app` 目录存在于当前目录
3. Python 版本为 3.8+

### Q: 配置验证错误
A: 这是正常的，因为我们移除了 Pinecone 配置但 `.env.local` 中还有相关配置。已在配置中设置忽略未知字段。

### Q: 数据库连接失败
A: 检查：
1. PostgreSQL 服务是否运行
2. 数据库连接字符串是否正确
3. 数据库用户权限是否足够

## 推荐的运行顺序

1. **环境检查**：`python scripts/check_pgvector_env.py`
2. **数据库迁移**：`python scripts/migrate_vectors.py`
3. **文档向量化**：`python scripts/revectorize_documents.py`
4. **功能测试**：`python -m pytest tests/ -v`

## PowerShell 用户注意事项

如果使用 PowerShell，可能需要调整执行策略：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

或者直接使用 CMD 来运行批处理文件。