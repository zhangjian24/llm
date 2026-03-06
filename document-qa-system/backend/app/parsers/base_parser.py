"""
文档解析器基类
定义解析器的统一接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Type


class DocumentParser(ABC):
    """
    文档解析器抽象基类
    
    所有文档解析器都必须继承此类并实现 parse 方法
    """
    
    @abstractmethod
    async def parse(self, file_content: bytes) -> str:
        """
        解析文档内容为纯文本
        
        Args:
            file_content: 文件二进制内容
            
        Returns:
            str: 解析后的文本内容
            
        Raises:
            DocumentParseError: 解析失败时抛出
        """
        pass
    
    @classmethod
    def get_supported_mime_types(cls) -> list[str]:
        """
        获取支持的 MIME 类型列表
        
        Returns:
            list[str]: MIME 类型列表
        """
        return []


class ParserRegistry:
    """
    解析器注册表（插件化设计）
    
    使用示例:
        ParserRegistry.register("pdf", PDFParser)
        parser = ParserRegistry.get_parser("application/pdf")
    """
    
    _parsers: Dict[str, Type[DocumentParser]] = {}
    
    @classmethod
    def register(cls, mime_type: str, parser_class: Type[DocumentParser]):
        """
        注册解析器
        
        Args:
            mime_type: MIME 类型
            parser_class: 解析器类
        """
        cls._parsers[mime_type] = parser_class
    
    @classmethod
    def get_parser(cls, mime_type: str) -> DocumentParser:
        """
        获取解析器实例
        
        Args:
            mime_type: MIME 类型
            
        Returns:
            DocumentParser: 解析器实例
            
        Raises:
            UnsupportedFileTypeError: 不支持的文件类型
        """
        parser_class = cls._parsers.get(mime_type)
        if not parser_class:
            from app.exceptions import UnsupportedFileTypeError
            raise UnsupportedFileTypeError(mime_type)
        
        return parser_class()
    
    @classmethod
    def is_supported(cls, mime_type: str) -> bool:
        """
        判断是否支持该 MIME 类型
        
        Args:
            mime_type: MIME 类型
            
        Returns:
            bool: 是否支持
        """
        return mime_type in cls._parsers
