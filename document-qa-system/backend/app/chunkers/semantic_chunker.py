"""
语义分块算法
基于段落和语义边界的智能分块
"""
from typing import List
from dataclasses import dataclass


@dataclass
class TextChunk:
    """
    文本块数据类
    
    Attributes:
        content: 文本内容
        token_count: Token 数量（估算）
        start_index: 在原文中的起始位置
        end_index: 在原文中的结束位置
    """
    content: str
    token_count: int = 0
    start_index: int = 0
    end_index: int = 0
    
    def __post_init__(self):
        # 估算 token 数量（中文约 4 字符/token，英文约 4 字符/token）
        self.token_count = len(self.content) // 4


class TextChunker:
    """
    文本分块器
    
    策略:
    1. 先按段落分割（保留语义完整性）
    2. 过大的段落按句子二次分割
    3. 合并小段落至目标大小范围
    
    Attributes:
        chunk_size: 目标块大小（字符数）
        overlap: 块间重叠（字符数）
    """
    
    def __init__(self, chunk_size: int = 800, overlap: int = 150):
        """
        初始化分块器
        
        Args:
            chunk_size: 目标块大小
            overlap: 重叠大小
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_by_semantic(self, text: str) -> List[TextChunk]:
        """
        基于语义边界的分块算法
        
        Args:
            text: 原始文本
            
        Returns:
            List[TextChunk]: 文本块列表
        """
        # Step 1: 按段落分割
        paragraphs = self._split_by_paragraph(text)
        
        # Step 2: 过滤空段落
        paragraphs = [p for p in paragraphs if p.strip()]
        
        # Step 3: 合并段落至目标大小
        chunks = []
        current_chunk = ""
        current_start = 0
        
        char_index = 0
        for paragraph in paragraphs:
            para_start = char_index
            para_end = char_index + len(paragraph)
            
            if not current_chunk:
                # 当前块为空，直接添加
                current_chunk = paragraph
                current_start = para_start
            elif len(current_chunk) + len(paragraph) <= self.chunk_size:
                # 可以合并到当前块
                current_chunk += "\n\n" + paragraph
            else:
                # 当前块已满，保存并开始新块
                if current_chunk:
                    chunk = TextChunk(
                        content=current_chunk,
                        start_index=current_start,
                        end_index=para_start
                    )
                    chunks.append(chunk)
                
                # 如果段落本身就超过 chunk_size，需要拆分
                if len(paragraph) > self.chunk_size:
                    sub_chunks = self._split_large_paragraph(paragraph)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = paragraph
                    current_start = para_start
            
            char_index = para_end
        
        # 添加最后一个块
        if current_chunk:
            # 如果最后一个块超过 chunk_size，需要拆分
            if len(current_chunk) > self.chunk_size:
                sub_chunks = self._split_large_paragraph(current_chunk)
                chunks.extend(sub_chunks)
            else:
                chunk = TextChunk(
                    content=current_chunk,
                    start_index=current_start,
                    end_index=len(text)
                )
                chunks.append(chunk)
        
        return chunks
    
    def _split_by_paragraph(self, text: str) -> List[str]:
        """
        按段落分割文本
        
        Args:
            text: 原始文本
            
        Returns:
            List[str]: 段落列表（过滤空段落）
        """
        # 按双换行符分割（Markdown 段落）
        paragraphs = text.split('\n\n')
        
        # 清理每段的首尾空白并过滤空段落
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        return paragraphs
    
    def _split_large_paragraph(self, paragraph: str, max_size: int = None) -> List[TextChunk]:
        """
        拆分大段落（按句子 + 固定长度）
            
        Args:
            paragraph: 大段落
            max_size: 最大块大小
                
        Returns:
            List[TextChunk]: 文本块列表
        """
        if max_size is None:
            max_size = self.chunk_size
            
        # 按句子分割（中文句号、问号、感叹号）
        sentences = []
        current_sentence = ""
            
        for char in paragraph:
            current_sentence += char
            if char in '。！？!?':
                sentences.append(current_sentence.strip())
                current_sentence = ""
            
        # 处理剩余部分
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
            
        # 合并句子至目标大小（确保不超过 max_size）
        chunks = []
        current_chunk = ""
            
        for sentence in sentences:
            # 如果当前块 + 新句子超过限制，保存当前块
            if len(current_chunk) + len(sentence) > max_size:
                if current_chunk:
                    chunks.append(TextChunk(content=current_chunk))
                current_chunk = sentence
            else:
                # 可以添加到当前块
                current_chunk += sentence
            
        # 添加最后一个块
        if current_chunk:
            chunks.append(TextChunk(content=current_chunk))
            
        # 如果还有超过 max_size 的块，强制按固定长度拆分
        final_chunks = []
        for chunk in chunks:
            if len(chunk.content) > max_size:
                # 强制按 max_size 拆分
                content = chunk.content
                for i in range(0, len(content), max_size):
                    sub_content = content[i:i+max_size]
                    final_chunks.append(TextChunk(
                        content=sub_content,
                        start_index=chunk.start_index + i,
                        end_index=chunk.start_index + i + len(sub_content)
                    ))
            else:
                final_chunks.append(chunk)
            
        return final_chunks
