#!/usr/bin/env python3
"""
自动化测试报告生成器

使用方法:
    python generate_test_report.py --project "RAG 文档问答系统" --phase unit
"""
import argparse
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Optional


def parse_pytest_xml(xml_path: str) -> dict:
    """解析 pytest JUnit XML 结果文件"""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        testsuites = []
        for suite in root.findall('.//testsuite'):
            testcases = []
            for case in suite.findall('testcase'):
                testcase = {
                    'classname': case.get('classname', ''),
                    'name': case.get('name', ''),
                    'time': float(case.get('time', 0)),
                }
                
                # 检查是否有失败或错误
                failure = case.find('failure')
                error = case.find('error')
                skipped = case.find('skipped')
                
                if failure is not None:
                    testcase['status'] = 'FAILED'
                    testcase['message'] = failure.get('message', '')
                    testcase['type'] = 'failure'
                elif error is not None:
                    testcase['status'] = 'ERROR'
                    testcase['message'] = error.get('message', '')
                    testcase['type'] = 'error'
                elif skipped is not None:
                    testcase['status'] = 'SKIPPED'
                    testcase['message'] = skipped.get('message', '')
                    testcase['type'] = 'skipped'
                else:
                    testcase['status'] = 'PASSED'
                
                testcases.append(testcase)
            
            testsuites.append({
                'name': suite.get('name', ''),
                'tests': int(suite.get('tests', 0)),
                'failures': int(suite.get('failures', 0)),
                'errors': int(suite.get('errors', 0)),
                'skipped': int(suite.get('skipped', 0)),
                'time': float(suite.get('time', 0)),
                'testcases': testcases
            })
        
        # 汇总所有 testsuite
        total_tests = sum(ts['tests'] for ts in testsuites)
        total_failures = sum(ts['failures'] for ts in testsuites)
        total_errors = sum(ts['errors'] for ts in testsuites)
        total_skipped = sum(ts['skipped'] for ts in testsuites)
        total_time = sum(ts['time'] for ts in testsuites)
        
        return {
            'total': total_tests,
            'passed': total_tests - total_failures - total_errors - total_skipped,
            'failed': total_failures,
            'errors': total_errors,
            'skipped': total_skipped,
            'time': total_time,
            'testsuites': testsuites,
            'all_testcases': [tc for ts in testsuites for tc in ts['testcases']]
        }
    except FileNotFoundError:
        print(f"⚠️  警告：XML 文件不存在 {xml_path}")
        return None


def parse_coverage_json(json_path: str) -> Optional[dict]:
    """解析 coverage.py 生成的 JSON 报告"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        totals = data.get('totals', {})
        
        return {
            'statement_coverage': float(totals.get('percent_covered', 0)),
            'branch_coverage': float(totals.get('branches_percent_covered', 0)),
            'missing_lines': totals.get('missing', []),
            'covered_lines': totals.get('covered', []),
            'files': data.get('files', {})
        }
    except FileNotFoundError:
        print(f"⚠️  警告：覆盖率文件不存在 {json_path}")
        return None


def analyze_test_quality(results: dict) -> dict:
    """分析测试质量"""
    quality = {}
    
    # 计算通过率
    if results['total'] > 0:
        quality['pass_rate'] = (results['passed'] / results['total']) * 100
    else:
        quality['pass_rate'] = 0
    
    # 失败用例分类
    failed_cases = [
        tc for tc in results['all_testcases']
        if tc['status'] in ['FAILED', 'ERROR']
    ]
    
    # 按模块统计失败
    module_failures = {}
    for case in failed_cases:
        module = case['classname'].split('.')[0]
        if module not in module_failures:
            module_failures[module] = 0
        module_failures[module] += 1
    
    quality['module_failures'] = module_failures
    
    # 评估测试充分性
    if quality['pass_rate'] >= 95:
        quality['assessment'] = '优秀'
    elif quality['pass_rate'] >= 80:
        quality['assessment'] = '良好'
    elif quality['pass_rate'] >= 60:
        quality['assessment'] = '合格'
    else:
        quality['assessment'] = '需改进'
    
    return quality


def generate_markdown_report(
    project_name: str,
    test_phase: str,
    pytest_results: dict,
    coverage_data: Optional[dict],
    output_path: str
):
    """生成 Markdown 格式的测试分析报告"""
    
    quality = analyze_test_quality(pytest_results)
    
    report = f"""# {project_name} - {test_phase}测试分析报告

## 📊 1. 执行概况

| 指标 | 数值 |
|------|------|
| **执行时间** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
| **测试阶段** | {test_phase} |
| **总用例数** | {pytest_results['total']} |
| **通过数** | {pytest_results['passed']} |
| **失败数** | {pytest_results['failed'] + pytest_results['errors']} |
| **跳过数** | {pytest_results['skipped']} |
| **执行时长** | {pytest_results['time']:.2f}秒 |
| **通过率** | {quality['pass_rate']:.1f}% |

{f"**代码覆盖率**: {coverage_data['statement_coverage']:.1f}%" if coverage_data else ""}
{f"- 语句覆盖率：{coverage_data['statement_coverage']:.1f}%" if coverage_data else ""}
{f"- 分支覆盖率：{coverage_data['branch_coverage']:.1f}%" if coverage_data and coverage_data['branch_coverage'] > 0 else ""}

---

## 📈 2. 测试结果详情

### 2.1 按模块统计

| 模块/套件 | 用例数 | 通过 | 失败 | 错误 | 跳过 | 耗时 (秒) |
|-----------|--------|------|------|------|------|-----------|
"""
    
    # 添加每个 testsuite 的统计
    for suite in pytest_results['testsuites']:
        module_name = suite['name'].split('.')[-1] if '.' in suite['name'] else suite['name']
        report += f"| {module_name} | {suite['tests']} | {suite['tests'] - suite['failures'] - suite['errors'] - suite['skipped']} | {suite['failures']} | {suite['errors']} | {suite['skipped']} | {suite['time']:.2f} |\n"
    
    # 添加失败用例详情
    failed_cases = [
        tc for tc in pytest_results['all_testcases']
        if tc['status'] in ['FAILED', 'ERROR']
    ]
    
    if failed_cases:
        report += """
### 2.2 失败用例分析

| 用例 ID | 测试方法 | 模块 | 失败类型 | 错误信息 |
|---------|----------|------|----------|----------|
"""
        for i, case in enumerate(failed_cases[:10], 1):  # 只显示前 10 个
            short_msg = case.get('message', '')[:50].replace('\n', ' ')
            report += f"| {test_phase.upper()}-{i:03d} | {case['name']} | {case['classname'].split('.')[0]} | {case['type']} | {short_msg}... |\n"
    
    # 覆盖率分析
    if coverage_data:
        report += """
---

## 📉 3. 覆盖率分析

### 3.1 总体覆盖率

"""
        if coverage_data['statement_coverage'] >= 80:
            report += f"✅ **代码覆盖率达到目标** ({coverage_data['statement_coverage']:.1f}% ≥ 80%)\n\n"
        else:
            report += f"⚠️  **代码覆盖率未达标** ({coverage_data['statement_coverage']:.1f}% < 80%)\n\n"
        
        # 列出未覆盖的关键文件
        if coverage_data['files']:
            low_coverage_files = [
                (file, data['summary']['percent_covered'])
                for file, data in coverage_data['files'].items()
                if data['summary']['percent_covered'] < 50
            ]
            
            if low_coverage_files:
                report += "### 3.2 低覆盖率文件（< 50%）\n\n"
                report += "| 文件 | 覆盖率 |\n|------|--------|\n"
                for file, cov in sorted(low_coverage_files, key=lambda x: x[1])[:10]:
                    report += f"| {file.split('/')[-1]} | {cov:.1f}% |\n"
    
    # 质量评估
    report += f"""
---

## 🎯 4. 质量评估

### 4.1 测试充分性

- **测试质量评分**: {quality['assessment']}
- **通过率**: {quality['pass_rate']:.1f}%

"""
    
    if quality['pass_rate'] >= 95:
        report += "✅ 测试用例执行率优秀，几乎全部通过\n"
    elif quality['pass_rate'] >= 80:
        report += "✅ 测试用例执行率良好，少量失败需修复\n"
    elif quality['pass_rate'] >= 60:
        report += "⚠️ 测试用例执行率合格，但有较多失败用例\n"
    else:
        report += "❌ 测试用例执行率不足，需大量修复和改进\n"
    
    # 改进建议
    report += """
---

## 💡 5. 改进建议

### 5.1 短期（立即执行）

"""
    
    if pytest_results['failed'] > 0 or pytest_results['errors'] > 0:
        report += f"1. [ ] **修复 {pytest_results['failed'] + pytest_results['errors']} 个失败用例**\n"
        report += "   - 优先修复核心功能的测试\n"
        report += "   - 分析失败原因，是代码 bug 还是测试问题\n"
    
    if coverage_data and coverage_data['statement_coverage'] < 80:
        report += f"2. [ ] **提升代码覆盖率至 80%+** (当前：{coverage_data['statement_coverage']:.1f}%)\n"
        report += "   - 为未测试的核心功能添加测试\n"
        report += "   - 补充边界条件和异常路径测试\n"
    
    report += """
### 5.2 中期（下个迭代）

1. [ ] 增加集成测试覆盖关键业务流程
2. [ ] 实现性能基准测试
3. [ ] 添加端到端 (E2E) 测试场景

---

## ✅ 6. 结论

"""
    
    # 根据结果给出结论
    if quality['pass_rate'] >= 95 and (not coverage_data or coverage_data['statement_coverage'] >= 80):
        report += """### ✅ 通过测试，准予发布

- 所有核心功能测试通过
- 代码覆盖率达标
- 无严重缺陷

**建议**: 可以进入下一阶段（集成测试/UAT）
"""
    elif quality['pass_rate'] >= 80:
        report += """### ⚠️ 有条件通过

- 大部分测试通过
- 存在少量失败用例需修复
- 建议在修复后复测

**建议**: 修复失败用例后可发布
"""
    else:
        report += """### ❌ 不通过，需重新测试

- 失败用例过多
- 核心功能可能存在缺陷

**建议**: 修复所有失败用例并重新测试
"""
    
    # 保存报告
    Path(output_path).write_text(report, encoding='utf-8')
    print(f"\n✅ 测试报告已生成：{output_path}")
    print(f"📊 测试质量评估：{quality['assessment']}")
    print(f"📈 通过率：{quality['pass_rate']:.1f}%")
    if coverage_data:
        print(f"📉 代码覆盖率：{coverage_data['statement_coverage']:.1f}%")


def main():
    parser = argparse.ArgumentParser(description='生成测试分析报告')
    parser.add_argument('--project', type=str, default='RAG 文档问答系统',
                        help='项目名称')
    parser.add_argument('--phase', type=str, default='unit',
                        choices=['unit', 'integration', 'e2e', 'uat'],
                        help='测试阶段')
    parser.add_argument('--xml', type=str, default='test-results/results.xml',
                        help='pytest JUnit XML 文件路径')
    parser.add_argument('--coverage', type=str, default='coverage.json',
                        help='coverage.py JSON 文件路径')
    parser.add_argument('--output', type=str, default='docs/test_report.md',
                        help='输出报告路径')
    
    args = parser.parse_args()
    
    print(f"🔍 开始生成测试报告...")
    print(f"   项目：{args.project}")
    print(f"   阶段：{args.phase}")
    
    # 解析测试结果
    pytest_results = parse_pytest_xml(args.xml)
    coverage_data = parse_coverage_json(args.coverage)
    
    if pytest_results:
        # 生成报告
        generate_markdown_report(
            project_name=args.project,
            test_phase=args.phase,
            pytest_results=pytest_results,
            coverage_data=coverage_data,
            output_path=args.output
        )
    else:
        print("❌ 无法解析测试结果，请检查 XML 文件是否正确")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
