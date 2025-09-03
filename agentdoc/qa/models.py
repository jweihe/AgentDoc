"""问答系统数据模型

定义问答系统中使用的核心数据结构。
"""

from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class QuestionType(Enum):
    """问题类型枚举"""
    FACTUAL = "factual"  # 事实性问题
    REASONING = "reasoning"  # 推理性问题
    MULTI_HOP = "multi_hop"  # 多跳问题
    COMPARISON = "comparison"  # 比较性问题
    SUMMARIZATION = "summarization"  # 总结性问题


class ConfidenceLevel(Enum):
    """置信度等级"""
    HIGH = "high"  # 高置信度 (>0.8)
    MEDIUM = "medium"  # 中等置信度 (0.5-0.8)
    LOW = "low"  # 低置信度 (<0.5)


@dataclass
class Citation:
    """引用信息"""
    document_id: str  # 文档ID
    page_number: Optional[int] = None  # 页码
    chunk_id: Optional[str] = None  # 文档块ID
    start_position: Optional[int] = None  # 开始位置
    end_position: Optional[int] = None  # 结束位置
    text: Optional[str] = None  # 引用文本
    confidence: float = 0.0  # 引用置信度
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'document_id': self.document_id,
            'page_number': self.page_number,
            'chunk_id': self.chunk_id,
            'start_position': self.start_position,
            'end_position': self.end_position,
            'text': self.text,
            'confidence': self.confidence
        }


@dataclass
class DocumentChunk:
    """文档块"""
    chunk_id: str  # 块ID
    document_id: str  # 文档ID
    content: str  # 内容
    page_number: Optional[int] = None  # 页码
    start_position: int = 0  # 开始位置
    end_position: int = 0  # 结束位置
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据
    embedding: Optional[List[float]] = None  # 向量嵌入
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'chunk_id': self.chunk_id,
            'document_id': self.document_id,
            'content': self.content,
            'page_number': self.page_number,
            'start_position': self.start_position,
            'end_position': self.end_position,
            'metadata': self.metadata,
            'embedding': self.embedding
        }


@dataclass
class ReasoningStep:
    """推理步骤"""
    step_id: str  # 步骤ID
    description: str  # 步骤描述
    input_data: Dict[str, Any]  # 输入数据
    output_data: Dict[str, Any]  # 输出数据
    citations: List[Citation] = field(default_factory=list)  # 相关引用
    confidence: float = 0.0  # 置信度
    reasoning_type: str = "deduction"  # 推理类型
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'step_id': self.step_id,
            'description': self.description,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'citations': [c.to_dict() for c in self.citations],
            'confidence': self.confidence,
            'reasoning_type': self.reasoning_type
        }


@dataclass
class Question:
    """问题"""
    question_id: str  # 问题ID
    text: str  # 问题文本
    question_type: QuestionType = QuestionType.FACTUAL  # 问题类型
    context: Optional[str] = None  # 上下文
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据
    created_at: datetime = field(default_factory=datetime.now)  # 创建时间
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'question_id': self.question_id,
            'text': self.text,
            'question_type': self.question_type.value,
            'context': self.context,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class Answer:
    """答案"""
    answer_id: str  # 答案ID
    text: str  # 答案文本
    confidence: float  # 置信度
    confidence_level: ConfidenceLevel  # 置信度等级
    citations: List[Citation] = field(default_factory=list)  # 引用列表
    precise_citations: Optional[List[Citation]] = field(default_factory=list)  # 精确引用列表
    reasoning_steps: List[ReasoningStep] = field(default_factory=list)  # 推理步骤
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据
    generated_at: datetime = field(default_factory=datetime.now)  # 生成时间
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'answer_id': self.answer_id,
            'text': self.text,
            'confidence': self.confidence,
            'confidence_level': self.confidence_level.value,
            'citations': [c.to_dict() for c in self.citations],
            'reasoning_steps': [s.to_dict() for s in self.reasoning_steps],
            'metadata': self.metadata,
            'generated_at': self.generated_at.isoformat()
        }


@dataclass
class QAResult:
    """问答结果"""
    question: Question  # 问题
    answer: Answer  # 答案
    processing_time: float  # 处理时间（秒）
    model_used: str  # 使用的模型
    retrieval_results: List[DocumentChunk] = field(default_factory=list)  # 检索结果
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'question': self.question.to_dict(),
            'answer': self.answer.to_dict(),
            'processing_time': self.processing_time,
            'model_used': self.model_used,
            'retrieval_results': [r.to_dict() for r in self.retrieval_results]
        }


@dataclass
class QASession:
    """问答会话"""
    session_id: str  # 会话ID
    qa_results: List[QAResult] = field(default_factory=list)  # 问答结果列表
    context: Dict[str, Any] = field(default_factory=dict)  # 会话上下文
    created_at: datetime = field(default_factory=datetime.now)  # 创建时间
    updated_at: datetime = field(default_factory=datetime.now)  # 更新时间
    
    def add_qa_result(self, qa_result: QAResult) -> None:
        """添加问答结果"""
        self.qa_results.append(qa_result)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'session_id': self.session_id,
            'qa_results': [r.to_dict() for r in self.qa_results],
            'context': self.context,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }