"""
TextChunker 单元测试
"""
import pytest
from app.chunkers.semantic_chunker import TextChunker, TextChunk


class TestTextChunker:
    """TextChunker 单元测试类"""
    
    @pytest.fixture
    def chunker(self):
        """创建分块器实例"""
        return TextChunker(chunk_size=100, overlap=20)
    
    def test_chunk_by_semantic_empty_text(self, chunker):
        """测试空文本分块"""
        text = ""
        chunks = chunker.chunk_by_semantic(text)
        
        assert len(chunks) == 0
    
    def test_chunk_by_semantic_single_paragraph(self, chunker):
        """测试单个段落分块"""
        text = "这是一个测试段落。内容不是很长，应该可以作为一个完整的块。"
        chunks = chunker.chunk_by_semantic(text)
        
        assert len(chunks) >= 1
        assert chunks[0].content == text
        assert chunks[0].token_count > 0
    
    def test_chunk_by_semantic_multiple_paragraphs(self, chunker):
        """测试多个段落分块"""
        text = "第一段内容。\n\n第二段内容。\n\n第三段内容。"
        chunks = chunker.chunk_by_semantic(text)
        
        assert len(chunks) >= 1
        # 验证所有块的内容都不为空
        assert all(chunk.content.strip() for chunk in chunks)
    
    def test_chunk_by_semantic_large_paragraph(self, chunker):
        """测试大段落拆分"""
        # 创建一个包含超长句子的段落（总长显著超过 chunk_size=100）
        very_long_sentence = "这是一个非常非常非常非常非常非常非常非常长的句子。"
        text = very_long_sentence * 6  # 6 个长句，共 150 字符
        
        chunks = chunker.chunk_by_semantic(text)
        
        # 应该拆分成多个块（因为总长 150 > 100）
        assert len(chunks) >= 2
        # 验证每个块的大小都不超过限制太多
        for chunk in chunks:
            assert len(chunk.content) <= chunker.chunk_size * 1.5
    
    def test_chunk_token_count_estimation(self, chunker):
        """测试 token 数量估算"""
        text = "测试内容" * 10
        chunks = chunker.chunk_by_semantic(text)
        
        assert len(chunks) > 0
        # 验证 token 数量估算合理（约 4 字符/token）
        for chunk in chunks:
            expected_tokens = len(chunk.content) // 4
            assert chunk.token_count == expected_tokens
    
    def test_split_by_paragraph(self, chunker):
        """测试段落分割方法"""
        text = "第一段。\n\n第二段。\n\n\n\n第三段。"
        paragraphs = chunker._split_by_paragraph(text)
        
        assert len(paragraphs) == 3
        assert "第一段。" in paragraphs
        assert "第二段。" in paragraphs
        assert "第三段。" in paragraphs
    
    def test_merge_paragraphs_logic(self, chunker):
        """测试段落合并逻辑"""
        text = "小段 1。\n\n小段 2。\n\n小段 3。\n\n小段 4。"
        chunks = chunker.chunk_by_semantic(text)
        
        # 验证小段落被合并
        assert len(chunks) >= 1
        # 第一个块应该包含多个段落
        if len(chunks) == 1:
            assert "小段 1" in chunks[0].content
            assert "小段 4" in chunks[0].content


class TestTextChunk:
    """TextChunk 数据类测试"""
    
    def test_text_chunk_creation(self):
        """测试文本块创建"""
        content = "测试内容"
        chunk = TextChunk(content=content)
        
        assert chunk.content == content
        assert chunk.token_count == len(content) // 4
        assert chunk.start_index == 0
        assert chunk.end_index == 0
    
    def test_text_chunk_with_position(self):
        """测试带位置的文本块"""
        content = "测试内容"
        chunk = TextChunk(
            content=content,
            start_index=10,
            end_index=20
        )
        
        assert chunk.content == content
        assert chunk.start_index == 10
        assert chunk.end_index == 20
