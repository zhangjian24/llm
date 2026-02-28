# 文档问答系统 - 测试用例

## 功能测试清单

### 1. 文档上传测试

#### 测试用例 1.1: 支持的文件格式
- [ ] PDF文件上传
- [ ] TXT文件上传  
- [ ] DOCX文件上传
- [ ] DOC文件上传
- [ ] HTML文件上传

#### 测试用例 1.2: 文件大小限制
- [ ] 小于10MB文件正常上传
- [ ] 大于10MB文件拒绝上传
- [ ] 空文件处理

#### 测试用例 1.3: 批量上传
- [ ] 同时上传多个文件
- [ ] 混合格式文件上传
- [ ] 上传进度显示

### 2. 文档处理测试

#### 测试用例 2.1: 文本提取准确性
- [ ] PDF文本提取完整
- [ ] Word文档格式保持
- [ ] 中文编码正确处理
- [ ] 特殊字符处理

#### 测试用例 2.2: 文档分块效果
- [ ] 长文档合理分块
- [ ] 分块大小适中
- [ ] 内容连贯性保持

### 3. 向量存储测试

#### 测试用例 3.1: 向量生成
- [ ] BGE模型正常加载
- [ ] 向量维度正确(768)
- [ ] 批量嵌入处理
- [ ] 向量质量验证

#### 测试用例 3.2: 数据库存储
- [ ] Pinecone连接正常
- [ ] 向量正确存储
- [ ] 元数据完整保存
- [ ] 索引创建成功

### 4. 问答功能测试

#### 测试用例 4.1: 基础问答
- [ ] 简单问题准确回答
- [ ] 复杂问题分解处理
- [ ] 多文档综合回答
- [ ] 答案相关性评估

#### 测试用例 4.2: 检索准确性
- [ ] 相关文档优先检索
- [ ] 相似度阈值控制
- [ ] Top-K结果合理性
- [ ] 检索速度测试

#### 测试用例 4.3: 答案质量
- [ ] 答案准确性验证
- [ ] 置信度评分合理
- [ ] 来源文档标注
- [ ] 回答格式规范

### 5. 接口测试

#### 测试用例 5.1: RESTful API
- [ ] POST /api/documents/upload
- [ ] GET /api/documents/list
- [ ] POST /api/chat/query
- [ ] GET /api/health

#### 测试用例 5.2: 错误处理
- [ ] 无效请求参数处理
- [ ] 系统异常捕获
- [ ] 错误信息友好提示
- [ ] 状态码正确返回

### 6. 前端界面测试

#### 测试用例 6.1: 用户体验
- [ ] 页面加载速度
- [ ] 响应式设计适配
- [ ] 交互流畅性
- [ ] 视觉效果美观

#### 测试用例 6.2: 功能完整性
- [ ] 导航栏功能正常
- [ ] 文件拖拽上传
- [ ] 聊天界面交互
- [ ] 状态实时更新

## 性能测试

### 负载测试
- [ ] 并发用户数: 10
- [ ] 并发用户数: 50  
- [ ] 并发用户数: 100
- [ ] 长时间运行稳定性

### 压力测试
- [ ] 大文件处理能力
- [ ] 高频查询响应
- [ ] 内存使用监控
- [ ] CPU占用率

## 兼容性测试

### 浏览器兼容性
- [ ] Chrome最新版
- [ ] Firefox最新版
- [ ] Safari最新版
- [ ] Edge最新版

### 操作系统兼容性
- [ ] Windows 10/11
- [ ] macOS最新版
- [ ] Ubuntu 20.04+
- [ ] CentOS 7+

## 安全测试

### 数据安全
- [ ] 文件上传安全检查
- [ ] SQL注入防护
- [ ] XSS攻击防护
- [ ] CSRF保护

### 访问控制
- [ ] API访问频率限制
- [ ] 文件访问权限控制
- [ ] 敏感信息保护

## 自动化测试脚本

```python
# test_document_upload.py
import pytest
import requests
from pathlib import Path

class TestDocumentUpload:
    def test_pdf_upload(self):
        """测试PDF文件上传"""
        files = {'file': open('test.pdf', 'rb')}
        response = requests.post(
            'http://localhost:8000/api/documents/upload',
            files=files
        )
        assert response.status_code == 200
        assert 'document_id' in response.json()

    def test_large_file_rejection(self):
        """测试大文件拒绝"""
        # 创建大于10MB的文件
        large_file = Path('large_test.txt')
        large_file.write_text('x' * (10 * 1024 * 1024 + 1))
        
        files = {'file': open(large_file, 'rb')}
        response = requests.post(
            'http://localhost:8000/api/documents/upload',
            files=files
        )
        assert response.status_code == 400
```

```javascript
// test_frontend.js
describe('前端界面测试', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000')
  })

  it('应该显示导航栏', () => {
    cy.get('nav').should('be.visible')
    cy.contains('文档问答系统').should('be.visible')
  })

  it('应该能够上传文件', () => {
    cy.get('[data-testid="upload-area"]').attachFile('test.pdf')
    cy.contains('上传成功').should('be.visible')
  })

  it('应该能够进行问答', () => {
    cy.get('[data-testid="chat-input"]').type('测试问题{enter}')
    cy.get('[data-testid="chat-message"]').should('be.visible')
  })
})
```

## 测试报告模板

### 测试执行报告

**测试日期**: 2024-02-22
**测试环境**: 
- 操作系统: Windows 11
- 浏览器: Chrome 120
- 后端版本: v1.0.0
- 前端版本: v1.0.0

**测试结果汇总**:
- 通过用例: XX/XX
- 失败用例: XX/XX
- 通过率: XX%

**主要发现**:
1. [问题描述及严重程度]
2. [性能瓶颈分析]
3. [用户体验改进建议]

**建议改进项**:
1. [具体改进建议1]
2. [具体改进建议2]

---
*测试负责人: [姓名]*
*联系方式: [邮箱]*