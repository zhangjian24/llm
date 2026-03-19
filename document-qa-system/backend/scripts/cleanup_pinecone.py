"""
迁移后清理脚本
移除 Pinecone 相关的代码和依赖，优化项目结构
"""

import os
import shutil
from pathlib import Path
import json
from typing import List, Dict, Any


class MigrationCleanup:
    """迁移清理工具"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.backend_root = self.project_root / "backend"
        
    def remove_pinecone_dependencies(self) -> List[str]:
        """移除 Pinecone 相关依赖"""
        print("🧹 移除 Pinecone 依赖...")
        removed_items = []
        
        # 更新 requirements.txt
        requirements_file = self.backend_root / "requirements.txt"
        if requirements_file.exists():
            with open(requirements_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 过滤掉 Pinecone 相关行
            cleaned_lines = []
            for line in lines:
                if 'pinecone' not in line.lower():
                    cleaned_lines.append(line)
                else:
                    removed_items.append(f"依赖: {line.strip()}")
            
            with open(requirements_file, 'w', encoding='utf-8') as f:
                f.writelines(cleaned_lines)
            
            print(f"✅ 更新 {requirements_file}")
        
        return removed_items
    
    def remove_pinecone_service_file(self) -> List[str]:
        """移除 Pinecone 服务文件"""
        print("🗑️  移除 Pinecone 服务文件...")
        removed_items = []
        
        pinecone_service_file = self.backend_root / "app" / "services" / "pinecone_service.py"
        if pinecone_service_file.exists():
            # 先备份到 archive 目录
            archive_dir = self.backend_root / "archive" / "pinecone_backup"
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            backup_file = archive_dir / "pinecone_service.py"
            shutil.copy2(pinecone_service_file, backup_file)
            removed_items.append(f"备份文件: {backup_file}")
            
            # 删除原文件
            pinecone_service_file.unlink()
            removed_items.append(f"删除文件: {pinecone_service_file}")
            print(f"✅ 移除 Pinecone 服务文件")
        
        return removed_items
    
    def clean_pinecone_references(self) -> List[str]:
        """清理代码中的 Pinecone 引用"""
        print("🔍 清理 Pinecone 引用...")
        removed_items = []
        
        # 需要检查的文件模式
        file_patterns = [
            "*.py",
            "*.md",
            "*.txt"
        ]
        
        # 需要清理的目录
        check_dirs = [
            self.backend_root / "app",
            self.backend_root / "tests",
            self.backend_root / "scripts",
            self.project_root / "docs"
        ]
        
        for check_dir in check_dirs:
            if not check_dir.exists():
                continue
                
            for pattern in file_patterns:
                for file_path in check_dir.rglob(pattern):
                    if file_path.is_file():
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # 检查是否包含 Pinecone 引用
                            if 'pinecone' in content.lower() or 'Pinecone' in content:
                                # 备份原文件
                                rel_path = file_path.relative_to(self.project_root)
                                backup_path = self.backend_root / "archive" / "pinecone_backup" / rel_path
                                backup_path.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(file_path, backup_path)
                                removed_items.append(f"备份文件: {rel_path}")
                                
                                # 清理引用（这里只记录，不实际修改）
                                removed_items.append(f"发现 Pinecone 引用: {rel_path}")
                                
                        except Exception as e:
                            print(f"⚠️  处理文件 {file_path} 时出错: {e}")
        
        return removed_items
    
    def remove_pinecone_test_files(self) -> List[str]:
        """移除 Pinecone 测试文件"""
        print("🧪 移除 Pinecone 测试文件...")
        removed_items = []
        
        test_files = [
            self.backend_root / "test_pinecone_service.py",
            self.backend_root / "check_pinecone.py"
        ]
        
        for test_file in test_files:
            if test_file.exists():
                # 备份到 archive
                archive_dir = self.backend_root / "archive" / "pinecone_backup"
                archive_dir.mkdir(parents=True, exist_ok=True)
                
                backup_file = archive_dir / test_file.name
                shutil.copy2(test_file, backup_file)
                removed_items.append(f"备份测试文件: {backup_file}")
                
                # 删除原文件
                test_file.unlink()
                removed_items.append(f"删除测试文件: {test_file}")
                print(f"✅ 移除测试文件 {test_file.name}")
        
        return removed_items
    
    def update_environment_config(self) -> List[str]:
        """更新环境配置文件"""
        print("⚙️  更新环境配置...")
        removed_items = []
        
        # 更新 .env.example
        env_example = self.backend_root / ".env.example"
        if env_example.exists():
            with open(env_example, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 移除 Pinecone 相关配置
            cleaned_lines = []
            removing_section = False
            
            for line in lines:
                if '# Pinecone 配置' in line or '# ==================== Pinecone 向量数据库 ====================' in line:
                    removing_section = True
                    removed_items.append(f"移除配置段落: Pinecone 配置")
                
                if removing_section:
                    if line.strip() == '' or (line.startswith('#') and 'Pinecone' not in line and '向量数据库' not in line):
                        removing_section = False
                        if line.strip() != '':
                            cleaned_lines.append(line)
                else:
                    if not any(keyword in line for keyword in ['PINECONE_', 'pinecone']):
                        cleaned_lines.append(line)
                    else:
                        removed_items.append(f"移除配置行: {line.strip()}")
            
            with open(env_example, 'w', encoding='utf-8') as f:
                f.writelines(cleaned_lines)
            
            print(f"✅ 更新 {env_example}")
        
        return removed_items
    
    def create_cleanup_report(self, cleanup_actions: Dict[str, List[str]]):
        """创建清理报告"""
        print("\n" + "=" * 60)
        print("📋 清理报告")
        print("=" * 60)
        
        total_items = 0
        for category, items in cleanup_actions.items():
            if items:
                print(f"\n{category}:")
                for item in items:
                    print(f"  - {item}")
                total_items += len(items)
        
        print(f"\n总计清理项目: {total_items}")
        
        # 保存报告
        report_file = self.backend_root / "archive" / "pinecone_backup" / "cleanup_report.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        report_data = {
            "cleanup_actions": cleanup_actions,
            "total_items_removed": total_items,
            "timestamp": __import__('time').time()
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细报告已保存到: {report_file}")
        print(f"备份文件位于: {self.backend_root / 'archive' / 'pinecone_backup'}")
    
    def run_cleanup(self, safe_mode: bool = True):
        """执行清理操作"""
        print("🚀 开始迁移后清理")
        print("=" * 60)
        print(f"项目根目录: {self.project_root}")
        print(f"安全模式: {'开启' if safe_mode else '关闭'}")
        print()
        
        cleanup_actions = {
            "移除依赖": [],
            "移除服务文件": [],
            "清理引用": [],
            "移除测试文件": [],
            "更新配置": []
        }
        
        try:
            # 1. 移除依赖
            cleanup_actions["移除依赖"] = self.remove_pinecone_dependencies()
            
            # 2. 移除服务文件
            cleanup_actions["移除服务文件"] = self.remove_pinecone_service_file()
            
            # 3. 移除测试文件
            cleanup_actions["移除测试文件"] = self.remove_pinecone_test_files()
            
            # 4. 更新环境配置
            cleanup_actions["更新配置"] = self.update_environment_config()
            
            # 5. 清理引用（仅记录，不修改）
            cleanup_actions["清理引用"] = self.clean_pinecone_references()
            
            # 生成报告
            self.create_cleanup_report(cleanup_actions)
            
            print("\n" + "=" * 60)
            print("✅ 清理完成!")
            print("⚠️  注意：引用清理仅为扫描，未实际修改文件")
            print("💡 建议手动检查并更新相关文档")
            
        except Exception as e:
            print(f"\n❌ 清理过程中出错: {e}")
            raise


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='迁移后清理工具')
    parser.add_argument('--project-root', default='.', help='项目根目录')
    parser.add_argument('--safe-mode', action='store_true', default=True, help='安全模式（默认开启）')
    
    args = parser.parse_args()
    
    cleaner = MigrationCleanup(args.project_root)
    cleaner.run_cleanup(safe_mode=args.safe_mode)


if __name__ == "__main__":
    main()