# -*- coding: utf-8 -*-
"""智能问答系统模块

提供基于文档内容的智能问答功能，包括：
- 文档索引和检索
- 精确问答
- 复杂推理和多跳问答
- 引用原文位置和页码
"""

from .engine import QAEngine, QAConfig
from .indexer import DocumentIndexer
from .retriever import DocumentRetriever, RetrievalConfig
from .citation import CitationManager, CitationConfig
from .reasoning import SimpleReasoner, ReasoningConfig
from .models import (
    Question,
    Answer,
    Citation,
    DocumentChunk,
    QAResult,
    ReasoningStep,
    QuestionType
)

__all__ = [
    'QAEngine',
    'QAConfig',
    'DocumentIndexer', 
    'DocumentRetriever',
    'RetrievalConfig',
    'CitationManager',
    'CitationConfig',
    'SimpleReasoner',
    'ReasoningConfig',
    'Question',
    'Answer',
    'Citation',
    'DocumentChunk',
    'QAResult',
    'ReasoningStep',
    'QuestionType'
]