"""引用管理器模块

负责管理文档引用，包括页码定位、原文位置标记等功能。
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from .models import Citation, DocumentChunk, Answer
from agentdoc.core.logger import get_logger


@dataclass
class CitationConfig:
    """引用配置"""
    max_citations_per_answer: int = 5
    min_citation_length: int = 10
    max_citation_length: int = 200
    include_context: bool = True
    context_window: int = 50


class CitationManager:
    """引用管理器
    
    负责从文档块中提取引用信息，包括页码、位置等。
    """
    
    def __init__(self, config: Optional[CitationConfig] = None):
        self.config = config or CitationConfig()
    
    def extract_citations(
        self, 
        answer_text: str, 
        source_chunks: List[DocumentChunk]
    ) -> List[Citation]:
        """从答案文本和源文档块中提取引用"""
        citations = []
        
        for chunk in source_chunks:
            # 查找答案中引用的文本片段
            cited_texts = self._find_cited_text(answer_text, chunk.content)
            
            for cited_text, start_pos, end_pos in cited_texts:
                citation = Citation(
                    document_id=chunk.document_id,
                    page_number=chunk.page_number,
                    chunk_id=chunk.chunk_id,
                    text=cited_text,
                    positions=(start_pos, end_pos),
                    confidence=self._calculate_citation_confidence(cited_text, chunk.content)
                )
                citations.append(citation)
        
        # 按置信度排序并限制数量
        citations.sort(key=lambda x: x.confidence, reverse=True)
        citations = citations[:self.config.max_citations_per_answer]
        
        get_logger(self.__class__.__name__).info(f"提取了 {len(citations)} 个引用")
        return citations
    
    def _find_cited_text(
        self, 
        answer_text: str, 
        chunk_content: str
    ) -> List[Tuple[str, int, int]]:
        """在文档块中查找被引用的文本片段"""
        cited_texts = []
        
        # 将答案分解为句子
        sentences = self._split_into_sentences(answer_text)
        
        for sentence in sentences:
            # 查找句子中的关键短语
            phrases = self._extract_key_phrases(sentence)
            
            for phrase in phrases:
                if len(phrase) < self.config.min_citation_length:
                    continue
                
                # 在文档块中查找匹配的文本
                matches = self._find_text_matches(phrase, chunk_content)
                
                for match_text, start_pos, end_pos in matches:
                    if len(match_text) <= self.config.max_citation_length:
                        cited_texts.append((match_text, start_pos, end_pos))
        
        return cited_texts
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """将文本分解为句子"""
        # 简单的句子分割
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _extract_key_phrases(self, sentence: str) -> List[str]:
        """从句子中提取关键短语"""
        # 简化版：提取较长的词组
        words = sentence.split()
        phrases = []
        
        # 提取2-6个词的短语
        for i in range(len(words)):
            for j in range(i + 2, min(i + 7, len(words) + 1)):
                phrase = ' '.join(words[i:j])
                if len(phrase) >= self.config.min_citation_length:
                    phrases.append(phrase)
        
        return phrases
    
    def _find_text_matches(
        self, 
        phrase: str, 
        content: str
    ) -> List[Tuple[str, int, int]]:
        """在内容中查找文本匹配"""
        matches = []
        phrase_lower = phrase.lower()
        content_lower = content.lower()
        
        # 精确匹配
        start = 0
        while True:
            pos = content_lower.find(phrase_lower, start)
            if pos == -1:
                break
            
            end_pos = pos + len(phrase)
            match_text = content[pos:end_pos]
            matches.append((match_text, pos, end_pos))
            start = pos + 1
        
        # 模糊匹配（简化版）
        if not matches:
            words = phrase_lower.split()
            if len(words) >= 3:
                # 查找包含大部分关键词的文本段
                for i in range(len(content) - len(phrase)):
                    segment = content_lower[i:i + len(phrase) + 50]
                    word_count = sum(1 for word in words if word in segment)
                    
                    if word_count >= len(words) * 0.7:  # 70%的词匹配
                        match_text = content[i:i + len(phrase)]
                        matches.append((match_text, i, i + len(phrase)))
                        break
        
        return matches
    
    def _calculate_citation_confidence(self, cited_text: str, chunk_content: str) -> float:
        """计算引用的置信度"""
        # 基于文本长度和匹配度的简单置信度计算
        base_confidence = 0.5
        
        # 长度奖励
        length_bonus = min(len(cited_text) / 100, 0.3)
        
        # 完整性奖励（是否是完整的句子或短语）
        completeness_bonus = 0.0
        if cited_text.strip().endswith(('.', '!', '?', '。', '！', '？')):
            completeness_bonus = 0.1
        
        # 位置奖励（在文档块中的相对位置）
        position_in_chunk = chunk_content.find(cited_text) / len(chunk_content)
        position_bonus = 0.1 if 0.2 <= position_in_chunk <= 0.8 else 0.0
        
        confidence = base_confidence + length_bonus + completeness_bonus + position_bonus
        return min(confidence, 1.0)
    
    def format_citations(self, citations: List[Citation]) -> str:
        """格式化引用信息为可读文本"""
        if not citations:
            return "无引用信息"
        
        formatted_citations = []
        for i, citation in enumerate(citations, 1):
            citation_text = (
                f"[{i}] 文档: {citation.document_id}, "
                f"页码: {citation.page_number}, "
                f"引用: \"{citation.text[:100]}{'...' if len(citation.text) > 100 else ''}\""
            )
            formatted_citations.append(citation_text)
        
        return "\n".join(formatted_citations)
    
    def validate_citations(self, citations: List[Citation]) -> List[Citation]:
        """验证和清理引用列表"""
        valid_citations = []
        
        for citation in citations:
            # 检查引用文本长度
            if (self.config.min_citation_length <= 
                len(citation.text) <= 
                self.config.max_citation_length):
                
                # 检查置信度
                if citation.confidence > 0.3:
                    valid_citations.append(citation)
        
        # 去重
        unique_citations = []
        seen_texts = set()
        
        for citation in valid_citations:
            if citation.text not in seen_texts:
                unique_citations.append(citation)
                seen_texts.add(citation.text)
        
        get_logger(self.__class__.__name__).info(f"验证后保留 {len(unique_citations)} 个有效引用")
        return unique_citations
    
    def get_citation_statistics(self, citations: List[Citation]) -> Dict[str, Any]:
        """获取引用统计信息"""
        if not citations:
            return {"total_citations": 0}
        
        return {
            "total_citations": len(citations),
            "avg_confidence": sum(c.confidence for c in citations) / len(citations),
            "avg_text_length": sum(len(c.text) for c in citations) / len(citations),
            "documents_cited": len(set(c.document_id for c in citations)),
            "pages_cited": len(set(c.page_number for c in citations if c.page_number))
        }