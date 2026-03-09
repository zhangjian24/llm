"""
文档解析器模块
"""
from .base_parser import DocumentParser, ParserRegistry
from .pdf_parser import PDFParser
from .docx_parser import DocxParser
from .text_parser import TextParser

# 自动注册所有解析器
# 这样在导入 app.parsers 时会自动完成注册
ParserRegistry.register("application/pdf", PDFParser)
ParserRegistry.register(
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    DocxParser
)
ParserRegistry.register("text/plain", TextParser)
ParserRegistry.register("text/markdown", TextParser)

__all__ = [
    "DocumentParser",
    "ParserRegistry",
    "PDFParser",
    "DocxParser",
    "TextParser"
]
