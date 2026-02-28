# Pinecone SDK 更新说明

## 概述

根据 Pinecone 官方最新的 Python SDK 文档，我们对系统进行了重要更新，以确保与最新版本的兼容性和最佳实践。

## 主要变更

### 1. 依赖包更新

**旧版本:**
```
pinecone-client==3.0.0
```

**新版本:**
```
pinecone==5.3.0
```

**变更原因:** Pinecone 官方已将包名从 `pinecone-client` 更改为 `pinecone`，并且发布了全新的 v5.x 版本。

### 2. 初始化方式变更

**旧方式:**
```python
import pinecone
pinecone.init(api_key=api_key, environment=environment)
```

**新方式:**
```python
from pinecone import Pinecone, ServerlessSpec
pc = Pinecone(api_key=api_key)
```

**变更说明:**
- 使用面向对象的方式初始化客户端
- 不再需要指定 environment 参数
- 采用 ServerlessSpec 配置索引规格

### 3. 索引管理变更

**旧方式:**
```python
# 检查索引
if index_name not in pinecone.list_indexes():
    # 创建索引
    pinecone.create_index(name=index_name, dimension=dimension, metric="cosine")

# 连接索引
index = pinecone.Index(index_name)
```

**新方式:**
```python
# 检查索引
existing_indexes = pc.list_indexes().names()
if index_name not in existing_indexes:
    # 创建索引
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

# 连接索引
index = pc.Index(index_name)
```

### 4. 配置文件更新

移除了不再需要的 `PINECONE_ENVIRONMENT` 配置项，因为新版本的 SDK 不再需要此参数。

## 升级步骤

### 1. 更新依赖
```bash
cd backend
pip uninstall pinecone-client
pip install pinecone==5.3.0
```

### 2. 更新环境变量
在 `.env` 文件中移除 `PINECONE_ENVIRONMENT` 配置项：
```bash
# 移除这行
PINECONE_ENVIRONMENT=your_environment_here
```

### 3. 重启服务
```bash
# 如果使用 Docker
docker-compose down
docker-compose up --build

# 如果手动运行
# 重启后端服务
```

## 新增功能优势

### 1. Serverless 索引支持
新版本默认使用 Serverless 索引，具有以下优势：
- 自动扩缩容
- 按使用付费
- 无需管理基础设施

### 2. 改进的 API 设计
- 更直观的面向对象接口
- 更好的错误处理
- 更清晰的文档结构

### 3. 性能优化
- 更快的初始化速度
- 改进的连接池管理
- 更好的并发处理能力

## 注意事项

1. **向后兼容性**: 旧索引会自动兼容新 SDK
2. **API 密钥**: 确保使用有效的 Pinecone API 密钥
3. **区域选择**: 默认使用 us-east-1 区域，可根据需要调整
4. **计费模式**: Serverless 索引按使用量计费

## 故障排除

### 常见问题

**1. ImportError: cannot import name 'Pinecone'**
- 确保已正确安装 `pinecone==5.3.0`
- 检查是否有旧版本冲突

**2. Authentication Error**
- 验证 `PINECONE_API_KEY` 是否正确设置
- 确认 API 密钥具有相应权限

**3. Index Creation Failed**
- 检查索引名称是否符合命名规范
- 确认账户配额是否充足

### 验证更新

运行验证脚本检查系统状态：
```bash
python verify_system.py
```

## 参考资料

- [Pinecone Python SDK 官方文档](https://docs.pinecone.io/reference/sdks/python/overview)
- [迁移指南](https://github.com/pinecone-io/pinecone-python-client/blob/main/docs/upgrading.md)
- [API 参考](https://sdk.pinecone.io/python/)