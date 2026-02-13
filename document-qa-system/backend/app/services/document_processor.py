import PyPDF2
import docx
from typing import List, Dict, Any, Optional
import re
from app.core.config import settings
from app.utils.helpers import generate_chunk_id, calculate_tokens
from app.core.exceptions import DocumentProcessingException
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class DocumentProcessor:
    """文档处理器"""
    
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
    
    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """从PDF文件提取文本"""
        try:
            pdf_reader = PyPDF2.PdfReader(file_content)
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"PDF文本提取失败: {str(e)}")
            raise DocumentProcessingException(f"PDF处理失败: {str(e)}")
    
    def extract_text_from_docx(self, file_content: bytes) -> str:
        """从DOCX文件提取文本"""
        try:
            from io import BytesIO
            doc = docx.Document(BytesIO(file_content))
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"DOCX文本提取失败: {str(e)}")
            raise DocumentProcessingException(f"DOCX处理失败: {str(e)}")
    
    def extract_text_from_txt(self, file_content: bytes, encoding: str = 'utf-8') -> str:
        """从TXT文件提取文本"""
        try:
            text = file_content.decode(encoding)
            return text.strip()
            
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                text = file_content.decode('gbk')
                return text.strip()
            except UnicodeDecodeError:
                raise DocumentProcessingException("不支持的文本编码格式")
        except Exception as e:
            logger.error(f"TXT文本提取失败: {str(e)}")
            raise DocumentProcessingException(f"TXT处理失败: {str(e)}")
    
    def clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符（保留中文、英文、数字和基本标点）
        text = re.sub(r'[^\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df\u2a700-\u2b73f'
                      r'\u2b740-\u2b81f\u2b820-\u2ceaf\uf900-\ufaff\u3300-\u33ff'
                      r'\ufe30-\ufe4f\uf900-\ufaff\u2f800-\u2fa1f'
                      r'a-zA-Z0-9\s\.,!?;:()"\']', '', text)
        return text.strip()
    
    def split_text_into_chunks(self, text: str, chunk_size: Optional[int] = None, 
                              overlap: Optional[int] = None) -> List[str]:
        """将文本分割成块"""
        if chunk_size is None:
            chunk_size = self.chunk_size
        if overlap is None:
            overlap = self.chunk_overlap
        
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            # 确定结束位置
            end = min(start + chunk_size, len(text))
            
            # 如果不是最后一块且需要重叠
            if end < len(text) and overlap > 0:
                # 寻找合适的分割点（句子边界）
                split_point = self._find_best_split_point(text, start, end, overlap)
                if split_point > start:
                    end = split_point
                else:
                    # 如果找不到合适的分割点，强制在指定位置分割
                    end = start + chunk_size
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # 移动起始位置
            start = end - overlap if overlap < end else end
        
        return chunks
    
    def _find_best_split_point(self, text: str, start: int, end: int, 
                              min_overlap: int) -> int:
        """寻找最佳分割点"""
        # 优先寻找句子边界
        for delimiter in ['。', '！', '？', '.', '!', '?']:
            pos = text.rfind(delimiter, start + min_overlap, end)
            if pos != -1:
                return pos + 1
        
        # 寻找段落边界
        pos = text.rfind('\n', start + min_overlap, end)
        if pos != -1:
            return pos + 1
        
        # 寻找词语边界
        pos = text.rfind(' ', start + min_overlap, end)
        if pos != -1:
            return pos + 1
        
        return end  # 如果找不到合适的位置，就在末尾分割
    
    def process_document(self, file_content: bytes, filename: str, 
                        content_type: str) -> Dict[str, Any]:
        """处理文档"""
        try:
            logger.info(f"开始处理文档: {filename}")
            
            # 根据文件类型提取文本
            if content_type == 'application/pdf':
                raw_text = self.extract_text_from_pdf(file_content)
            elif content_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                                'application/msword']:
                raw_text = self.extract_text_from_docx(file_content)
            elif content_type == 'text/plain':
                raw_text = self.extract_text_from_txt(file_content)
            else:
                raise DocumentProcessingException(f"不支持的文件类型: {content_type}")
            
            if not raw_text:
                raise DocumentProcessingException("文档内容为空")
            
            # 清理文本
            cleaned_text = self.clean_text(raw_text)
            
            # 分割成块
            chunks = self.split_text_into_chunks(cleaned_text)
            
            # 生成块数据
            chunk_data = []
            for i, chunk in enumerate(chunks):
                chunk_id = generate_chunk_id(filename, i)
                tokens = calculate_tokens(chunk)
                
                chunk_data.append({
                    'id': chunk_id,
                    'text': chunk,
                    'tokens': tokens,
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                })
            
            result = {
                'filename': filename,
                'content_type': content_type,
                'raw_text_length': len(raw_text),
                'cleaned_text_length': len(cleaned_text),
                'chunks': chunk_data,
                'total_chunks': len(chunks),
                'total_tokens': sum(chunk['tokens'] for chunk in chunk_data)
            }
            
            logger.info(f"文档处理完成: {filename}, 共 {len(chunks)} 个文本块")
            return result
            
        except Exception as e:
            logger.error(f"文档处理失败 {filename}: {str(e)}")
            raise DocumentProcessingException(f"文档处理失败: {str(e)}")

# 全局文档处理器实例
document_processor = DocumentProcessor()