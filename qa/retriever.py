"""文档检索器模块

实现基于向量相似度的文档检索功能，支持语义搜索和混合检索策略。
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .models import DocumentChunk, Question
from agentdoc.core.logger import get_logger


@dataclass
class RetrievalConfig:
    """检索配置"""
    top_k: int = 5
    semantic_weight: float = 0.7
    keyword_weight: float = 0.3
    min_similarity: float = 0.1
    max_chunks_per_doc: int = 3
    enable_reranking: bool = True


class DocumentRetriever:
    """文档检索器
    
    基于向量相似度和关键词匹配的混合检索策略。
    """
    
    def __init__(self, config: Optional[RetrievalConfig] = None):
        self.config = config or RetrievalConfig()
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.tfidf_matrix = None
        self.chunks: List[DocumentChunk] = []
        self.chunk_texts: List[str] = []
        
    def add_chunks(self, chunks: List[DocumentChunk]):
        """添加文档块到检索索引"""
        self.chunks.extend(chunks)
        self.chunk_texts.extend([chunk.content for chunk in chunks])
        
        # 重新构建TF-IDF矩阵
        if self.chunk_texts:
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.chunk_texts)
            logger.info(f"已添加 {len(chunks)} 个文档块到检索索引")
    
    def clear_chunks(self):
        """清空所有文档块"""
        self.chunks.clear()
        self.chunk_texts.clear()
        self.tfidf_matrix = None
        logger.info("已清空检索索引")
    
    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[DocumentChunk]:
        """检索相关文档块
        
        Args:
            query: 查询文本
            top_k: 返回的最大结果数
            
        Returns:
            相关文档块列表
        """
        if not self.chunks:
            get_logger(self.__class__.__name__).warning("检索索引为空")
            return []
        
        k = top_k or self.config.top_k
        
        # 简化版检索实现
        query_text = query.lower()
        scored_chunks = []
        
        for chunk in self.chunks:
            # 简单的文本匹配评分
            content_lower = chunk.content.lower()
            score = 0.0
            
            # 关键词匹配
            query_words = query_text.split()
            for word in query_words:
                if word in content_lower:
                    score += 1.0
            
            # 标准化分数
            if query_words:
                score = score / len(query_words)
            
            if score >= self.config.min_similarity:
                scored_chunks.append((chunk, score))
        
        # 按分数排序并返回前K个
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        top_chunks = scored_chunks[:k]
        
        get_logger(self.__class__.__name__).info(f"检索到 {len(top_chunks)} 个相关文档块")
        return [chunk for chunk, _ in top_chunks]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取检索器统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "total_chunks": len(self.chunks),
            "config": {
                "top_k": self.config.top_k,
                "semantic_weight": self.config.semantic_weight,
                "keyword_weight": self.config.keyword_weight,
                "min_similarity": self.config.min_similarity,
                "max_chunks_per_doc": self.config.max_chunks_per_doc,
                "enable_reranking": self.config.enable_reranking
            }
        }