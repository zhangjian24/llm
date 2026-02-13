import hashlib
import uuid
from datetime import datetime
from typing import List, Dict, Any
import tiktoken

def generate_document_id(filename: str, content: bytes) -> str:
    """生成文档唯一ID"""
    content_hash = hashlib.sha256(content).hexdigest()[:16]
    filename_hash = hashlib.sha256(filename.encode()).hexdigest()[:8]
    return f"doc_{filename_hash}_{content_hash}"

def generate_chunk_id(document_id: str, chunk_index: int) -> str:
    """生成文本块唯一ID"""
    return f"{document_id}_chunk_{chunk_index}"

def calculate_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """计算文本token数量"""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # 估算：中文约1个字符=1.5个token，英文约3个字符=1个token
        chinese_chars = len([c for c in text if ord(c) > 127])
        english_chars = len(text) - chinese_chars
        return int(chinese_chars * 1.5 + english_chars / 3)

def format_timestamp(dt: datetime) -> str:
    """格式化时间戳"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def sanitize_filename(filename: str) -> str:
    """清理文件名"""
    # 移除危险字符
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    return filename.strip()

def truncate_text(text: str, max_length: int = 100) -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def merge_metadata(*metadatas: Dict[str, Any]) -> Dict[str, Any]:
    """合并多个元数据字典"""
    result = {}
    for metadata in metadatas:
        result.update(metadata)
    return result