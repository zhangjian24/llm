"""
RAG 文档问答系统 - API测试执行器
生成测试报告
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_test(script_name):
    """运行测试脚本并捕获输出"""
    print(f"\n{'='*80}")
    print(f"执行测试：{script_name}")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*80)
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=120,
            encoding='utf-8'
        )
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        return result.returncode == 0, result.stdout + result.stderr
        
    except subprocess.TimeoutExpired:
        print(f"测试超时（>120 秒）")
        return False, "TIMEOUT"
    except Exception as e:
        print(f"执行失败：{e}")
        return False, str(e)

def generate_report(results, output_path):
    """生成测试报告"""
    report = []
    report.append("# RAG 文档问答系统 - API测试报告\n")
    report.append(f"**执行时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"**测试环境**: Windows / Python {sys.version.split()[0]}\n")
    report.append("")
    
    for script_name, (success, output) in results.items():
        report.append(f"## 测试：{script_name}\n")
        report.append(f"**状态**: {'✅ 通过' if success else '❌ 失败'}\n")
        report.append(f"**输出**:\n```text\n{output[:2000]}\n```\n")
        report.append("")
    
    # 总结
    passed = sum(1 for _, (s, _) in results.items() if s)
    total = len(results)
    report.append("## 测试总结\n")
    report.append(f"- **总测试数**: {total}\n")
    report.append(f"- **通过数**: {passed}\n")
    report.append(f"- **失败数**: {total - passed}\n")
    report.append(f"- **通过率**: {passed/total*100:.1f}%\n")
    
    report_text = "\n".join(report)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print(f"\n测试报告已保存到：{output_path}")
    return report_text

if __name__ == "__main__":
    backend_dir = Path(__file__).parent
    
    tests = {
        "run_api_tests.py": None,
        "test_api_complete.py": None
    }
    
    for script in tests.keys():
        script_path = backend_dir / script
        if script_path.exists():
            success, output = run_test(str(script_path))
            tests[script] = (success, output)
        else:
            print(f"脚本不存在：{script}")
            tests[script] = (False, f"File not found: {script}")
    
    # 生成报告
    report_path = backend_dir / "API_TEST_REPORT.md"
    report = generate_report(tests, report_path)
    print("\n" + "="*80)
    print(report)
