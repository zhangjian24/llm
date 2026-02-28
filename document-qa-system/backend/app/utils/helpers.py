import os
import hashlib
from typing import Optional

def generate_document_id(content: str, filename: str) -> str:
    """生成文档唯一ID"""
    content_hash = hashlib.md5(content.encode()).hexdigest()
    return f"{os.path.splitext(filename)[0]}_{content_hash[:8]}"

def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f}{size_names[i]}"

def sanitize_filename(filename: str) -> str:
    """清理文件名"""
    # 移除不允许的字符
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()

def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """验证文件扩展名"""
    _, ext = os.path.splitext(filename.lower())
    return ext in allowed_extensions

def extract_text_from_error(error: Exception) -> str:
    """从异常中提取错误文本"""
    return str(error).split(":")[-1].strip() if ":" in str(error) else str(error)