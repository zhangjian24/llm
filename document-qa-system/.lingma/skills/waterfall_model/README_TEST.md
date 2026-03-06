# 🧪 测试技能提示词使用说明

## 📋 概述

本目录包含一套专业、通用、可执行的测试技能提示词，用于指导 AI 或开发人员系统性地完成全栈项目的测试工作。

**文件结构**:
```
waterfall_model/
├── test_skill_prompt.md    # 核心提示词文档（803 行）
├── README_TEST.md          # 本说明文档
└── examples/               # 示例代码（可选）
    ├── test_service_example.py
    └── test_component_example.tsx
```

---

## 🎯 核心提示词文档

### `test_skill_prompt.md`

这是主要的测试技能提示词文件，包含完整的测试流程指导。

**内容结构**:

1. **第一步：明确测试目标**
   - 分析项目架构
   - 定义测试范围（单元/集成/E2E）
   - 制定测试策略（MVP/生产模式）

2. **第二步：环境准备与依赖安装**
   - 后端测试环境配置
   - 前端测试环境配置
   - 测试环境变量设置

3. **第三步：编写测试用例**
   - 后端单元测试模板（5 个示例）
   - 前端单元测试模板（2 个示例）
   - Mock 和夹具使用指南

4. **第四步：执行测试与收集结果**
   - pytest 命令详解
   - vitest 命令详解
   - CI/CD 集成模式

5. **第五步：生成结构化测试报告**
   - 测试报告模板
   - 自动化生成脚本
   - 质量评估标准

6. **第六步：质量保证清单**
   - 测试完整性检查
   - 测试质量检查
   - 覆盖率要求

7. **附录**
   - 常用断言参考
   - 测试最佳实践
   - FIRST 原则
   - AAA 模式

---

## 🚀 快速开始

### 场景 1: 为现有项目添加测试

```bash
# 1. 阅读提示词文档
cat .lingma/skills/waterfall_model/test_skill_prompt.md

# 2. 按照第一步分析项目架构
tree -L 3 -I 'node_modules|__pycache__'

# 3. 安装测试依赖
cd backend
pip install pytest pytest-asyncio pytest-cov

# 4. 按照提示词编写测试用例
# 参考 "第三步：编写测试用例" 中的模板

# 5. 执行测试
pytest tests/ --cov=app --cov-report=html

# 6. 生成测试报告
python ../scripts/generate_test_report.py
```

### 场景 2: 为新项目建立测试体系

```bash
# 1. 创建测试目录结构
mkdir -p backend/tests/{unit,integration}
mkdir -p frontend/src/{components,services,stores}/__tests__

# 2. 创建测试配置文件
cp backend/tests/conftest.py.example backend/tests/conftest.py

# 3. 按照提示词逐步实施
# 遵循 "第一步" → "第六步" 的完整流程
```

### 场景 3: MVP 阶段快速测试

```bash
# 使用 MVP 模式（简化版）
# 在提示词中设置 mvp_mode=true

# 优先级:
# P0: 核心业务逻辑测试 (DocumentService, TextChunker)
# P1: API 端点测试
# P2: 可忽略性能测试、UI 组件测试
```

---

## 📊 自动化报告生成器

### `scripts/generate_test_report.py`

这是一个 Python 脚本，用于从 pytest 结果自动生成《测试分析报告》。

**使用方法**:

```bash
# 基本用法
python scripts/generate_test_report.py \
  --project "RAG 文档问答系统" \
  --phase unit

# 指定输入文件
python scripts/generate_test_report.py \
  --project "MyProject" \
  --phase integration \
  --xml test-results/integration.xml \
  --coverage coverage.json \
  --output docs/integration_test_report.md

# 查看帮助
python scripts/generate_test_report.py --help
```

**输出示例**:

```markdown
# RAG 文档问答系统 - unit 测试分析报告

## 📊 1. 执行概况

| 指标 | 数值 |
|------|------|
| 执行时间 | 2026-03-05 18:30:00 |
| 测试阶段 | unit |
| 总用例数 | 15 |
| 通过数 | 15 |
| 失败数 | 0 |
| 跳过数 | 0 |
| 执行时长 | 1.23 秒 |
| 通过率 | 100.0% |

**代码覆盖率**: 88.6%
- 语句覆盖率：88.6%
- 分支覆盖率：75.2%

---

## 📈 2. 测试结果详情
...
```

---

## 🎯 适用场景

### 适用于以下项目类型:

1. **FastAPI + React 全栈项目** ✅
   - 完美匹配
   - 所有示例都基于此技术栈

2. **Python 后端项目** ✅
   - 可直接使用后端测试部分
   - 忽略前端相关内容

3. **TypeScript/JavaScript 前端项目** ✅
   - 可直接使用前端测试部分
   - 参考 Vitest + Testing Library 示例

4. **其他框架项目** ⚠️
   - 需要适当调整命令和工具
   - 测试理念和流程通用

---

## 📝 测试报告模板

使用提示词生成的测试报告包含以下内容:

### 标准格式

```markdown
# [项目名称] 测试分析报告

## 1. 执行概况
- 执行时间、测试阶段、用例统计

## 2. 测试结果详情
- 按模块统计表格
- 失败用例详细分析

## 3. 覆盖率分析
- 总体覆盖率
- 未覆盖的关键代码

## 4. 质量评估
- 测试充分性评价
- 风险评估

## 5. 改进建议
- 短期（立即执行）
- 中期（下个迭代）

## 6. 结论
- 通过/有条件通过/不通过
```

---

## 🔧 配套工具

### 推荐的测试工具链

#### 后端 (Python)
- **测试框架**: pytest 7.4+
- **异步支持**: pytest-asyncio 0.23+
- **覆盖率**: pytest-cov 4.1+
- **HTTP Mock**: respx 0.20+
- **数据库**: SQLAlchemy Async

#### 前端 (TypeScript/React)
- **测试框架**: Vitest 1.3+
- **组件测试**: @testing-library/react 14.2+
- **覆盖率**: @vitest/coverage-v8 1.3+
- **Mock**: vi.fn() (内置)

#### 通用工具
- **代码格式化**: black, prettier
- **Linting**: flake8, eslint
- **CI/CD**: GitHub Actions, GitLab CI

---

## 💡 最佳实践

### 1. 测试左移（Shift Left）

在编码阶段就开始编写测试:

```bash
# Git Hook: 提交前自动运行测试
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "🔍 运行单元测试..."
cd backend && pytest tests/unit -q
if [ $? -ne 0 ]; then
    echo "❌ 测试失败，禁止提交"
    exit 1
fi
echo "✅ 测试通过"
EOF
chmod +x .git/hooks/pre-commit
```

### 2. 持续集成

在 CI/CD 流水线中集成测试:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        cd backend
        pytest tests/ --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
```

### 3. 测试驱动开发（TDD）

遵循"红 - 绿 - 重构"循环:

1. **红**: 先写一个失败的测试
2. **绿**: 编写刚好让测试通过的代码
3. **重构**: 优化代码结构，保持测试通过

---

## 📚 学习资源

### 推荐阅读

1. **pytest 官方文档**: https://docs.pytest.org/
2. **Testing Library**: https://testing-library.com/
3. **Vitest 文档**: https://vitest.dev/
4. **pytest-cov 文档**: https://pytest-cov.readthedocs.io/

### 相关书籍

- 《Python 测试驱动开发》
- 《测试驱动的面向对象软件开发》
- 《Google 软件测试之道》

---

## 🔄 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0 | 2026-03-05 | 初始版本，包含完整测试流程 |
| v1.1 | TBD | 增加 E2E 测试示例 |
| v1.2 | TBD | 增加性能测试模板 |

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进这套测试技能提示词。

**改进方向**:
- 增加更多测试场景示例
- 补充性能测试模板
- 添加安全测试指南
- 完善 E2E 测试流程

---

## 📞 联系方式

- **项目地址**: d:/jianzhang/Documents/Codes/llm/document-qa-system
- **技能文件**: `.lingma/skills/waterfall_model/test_skill_prompt.md`
- **反馈建议**: [待填写]

---

**最后更新**: 2026-03-05  
**维护者**: [待填写]  
**许可证**: MIT
