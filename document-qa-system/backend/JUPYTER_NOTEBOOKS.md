# 📓 Jupyter Notebook 使用指南

## 📋 Notebook 文件说明

### 1. `document_qa_system.ipynb` - 基础演示版
- **用途**: 快速入门和基础功能演示
- **特点**: 简洁明了，适合初学者
- **包含内容**:
  - 环境检查和依赖安装
  - 核心模块导入
  - 基本功能测试
  - 简单的文档处理示例

### 2. `document_qa_system_complete.ipynb` - 完整功能版
- **用途**: 全面的功能演示和测试
- **特点**: 功能完整，包含详细测试
- **包含内容**:
  - 完整的环境配置和依赖管理
  - 所有核心服务的详细测试
  - 性能基准测试
  - 系统维护工具
  - 详细的测试报告

## 🚀 使用步骤

### 1. 环境准备
```bash
# 安装Jupyter
pip install jupyter notebook

# 或者使用JupyterLab
pip install jupyterlab
```

### 2. 启动Jupyter
```bash
# 在backend目录下启动
cd backend
jupyter notebook

# 或使用JupyterLab
jupyter lab
```

### 3. 配置API密钥
在Notebook中找到环境配置部分，替换为您的实际密钥：

```python
# Pinecone配置
os.environ['PINECONE_API_KEY'] = 'your_actual_pinecone_api_key'
os.environ['PINECONE_ENVIRONMENT'] = 'gcp-starter'  # 或其他环境

# 千问API配置
os.environ['DASHSCOPE_API_KEY'] = 'your_actual_dashscope_api_key'
```

### 4. 按顺序执行单元格
建议按以下顺序执行：

1. **环境检查** - 确保依赖包已安装
2. **模块导入** - 导入所有必要模块
3. **环境配置** - 设置API密钥
4. **功能测试** - 逐一测试各项功能
5. **完整演示** - 运行完整的工作流程

## 🧪 测试内容详解

### 向量数据库测试
- 连接Pinecone服务
- 创建/连接向量索引
- 获取索引统计信息

### 嵌入模型测试
- 文本编码功能
- 批量编码性能
- 文本相似度计算

### 文档处理测试
- 文本提取和清理
- 智能分块处理
- Token计算

### 向量存储测试
- 向量数据存储
- 元数据管理
- 存储验证

### 语义搜索测试
- 相似度搜索
- 结果排序
- 多查询测试

### 智能问答测试
- 完整问答流程
- 置信度评估
- 引用溯源

## ⚠️ 注意事项

### API密钥安全
- 不要在公开仓库中提交真实的API密钥
- 使用环境变量或配置文件管理密钥
- 定期轮换API密钥

### 性能考虑
- 首次运行可能较慢（模型加载）
- 建议在有GPU的环境中运行嵌入模型
- 大文档处理可能消耗较多内存

### 错误处理
- 网络连接问题：检查API密钥和服务状态
- 内存不足：减少批量处理大小
- 依赖缺失：按提示安装相应包

## 🛠️ 故障排除

### 常见问题

1. **模块导入失败**
   ```bash
   pip install -r requirements.txt
   ```

2. **API连接错误**
   - 检查网络连接
   - 验证API密钥有效性
   - 确认服务配额

3. **内存不足**
   - 减少文档处理批量大小
   - 关闭其他占用内存的程序
   - 使用更小的嵌入模型

4. **CUDA相关错误**
   ```python
   # 如果没有GPU，强制使用CPU
   import os
   os.environ['CUDA_VISIBLE_DEVICES'] = ''
   ```

## 📊 性能优化建议

### 嵌入模型优化
```python
# 使用更小的模型以提高速度
settings.EMBEDDING_MODEL_NAME = "BAAI/bge-small-zh-v1.5"  # 512维
# 而不是
settings.EMBEDDING_MODEL_NAME = "BAAI/bge-large-zh-v1.5"  # 1024维
```

### 批量处理优化
```python
# 调整批量大小
encoder.bge_encoder.encode_batch(texts, batch_size=16)  # 默认32
```

### 缓存策略
```python
# 对频繁查询的结果进行缓存
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_similarity(text1, text2):
    return encoder.bge_encoder.similarity(text1, text2)
```

## 📈 监控和日志

Notebook中包含了基本的性能监控代码，您可以：

1. **查看执行时间**：
   ```python
   import time
   start = time.time()
   # 执行操作
   print(f"执行耗时: {time.time() - start:.2f}秒")
   ```

2. **检查系统资源**：
   ```python
   import psutil
   print(f"内存使用: {psutil.virtual_memory().percent}%")
   ```

## 🎯 学习路径建议

### 初学者路线
1. 运行 `document_qa_system.ipynb`
2. 理解每个模块的基本功能
3. 修改测试数据进行练习

### 进阶路线
1. 运行 `document_qa_system_complete.ipynb`
2. 深入理解各组件的工作原理
3. 尝试调整参数优化性能
4. 扩展功能（如添加新的文档格式支持）

### 专业路线
1. 分析性能瓶颈
2. 实现自定义的嵌入模型
3. 优化检索算法
4. 集成更多AI服务

## 📚 相关资源

- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [Pinecone向量数据库](https://www.pinecone.io/)
- [Sentence Transformers](https://www.sbert.net/)
- [LangChain文档](https://docs.langchain.com/)
- [千问API文档](https://help.aliyun.com/zh/dashscope/)