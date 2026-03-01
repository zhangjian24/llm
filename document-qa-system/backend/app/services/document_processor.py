import os
import uuid
import re
from typing import List, Dict, Any
from pathlib import Path
import PyPDF2
from docx import Document
from bs4 import BeautifulSoup
import asyncio

from app.core.config import settings
from app.core.logging_config import logger
from app.core.exceptions import DocumentProcessingError

class DocumentProcessor:
    """文档处理器 - 支持多种文档格式"""
    
    def __init__(self):
        self.supported_extensions = settings.allowed_extensions_list
        self.upload_folder = Path(settings.UPLOAD_FOLDER)
        self.upload_folder.mkdir(exist_ok=True)
        
    async def process_document(self, file_path: str, filename: str) -> Dict[str, Any]:
        """处理文档并提取文本内容"""
        try:
            extension = Path(filename).suffix.lower()
            
            if extension not in self.supported_extensions:
                raise DocumentProcessingError(f"不支持的文件格式: {extension}")
            
            # 根据文件类型选择处理方法
            if extension == '.pdf':
                text_content = await self._process_pdf(file_path)
            elif extension in ['.docx', '.doc']:
                text_content = await self._process_docx(file_path)
            elif extension in ['.txt']:
                text_content = await self._process_txt(file_path)
            elif extension in ['.html', '.htm']:
                text_content = await self._process_html(file_path)
            else:
                raise DocumentProcessingError(f"未实现的文件格式处理: {extension}")
            
            # 生成文档ID
            document_id = str(uuid.uuid4())
            
            # 分割文本为chunks
            chunks = self._split_text_into_chunks(text_content)
            
            result = {
                'document_id': document_id,
                'filename': filename,
                'content': text_content,
                'chunks': chunks,
                'chunk_count': len(chunks),
                'file_size': os.path.getsize(file_path),
                'file_extension': extension
            }
            
            logger.info(f"文档处理完成: {filename}, chunks: {len(chunks)}")
            return result
            
        except Exception as e:
            logger.error(f"文档处理失败 {filename}: {str(e)}")
            raise DocumentProcessingError(f"文档处理失败: {str(e)}")
    
    async def _process_pdf(self, file_path: str) -> str:
        """处理PDF文件"""
        try:
            text_content = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text() + "\n"
            return text_content.strip()
        except Exception as e:
            raise DocumentProcessingError(f"PDF处理失败: {str(e)}")
    
    async def _process_docx(self, file_path: str) -> str:
        """处理Word文档"""
        try:
            doc = Document(file_path)
            text_content = ""
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
            return text_content.strip()
        except Exception as e:
            raise DocumentProcessingError(f"Word文档处理失败: {str(e)}")
    
    async def _process_txt(self, file_path: str) -> str:
        """处理文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as file:
                    return file.read().strip()
            except Exception:
                raise DocumentProcessingError("文本文件编码无法识别")
        except Exception as e:
            raise DocumentProcessingError(f"文本文件处理失败: {str(e)}")
    
    async def _process_html(self, file_path: str) -> str:
        """处理HTML文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                # 移除script和style标签
                for script in soup(["script", "style"]):
                    script.decompose()
                return soup.get_text().strip()
        except Exception as e:
            raise DocumentProcessingError(f"HTML文件处理失败: {str(e)}")
    
    def _split_text_into_chunks(self, text: str, chunk_size: int = 512, overlap: int = 77) -> List[str]:
        """将文本分割成chunks用于向量化 - 基于文章推荐的最佳实践
        Chunk Size: 512 tokens (黄金值)
        Overlap: 15% (77 tokens) - 平衡信息完整性和索引规模
        分隔符优先级：段落、句子、空格
        """
        if not text:
            return []
        
        # 定义分隔符优先级
        separators = [
            "\n\n",  # 段落分隔
            "\n",    # 行分隔
            "。", "！", "？",  # 中文句号、感叹号、问号
            ".", "!", "?",  # 英文句号、感叹号、问号
            " ",     # 空格
            ""       # 空字符串（最后兜底）
        ]
        
        # 递归字符切分逻辑
        chunks = []
        current_pos = 0
        
        while current_pos < len(text):
            # 尝试按优先级查找分隔符
            found_separator = None
            separator_pos = len(text)
            
            for sep in separators:
                if sep == "":
                    continue
                pos = text.find(sep, current_pos + chunk_size - overlap)
                if pos != -1 and pos < separator_pos:
                    separator_pos = pos
                    found_separator = sep
            
            # 如果没有找到合适的分隔符，使用固定位置
            if found_separator is None:
                end_pos = min(current_pos + chunk_size, len(text))
            else:
                end_pos = separator_pos + len(found_separator)
            
            # 确保最小长度
            if end_pos - current_pos < 20:
                end_pos = min(current_pos + 512, len(text))
            
            chunk = text[current_pos:end_pos].strip()
            if chunk and len(chunk) > 20:
                chunks.append(chunk)
            
            # 更新当前位置，考虑重叠
            current_pos = max(current_pos + chunk_size - overlap, end_pos - overlap)
            
            # 防止无限循环
            if current_pos >= len(text):
                break
        
        return chunks
    
    def save_uploaded_file(self, file_data: bytes, filename: str) -> str:
        """保存上传的文件"""
        try:
            # 生成唯一文件名
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = self.upload_folder / unique_filename
            
            # 写入文件
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            logger.info(f"文件保存成功: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"文件保存失败: {str(e)}")
            raise DocumentProcessingError(f"文件保存失败: {str(e)}")
    
    def delete_document_file(self, file_path: str) -> bool:
        """删除文档文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"文件删除成功: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"文件删除失败: {str(e)}")
            return False

# 创建全局实例
document_processor = DocumentProcessor()