"""
PDF 文档解析器
使用 PyMuPDF (fitz) 进行解析
"""
import fitz  # PyMuPDF
from typing import Dict
from .base_parser import DocumentParser
from app.exceptions import DocumentParseError


class PDFParser(DocumentParser):
    """
    PDF 文档解析器
    
    特性:
    - 提取所有页面的文本
    - 保留基本的段落结构
    - 支持加密 PDF（如果提供密码）
    """
    
    @classmethod
    def get_supported_mime_types(cls) -> list[str]:
        return ["application/pdf"]
    
    async def parse(self, file_content: bytes) -> str:
        """
        解析 PDF 文件为文本
        
        Args:
            file_content: PDF 文件二进制内容
            
        Returns:
            str: 提取的文本内容
            
        Raises:
            DocumentParseError: 解析失败时抛出
        """
        try:
            # 打开 PDF
            doc = fitz.open(stream=file_content, filetype="pdf")
            
            # 提取所有页面的文本
            text_parts = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text("text")
                
                # 添加页码标记（可选）
                if page_text.strip():
                    text_parts.append(f"[第{page_num + 1}页]\n{page_text}")
            
            # 关闭文档
            doc.close()
            
            # 合并所有页面文本
            full_text = "\n\n".join(text_parts)
            
            return full_text.strip()
            
        except Exception as e:
            raise DocumentParseError(f"PDF 解析失败：{str(e)}")
