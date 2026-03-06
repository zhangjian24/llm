"""
TXT/Markdown 文档解析器
直接读取文本内容
"""
import chardet
from typing import Dict
from .base_parser import DocumentParser
from app.exceptions import DocumentParseError


class TextParser(DocumentParser):
    """
    纯文本/Markdown 文档解析器
    
    特性:
    - 自动检测编码
    - 支持 TXT 和 Markdown 格式
    """
    
    @classmethod
    def get_supported_mime_types(cls) -> list[str]:
        return ["text/plain", "text/markdown"]
    
    async def parse(self, file_content: bytes) -> str:
        """
        解析文本文件
        
        Args:
            file_content: 文件二进制内容
            
        Returns:
            str: 提取的文本内容
            
        Raises:
            DocumentParseError: 解析失败时抛出
        """
        try:
            # 自动检测编码
            detected = chardet.detect(file_content)
            encoding = detected['encoding'] or 'utf-8'
            
            # 解码文本
            try:
                text = file_content.decode(encoding)
            except UnicodeDecodeError:
                # 尝试备用编码
                text = file_content.decode('utf-8', errors='ignore')
            
            return text.strip()
            
        except Exception as e:
            raise DocumentParseError(f"文本文件解析失败：{str(e)}")
