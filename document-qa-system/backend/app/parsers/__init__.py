"""
文档解析器模块
"""
from .base_parser import DocumentParser, ParserRegistry
from .pdf_parser import PDFParser
from .docx_parser import DocxParser
from .text_parser import TextParser

__all__ = [
    "DocumentParser",
    "ParserRegistry", 
    "PDFParser",
    "DocxParser",
    "TextParser"
]
